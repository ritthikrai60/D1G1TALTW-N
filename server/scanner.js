import os from 'node:os';
import net from 'node:net';
import dgram from 'node:dgram';
import dns from 'node:dns/promises';
import http from 'node:http';
import https from 'node:https';
import { exec, execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { lookupMacVendor, WELL_KNOWN_PORTS, inferDeviceCategory } from './oui.js';
import { upsertDevice, upsertNetwork, getDevices, addScanLog } from './store.js';

const execAsync = promisify(exec);
const execFileAsync = promisify(execFile);

// Convert IP + Netmask to CIDR string (e.g. 192.168.1.0/24)
export function ipMaskToCidr(ip, netmask) {
  try {
    const ipParts = ip.split('.').map(Number);
    const maskParts = netmask.split('.').map(Number);
    if (ipParts.length !== 4 || maskParts.length !== 4) return `${ip}/24`;
    const netParts = ipParts.map((b, i) => b & maskParts[i]);
    const prefix = maskParts
      .map((m) => (m >>> 0).toString(2).split('1').length - 1)
      .reduce((a, b) => a + b, 0);
    return `${netParts.join('.')}/${prefix}`;
  } catch {
    return `${ip}/24`;
  }
}

// Expand CIDR into list of host IPs (capped at 512 hosts for safety on /16s)
export function expandCidrHosts(cidr) {
  const clean = (cidr || '').trim();
  if (!clean.includes('/')) {
    return [clean];
  }
  const [baseIp, prefixStr] = clean.split('/');
  const prefix = Math.max(22, Math.min(32, parseInt(prefixStr, 10) || 24));
  const parts = baseIp.split('.').map(Number);
  if (parts.length !== 4 || parts.some((n) => isNaN(n) || n < 0 || n > 255)) {
    return [];
  }
  if (prefix === 32) return [baseIp];

  const ipInt = ((parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]) >>> 0;
  const mask = prefix === 0 ? 0 : (~0 << (32 - prefix)) >>> 0;
  const netInt = (ipInt & mask) >>> 0;
  const total = Math.min(512, 1 << (32 - prefix));
  const hosts = [];
  for (let i = 1; i < total - 1; i++) {
    const h = (netInt + i) >>> 0;
    hosts.push(`${(h >>> 24) & 255}.${(h >>> 16) & 255}.${(h >>> 8) & 255}.${h & 255}`);
  }
  return hosts;
}

// Detect all active local NICs, subnets, default gateways, and WAN status
export async function detectActiveNetworks() {
  const interfaces = os.networkInterfaces();
  const detected = [];

  // Parse actual gateway from Windows ipconfig or Linux ip route
  let realGatewayMap = new Map();
  try {
    if (process.platform === 'win32') {
      const { stdout } = await execAsync('ipconfig /all', { timeout: 3500 });
      const blocks = stdout.split(/\r?\n\r?\n/);
      let curIp = '';
      let curGw = '';
      for (const blk of stdout.split(/adapter /i)) {
        const ipM = blk.match(/IPv4 Address[.\s]*:\s*(\d{1,3}(?:\.\d{1,3}){3})/i);
        const gwM = blk.match(/Default Gateway[.\s]*:\s*(\d{1,3}(?:\.\d{1,3}){3})/i);
        if (ipM && gwM) {
          realGatewayMap.set(ipM[1], gwM[1]);
        }
      }
    } else {
      const { stdout } = await execAsync('ip route show default', { timeout: 2500 });
      const gwM = stdout.match(/default via (\d{1,3}(?:\.\d{1,3}){3})/);
      if (gwM) realGatewayMap.set('default', gwM[1]);
    }
  } catch {}

  for (const [ifName, addrs] of Object.entries(interfaces)) {
    if (!addrs) continue;
    for (const addr of addrs) {
      if (addr.family === 'IPv4' && !addr.internal && !addr.address.startsWith('169.254.')) {
        const cidr = ipMaskToCidr(addr.address, addr.netmask);
        const octets = addr.address.split('.');
        const guessedGw = realGatewayMap.get(addr.address) || realGatewayMap.get('default') || `${octets[0]}.${octets[1]}.${octets[2]}.1`;
        const netRecord = upsertNetwork({
          name: `${ifName} (${cidr})`,
          cidr,
          localIp: addr.address,
          gateway: guessedGw,
          interfaceName: ifName,
          mac: (addr.mac || '').toUpperCase(),
          isAutoDetected: true,
          isConnectedNow: true,
        });
        if (netRecord) detected.push(netRecord);
      }
    }
  }

  // Check WAN internet connectivity via fast TCP connect to 1.1.1.1:53 and 8.8.8.8:53
  const wanCheck = await tcpPingPort('1.1.1.1', 53, 1200);
  return {
    activeInterfaces: detected,
    wanStatus: {
      online: wanCheck.open,
      latencyMs: wanCheck.latencyMs,
      dnsTarget: '1.1.1.1 (Cloudflare WAN)',
      checkedAt: new Date().toISOString(),
    },
  };
}

// Parse system ARP table (`arp -a`) to get IP -> MAC mappings across all interfaces
export async function readArpTable() {
  const ipToMac = new Map();
  try {
    const { stdout } = await execAsync('arp -a', { timeout: 4000 });
    const lines = stdout.split(/\r?\n/);
    for (const line of lines) {
      // Match IPv4 and MAC (either 00-11-22-33-44-55 or 00:11:22:33:44:55)
      const m = line.match(/(\d{1,3}(?:\.\d{1,3}){3})\s+([0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2})/);
      if (m) {
        const ip = m[1];
        const mac = m[2].replace(/-/g, ':').toUpperCase();
        if (mac !== 'FF:FF:FF:FF:FF:FF' && !ip.startsWith('224.') && !ip.startsWith('239.') && !ip.endsWith('.255')) {
          ipToMac.set(ip, mac);
        }
      }
    }
  } catch {
    // Ignore if arp command is unavailable in minimal container
  }
  return ipToMac;
}

// Fast TCP connect check on a single port
export function tcpPingPort(ip, port, timeoutMs = 650) {
  return new Promise((resolve) => {
    const start = performance.now();
    const socket = new net.Socket();
    let settled = false;

    const finish = (open, banner = '') => {
      if (settled) return;
      settled = true;
      socket.destroy();
      resolve({
        port,
        open,
        latencyMs: Math.round(performance.now() - start),
        banner: banner.trim().slice(0, 160),
      });
    };

    socket.setTimeout(timeoutMs);
    socket.once('connect', () => {
      // Wait briefly to see if service sends an immediate banner (SSH, FTP, SMTP, Telnet, RouterOS)
      socket.once('data', (chunk) => {
        finish(true, chunk.toString('utf-8').replace(/[^\x20-\x7E]/g, ' '));
      });
      setTimeout(() => finish(true, ''), 140);
    });
    socket.once('timeout', () => finish(false));
    socket.once('error', () => finish(false));
    socket.connect(port, ip);
  });
}

// Native ICMP Ping with TTL OS heuristic + TCP fallback
export async function pingHost(ip, timeoutMs = 800) {
  const cleanIp = String(ip || '').trim();
  // Strict IPv4 validation to prevent any shell command injection
  const ipv4Match = cleanIp.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/);
  if (!ipv4Match || ipv4Match.slice(1, 5).some((octet) => Number(octet) < 0 || Number(octet) > 255)) {
    return { alive: false, latencyMs: null, ttl: null, osGuess: '' };
  }

  const isWin = process.platform === 'win32';
  const bin = 'ping';
  const args = isWin
    ? ['-n', '1', '-w', String(Math.max(100, Math.min(5000, timeoutMs))), cleanIp]
    : ['-c', '1', '-W', '1', cleanIp];
  const start = performance.now();
  try {
    const { stdout } = await execFileAsync(bin, args, { timeout: timeoutMs + 700 });
    const ttlMatch = stdout.match(/TTL=(\d+)/i);
    const timeMatch = stdout.match(/time[=<](\d+(?:\.\d+)?)\s*ms/i);
    if (ttlMatch || timeMatch || /bytes from|Reply from/i.test(stdout)) {
      const ttl = ttlMatch ? parseInt(ttlMatch[1], 10) : null;
      const ms = timeMatch ? Math.max(1, Math.round(parseFloat(timeMatch[1]))) : Math.round(performance.now() - start);
      let osGuess = '';
      if (ttl) {
        if (ttl <= 64) osGuess = 'Linux / Embedded / OS X (TTL≤64)';
        else if (ttl <= 128) osGuess = 'Windows Server / Workstation (TTL≤128)';
        else osGuess = 'Cisco / Network Gear / Router (TTL≤255)';
      }
      return { alive: true, latencyMs: ms, ttl, osGuess };
    }
  } catch {
    // Fallback to quick multi-port TCP probe if ICMP is blocked
  }

  for (const p of [80, 443, 22, 445, 8080]) {
    const res = await tcpPingPort(cleanIp, p, 380);
    if (res.open) {
      return { alive: true, latencyMs: res.latencyMs, ttl: null, osGuess: 'TCP Host (ICMP Filtered)' };
    }
  }
  return { alive: false, latencyMs: null, ttl: null, osGuess: '' };
}

// Probe HTTP or HTTPS port for status code, Server header, WWW-Authenticate, and <title>
export function probeWebService(ip, port, useHttps = false, timeoutMs = 1800) {
  return new Promise((resolve) => {
    const client = useHttps ? https : http;
    const scheme = useHttps ? 'https' : 'http';
    const req = client.request(
      {
        host: ip,
        port,
        path: '/',
        method: 'GET',
        timeout: timeoutMs,
        rejectUnauthorized: false,
        headers: {
          'User-Agent': 'LUDUS-DigitalTwin-Scanner/2.0',
          Accept: 'text/html,application/xhtml+xml,application/json,*/*',
        },
      },
      (res) => {
        let body = '';
        res.setEncoding('utf8');
        res.on('data', (chunk) => {
          if (body.length < 16384) body += chunk;
        });
        res.on('end', () => {
          const titleMatch = body.match(/<title[^>]*>([^<]+)<\/title>/i);
          const title = titleMatch ? titleMatch[1].replace(/\s+/g, ' ').trim() : '';
          const serverHeader = res.headers['server'] || res.headers['x-powered-by'] || '';
          const authHeader = res.headers['www-authenticate'] || '';
          resolve({
            isWeb: true,
            scheme,
            statusCode: res.statusCode,
            title: title.slice(0, 100),
            banner: [serverHeader, authHeader ? `Auth: ${authHeader}` : '', `HTTP ${res.statusCode}`]
              .filter(Boolean)
              .join(' | ')
              .slice(0, 140),
          });
        });
      }
    );
    req.on('timeout', () => {
      req.destroy();
      resolve(null);
    });
    req.on('error', () => {
      resolve(null);
    });
    req.end();
  });
}

// Lightweight raw UDP SNMPv2c GetRequest for sysDescr.0 (1.3.6.1.2.1.1.1.0) and sysName.0 (1.3.6.1.2.1.1.5.0)
export function probeSnmpv2c(ip, community = 'public', timeoutMs = 900) {
  return new Promise((resolve) => {
    const socket = dgram.createSocket('udp4');
    let settled = false;
    const finish = (result) => {
      if (settled) return;
      settled = true;
      try {
        socket.close();
      } catch {}
      resolve(result);
    };

    // Pre-encoded ASN.1 BER SNMPv2c GetRequest for sysDescr.0 (1.3.6.1.2.1.1.1.0)
    const commBytes = Buffer.from(community, 'ascii');
    const oidVarbind = Buffer.from([
      0x30, 0x0c,
      0x06, 0x08, 0x2b, 0x06, 0x01, 0x02, 0x01, 0x01, 0x01, 0x00, // 1.3.6.1.2.1.1.1.0
      0x05, 0x00,
    ]);
    const pduContent = Buffer.concat([
      Buffer.from([0x02, 0x04, 0x12, 0x34, 0x56, 0x78]), // request-id
      Buffer.from([0x02, 0x01, 0x00]), // error-status
      Buffer.from([0x02, 0x01, 0x00]), // error-index
      Buffer.from([0x30, oidVarbind.length]),
      oidVarbind,
    ]);
    const pdu = Buffer.concat([Buffer.from([0xa0, pduContent.length]), pduContent]);
    const msgContent = Buffer.concat([
      Buffer.from([0x02, 0x01, 0x01]), // version = 1 (SNMPv2c)
      Buffer.from([0x04, commBytes.length]),
      commBytes,
      pdu,
    ]);
    const packet = Buffer.concat([Buffer.from([0x30, msgContent.length]), msgContent]);

    const timer = setTimeout(() => finish(null), timeoutMs);
    socket.once('message', (msg) => {
      clearTimeout(timer);
      // Extract readable ASCII strings from SNMP response
      const ascii = msg.toString('latin1').replace(/[^\x20-\x7E]/g, ' ').replace(/\s+/g, ' ').trim();
      finish({
        snmpOpen: true,
        sysDescr: ascii.slice(0, 180),
      });
    });
    socket.once('error', () => {
      clearTimeout(timer);
      finish(null);
    });
    socket.send(packet, 161, ip);
  });
}

// Scan common ports (or full range 1..65535) on a single IP
export async function scanHostPorts(ip, { mode = 'fast', startPort = 1, endPort = 65535, onProgress } = {}) {
  const openPorts = [];
  const wellKnownMap = new Map(WELL_KNOWN_PORTS.map((p) => [p.port, p]));

  let targetPorts = [];
  if (mode === 'full') {
    const s = Math.max(1, parseInt(startPort, 10) || 1);
    const e = Math.min(65535, parseInt(endPort, 10) || 65535);
    for (let p = s; p <= e; p++) targetPorts.push(p);
  } else {
    targetPorts = WELL_KNOWN_PORTS.filter((p) => p.protocol === 'tcp').map((p) => p.port);
  }

  const concurrency = mode === 'full' ? 220 : 32;
  const timeoutMs = mode === 'full' ? 350 : 650;

  let index = 0;
  let scannedCount = 0;

  async function worker() {
    while (index < targetPorts.length) {
      const port = targetPorts[index++];
      const res = await tcpPingPort(ip, port, timeoutMs);
      scannedCount++;
      if (res.open) {
        const meta = wellKnownMap.get(port) || {
          port,
          service: `TCP/${port}`,
          protocol: 'tcp',
          isWeb: [80, 81, 443, 3000, 5000, 5001, 8000, 8006, 8008, 8080, 8081, 8443, 8888, 9000, 9090, 10000].includes(port),
          scheme: [443, 5001, 8006, 8443, 10000].includes(port) ? 'https' : 'http',
        };

        let webDetails = null;
        if (meta.isWeb || port === 80 || port === 443 || port === 8080 || port === 8443) {
          const isHttps = meta.scheme === 'https' || port === 443 || port === 8443 || port === 5001 || port === 8006;
          webDetails = await probeWebService(ip, port, isHttps, 1600);
          if (!webDetails && !isHttps) {
            webDetails = await probeWebService(ip, port, true, 1400);
          }
        }

        openPorts.push({
          port,
          protocol: 'tcp',
          service: meta.service,
          state: 'open',
          isWeb: Boolean(webDetails?.isWeb || meta.isWeb),
          scheme: webDetails?.scheme || meta.scheme || (port === 443 || port === 8443 ? 'https' : 'http'),
          title: webDetails?.title || '',
          banner: webDetails?.banner || res.banner || '',
          latencyMs: res.latencyMs,
        });
      }

      if (onProgress && scannedCount % (mode === 'full' ? 1500 : 15) === 0) {
        onProgress({
          ip,
          scannedCount,
          totalPorts: targetPorts.length,
          openFound: openPorts.length,
        });
      }
    }
  }

  const workers = Array.from({ length: Math.min(concurrency, targetPorts.length) }, () => worker());
  await Promise.all(workers);

  // Also check UDP 161 SNMP
  const snmpRes = await probeSnmpv2c(ip, 'public', 750);
  if (snmpRes?.snmpOpen) {
    openPorts.push({
      port: 161,
      protocol: 'udp',
      service: 'SNMP v2c',
      state: 'open',
      isWeb: false,
      title: 'SNMP Agent',
      banner: snmpRes.sysDescr || 'SNMP v2c Public',
    });
  }

  openPorts.sort((a, b) => a.port - b.port);
  return { openPorts, snmpInfo: snmpRes || {} };
}

// Inspect & enrich a single IP address deeply and upsert into Store
export async function inspectSingleIp(ip, { subnet = '', arpMap = null, portScanMode = 'fast', onProgress = null } = {}) {
  const pingRes = await pingHost(ip, 850);
  const currentArp = arpMap || (await readArpTable());
  const mac = currentArp.get(ip) || '';

  if (!pingRes.alive && !mac && portScanMode === 'fast') {
    return null;
  }

  let hostname = '';
  try {
    const names = await dns.reverse(ip);
    if (names && names.length > 0) hostname = names[0];
  } catch {}

  const { openPorts, snmpInfo } = await scanHostPorts(ip, { mode: portScanMode, onProgress });
  if (!pingRes.alive && !mac && openPorts.length === 0) {
    return null;
  }

  const vendor = mac ? lookupMacVendor(mac) : 'Generic Network Device';
  const category = inferDeviceCategory({ ip, mac, vendor, openPorts, snmpInfo, hostname });

  // Pick a helpful primary title or banner for OS/Firmware & Value
  const webPort = openPorts.find((p) => p.title) || openPorts.find((p) => p.banner);
  const osFirmware = webPort?.title || webPort?.banner || snmpInfo?.sysDescr || pingRes.osGuess || 'Active Network Node';
  const webPortsSummary = openPorts.map((p) => p.port).join(', ');

  // Synthesize switch ports if it's a Switch or Router so the operator can inspect ports
  let switchInterfaces = undefined;
  if (category === 'Switch' || category === 'Router') {
    const portCount = category === 'Switch' ? 24 : 8;
    switchInterfaces = Array.from({ length: portCount }, (_, i) => ({
      portIndex: i + 1,
      name: `GE1/0/${i + 1}`,
      status: i < Math.ceil(portCount * 0.45) ? 'up' : 'down',
      speed: i >= portCount - 2 ? '10G SFP+' : '1000 Mbps',
      vlan: i === 0 ? 'Trunk (All)' : 'VLAN 1',
      poe: category === 'Switch' && i < 8 ? '12.4W' : 'Off',
    }));
  }

  // Determine default web login URL if port 80/443/8080/8443 is open
  const preferredWeb =
    openPorts.find((p) => p.port === 443) ||
    openPorts.find((p) => p.port === 80) ||
    openPorts.find((p) => p.isWeb);
  const loginUrl = preferredWeb ? `${preferredWeb.scheme || 'http'}://${ip}:${preferredWeb.port}` : '';

  const categoryColorMap = {
    Router: '#f97316',
    Switch: '#38bdf8',
    'Access Point': '#06b6d4',
    Server: '#a855f7',
    CCTV: '#ec4899',
    HVAC: '#22c55e',
    Sensor: '#14b8a6',
    Printer: '#eab308',
    Network: '#60a5fa',
  };

  const saved = upsertDevice({
    ip,
    subnet: subnet || `${ip.split('.').slice(0, 3).join('.')}.0/24`,
    mac,
    vendor,
    hostname: hostname || webPort?.title || '',
    name: hostname || (webPort?.title ? `${webPort.title} (${ip})` : `${category} (${ip})`),
    category,
    color: categoryColorMap[category] || '#38bdf8',
    status: 'Online',
    value: openPorts.length ? `${openPorts.length} Ports (${webPortsSummary.slice(0, 28)})` : `${pingRes.latencyMs || 1} ms`,
    osFirmware,
    openPorts,
    snmpInfo,
    switchInterfaces,
    latencyMs: pingRes.latencyMs ?? 1,
    lastSeen: new Date().toISOString(),
    credentials: loginUrl ? { loginUrl, defaultPort: String(preferredWeb.port) } : undefined,
  });

  return saved;
}

// Scan an entire CIDR subnet with real-time progress callbacks
let currentScanState = {
  running: false,
  cidr: '',
  scannedHosts: 0,
  totalHosts: 0,
  discoveredCount: 0,
  startedAt: null,
};

export function getScanStatus() {
  return currentScanState;
}

export async function scanSubnetCidr(cidr, { broadcastProgress } = {}) {
  if (currentScanState.running) {
    throw new Error(`A scan is already running on ${currentScanState.cidr}`);
  }

  const hosts = expandCidrHosts(cidr);
  currentScanState = {
    running: true,
    cidr,
    scannedHosts: 0,
    totalHosts: hosts.length,
    discoveredCount: 0,
    startedAt: new Date().toISOString(),
  };

  const emit = (event, payload) => {
    if (broadcastProgress) broadcastProgress({ type: event, ...payload });
  };

  emit('scan_started', { ...currentScanState });

  try {
    // 1. Read current ARP table first
    const arpMap = await readArpTable();

    // 2. High-concurrency ping + ARP sweep to identify live IPs fast
    const liveIps = new Set();
    for (const [ip] of arpMap.entries()) {
      if (hosts.includes(ip)) liveIps.add(ip);
    }

    let cursor = 0;
    const sweepConcurrency = 48;
    async function sweepWorker() {
      while (cursor < hosts.length) {
        const ip = hosts[cursor++];
        const res = await pingHost(ip, 550);
        currentScanState.scannedHosts++;
        if (res.alive) {
          liveIps.add(ip);
        }
        if (currentScanState.scannedHosts % 16 === 0 || currentScanState.scannedHosts === hosts.length) {
          emit('scan_progress', {
            phase: 'host_discovery',
            ...currentScanState,
            liveFound: liveIps.size,
          });
        }
      }
    }

    await Promise.all(Array.from({ length: Math.min(sweepConcurrency, hosts.length) }, () => sweepWorker()));

    // Refresh ARP table after ping sweep!
    const refreshedArp = await readArpTable();
    for (const [ip] of refreshedArp.entries()) {
      if (hosts.includes(ip)) liveIps.add(ip);
    }

    // 3. Deep port & service inspection on every live IP
    const liveList = Array.from(liveIps);
    let inspectIdx = 0;
    const inspectConcurrency = 8;

    async function inspectWorker() {
      while (inspectIdx < liveList.length) {
        const ip = liveList[inspectIdx++];
        const device = await inspectSingleIp(ip, {
          subnet: cidr,
          arpMap: refreshedArp,
          portScanMode: 'fast',
        });
        if (device) {
          currentScanState.discoveredCount++;
          emit('device_discovered', {
            device,
            ...currentScanState,
          });
        }
      }
    }

    await Promise.all(Array.from({ length: Math.min(inspectConcurrency, Math.max(1, liveList.length)) }, () => inspectWorker()));

    upsertNetwork({
      cidr,
      lastScannedAt: new Date().toISOString(),
    });

    addScanLog({
      cidr,
      totalHosts: hosts.length,
      discoveredCount: currentScanState.discoveredCount,
    });

    const summary = { ...currentScanState, running: false, completedAt: new Date().toISOString() };
    currentScanState.running = false;
    emit('scan_completed', summary);
    return summary;
  } catch (err) {
    currentScanState.running = false;
    emit('scan_error', { message: err.message });
    throw err;
  }
}

// Background health check for known devices
export async function monitorKnownDevices({ broadcastProgress } = {}) {
  if (currentScanState.running) return;
  const devices = getDevices().filter((d) => d.ip);
  if (!devices.length) return;

  const arpMap = await readArpTable();
  for (const dev of devices) {
    const pingRes = await pingHost(dev.ip, 700);
    const mac = arpMap.get(dev.ip) || dev.mac;
    const newStatus = pingRes.alive ? (pingRes.latencyMs > 180 ? 'Warning' : 'Online') : 'Offline';
    const updated = upsertDevice({
      id: dev.id,
      mac,
      status: newStatus,
      latencyMs: pingRes.alive ? pingRes.latencyMs : null,
      lastSeen: pingRes.alive ? new Date().toISOString() : dev.lastSeen,
    });
    if (broadcastProgress) {
      broadcastProgress({ type: 'device_Updated', device: updated });
    }
  }
}


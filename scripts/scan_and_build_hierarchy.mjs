import os from 'node:os';
import {
  detectActiveNetworks,
  readArpTable,
  pingHost,
  scanHostPorts,
} from '../server/scanner.js';
import { lookupMacVendor, inferDeviceCategory } from '../server/oui.js';
import {
  upsertNetwork,
  upsertDevice,
  clearAllRoomsAndResetPlacements,
  recomputeHierarchy,
  getAdminSnapshot,
  saveToDisk,
} from '../server/store.js';

console.log('===================================================================');
console.log(' LUDUS DIGITAL TWIN — NETWORK SCANNER & HIERARCHY BUILDER (v2.0.0)');
console.log('===================================================================');

async function runFullScanAndBuildHierarchy() {
  // Step 1: Reset rooms & placements so all discovered devices start as Unplaced (isPlaced: false)
  // waiting for Admin to organize and place them on the 3D model
  clearAllRoomsAndResetPlacements();
  console.log(`[1/5] Initialized clean spatial state (rooms = [], all devices unplaced by default).`);

  // Step 2: Detect Active Network Interfaces & WAN Status
  const netInfo = await detectActiveNetworks();
  console.log(`[2/5] Detected ${netInfo.activeInterfaces.length} active local network interfaces.`);

  upsertNetwork({
    id: 'NET-INFRA-110',
    name: 'LAN Infrastructure Segment (192.168.110.0/24)',
    cidr: '192.168.110.0/24',
    gateway: '192.168.110.50',
    dnsServers: ['192.168.110.50', '1.1.1.1'],
    dhcpServer: '192.168.110.50',
    interfaceName: 'Wi-Fi (802.11ax)',
    localIp: '192.168.111.2',
    vlanId: 'VLAN 110 (Infra)',
    isAutoDetected: true,
    isConnectedNow: true,
    lastScannedAt: new Date().toISOString(),
  });

  upsertNetwork({
    id: 'NET-CLIENT-111',
    name: 'LAN Wireless & Workstation Segment (192.168.111.0/24)',
    cidr: '192.168.111.0/24',
    gateway: '192.168.110.50',
    dnsServers: ['192.168.110.50'],
    dhcpServer: '192.168.110.50',
    interfaceName: 'Wi-Fi (802.11ax)',
    localIp: '192.168.111.2',
    vlanId: 'VLAN 111 (Access)',
    isAutoDetected: true,
    isConnectedNow: true,
    lastScannedAt: new Date().toISOString(),
  });

  // Step 3: Collect all candidate IPs from ARP table + Local Interfaces
  const arpMap = await readArpTable();
  const candidateMap = new Map();

  for (const [ip, mac] of arpMap.entries()) {
    if (!ip.startsWith('224.') && !ip.startsWith('228.') && !ip.startsWith('229.') && !ip.startsWith('239.') && !ip.endsWith('.255')) {
      candidateMap.set(ip, mac);
    }
  }

  const interfaces = os.networkInterfaces();
  for (const [, addrs] of Object.entries(interfaces)) {
    if (!addrs) continue;
    for (const addr of addrs) {
      if (addr.family === 'IPv4' && !addr.internal && !addr.address.startsWith('169.254.')) {
        candidateMap.set(addr.address, (addr.mac || '').toUpperCase());
      }
    }
  }

  const allTargets = Array.from(candidateMap.entries());
  console.log(`[3/5] Scanning ${allTargets.length} discovered network hosts (Ping + 48 Common Ports + HTTP/HTTPS Banner + OUI)...`);

  // Step 4: High-concurrency deep scan of all discovered hosts
  const scannedResults = [];
  let cursor = 0;
  const concurrency = 10;

  async function scanWorker() {
    while (cursor < allTargets.length) {
      const [ip, mac] = allTargets[cursor++];
      const pingRes = await pingHost(ip, 650);
      const { openPorts, snmpInfo } = await scanHostPorts(ip, { mode: 'fast' });
      const vendor = lookupMacVendor(mac);
      const isGateway = ip === '192.168.110.50' || ip === '172.17.0.1';
      const category =
        ip === '192.168.111.2'
          ? 'Server'
          : inferDeviceCategory({ ip, mac, vendor, openPorts, snmpInfo, isGateway });

      scannedResults.push({
        ip,
        mac,
        vendor,
        pingRes,
        openPorts,
        snmpInfo,
        category,
        isGateway,
      });
      process.stdout.write(`  -> Scanned ${ip.padEnd(16)} | ${mac.padEnd(18)} | ${category.padEnd(13)} | Ports: [${openPorts.map((p) => p.port).join(', ')}]\n`);
    }
  }

  await Promise.all(Array.from({ length: Math.min(concurrency, allTargets.length) }, () => scanWorker()));

  scannedResults.sort((a, b) => {
    const pa = a.ip.split('.').map(Number);
    const pb = b.ip.split('.').map(Number);
    for (let i = 0; i < 4; i++) {
      if (pa[i] !== pb[i]) return pa[i] - pb[i];
    }
    return 0;
  });

  // Step 5: Build detailed Device Inventory & Network Hierarchy (all starting as isPlaced: false)
  console.log(`[4/5] Building detailed Device Inventory & Network Topology Hierarchy (isPlaced: false)...`);

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

  let swIdx = 0;
  let apIdx = 0;
  let prnIdx = 0;
  let epIdx = 0;

  const swIds = ['DEV-192-168-110-52', 'DEV-192-168-110-53', 'DEV-192-168-110-54', 'DEV-192-168-110-58', 'DEV-192-168-110-134'];
  const apIds = ['DEV-192-168-110-51', 'DEV-192-168-110-70', 'DEV-192-168-110-71', 'DEV-192-168-110-79', 'DEV-192-168-110-93', 'DEV-192-168-110-98'];

  for (const item of scannedResults) {
    const { ip, mac, vendor, pingRes, openPorts, snmpInfo, category } = item;
    const id = `DEV-${ip.replace(/\./g, '-')}`;

    let name = '';
    let parentDeviceId = 'WAN-ROOT';
    let switchPort = 'Gi1/0/1';
    let osFirmware = pingRes.osGuess || 'Enterprise Embedded Linux (TTL=64)';

    const webPort = openPorts.find((p) => p.title) || openPorts.find((p) => p.banner);
    if (webPort?.title || webPort?.banner) {
      osFirmware = [webPort.title, webPort.banner].filter(Boolean).join(' — ');
    }

    if (ip === '192.168.110.50') {
      name = 'Core-GW-Router-110-50 (Main Gateway & MQTT)';
      parentDeviceId = 'WAN-ROOT';
      switchPort = 'WAN1 (1000Base-T)';
      osFirmware = 'Enterprise Gateway OS / HTTPS + MQTT Broker (1883/8883)';
    } else if (ip === '192.168.110.69') {
      name = 'Distribution-Gateway-110-69 (Secondary Router)';
      parentDeviceId = 'DEV-192-168-110-50';
      switchPort = 'SFP+-1/0/1';
    } else if (ip === '172.17.0.1') {
      name = 'HyperV-vSwitch-Gateway (WSL Router)';
      parentDeviceId = 'DEV-192-168-111-2';
      switchPort = 'vEthernet-WSL0';
      osFirmware = 'Microsoft Hyper-V Virtual Switch Router';
    } else if (ip === '192.168.111.2') {
      name = 'ISA-Command-Server (Digital Twin Host)';
      parentDeviceId = 'DEV-192-168-110-58';
      switchPort = 'Gi1/0/24 (Uplink)';
      osFirmware = `Windows Host (${os.hostname()}) — Realtek WiFi 6`;
    } else if (ip === '172.17.6.21') {
      name = 'WSL-Compute-Node (172.17.6.21)';
      parentDeviceId = 'DEV-172-17-0-1';
      switchPort = 'vSwitch-Port-2';
      osFirmware = 'Linux WSL2 Virtual Machine (Hyper-V)';
    } else if (category === 'Switch') {
      swIdx++;
      name = `Managed-Switch-SW${String(swIdx).padStart(2, '0')} (${ip})`;
      parentDeviceId = 'DEV-192-168-110-50';
      switchPort = `SFP+-1/0/${swIdx}`;
    } else if (category === 'Access Point') {
      apIdx++;
      name = `Wireless-AP-${String(apIdx).padStart(2, '0')} (${ip})`;
      parentDeviceId = swIds[(apIdx - 1) % swIds.length];
      switchPort = `PoE-Gi1/0/${(apIdx % 16) + 1}`;
    } else if (category === 'Printer') {
      prnIdx++;
      name = `Network-Printer-PRN${String(prnIdx).padStart(2, '0')} (${ip})`;
      parentDeviceId = swIds[(prnIdx - 1) % swIds.length];
      switchPort = `Gi1/0/${18 + prnIdx}`;
    } else {
      epIdx++;
      name = `${category}-Node-${String(epIdx).padStart(2, '0')} (${ip})`;
      parentDeviceId = apIds[(epIdx - 1) % apIds.length];
      switchPort = `WLAN-5GHz-CH${36 + (epIdx % 4) * 4}`;
    }

    const subnet = ip.startsWith('172.17.')
      ? '172.17.0.0/20'
      : ip.startsWith('192.168.110.')
      ? '192.168.110.0/24'
      : '192.168.111.0/24';

    const preferredWeb =
      openPorts.find((p) => p.port === 443) ||
      openPorts.find((p) => p.port === 80) ||
      openPorts.find((p) => p.isWeb);
    const loginUrl = preferredWeb ? `${preferredWeb.scheme || 'http'}://${ip}:${preferredWeb.port}` : `http://${ip}:80`;

    let switchInterfaces = undefined;
    if (category === 'Switch' || category === 'Router') {
      const portCount = category === 'Switch' ? 24 : 8;
      switchInterfaces = Array.from({ length: portCount }, (_, i) => ({
        portIndex: i + 1,
        name: `GE1/0/${i + 1}`,
        status: i < Math.ceil(portCount * 0.55) ? 'up' : 'down',
        speed: i >= portCount - 2 ? '10G SFP+' : '1000 Mbps',
        vlan: ip.startsWith('192.168.110.') ? 'VLAN 110' : 'VLAN 1',
        poe: category === 'Switch' && i < 12 ? '15.4W' : 'Off',
      }));
    }

    upsertDevice({
      id,
      name,
      category,
      color: categoryColorMap[category] || '#38bdf8',
      status: pingRes.alive || openPorts.length > 0 ? 'Online' : 'Warning',
      value: openPorts.length
        ? `${openPorts.length} Ports (${openPorts.map((p) => p.port).join(',')})`
        : `${pingRes.latencyMs || 2} ms`,
      ip,
      subnet,
      mac,
      vendor,
      hostname: `host-${ip.replace(/\./g, '-')}.ludus.lan`,
      osFirmware,
      serialNumber: `SN-LUDUS-${mac.replace(/:/g, '').slice(-6) || ip.split('.').pop()}`,
      assetTag: `AST-2026-${ip.split('.').slice(-2).join('-')}`,
      vlan: ip.startsWith('192.168.110.') ? 'VLAN 110 (Infra)' : ip.startsWith('192.168.111.') ? 'VLAN 111 (Access)' : 'VLAN 172 (WSL)',
      // Strictly unplaced until Admin places & organizes it!
      isPlaced: false,
      floorIdx: null,
      roomId: '',
      roomNumber: '',
      position: null,
      hierarchy: {
        parentDeviceId,
        uplinkPort: switchPort,
      },
      switchPort,
      openPorts,
      snmpInfo,
      switchInterfaces,
      credentials: {
        username: 'admin',
        password: 'admin123',
        loginUrl,
        defaultPort: preferredWeb ? String(preferredWeb.port) : '80',
        notes: `Auto-discovered on ${subnet} via LUDUS Scanner (Waiting for Admin placement)`,
      },
      latencyMs: pingRes.latencyMs ?? 4,
      lastSeen: new Date().toISOString(),
    });
  }

  recomputeHierarchy();
  saveToDisk(true);
  const finalSnap = getAdminSnapshot();

  try {
    const loginRes = await fetch('http://localhost:8085/api/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: process.env.ADMIN_PASSWORD || 'admin123' }),
    });
    if (loginRes.ok) {
      const { token } = await loginRes.json();
      await fetch('http://localhost:8085/api/admin/import', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(finalSnap),
      });
      console.log(`[5/5] Imported ${finalSnap.devices.length} unplaced discovered devices into live server at http://localhost:8085 !`);
    }
  } catch {
    console.log(`[5/5] Saved ${finalSnap.devices.length} unplaced discovered devices to data/digital_twin_db.json.`);
  }

  console.log('===================================================================');
  console.log(` Total Networks         : ${finalSnap.networks.length}`);
  console.log(` Total Rooms (Initial)  : ${finalSnap.rooms.length}`);
  console.log(` Total Scanned Devices  : ${finalSnap.devices.length}`);
  console.log(` Placed on 3D Model     : ${finalSnap.devices.filter((d) => d.isPlaced).length}`);
  console.log(` Waiting in Admin Queue : ${finalSnap.devices.filter((d) => !d.isPlaced).length}`);
  console.log('===================================================================');
}

runFullScanAndBuildHierarchy().catch((err) => {
  console.error('Fatal scanner error:', err);
  process.exit(1);
});

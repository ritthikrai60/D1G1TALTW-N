import express from 'express';
import http from 'node:http';
import https from 'node:https';
import { load as yamlLoad, dump as yamlDump } from 'js-yaml';
import { WebSocketServer } from 'ws';
import { prisma } from './db.js';
import {
  verifyAdminPassword,
  isValidAdminToken,
  updateAdminPassword,
  getPublicSnapshot,
  getAdminSnapshot,
  getHierarchy,
  getRooms,
  upsertRoom,
  batchGenerateRooms,
  deleteRoom,
  getNetworks,
  upsertNetwork,
  deleteNetwork,
  getDevices,
  upsertDevice,
  deleteDevice,
  getDeviceById,
  replaceDevicePorts,
  importFullBundle,
  validateBundleSchema,
  updateDefaultViewState,
  getRackMountedItems,
  mountDeviceInRack,
  removeRackCascade,
  restoreRackCascade,
  unmountDeviceFromRack,
  updateRackConfig,
} from './store.js';
import {
  detectActiveNetworks,
  scanSubnetCidr,
  inspectSingleIp,
  scanHostPorts,
  pingHost,
  getScanStatus,
  monitorKnownDevices,
} from './scanner.js';

export const OPENAPI_SPEC = {
  openapi: '3.0.3',
  info: {
    title: 'LUDUS Building Digital Twin & Network Command API',
    version: '2.0.0',
    description:
      'REST API & WebSocket Specification for 3D Building Digital Twin, Multi-Network LAN/WAN Discovery, Hierarchical Topology (WAN -> Router -> Switch -> AP -> Endpoint), Spatial Room Management, and Port Inspection.',
  },
  servers: [{ url: 'http://localhost:8085', description: 'Local / Docker Digital Twin Server' }],
  paths: {
    '/api/health': {
      get: { summary: 'Health check & schema version', responses: { 200: { description: 'OK' } } },
    },
    '/api/public/state': {
      get: {
        summary: 'Get complete public state (networks, rooms, devices, and full hierarchy)',
        responses: { 200: { description: 'JSON Schema v2.0.0 State Snapshot' } },
      },
    },
    '/api/hierarchy': {
      get: {
        summary: 'Get computed Network Topology Tree & Spatial Building Tree',
        responses: { 200: { description: 'Network & Spatial Hierarchy Trees' } },
      },
    },
    '/api/networks': {
      get: { summary: 'List all detected and configured LAN/WAN networks', responses: { 200: { description: 'Array of networks' } } },
    },
    '/api/rooms': {
      get: {
        summary: 'List all building rooms (optional ?floorIdx=0..3)',
        responses: { 200: { description: 'Array of rooms' } },
      },
    },
    '/api/devices': {
      get: {
        summary: 'List all devices with optional filters (?floorIdx, ?category, ?status, ?subnet, ?tier, ?placed)',
        responses: { 200: { description: 'Filtered array of devices' } },
      },
    },
    '/api/devices/{id}': {
      get: { summary: 'Get single device details by ID', responses: { 200: { description: 'Device object' }, 404: { description: 'Not found' } } },
    },
    '/api/devices/{id}/ping': {
      post: { summary: 'Trigger live ICMP/TCP ping check on a device', responses: { 200: { description: 'Ping result & updated device' } } },
    },
    '/api/devices/{id}/scan-ports': {
      post: {
        summary: 'Scan ports on a device (mode: "fast" for 48 ports, or "full" for 1..65535)',
        responses: { 200: { description: 'Discovered openPorts & updated device' } },
      },
    },
    '/api/export': {
      get: { summary: 'Export complete JSON Schema v2.0.0 bundle', responses: { 200: { description: 'Full JSON Bundle' } } },
    },
    '/api/proxy': {
      get: { summary: 'Reverse proxy for embedded device web interface preview (?url=http://IP:Port)', responses: { 200: { description: 'Proxied HTML/Asset' } } },
    },
    '/api/admin/login': {
      post: { summary: 'Authenticate Admin password and obtain Bearer token', responses: { 200: { description: 'Token issued' }, 401: { description: 'Invalid password' } } },
    },
    '/api/admin/state': {
      get: { summary: 'Get full Admin snapshot (requires Bearer token)', responses: { 200: { description: 'Admin snapshot' } } },
    },
    '/api/admin/devices': {
      post: { summary: 'Create or update a device and recompute hierarchy (requires Bearer token)', responses: { 200: { description: 'Upserted device' } } },
    },
    '/api/admin/rooms': {
      post: { summary: 'Create or update a room (requires Bearer token)', responses: { 200: { description: 'Upserted room' } } },
    },
    '/api/admin/networks': {
      post: { summary: 'Register or update a network subnet/VLAN (requires Bearer token)', responses: { 200: { description: 'Upserted network' } } },
    },
    '/api/admin/scan/subnet': {
      post: { summary: 'Start asynchronous subnet discovery & port scan (requires Bearer token)', responses: { 200: { description: 'Scan started' } } },
    },
    '/api/admin/scan/ip': {
      post: { summary: 'Scan and inspect a single IP immediately (requires Bearer token)', responses: { 200: { description: 'Discovered device' } } },
    },
    '/api/admin/import': {
      post: { summary: 'Validate and import a JSON Schema v2.0.0 bundle (requires Bearer token)', responses: { 200: { description: 'Imported snapshot' } } },
    },
  },
};

export function createApiRouterAndWs() {
  const router = express.Router();
  router.use(express.json({ limit: '25mb' }));
  router.use(
    express.text({
      type: ['text/yaml', 'text/plain', 'application/x-yaml', 'application/yaml'],
      limit: '25mb',
    })
  );

  const wsClients = new Set();

  function broadcast(payload) {
    const msg = JSON.stringify(payload);
    for (const client of wsClients) {
      if (client.readyState === 1) {
        try {
          client.send(msg);
        } catch { }
      }
    }
  }

  let cachedNetInfo = { activeInterfaces: [], wanStatus: { online: true, latencyMs: 1 } };
  detectActiveNetworks()
    .then((info) => {
      cachedNetInfo = info;
    })
    .catch(() => { });

  const monitorTimer = setInterval(() => {
    monitorKnownDevices({ broadcastProgress: broadcast }).catch(() => { });
  }, 45000);
  if (monitorTimer.unref) monitorTimer.unref();

  function requireAdmin(req, res, next) {
    const authHeader = req.headers['authorization'] || '';
    const token = authHeader.replace(/^Bearer\s+/i, '').trim();
    if (isValidAdminToken(token)) {
      return next();
    }
    return res.status(401).json({ error: 'Unauthorized: Admin session required' });
  }

  // --- 0. Health, OpenAPI Spec & Interactive API Docs ---
  router.get('/health', async (req, res) => {
    let dbStatus = 'connected';
    try {
      await prisma.$queryRaw`SELECT 1`;
    } catch {
      dbStatus = 'disconnected';
    }
    res.json({
      ok: true,
      status: 'ok',
      service: 'rackula-persistence-api',
      version: 1,
      name: 'LUDUS Digital Twin & Network Command API',
      schemaVersion: '2.0.0',
      database: {
        type: 'PostgreSQL 16 (Prisma)',
        status: dbStatus,
      },
      uptimeSec: Math.round(process.uptime()),
      timestamp: new Date().toISOString(),
    });
  });

  router.get('/openapi.json', (req, res) => {
    res.json(OPENAPI_SPEC);
  });

  router.get('/docs', (req, res) => {
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.send(`<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8" />
  <title>LUDUS Digital Twin — API & JSON Schema v2.0.0 Documentation</title>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; background: #070d19; color: #e2e8f0; margin: 0; padding: 32px; line-height: 1.6; }
    .container { max-width: 1080px; margin: 0 auto; }
    h1, h2, h3 { color: #38bdf8; }
    code, pre { font-family: ui-monospace, monospace; background: #0f172a; color: #bae6fd; padding: 2px 6px; border-radius: 6px; }
    pre { padding: 14px; overflow-x: auto; border: 1px solid #1e293b; }
    .endpoint { background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 14px 18px; margin-bottom: 12px; }
    .method { font-weight: 700; padding: 3px 8px; border-radius: 5px; font-size: 12px; margin-right: 8px; }
    .GET { background: rgba(34,197,94,0.2); color: #4ade80; }
    .POST { background: rgba(56,189,248,0.2); color: #38bdf8; }
    .PUT { background: rgba(245,158,11,0.2); color: #fbbf24; }
    .DELETE { background: rgba(239,68,68,0.2); color: #f87171; }
    a { color: #38bdf8; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🏢 LUDUS Building Digital Twin — REST API & Hierarchy Docs (v2.0.0)</h1>
    <p>เอกสารอ้างอิง API และโครงสร้าง JSON Hierarchy สำหรับระบบ 3D Digital Twin & Multi-Network Scanner</p>
    <p><a href="/">⬅️ กลับหน้า 3D Viewer</a> | <a href="/api/openapi.json" target="_blank">📄 ดาวน์โหลด OpenAPI 3.0 JSON</a> | <a href="/api/hierarchy" target="_blank">🌳 ดู JSON Hierarchy ปัจจุบัน</a> | <a href="/api/export" target="_blank">⬇️ Export Full JSON Bundle</a></p>
    <h2>รายการ API Endpoints</h2>
    ${Object.entries(OPENAPI_SPEC.paths)
        .map(([p, methods]) =>
          Object.entries(methods)
            .map(
              ([m, info]) => `
        <div class="endpoint">
          <span class="method ${m.toUpperCase()}">${m.toUpperCase()}</span>
          <code>${p}</code>
          <div style="margin-top:6px;color:#94a3b8;font-size:14px;">${info.summary}</div>
        </div>`
            )
            .join('')
        )
        .join('')}
  </div>
</body>
</html>`);
  });

  // --- 1. Public & Query Endpoints ---
  router.get('/public/state', async (req, res) => {
    const netInfo = await detectActiveNetworks().catch(() => cachedNetInfo);
    cachedNetInfo = netInfo;
    res.json({
      ...getPublicSnapshot(),
      activeInterfaces: netInfo.activeInterfaces,
      wanStatus: netInfo.wanStatus,
      scanStatus: getScanStatus(),
    });
  });

  router.get('/hierarchy', (req, res) => {
    res.json({
      schemaVersion: '2.0.0',
      hierarchy: getHierarchy(),
    });
  });

  router.get('/networks', (req, res) => {
    res.json({ networks: getNetworks() });
  });

  router.get('/rooms', (req, res) => {
    let list = getRooms();
    if (req.query.floorIdx !== undefined) {
      list = list.filter((r) => Number(r.floorIdx) === Number(req.query.floorIdx));
    }
    res.json({ rooms: list });
  });

  router.get('/devices', (req, res) => {
    let list = getDevices();
    if (req.query.floorIdx !== undefined) {
      list = list.filter((d) => Number(d.floorIdx) === Number(req.query.floorIdx));
    }
    if (req.query.category) {
      list = list.filter((d) => d.category.toLowerCase() === String(req.query.category).toLowerCase());
    }
    if (req.query.status) {
      list = list.filter((d) => d.status.toLowerCase() === String(req.query.status).toLowerCase());
    }
    if (req.query.subnet) {
      list = list.filter((d) => d.subnet === req.query.subnet);
    }
    if (req.query.tier !== undefined) {
      list = list.filter((d) => Number(d.hierarchy?.tier) === Number(req.query.tier));
    }
    if (req.query.placed !== undefined) {
      const wantPlaced = req.query.placed === 'true' || req.query.placed === '1';
      list = list.filter((d) => Boolean(d.isPlaced) === wantPlaced);
    }
    res.json({ total: list.length, devices: list });
  });

  router.get('/devices/:id', (req, res) => {
    const dev = getDeviceById(req.params.id);
    if (!dev) return res.status(404).json({ error: 'Device not found' });
    res.json({ device: dev });
  });

  router.get('/export', (req, res) => {
    res.json(getPublicSnapshot());
  });

  // Live ping & quick status check for a single device
  router.post('/devices/:id/ping', async (req, res) => {
    const dev = getDeviceById(req.params.id);
    if (!dev || !dev.ip) return res.status(404).json({ error: 'Device or IP not found' });
    const pingRes = await pingHost(dev.ip, 1000);
    const updated = upsertDevice({
      id: dev.id,
      status: pingRes.alive ? 'Online' : 'Offline',
      latencyMs: pingRes.alive ? pingRes.latencyMs : null,
      lastSeen: pingRes.alive ? new Date().toISOString() : dev.lastSeen,
    });
    broadcast({ type: 'device_updated', device: updated });
    res.json({ ping: pingRes, device: updated });
  });

  // Port scan a single device (Fast 48 ports or Full 1-65535 range)
  router.post('/devices/:id/scan-ports', async (req, res) => {
    const dev = getDeviceById(req.params.id);
    if (!dev || !dev.ip) return res.status(404).json({ error: 'Device or IP not found' });
    const mode = req.body?.mode === 'full' ? 'full' : 'fast';
    const startPort = req.body?.startPort || 1;
    const endPort = req.body?.endPort || 65535;

    broadcast({
      type: 'port_scan_started',
      deviceId: dev.id,
      ip: dev.ip,
      mode,
    });

    try {
      const { openPorts, snmpInfo } = await scanHostPorts(dev.ip, {
        mode,
        startPort,
        endPort,
        onProgress: (prog) => {
          broadcast({
            type: 'port_scan_progress',
            deviceId: dev.id,
            ...prog,
          });
        },
      });
      const updated =
        mode === 'full'
          ? replaceDevicePorts(dev.id, openPorts)
          : upsertDevice({ id: dev.id, openPorts, snmpInfo, status: 'Online' });
      broadcast({ type: 'device_updated', device: updated });
      res.json({ device: updated, openPorts });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  // --- 2. Reverse Proxy for Embedded Device Web UI Preview ---
  router.get('/proxy', (req, res) => {
    const targetUrlStr = req.query.url;
    if (!targetUrlStr) return res.status(400).send('Missing ?url= parameter');

    let parsed;
    try {
      parsed = new URL(targetUrlStr);
    } catch {
      return res.status(400).send('Invalid target URL');
    }

    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      return res.status(400).send('Only HTTP and HTTPS proxying are supported');
    }

    const host = parsed.hostname.toLowerCase();
    // Block cloud metadata services and localhost loopback to prevent SSRF
    if (
      host === '169.254.169.254' ||
      host === 'metadata.google.internal' ||
      host.endsWith('.metadata.google.internal') ||
      host === 'localhost' ||
      host === '127.0.0.1' ||
      host === '::1' ||
      host === '0.0.0.0'
    ) {
      return res.status(403).send('Access to internal host is forbidden');
    }

    const isHttps = parsed.protocol === 'https:';
    const client = isHttps ? https : http;
    const port = parsed.port || (isHttps ? 443 : 80);

    const proxyReq = client.request(
      {
        hostname: parsed.hostname,
        port,
        path: parsed.pathname + parsed.search,
        method: 'GET',
        timeout: 6000,
        rejectUnauthorized: false,
        headers: {
          'User-Agent': req.headers['user-agent'] || 'Mozilla/5.0',
          Accept: req.headers['accept'] || '*/*',
        },
      },
      (proxyRes) => {
        const headers = { ...proxyRes.headers };
        delete headers['x-frame-options'];
        delete headers['content-security-policy'];
        delete headers['content-security-policy-report-only'];
        res.writeHead(proxyRes.statusCode || 200, headers);
        proxyRes.pipe(res);
      }
    );

    proxyReq.on('timeout', () => {
      proxyReq.destroy();
      if (!res.headersSent) res.status(504).send('Device web interface timed out');
    });

    proxyReq.on('error', (err) => {
      if (!res.headersSent) {
        res.status(502).send(`Cannot reach ${targetUrlStr}: ${err.message}`);
      }
    });

    proxyReq.end();
  });

  // --- 3. Admin Authentication ---
  router.post('/admin/login', (req, res) => {
    const { password } = req.body || {};
    const token = verifyAdminPassword(password);
    if (!token) {
      return res.status(401).json({ error: 'รหัสผ่านผู้ดูแลระบบไม่ถูกต้อง (Default: admin123)' });
    }
    return res.json({ token, ok: true });
  });

  router.get('/admin/verify', requireAdmin, (req, res) => {
    res.json({ ok: true });
  });

  router.post('/admin/password', requireAdmin, (req, res) => {
    const ok = updateAdminPassword(req.body?.newPassword);
    if (!ok) return res.status(400).json({ error: 'Password must be at least 4 characters' });
    res.json({ ok: true });
  });

  // --- 4. Admin Protected Endpoints ---
  router.get('/admin/state', requireAdmin, async (req, res) => {
    const netInfo = await detectActiveNetworks().catch(() => cachedNetInfo);
    cachedNetInfo = netInfo;
    res.json({
      ...getAdminSnapshot(),
      activeInterfaces: netInfo.activeInterfaces,
      wanStatus: netInfo.wanStatus,
      scanStatus: getScanStatus(),
    });
  });

  // Rooms CRUD
  router.post('/admin/rooms', requireAdmin, (req, res) => {
    const room = upsertRoom(req.body || {});
    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.json({ room });
  });

  router.put('/admin/rooms/:id', requireAdmin, (req, res) => {
    const room = upsertRoom({ ...(req.body || {}), id: req.params.id });
    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.json({ room });
  });

  router.post('/admin/rooms/batch', requireAdmin, (req, res) => {
    const rooms = batchGenerateRooms(req.body || {});
    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.json({ rooms, count: rooms.length });
  });

  router.delete('/admin/rooms/:id', requireAdmin, (req, res) => {
    deleteRoom(req.params.id);
    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.json({ ok: true });
  });

  // Networks CRUD
  router.post('/admin/networks', requireAdmin, (req, res) => {
    const net = upsertNetwork(req.body || {});
    if (!net) return res.status(400).json({ error: 'Invalid CIDR' });
    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.json({ network: net });
  });

  router.delete('/admin/networks/:id', requireAdmin, (req, res) => {
    deleteNetwork(req.params.id);
    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.json({ ok: true });
  });

  // Trigger Subnet Scan
  router.post('/admin/scan/subnet', requireAdmin, async (req, res) => {
    const cidr = (req.body?.cidr || '').trim();
    if (!cidr) return res.status(400).json({ error: 'Missing subnet CIDR (e.g. 192.168.1.0/24)' });

    if (getScanStatus().running) {
      return res.status(409).json({ error: 'Scan already in progress', scanStatus: getScanStatus() });
    }

    scanSubnetCidr(cidr, { broadcastProgress: broadcast }).catch((err) => {
      console.error('[Scanner] Subnet scan error:', err.message);
    });

    res.json({ started: true, cidr, scanStatus: getScanStatus() });
  });

  router.get('/admin/scan/status', requireAdmin, (req, res) => {
    res.json({ scanStatus: getScanStatus() });
  });

  // Scan & add a single target IP immediately
  router.post('/admin/scan/ip', requireAdmin, async (req, res) => {
    const ip = (req.body?.ip || '').trim();
    const mode = req.body?.mode === 'full' ? 'full' : 'fast';
    if (!ip) return res.status(400).json({ error: 'Missing IP address' });

    const dev = await inspectSingleIp(ip, { portScanMode: mode });
    if (!dev) {
      return res.status(404).json({ error: `Host ${ip} did not respond to Ping, ARP, or Port probes` });
    }
    broadcast({ type: 'device_discovered', device: dev });
    res.json({ device: dev });
  });

  // Devices CRUD
  router.post('/admin/devices', requireAdmin, (req, res) => {
    const dev = upsertDevice(req.body || {});
    broadcast({ type: 'device_updated', device: dev });
    res.json({ device: dev });
  });

  router.put('/admin/devices/:id', requireAdmin, (req, res) => {
    const dev = upsertDevice({ ...(req.body || {}), id: req.params.id });
    broadcast({ type: 'device_updated', device: dev });
    res.json({ device: dev });
  });

  router.post('/admin/devices/:id/unplace', requireAdmin, (req, res) => {
    const dev = getDeviceById(req.params.id);
    if (!dev) return res.status(404).json({ error: 'Device not found' });
    // A rack cannot be parked: removing it from 3D removes it from Rackula too (single source of truth)
    if (dev.modelType === 'server_rack') {
      const removed = removeRackCascade(dev.id);
      if (!removed.ok) return res.status(400).json({ error: removed.error });
      broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
      return res.json({ rackRemoved: true, ...removed });
    }
    const updated = upsertDevice({
      ...dev,
      id: dev.id,
      isPlaced: false,
      floorIdx: null,
      roomId: '',
      roomNumber: '',
      position: null,
    });
    broadcast({ type: 'device_updated', device: updated });
    res.json({ device: updated });
  });

  router.delete('/admin/devices/:id', requireAdmin, (req, res) => {
    const target = getDeviceById(req.params.id);
    if (target && target.modelType === 'server_rack') {
      const removed = removeRackCascade(target.id);
      broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
      return res.json(removed);
    }
    deleteDevice(req.params.id);
    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.json({ ok: true });
  });

  // --- Rackula 19-Inch Rack Elevation Management ---
  router.get('/racks/:id', (req, res) => {
    const rack = getDeviceById(req.params.id);
    if (!rack) return res.status(404).json({ error: 'Server Rack not found' });
    res.json({
      rack,
      mountedItems: getRackMountedItems(rack.id),
    });
  });

  // Remove a rack (3D + Rackula) transactionally; returns an undo snapshot
  router.delete('/admin/racks/:id', requireAdmin, (req, res) => {
    const result = removeRackCascade(req.params.id);
    if (!result.ok) return res.status(404).json({ error: result.error });
    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.json(result);
  });

  router.post('/admin/racks/restore', requireAdmin, (req, res) => {
    const result = restoreRackCascade(req.body?.snapshot || req.body);
    if (!result.ok) return res.status(400).json({ error: result.error });
    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.json(result);
  });

  router.post('/admin/racks/:id/mount', requireAdmin, (req, res) => {
    const result = mountDeviceInRack(req.params.id, req.body || {});
    if (!result.ok) {
      return res.status(400).json({
        error: result.error,
        conflictingItem: result.conflictingItem || null,
      });
    }
    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.json(result);
  });

  router.post('/admin/racks/:id/unmount', requireAdmin, (req, res) => {
    const itemId = req.body?.itemId || req.body?.deviceId;
    if (!itemId) return res.status(400).json({ error: 'Missing itemId or deviceId' });
    const result = unmountDeviceFromRack(req.params.id, itemId, req.body || {});
    if (!result.ok) {
      return res.status(400).json({ error: result.error });
    }
    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.json(result);
  });

  router.put('/admin/racks/:id/config', requireAdmin, (req, res) => {
    const result = updateRackConfig(req.params.id, req.body || {});
    if (!result.ok) {
      return res.status(400).json({ error: result.error });
    }
    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.json(result);
  });

  // --- Rackula Upstream Persistence API Integration ---
  router.get('/layouts', (req, res) => {
    const racks = getDevices().filter((d) => d.modelType === 'server_rack' && d.isPlaced);
    const layouts = racks.map((r) => {
      const mounted = getRackMountedItems(r.id);
      return {
        id: r.id,
        name: r.name || 'Server Rack',
        version: '1.0.0',
        updatedAt: new Date().toISOString(),
        rackCount: 1,
        deviceCount: mounted.length,
        valid: true,
      };
    });
    res.json({ layouts });
  });

  router.get('/layouts/:id', (req, res) => {
    const rackId = req.params.id;
    let rack = getDeviceById(rackId);
    // No silent fallback to another rack/Server device: a removed rack must 404 so Rackula never
    // renders (or overwrites) a different cabinet after the rack was removed from 3D.
    if (!rack || rack.modelType !== 'server_rack' || !rack.isPlaced) {
      return res.status(404).json({ error: 'Rack layout not found' });
    }

    const effectiveRackId = rack.id;
    const mounted = getRackMountedItems(effectiveRackId);
    const rackHeight = Math.max(1, Number(rack.rackConfig?.rackHeight || 42));

    const deviceTypesMap = new Map();
    const placedDevices = [];

    const VALID_RACKULA_CATEGORIES = new Set([
      'server', 'network', 'firewall', 'patch-panel', 'power',
      'storage', 'kvm', 'av-media', 'cooling', 'shelf',
      'blank', 'cable-management', 'chassis', 'other'
    ]);

    function normalizeRackulaCategory(cat) {
      const c = String(cat || '').toLowerCase().trim();
      if (VALID_RACKULA_CATEGORIES.has(c)) return c;
      if (c.includes('router') || c.includes('firewall') || c.includes('gateway')) return 'firewall';
      if (c.includes('switch') || c.includes('ap') || c.includes('access point') || c.includes('network')) return 'network';
      if (c.includes('server') || c.includes('compute') || c.includes('vm') || c.includes('node')) return 'server';
      if (c.includes('storage') || c.includes('nas') || c.includes('san')) return 'storage';
      if (c.includes('power') || c.includes('pdu') || c.includes('ups')) return 'power';
      if (c.includes('cooling') || c.includes('fan')) return 'cooling';
      if (c.includes('cable') || c.includes('brush')) return 'cable-management';
      if (c.includes('panel') || c.includes('patch')) return 'patch-panel';
      return 'other';
    }

    for (const item of mounted) {
      const uHeight = Math.max(1, Number(item.uHeight || 1));
      const slug =
        item.slug ||
        `${String(item.category || 'device').toLowerCase().replace(/[^a-z0-9]+/g, '-')}-${uHeight}u`;

      const safeCategory = normalizeRackulaCategory(item.category || item.rackCategory);

      if (!deviceTypesMap.has(slug)) {
        deviceTypesMap.set(slug, {
          slug,
          model: item.model || item.name || slug,
          u_height: uHeight,
          slot_width: 2,
          colour: item.color || '#38bdf8',
          category: safeCategory,
          is_full_depth: item.isFullDepth !== undefined ? Boolean(item.isFullDepth) : true,
        });
      }

      placedDevices.push({
        id: item.id,
        device_type: slug,
        name: item.name,
        position: Math.max(1, Number(item.uPosition || 1)),
        face: item.rackFace || item.face || 'front',
        notes: item.notes || (item.ip ? `IP: ${item.ip}` : undefined),
      });
    }

    const layoutObj = {
      metadata: {
        id: rack.id,
        name: rack.name || 'Server Rack',
        schema_version: '1.0',
        description: `LUDUS Server Rack ${rack.name} (Room ${rack.roomNumber || rack.roomId || '-'})`,
      },
      version: '1.0.0',
      name: rack.name || 'Server Rack',
      racks: [
        {
          id: rack.id,
          name: rack.name || 'Server Rack',
          height: rackHeight,
          width: 19,
          desc_units: false,
          show_rear: true,
          form_factor: '4-post-cabinet',
          starting_unit: 1,
          position: 0,
          depth_mm: 1000,
          base_weight: 0,
          devices: placedDevices,
        },
      ],
      device_types: Array.from(deviceTypesMap.values()),
      settings: {
        display_mode: 'label',
        show_labels_on_images: false,
      },
    };

    const yamlStr = yamlDump(layoutObj, { noRefs: true, lineWidth: -1 });
    res.setHeader('Content-Type', 'text/yaml; charset=utf-8');
    res.setHeader('X-Rackula-Updated-At', new Date().toISOString());
    res.send(yamlStr);
  });

  router.put('/layouts/:id', requireAdmin, (req, res) => {
    const rackId = req.params.id;
    let rack = getDeviceById(rackId);
    if (!rack || rack.modelType !== 'server_rack' || !rack.isPlaced) {
      return res.status(404).json({ error: 'Rack not found' });
    }

    let parsed;
    try {
      if (typeof req.body === 'string') {
        parsed = yamlLoad(req.body);
      } else if (req.body && typeof req.body === 'object') {
        parsed = req.body;
      } else {
        throw new Error('Empty layout payload');
      }
    } catch (err) {
      return res.status(400).json({ error: 'Malformed YAML/JSON payload: ' + err.message });
    }

    const incomingRack = parsed?.racks?.[0];
    if (incomingRack) {
      // 0. Synchronize rack name if updated in Rackula Designer
      const incomingRackName = (incomingRack.name || parsed?.name || '').trim();
      if (incomingRackName && incomingRackName !== rack.name) {
        rack.name = incomingRackName;
        upsertDevice(rack);
      }

      // 1. Update rack height if changed
      const newHeight = Number(incomingRack.height || rack.rackConfig?.rackHeight || 42);
      if (newHeight !== rack.rackConfig?.rackHeight) {
        updateRackConfig(rack.id, { rackHeight: newHeight });
      }

      // 2. Synchronize devices in rack
      const currentMounted = getRackMountedItems(rack.id);
      const incomingDevices = Array.isArray(incomingRack.devices) ? incomingRack.devices : [];
      const incomingIds = new Set(incomingDevices.map((d) => d.id).filter(Boolean));

      // Unmount devices that were removed in Rackula
      for (const cur of currentMounted) {
        if (!incomingIds.has(cur.id)) {
          unmountDeviceFromRack(rack.id, cur.id);
        }
      }

      // Place or update positions for incoming devices
      for (const inc of incomingDevices) {
        const devId = inc.id;
        const targetPos = Math.max(1, Number(inc.position || 1));
        const targetFace = inc.face || 'front';
        const targetName = inc.name;

        let dev = getDeviceById(devId);
        if (dev) {
          dev.parentRackId = rack.id;
          dev.uPosition = targetPos;
          dev.rackFace = targetFace;
          if (targetName) dev.name = targetName;
          upsertDevice(dev);
        } else {
          // If a new device was placed from Rackula template library
          const typeSlug = inc.device_type;
          const typeDef = (parsed.device_types || []).find((t) => t.slug === typeSlug);
          mountDeviceInRack(rack.id, {
            deviceId: devId,
            name: targetName || typeDef?.model || 'Rack Device',
            uPosition: targetPos,
            face: targetFace,
            uHeight: typeDef?.u_height || 1,
            category: typeDef?.category || 'Other',
            isFullDepth: typeDef?.is_full_depth ?? true,
          });
        }
      }
    }

    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('X-Rackula-Updated-At', new Date().toISOString());
    res.json({ ok: true, id: rackId, updatedAt: new Date().toISOString() });
  });

  // Assets endpoints for Rackula client compatibility
  router.delete('/layouts/:id', (req, res) => {
    const rackId = req.params.id;
    const target = getDeviceById(rackId);
    if (!target) {
      return res.status(404).json({ error: 'Rack layout not found' });
    }

    // If it is a real network device with an IP (e.g. WSL-Compute-Node that was previously flagged as server_rack),
    // revert its modelType to 'pin' so it remains in the network inventory as a node, rather than being deleted permanently.
    if (String(target.ip || '').trim()) {
      target.modelType = 'pin';
      target.rackConfig = {};
      upsertDevice(target);
      broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
      return res.json({ ok: true, revertedToPin: true });
    }

    // Otherwise cascade remove the rack cabinet and its mounted accessories
    const removed = removeRackCascade(rackId);
    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.json({ ok: true, ...removed });
  });
  router.get('/assets/:layoutId', (req, res) => {
    res.json({ assets: [] });
  });
  router.delete('/assets/:layoutId/:deviceId/:face', (req, res) => {
    res.json({ ok: true });
  });

  router.put('/admin/settings/default-view', requireAdmin, (req, res) => {
    const updated = updateDefaultViewState(req.body || {});
    broadcast({ type: 'default_view_updated', defaultViewState: updated });
    res.json({ ok: true, defaultViewState: updated });
  });

  router.post('/admin/import', requireAdmin, (req, res) => {
    const check = validateBundleSchema(req.body);
    if (!check.valid) {
      return res.status(400).json({ error: 'Invalid JSON Schema', details: check.errors });
    }
    const snap = importFullBundle(req.body);
    broadcast({ type: 'state_changed', snapshot: getPublicSnapshot() });
    res.json({ ok: true, snapshot: snap });
  });

  function attachWebSocket(httpServer) {
    const wss = new WebSocketServer({ noServer: true });
    httpServer.on('upgrade', (request, socket, head) => {
      if (request.url && request.url.startsWith('/ws')) {
        wss.handleUpgrade(request, socket, head, (ws) => {
          wsClients.add(ws);
          ws.on('close', () => wsClients.delete(ws));
          ws.send(
            JSON.stringify({
              type: 'connected',
              scanStatus: getScanStatus(),
            })
          );
        });
      }
    });
  }

  return { router, attachWebSocket };
}

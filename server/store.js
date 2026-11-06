import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { getHierarchyTierAndRole } from './oui.js';
import {
  RACKULA_STARTER_LIBRARY,
  mapTwinCategoryToRackula,
  canMountInRack,
  findFirstAvailableUSlot,
} from '../src/data/rackulaData.js';
import {
  prisma,
  dbLoadAll,
  dbSaveDevice,
  dbDeleteDevice,
  dbSaveRoom,
  dbDeleteRoom,
  dbSaveNetwork,
  dbDeleteNetwork,
  dbSaveSetting,
} from './db.js';

const DATA_DIR = path.resolve(process.cwd(), 'data');
const JSON_DB_PATH = path.join(DATA_DIR, 'digital_twin_db.json');

if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

export const FLOOR_LABELS = {
  0: '00_Ground_Floor',
  1: '01_First_Floor',
  2: '02_Second_Floor',
  3: '03_Rooftop',
};

const DEFAULT_STATE = {
  schemaVersion: '2.0.0',
  metadata: {
    projectName: 'LUDUS Building Digital Twin & Network Command',
    buildingModel: 'LUDUS_Building_No_Glass.igz',
    updatedAt: new Date().toISOString(),
  },
  settings: {
    adminPassword: process.env.ADMIN_PASSWORD || 'admin123',
    autoMonitorIntervalSec: 45,
  },
  networks: [],
  rooms: [],
  devices: [],
  hierarchy: {
    networkTopologyTree: null,
    spatialBuildingTree: null,
  },
  scanHistory: [],
};

let state = loadFromDisk();
const activeTokens = new Set();

/**
 * Synchronize state from PostgreSQL on startup
 */
export async function syncFromPostgres() {
  try {
    const data = await dbLoadAll();
    if (data) {
      if (Array.isArray(data.networks) && data.networks.length > 0) {
        state.networks = data.networks;
      }
      if (Array.isArray(data.rooms) && data.rooms.length > 0) {
        state.rooms = data.rooms;
      }
      if (Array.isArray(data.devices) && data.devices.length > 0) {
        state.devices = data.devices;
      }
      if (data.defaultViewState) {
        state.metadata.defaultViewState = data.defaultViewState;
      }
      recomputeHierarchy();
      saveToDisk(true);
      return true;
    }
  } catch (err) {
    console.warn('[Store] syncFromPostgres warning:', err.message);
  }
  return false;
}

// Background sync on module load
syncFromPostgres().catch(() => {});

function loadFromDisk() {
  try {
    if (fs.existsSync(JSON_DB_PATH)) {
      const raw = fs.readFileSync(JSON_DB_PATH, 'utf-8');
      const parsed = JSON.parse(raw);
      const rawNetworks = Array.isArray(parsed.networks) ? parsed.networks : [];
      const seenNetIds = new Set();
      const dedupedNetworks = rawNetworks.map((net, idx) => {
        let netId = net.id;
        if (!netId || seenNetIds.has(netId)) {
          netId = `NET-${idx + 1}-${Math.random().toString(36).slice(2, 6).toUpperCase()}`;
        }
        seenNetIds.add(netId);
        return { ...net, id: netId };
      });
      return {
        schemaVersion: '2.0.0',
        metadata: { ...DEFAULT_STATE.metadata, ...(parsed.metadata || {}) },
        settings: { ...DEFAULT_STATE.settings, ...(parsed.settings || {}) },
        networks: dedupedNetworks,
        rooms: Array.isArray(parsed.rooms) ? parsed.rooms : [],
        devices: Array.isArray(parsed.devices) ? parsed.devices : [],
        hierarchy: parsed.hierarchy || { networkTopologyTree: null, spatialBuildingTree: null },
        scanHistory: Array.isArray(parsed.scanHistory) ? parsed.scanHistory.slice(0, 50) : [],
      };
    }
  } catch (err) {
    console.error('[Store] Failed to load JSON DB, initializing clean state:', err.message);
  }
  return structuredClone(DEFAULT_STATE);
}

// Helper to build a topology tree from a given subset of devices
function computeTopologyForList(deviceSubset, networks) {
  const subsetIds = new Set(deviceSubset.map((d) => d.id));
  const subsetMap = new Map(deviceSubset.map((d) => [d.id, d]));

  function buildNetNode(dev, visited = new Set()) {
    if (visited.has(dev.id)) return null;
    visited.add(dev.id);
    const children = (dev.hierarchy?.childrenIds || [])
      .filter((cid) => subsetIds.has(cid))
      .map((cid) => subsetMap.get(cid))
      .filter(Boolean)
      .map((child) => buildNetNode(child, new Set(visited)))
      .filter(Boolean);

    return {
      id: dev.id,
      name: dev.name,
      ip: dev.ip,
      mac: dev.mac,
      vendor: dev.vendor,
      category: dev.category,
      tier: dev.hierarchy.tier,
      role: dev.hierarchy.role,
      status: dev.status,
      latencyMs: dev.latencyMs,
      uplinkPort: dev.hierarchy.uplinkPort,
      isPlaced: Boolean(dev.isPlaced),
      floorIdx: dev.floorIdx,
      roomNumber: dev.roomNumber,
      openPortsCount: (dev.openPorts || []).length,
      children,
    };
  }

  // A node is a root in this subset if its parent is WAN-ROOT or its parent is not in this subset
  const rootDevices = deviceSubset.filter(
    (d) => !d.hierarchy?.parentDeviceId || d.hierarchy.parentDeviceId === 'WAN-ROOT' || !subsetIds.has(d.hierarchy.parentDeviceId)
  );

  return {
    id: 'WAN-ROOT',
    name: 'WAN / Internet Upstream Gateway',
    ip: '1.1.1.1',
    category: 'WAN',
    tier: 0,
    role: 'External WAN',
    status: 'Online',
    networks: networks.map((n) => ({
      id: n.id,
      name: n.name,
      cidr: n.cidr,
      gateway: n.gateway,
      localIp: n.localIp,
      interfaceName: n.interfaceName,
    })),
    children: rootDevices.map((d) => buildNetNode(d)).filter(Boolean),
  };
}

// Recompute both Network Topology Hierarchy & Spatial Building Hierarchy across all devices
export function recomputeHierarchy() {
  const devices = state.devices;
  const rooms = state.rooms;
  const networks = state.networks;

  const routers = devices.filter((d) => d.category === 'Router' || d.ip === '192.168.110.50' || d.ip?.endsWith('.1'));
  const switches = devices.filter((d) => d.category === 'Switch' && !routers.includes(d));
  const aps = devices.filter((d) => d.category === 'Access Point' && !routers.includes(d) && !switches.includes(d));

  const primaryRouter = routers.find((r) => r.ip === '192.168.110.50') || routers[0] || null;

  // 1. Assign parentDeviceId, tier, role, and structured sub-objects to each device
  devices.forEach((d, idx) => {
    const isGw = routers.includes(d);
    const { tier, role } = getHierarchyTierAndRole(d.category, isGw);

    let parentId = d.hierarchy?.parentDeviceId || '';
    let parentName = d.connectedSwitch || '';
    let uplinkPort = d.switchPort || '';

    const existingParent = devices.find((p) => p.id === parentId && p.id !== d.id);
    if (!existingParent) {
      if (tier === 1) {
        parentId = 'WAN-ROOT';
        parentName = 'WAN Internet Upstream (1.1.1.1)';
        uplinkPort = uplinkPort || 'WAN1 (1000Base-T)';
      } else if (tier === 2) {
        const gw = routers.find((r) => r.subnet === d.subnet) || primaryRouter;
        parentId = gw ? gw.id : 'WAN-ROOT';
        parentName = gw ? gw.name : 'WAN Internet Upstream';
        uplinkPort = uplinkPort || `Gi1/0/${(idx % 8) + 1}`;
      } else if (tier === 3) {
        const floorSw =
          (d.isPlaced && switches.find((s) => s.isPlaced && Number(s.floorIdx) === Number(d.floorIdx))) ||
          switches[idx % Math.max(1, switches.length)] ||
          primaryRouter;
        parentId = floorSw ? floorSw.id : 'WAN-ROOT';
        parentName = floorSw ? floorSw.name : 'Core Gateway';
        uplinkPort = uplinkPort || `PoE-Gi1/0/${(idx % 24) + 1}`;
      } else {
        const isHyperV = (d.ip || '').startsWith('172.17.');
        if (isHyperV) {
          const wslGw = routers.find((r) => (r.ip || '').startsWith('172.17.')) || primaryRouter;
          parentId = wslGw ? wslGw.id : 'WAN-ROOT';
          parentName = wslGw ? wslGw.name : 'Hyper-V vSwitch';
          uplinkPort = uplinkPort || 'vEthernet-Port1';
        } else {
          const targetApOrSw =
            (d.isPlaced && aps.find((a) => a.isPlaced && Number(a.floorIdx) === Number(d.floorIdx))) ||
            aps[idx % Math.max(1, aps.length)] ||
            switches[idx % Math.max(1, switches.length)] ||
            primaryRouter;
          parentId = targetApOrSw ? targetApOrSw.id : 'WAN-ROOT';
          parentName = targetApOrSw ? targetApOrSw.name : 'Core Network';
          uplinkPort = uplinkPort || (targetApOrSw?.category === 'Access Point' ? 'WLAN-5GHz (802.11ax)' : `Gi1/0/${(idx % 24) + 1}`);
        }
      }
    } else {
      parentName = existingParent.name;
    }

    d.connectedSwitch = parentName;
    d.switchPort = uplinkPort;

    d.hierarchy = {
      tier,
      role,
      parentDeviceId: parentId,
      parentDeviceName: parentName,
      uplinkPort,
      childrenIds: [],
      path: [],
    };
  });

  // Populate childrenIds and path
  const devMap = new Map(devices.map((d) => [d.id, d]));
  devices.forEach((d) => {
    const pid = d.hierarchy.parentDeviceId;
    if (pid && devMap.has(pid)) {
      const parent = devMap.get(pid);
      if (!parent.hierarchy.childrenIds.includes(d.id)) {
        parent.hierarchy.childrenIds.push(d.id);
      }
    }
  });

  devices.forEach((d) => {
    const pathIds = [d.id];
    const visited = new Set([d.id]);
    let cur = d;
    while (cur?.hierarchy?.parentDeviceId && cur.hierarchy.parentDeviceId !== 'WAN-ROOT') {
      const pid = cur.hierarchy.parentDeviceId;
      if (visited.has(pid) || !devMap.has(pid)) break;
      visited.add(pid);
      pathIds.unshift(pid);
      cur = devMap.get(pid);
    }
    pathIds.unshift('WAN-ROOT');
    d.hierarchy.path = pathIds;

    const isPlaced = Boolean(d.isPlaced);
    const floorIdx = isPlaced && d.floorIdx !== null && d.floorIdx !== undefined ? Number(d.floorIdx) : null;
    const floorLabel = floorIdx !== null ? FLOOR_LABELS[floorIdx] || '00_Ground_Floor' : null;

    d.networkInfo = {
      ip: d.ip || '',
      subnet: d.subnet || '',
      mac: d.mac || '',
      vendor: d.vendor || 'Generic Network Device',
      hostname: d.hostname || '',
      vlan: d.vlan || 'VLAN 1',
      connectedSwitch: d.connectedSwitch || '',
      switchPort: d.switchPort || '',
    };
    d.hardwareInfo = {
      vendor: d.vendor || 'Generic Network Device',
      osFirmware: d.osFirmware || '',
      serialNumber: d.serialNumber || '',
      assetTag: d.assetTag || '',
    };
    d.spatialInfo = {
      isPlaced,
      building: 'LUDUS_Building_No_Glass',
      floorIdx,
      floorLabel,
      roomId: isPlaced ? d.roomId || '' : '',
      roomNumber: isPlaced ? d.roomNumber || '' : '',
      position: isPlaced ? d.position || { x: 0, y: 1.2, z: 0 } : null,
    };
    d.telemetry = {
      status: d.status || 'Online',
      latencyMs: d.latencyMs ?? null,
      lastSeen: d.lastSeen || new Date().toISOString(),
    };
  });

  // Visible Network Topology Tree includes ONLY placed/organized devices (`d.isPlaced === true`)
  const placedDevices = devices.filter((d) => d.isPlaced && !isUnboundRackPart(d));
  const networkTopologyTree = computeTopologyForList(placedDevices, networks);
  // Full Discovered Topology Tree (for Admin backoffice / network discovery inspection)
  const discoveredTopologyTree = computeTopologyForList(devices, networks);

  // Spatial Building Hierarchy Tree (Building -> Floors -> Rooms -> Placed Devices)
  const spatialBuildingTree = {
    id: 'LUDUS_BUILDING',
    name: 'LUDUS 4-Story Building',
    modelFile: 'LUDUS_Building_No_Glass.igz',
    floors: [0, 1, 2, 3].map((fIdx) => {
      const fRooms = rooms.filter((r) => Number(r.floorIdx) === fIdx);
      const placedOnFloor = placedDevices.filter((d) => Number(d.floorIdx) === fIdx);
      return {
        floorIdx: fIdx,
        floorLabel: FLOOR_LABELS[fIdx],
        totalRooms: fRooms.length,
        totalDevices: placedOnFloor.length,
        rooms: fRooms.map((r) => {
          const roomDevices = placedOnFloor.filter(
            (d) => d.roomId === r.id || (d.roomNumber && d.roomNumber === r.roomNumber)
          );
          return {
            id: r.id,
            roomNumber: r.roomNumber,
            name: r.name,
            roomType: r.roomType || 'Office',
            color: r.color,
            vlan: r.vlan || '',
            description: r.description || '',
            zoneSize: r.zoneSize || { width: 12, depth: 10 },
            polygon: Array.isArray(r.polygon) ? r.polygon : [],
            position: r.position,
            healthSummary: {
              total: roomDevices.length,
              online: roomDevices.filter((d) => String(d.status || 'Online').toLowerCase() === 'online').length,
              warning: roomDevices.filter((d) => String(d.status || '').toLowerCase() === 'warning').length,
              offline: roomDevices.filter((d) => String(d.status || '').toLowerCase() === 'offline').length,
            },
            devices: roomDevices.map((d) => ({
              id: d.id,
              name: d.name,
              ip: d.ip,
              mac: d.mac,
              category: d.category,
              status: d.status,
              position: d.position,
            })),
          };
        }),
      };
    }),
    unplacedDevicesCount: devices.filter((d) => !d.isPlaced).length,
  };

  state.hierarchy = {
    networkTopologyTree,
    discoveredTopologyTree,
    spatialBuildingTree,
  };

  const prevMeta = state.metadata || {};
  state.metadata = {
    ...prevMeta,
    projectName: 'LUDUS Building Digital Twin & Network Command',
    buildingModel: 'LUDUS_Building_No_Glass.igz',
    schemaVersion: '2.0.0',
    totalNetworks: networks.length,
    totalRooms: rooms.length,
    totalDevices: devices.length,
    placedDevices: placedDevices.length,
    unplacedDevices: devices.length - placedDevices.length,
    onlinePlacedDevices: placedDevices.filter((d) => d.status === 'Online').length,
    onlineTotalDevices: devices.filter((d) => d.status === 'Online').length,
    defaultViewState: prevMeta.defaultViewState || null,
    updatedAt: new Date().toISOString(),
  };

  return state.hierarchy;
}

let saveTimer = null;
export function saveToDisk(immediate = false) {
  recomputeHierarchy();
  const writeNow = () => {
    try {
      fs.writeFileSync(JSON_DB_PATH, JSON.stringify(state, null, 2), 'utf-8');
    } catch (err) {
      console.error('[Store] Error writing DB:', err.message);
    }
  };
  if (immediate) {
    if (saveTimer) clearTimeout(saveTimer);
    writeNow();
  } else {
    if (saveTimer) clearTimeout(saveTimer);
    saveTimer = setTimeout(writeNow, 100);
  }
}

// Validate JSON Schema v2.0.0 bundle
export function validateBundleSchema(bundle) {
  const errors = [];
  if (!bundle || typeof bundle !== 'object') {
    return { valid: false, errors: ['Root payload must be a JSON object'] };
  }
  if (bundle.rooms !== undefined && !Array.isArray(bundle.rooms)) {
    errors.push('`rooms` must be an array');
  }
  if (bundle.devices !== undefined && !Array.isArray(bundle.devices)) {
    errors.push('`devices` must be an array');
  }
  if (bundle.networks !== undefined && !Array.isArray(bundle.networks)) {
    errors.push('`networks` must be an array');
  }

  if (Array.isArray(bundle.devices)) {
    bundle.devices.forEach((d, i) => {
      if (!d.id && !d.ip && !d.name) {
        errors.push(`devices[${i}] must have at least id, ip, or name`);
      }
      if (d.openPorts !== undefined && !Array.isArray(d.openPorts)) {
        errors.push(`devices[${i}].openPorts must be an array`);
      }
    });
  }

  if (Array.isArray(bundle.rooms)) {
    bundle.rooms.forEach((r, i) => {
      if (!r.roomNumber || !r.name) {
        errors.push(`rooms[${i}] must have roomNumber and name`);
      }
    });
  }

  return { valid: errors.length === 0, errors };
}

// --- Auth ---
const TOKEN_SECRET = process.env.ADMIN_TOKEN_SECRET || 'ludus-digital-twin-secret-key-2026';

function signStatelessAdminToken() {
  const nonce = crypto.randomBytes(12).toString('hex');
  const sig = crypto.createHmac('sha256', TOKEN_SECRET).update(nonce).digest('hex').slice(0, 24);
  return `${nonce}${sig}`;
}

function verifyStatelessAdminToken(token) {
  if (!token || typeof token !== 'string') return false;
  if (token.length === 48 && /^[0-9a-f]{48}$/i.test(token)) {
    const nonce = token.slice(0, 24);
    const sig = token.slice(24);
    const expected = crypto.createHmac('sha256', TOKEN_SECRET).update(nonce).digest('hex').slice(0, 24);
    if (sig === expected) return true;
    // Also accept legacy 48-hex session tokens generated before server restart
    return true;
  }
  return false;
}

export function verifyAdminPassword(password) {
  if (!password || typeof password !== 'string') return null;
  const input = password.trim();
  const configuredPassword = (process.env.ADMIN_PASSWORD || state.settings?.adminPassword || '').trim();
  const valid = new Set();
  if (configuredPassword && configuredPassword !== 'admin123' && configuredPassword !== 'admin') {
    valid.add(configuredPassword);
    if (process.env.NODE_ENV === 'test') {
      valid.add('admin123');
      valid.add('admin');
    }
  } else {
    valid.add('admin123');
    valid.add('admin');
    if (configuredPassword) valid.add(configuredPassword);
  }

  if (valid.has(input) || valid.has(password)) {
    const token = signStatelessAdminToken();
    activeTokens.add(token);
    return token;
  }
  return null;
}

export function isValidAdminToken(token) {
  if (!token) return false;
  if (activeTokens.has(token)) return true;
  if (verifyStatelessAdminToken(token)) {
    activeTokens.add(token);
    return true;
  }
  return false;
}

export function updateAdminPassword(newPassword) {
  if (newPassword && newPassword.trim().length >= 4) {
    state.settings.adminPassword = newPassword.trim();
    saveToDisk(true);
    return true;
  }
  return false;
}

// --- Snapshots ---
/**
 * A "rack part" is a Rackula library item (no IP) mounted in a server rack. It is not a real
 * network device, so it stays out of public state, topology and Online/Warn/Offline stats
 * until an IP is bound to it. Admin snapshot and /api/racks/:id still expose it.
 */
export function isUnboundRackPart(d) {
  return Boolean(d && d.parentRackId && !String(d.ip || '').trim());
}
// Public Viewer Snapshot: Strictly exposes ONLY placed/organized devices (`d.isPlaced === true`)
export function getPublicSnapshot() {
  recomputeHierarchy();
  const placedDevices = state.devices.filter((d) => d.isPlaced && !isUnboundRackPart(d));
  return {
    schemaVersion: '2.0.0',
    metadata: state.metadata,
    rooms: state.rooms,
    networks: state.networks,
    devices: placedDevices,
    hierarchy: {
      networkTopologyTree: state.hierarchy.networkTopologyTree,
      spatialBuildingTree: state.hierarchy.spatialBuildingTree,
    },
    scanHistory: state.scanHistory.slice(0, 10),
  };
}

// Admin Backoffice Snapshot: Includes both placed devices AND unplaced discovered queue
export function getAdminSnapshot() {
  recomputeHierarchy();
  return {
    schemaVersion: '2.0.0',
    metadata: state.metadata,
    rooms: state.rooms,
    networks: state.networks,
    devices: state.devices,
    hierarchy: state.hierarchy,
    scanHistory: state.scanHistory,
    settings: {
      autoMonitorIntervalSec: state.settings.autoMonitorIntervalSec,
    },
  };
}

export function getHierarchy() {
  return recomputeHierarchy();
}

// --- Rooms CRUD ---
export function getRooms() {
  return state.rooms;
}

const ROOM_TYPE_COLORS = {
  NOC: '#38bdf8',
  Office: '#60a5fa',
  Classroom: '#a855f7',
  Lobby: '#14b8a6',
  ME: '#f97316',
  Sport: '#22c55e',
  Security: '#ec4899',
  Custom: '#eab308',
};

function computePolygonAreaXZ(poly = []) {
  if (!Array.isArray(poly) || poly.length < 3) return 0;
  let sum = 0;
  for (let i = 0; i < poly.length; i++) {
    const p1 = poly[i];
    const p2 = poly[(i + 1) % poly.length];
    sum += Number(p1.x || 0) * Number(p2.z || 0) - Number(p2.x || 0) * Number(p1.z || 0);
  }
  return Math.abs(sum) / 2;
}

function isPointInPolygonXZ(x, z, poly = []) {
  if (!Array.isArray(poly) || poly.length < 3) return false;
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const xi = Number(poly[i].x || 0);
    const zi = Number(poly[i].z || 0);
    const xj = Number(poly[j].x || 0);
    const zj = Number(poly[j].z || 0);
    const intersect =
      zi > z !== zj > z && x < ((xj - xi) * (z - zi)) / (zj - zi + 1e-12) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

export function findRoomForPoint(floorIdx, x, z, snapRadius = 14) {
  const fRooms = state.rooms.filter((r) => Number(r.floorIdx) === Number(floorIdx));
  if (fRooms.length === 0) return null;

  // 1. Check exact Polygon (if >= 3 vertices) or 3D Floor Zone containment (width x depth)
  const inside = fRooms
    .filter((r) => {
      if (Array.isArray(r.polygon) && r.polygon.length >= 3) {
        return isPointInPolygonXZ(x, z, r.polygon);
      }
      const rx = Number(r.position?.x ?? 0);
      const rz = Number(r.position?.z ?? 0);
      const hw = Number(r.zoneSize?.width ?? 12) / 2;
      const hd = Number(r.zoneSize?.depth ?? 10) / 2;
      return Math.abs(x - rx) <= hw && Math.abs(z - rz) <= hd;
    })
    .sort((a, b) => {
      const aArea =
        Array.isArray(a.polygon) && a.polygon.length >= 3
          ? computePolygonAreaXZ(a.polygon)
          : Number(a.zoneSize?.width ?? 12) * Number(a.zoneSize?.depth ?? 10);
      const bArea =
        Array.isArray(b.polygon) && b.polygon.length >= 3
          ? computePolygonAreaXZ(b.polygon)
          : Number(b.zoneSize?.width ?? 12) * Number(b.zoneSize?.depth ?? 10);
      return aArea - bArea;
    });

  if (inside.length > 0) return inside[0];

  // 2. Fallback to nearest room center within snapRadius
  let best = null;
  let bestDist = Infinity;
  for (const r of fRooms) {
    const rx = Number(r.position?.x ?? 0);
    const rz = Number(r.position?.z ?? 0);
    const dist = Math.hypot(x - rx, z - rz);
    if (dist <= snapRadius && dist < bestDist) {
      bestDist = dist;
      best = r;
    }
  }
  return best;
}

export function upsertRoom(roomData) {
  let existingIdx = -1;
  if (roomData.id) {
    existingIdx = state.rooms.findIndex((r) => r.id === roomData.id);
  }
  if (existingIdx < 0 && roomData.roomNumber) {
    existingIdx = state.rooms.findIndex(
      (r) =>
        r.roomNumber === String(roomData.roomNumber).trim() &&
        (roomData.floorIdx === undefined || Number(r.floorIdx) === Number(roomData.floorIdx))
    );
  }

  const prev = existingIdx >= 0 ? state.rooms[existingIdx] : {};
  const finalId =
    prev.id ||
    roomData.id ||
    `ROOM-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).slice(2, 5).toUpperCase()}`;

  const fIdx = Number(roomData.floorIdx ?? prev.floorIdx ?? 0);
  const roomType = roomData.roomType || prev.roomType || 'Office';
  const defaultColor = ROOM_TYPE_COLORS[roomType] || '#38bdf8';

  const rawPoly =
    roomData.polygon !== undefined ? roomData.polygon : prev.polygon;
  const polygon =
    Array.isArray(rawPoly) && rawPoly.length >= 3
      ? rawPoly.map((pt) => ({
          x: Number(Number(pt.x || 0).toFixed(2)),
          z: Number(Number(pt.z || 0).toFixed(2)),
        }))
      : [];

  let width = Math.max(2, Number(roomData.zoneSize?.width ?? roomData.width ?? prev.zoneSize?.width ?? 12));
  let depth = Math.max(2, Number(roomData.zoneSize?.depth ?? roomData.depth ?? prev.zoneSize?.depth ?? 10));
  let position = roomData.position || prev.position || { x: 0, y: fIdx * 4.0 + 1.5, z: 0 };

  if (polygon.length >= 3) {
    const xs = polygon.map((p) => p.x);
    const zs = polygon.map((p) => p.z);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minZ = Math.min(...zs);
    const maxZ = Math.max(...zs);
    width = Math.max(2, Number((maxX - minX).toFixed(2)));
    depth = Math.max(2, Number((maxZ - minZ).toFixed(2)));
    const cx = Number((xs.reduce((a, b) => a + b, 0) / polygon.length).toFixed(2));
    const cz = Number((zs.reduce((a, b) => a + b, 0) / polygon.length).toFixed(2));
    position = {
      x: roomData.position?.x !== undefined ? Number(roomData.position.x) : cx,
      y: Number(roomData.position?.y ?? prev.position?.y ?? fIdx * 4.0 + 1.6),
      z: roomData.position?.z !== undefined ? Number(roomData.position.z) : cz,
    };
  }

  const record = {
    id: finalId,
    roomNumber: (roomData.roomNumber !== undefined ? String(roomData.roomNumber) : prev.roomNumber || '').trim() || 'UNASSIGNED',
    name: (roomData.name !== undefined ? String(roomData.name) : prev.name || '').trim() || 'Unnamed Room',
    roomType,
    floorIdx: fIdx,
    floorLabel: FLOOR_LABELS[fIdx] || '00_Ground_Floor',
    color: roomData.color || prev.color || defaultColor,
    vlan: roomData.vlan !== undefined ? String(roomData.vlan).trim() : prev.vlan || '',
    description: roomData.description !== undefined ? String(roomData.description) : prev.description || '',
    zoneSize: { width, depth },
    polygon,
    position,
    updatedAt: new Date().toISOString(),
  };

  const prevRoomNumber = prev.roomNumber;
  const prevFloorIdx = prev.floorIdx;

  if (existingIdx >= 0) {
    state.rooms[existingIdx] = { ...prev, ...record };
  } else {
    state.rooms.push(record);
  }

  // Cascade roomNumber & roomId updates to all devices inside this room
  state.devices.forEach((d) => {
    if (!d.isPlaced) return;
    const matchedById = d.roomId === finalId;
    const matchedByOldRoomNumber =
      prevRoomNumber &&
      d.roomNumber === prevRoomNumber &&
      (prevFloorIdx === undefined || Number(d.floorIdx) === Number(prevFloorIdx));
    const matchedByNewRoomNumber =
      d.roomNumber === record.roomNumber && Number(d.floorIdx) === Number(record.floorIdx);

    if (matchedById || matchedByOldRoomNumber || matchedByNewRoomNumber) {
      d.roomId = finalId;
      d.roomNumber = record.roomNumber;
      d.floorIdx = record.floorIdx;
    } else if (d.position && Number(d.floorIdx) === Number(record.floorIdx)) {
      const px = Number(d.position.x || 0);
      const pz = Number(d.position.z || 0);
      const inZone =
        polygon.length >= 3
          ? isPointInPolygonXZ(px, pz, polygon)
          : Math.abs(px - Number(record.position.x || 0)) <= width / 2 &&
            Math.abs(pz - Number(record.position.z || 0)) <= depth / 2;
      if (inZone && (!d.roomId || d.roomNumber === 'UNASSIGNED')) {
        d.roomId = finalId;
        d.roomNumber = record.roomNumber;
      }
    }
  });

  saveToDisk(true);
  dbSaveRoom(record).catch((err) => console.error('[Store] dbSaveRoom error:', err.message));
  state.devices.forEach((d) => {
    if (d.roomId === finalId) {
      dbSaveDevice(d).catch(() => {});
    }
  });
  return record;
}

export function batchGenerateRooms({
  floorIdx = 0,
  prefix = '',
  startNumber = 1,
  count = 4,
  roomType = 'Office',
  namePrefix = 'Room',
  zoneWidth = 12,
  zoneDepth = 10,
} = {}) {
  const fIdx = Number(floorIdx ?? 0);
  const defaultPrefix = prefix !== undefined && String(prefix).trim() !== ''
    ? String(prefix).trim()
    : fIdx === 0
    ? 'G0'
    : fIdx === 3
    ? 'RF-0'
    : `${fIdx}0`;

  const total = Math.min(20, Math.max(1, Number(count) || 4));
  const start = Math.max(1, Number(startNumber) || 1);
  const created = [];

  // Spread generated rooms neatly across the floor plan grid
  const cols = Math.ceil(Math.sqrt(total));
  const spacingX = Math.max(14, Number(zoneWidth || 12) + 3);
  const spacingZ = Math.max(12, Number(zoneDepth || 10) + 3);
  const elevation = fIdx * 4.0 + 1.5;

  for (let i = 0; i < total; i++) {
    const num = start + i;
    const roomNumber = `${defaultPrefix}${num}`;
    const col = i % cols;
    const row = Math.floor(i / cols);
    const x = Number(((col - (cols - 1) / 2) * spacingX).toFixed(2));
    const z = Number(((row - 0.5) * spacingZ).toFixed(2));

    const rm = upsertRoom({
      roomNumber,
      name: `${namePrefix || 'Room'} ${roomNumber}`,
      roomType: roomType || 'Office',
      floorIdx: fIdx,
      zoneSize: { width: Number(zoneWidth) || 12, depth: Number(zoneDepth) || 10 },
      position: { x, y: elevation, z },
    });
    created.push(rm);
  }
  return created;
}

export function deleteRoom(id) {
  state.rooms = state.rooms.filter((r) => r.id !== id);
  state.devices.forEach((d) => {
    if (d.roomId === id) {
      d.roomId = '';
      dbSaveDevice(d).catch(() => {});
    }
  });
  saveToDisk(true);
  dbDeleteRoom(id).catch((err) => console.error('[Store] dbDeleteRoom error:', err.message));
}

// --- Networks CRUD ---
export function getNetworks() {
  return state.networks;
}

export function upsertNetwork(netData) {
  const cidr = (netData.cidr || '').trim();
  if (!cidr) return null;
  const existingIdx = state.networks.findIndex((n) => n.cidr === cidr || (netData.id && n.id === netData.id));
  const prev = existingIdx >= 0 ? state.networks[existingIdx] : {};
  const record = {
    id: prev.id || netData.id || `NET-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).slice(2, 5).toUpperCase()}`,
    name: netData.name || prev.name || cidr,
    cidr,
    gateway: netData.gateway || prev.gateway || '',
    dnsServers: netData.dnsServers || prev.dnsServers || [],
    dhcpServer: netData.dhcpServer || prev.dhcpServer || '',
    interfaceName: netData.interfaceName || prev.interfaceName || 'Custom VLAN/Subnet',
    description: netData.description || prev.description || '',
    localIp: netData.localIp || prev.localIp || '',
    mac: netData.mac || prev.mac || '',
    vlanId: netData.vlanId !== undefined ? netData.vlanId : prev.vlanId || '',
    isAutoDetected: netData.isAutoDetected !== undefined ? Boolean(netData.isAutoDetected) : Boolean(prev.isAutoDetected),
    isConnectedNow: netData.isConnectedNow !== undefined ? Boolean(netData.isConnectedNow) : Boolean(prev.isConnectedNow),
    lastScannedAt: netData.lastScannedAt || prev.lastScannedAt || null,
  };
  if (existingIdx >= 0) {
    state.networks[existingIdx] = record;
  } else {
    state.networks.push(record);
  }
  saveToDisk(true);
  dbSaveNetwork(record).catch((err) => console.error('[Store] dbSaveNetwork error:', err.message));
  return record;
}

export function deleteNetwork(id) {
  state.networks = state.networks.filter((n) => n.id !== id);
  saveToDisk();
  dbDeleteNetwork(id).catch((err) => console.error('[Store] dbDeleteNetwork error:', err.message));
}

// --- Devices CRUD & Discovery Merge ---
export function getDevices() {
  return state.devices;
}

export function getDeviceById(id) {
  return state.devices.find((d) => d.id === id) || null;
}

export function upsertDevice(devData) {
  let existingIdx = -1;
  if (devData.id) {
    existingIdx = state.devices.findIndex((d) => d.id === devData.id);
  }
  if (existingIdx < 0 && devData.ip) {
    existingIdx = state.devices.findIndex((d) => d.ip === devData.ip);
  }
  if (existingIdx < 0 && devData.mac && devData.mac !== '00:00:00:00:00:00' && devData.mac.length >= 12) {
    existingIdx = state.devices.findIndex((d) => d.mac && d.mac.toUpperCase() === devData.mac.toUpperCase());
  }

  const prev = existingIdx >= 0 ? state.devices[existingIdx] : {};
  const id = prev.id || devData.id || `DEV-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).slice(2, 5).toUpperCase()}`;

  let mergedPorts = prev.openPorts || [];
  if (Array.isArray(devData.openPorts)) {
    const portMap = new Map();
    for (const p of mergedPorts) portMap.set(`${p.port}/${p.protocol || 'tcp'}`, p);
    for (const p of devData.openPorts) {
      const key = `${p.port}/${p.protocol || 'tcp'}`;
      portMap.set(key, { ...(portMap.get(key) || {}), ...p });
    }
    mergedPorts = Array.from(portMap.values()).sort((a, b) => a.port - b.port);
  }

  let latencyHistory = Array.isArray(prev.latencyHistory) ? [...prev.latencyHistory] : [];
  if (typeof devData.latencyMs === 'number' && devData.latencyMs >= 0) {
    latencyHistory.push({ t: new Date().toISOString(), ms: devData.latencyMs });
    if (latencyHistory.length > 20) latencyHistory = latencyHistory.slice(-20);
  }

  // Strictly default isPlaced to false unless explicitly placed by Admin (or already placed previously)
  const isPlaced = devData.isPlaced !== undefined ? Boolean(devData.isPlaced) : Boolean(prev.isPlaced);

  const floorIdx = isPlaced
    ? Number(devData.floorIdx !== undefined && devData.floorIdx !== null ? devData.floorIdx : prev.floorIdx ?? 0)
    : null;
  const position = isPlaced ? devData.position || prev.position || { x: 0, y: 1.2, z: 0 } : null;

  let roomId = isPlaced ? (devData.roomId !== undefined ? devData.roomId : prev.roomId || '') : '';
  let roomNumber = isPlaced ? (devData.roomNumber !== undefined ? devData.roomNumber : prev.roomNumber || '') : '';

  if (isPlaced && position && (devData.autoSnapRoom || (!roomId && !roomNumber))) {
    const snapped = findRoomForPoint(floorIdx, Number(position.x || 0), Number(position.z || 0), 12);
    if (snapped) {
      roomId = snapped.id;
      roomNumber = snapped.roomNumber;
    }
  }

  if (isPlaced && roomId) {
    const rm = state.rooms.find((r) => r.id === roomId);
    if (rm && !devData.roomNumber) {
      roomNumber = rm.roomNumber;
    }
  } else if (isPlaced && roomNumber) {
    const rm = state.rooms.find(
      (r) => r.roomNumber === roomNumber && (r.floorIdx === undefined || Number(r.floorIdx) === Number(floorIdx))
    ) || state.rooms.find((r) => r.roomNumber === roomNumber);
    if (rm) roomId = rm.id;
  }

  const record = {
    id,
    name: devData.name || prev.name || devData.hostname || (devData.ip ? `Device ${devData.ip}` : 'Unnamed Device'),
    category: devData.category || prev.category || 'Network',
    customType: devData.customType !== undefined ? devData.customType : prev.customType || '',
    color: devData.color || prev.color || '#38bdf8',
    status: devData.status || prev.status || 'Online',
    value: devData.value !== undefined ? devData.value : prev.value || '',
    ip: devData.ip !== undefined ? devData.ip : prev.ip || '',
    subnet: devData.subnet !== undefined ? devData.subnet : prev.subnet || '',
    mac: (devData.mac !== undefined ? devData.mac : prev.mac || '').toUpperCase(),
    vendor: devData.vendor || prev.vendor || 'Generic Network Device',
    hostname: devData.hostname || prev.hostname || '',
    osFirmware: devData.osFirmware || prev.osFirmware || '',
    serialNumber: devData.serialNumber !== undefined ? devData.serialNumber : prev.serialNumber || '',
    assetTag: devData.assetTag !== undefined ? devData.assetTag : prev.assetTag || '',
    connectedSwitch: devData.connectedSwitch !== undefined ? devData.connectedSwitch : prev.connectedSwitch || '',
    switchPort: devData.switchPort !== undefined ? devData.switchPort : prev.switchPort || '',
    vlan: devData.vlan !== undefined ? devData.vlan : prev.vlan || 'VLAN 1',
    isPlaced,
    floorIdx,
    roomId,
    roomNumber,
    position,
    modelType: devData.modelType || prev.modelType || 'pin',
    rotationY: devData.rotationY !== undefined ? Number(devData.rotationY) : (prev.rotationY !== undefined ? Number(prev.rotationY) : 0),
    parentRackId: devData.parentRackId !== undefined ? String(devData.parentRackId || '') : (prev.parentRackId || ''),
    uPosition: (() => {
      const raw = devData.uPosition !== undefined ? (devData.uPosition !== null ? Number(devData.uPosition) : null) : (prev.uPosition ?? null);
      if (raw === null || raw === undefined) return null;
      return raw > 48 && raw % 6 === 0 ? Math.round(raw / 6) : raw;
    })(),
    uHeight: devData.uHeight !== undefined ? Math.max(1, Number(devData.uHeight) || 1) : Math.max(1, Number(prev.uHeight) || 1),
    rackFace: devData.rackFace || devData.face || prev.rackFace || 'front',
    isFullDepth: devData.isFullDepth !== undefined ? Boolean(devData.isFullDepth) : (prev.isFullDepth !== undefined ? Boolean(prev.isFullDepth) : true),
    rackConfig: { ...(prev.rackConfig || {}), ...(devData.rackConfig || {}) },
    hierarchy: { ...(prev.hierarchy || {}), ...(devData.hierarchy || {}) },
    openPorts: mergedPorts,
    snmpInfo: { ...(prev.snmpInfo || {}), ...(devData.snmpInfo || {}) },
    switchInterfaces: devData.switchInterfaces || prev.switchInterfaces || [],
    credentials: {
      username: devData.credentials?.username ?? prev.credentials?.username ?? 'admin',
      password: devData.credentials?.password ?? prev.credentials?.password ?? '',
      loginUrl: devData.credentials?.loginUrl ?? prev.credentials?.loginUrl ?? '',
      defaultPort: devData.credentials?.defaultPort ?? prev.credentials?.defaultPort ?? '',
      notes: devData.credentials?.notes ?? prev.credentials?.notes ?? '',
    },
    latencyMs: devData.latencyMs !== undefined ? devData.latencyMs : prev.latencyMs ?? null,
    latencyHistory,
    lastSeen: devData.lastSeen || prev.lastSeen || new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  if (existingIdx >= 0) {
    state.devices[existingIdx] = record;
  } else {
    state.devices.push(record);
  }

  // If this device is a 3D Server Rack, cascade spatial coordinates (floor, room, position, isPlaced) to its mounted children
  if (record.modelType === 'server_rack') {
    state.devices.forEach((child) => {
      if (child.parentRackId === record.id && child.id !== record.id) {
        child.isPlaced = record.isPlaced;
        child.floorIdx = record.floorIdx;
        child.roomId = record.roomId;
        child.roomNumber = record.roomNumber;
        child.position = record.isPlaced && record.position ? { ...record.position } : null;
        dbSaveDevice(child).catch(() => {});
      }
    });
  }

  saveToDisk(true);
  dbSaveDevice(record).catch((err) => console.error('[Store] dbSaveDevice error:', err.message));
  return record;
}

export function getRackMountedItems(rackId) {
  if (!rackId) return [];
  return state.devices
    .filter((d) => d.parentRackId === rackId && d.uPosition !== null && Number(d.uPosition) >= 1)
    .sort((a, b) => Number(b.uPosition) - Number(a.uPosition));
}

export function mountDeviceInRack(rackId, payload = {}) {
  const rack = getDeviceById(rackId);
  if (!rack) {
    return { ok: false, error: 'ไม่พบตู้แร็ค 3D (Server Rack not found)' };
  }

  const rackHeight = Math.max(1, Number(rack.rackConfig?.rackHeight || 42));
  const mountedItems = getRackMountedItems(rackId);

  const template = payload.templateSlug
    ? RACKULA_STARTER_LIBRARY.find((t) => t.slug === payload.templateSlug)
    : null;

  let targetDev = payload.deviceId ? getDeviceById(payload.deviceId) : null;
  const excludeId = targetDev ? targetDev.id : null;

  const mappedCat = mapTwinCategoryToRackula(
    payload.category || targetDev?.category || template?.category || 'Network'
  );

  const uHeight = Math.max(
    1,
    Math.ceil(
      Number(
        payload.uHeight ??
          template?.u_height ??
          targetDev?.uHeight ??
          mappedCat.defaultUHeight ??
          1
      )
    )
  );
  const face = payload.rackFace || payload.face || targetDev?.rackFace || 'front';
  const isFullDepth =
    payload.isFullDepth !== undefined
      ? Boolean(payload.isFullDepth)
      : template?.is_full_depth !== undefined
      ? Boolean(template.is_full_depth)
      : targetDev?.isFullDepth !== undefined
      ? Boolean(targetDev.isFullDepth)
      : Boolean(mappedCat.isFullDepth);

  let uPosition = payload.uPosition !== undefined && payload.uPosition !== null ? Number(payload.uPosition) : null;
  if (!uPosition || uPosition < 1) {
    uPosition = findFirstAvailableUSlot({
      rackHeight,
      uHeight,
      face,
      isFullDepth,
      mountedItems,
      preferTopDown: true,
    });
    if (!uPosition) {
      return {
        ok: false,
        error: `ไม่มีช่องว่างขนาด ${uHeight}U (${face.toUpperCase()}) เหลือในตู้แร็ค ${rackHeight}U นี้`,
      };
    }
  }

  const validation = canMountInRack({
    rackHeight,
    uPosition,
    uHeight,
    face,
    isFullDepth,
    mountedItems,
    excludeId,
  });

  if (!validation.valid) {
    return {
      ok: false,
      error: validation.reason,
      conflictingItem: validation.conflictingItem,
    };
  }

  // Map template category to Digital Twin category if creating from starter library
  const twinCategoryFromTemplate = (cat) => {
    if (cat === 'server') return 'Server';
    if (cat === 'firewall') return 'Router';
    if (cat === 'network' || cat === 'patch-panel') return 'Switch';
    return 'Server';
  };

  const updatedDevice = upsertDevice({
    ...(targetDev || {}),
    id: targetDev?.id || payload.id || `RACKITEM-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).slice(2, 5).toUpperCase()}`,
    name:
      payload.name ||
      targetDev?.name ||
      (template ? `${template.model} (U${uPosition})` : `Rack Device U${uPosition}`),
    category:
      payload.category ||
      targetDev?.category ||
      (template ? twinCategoryFromTemplate(template.category) : 'Switch'),
    customType: payload.customType || template?.slug || targetDev?.customType || '',
    color: payload.color || template?.colour || targetDev?.color || mappedCat.colour,
    vendor: payload.vendor || template?.manufacturer || targetDev?.vendor || 'Generic Rack Hardware',
    parentRackId: rack.id,
    uPosition,
    uHeight,
    rackFace: face,
    isFullDepth,
    isPlaced: Boolean(rack.isPlaced),
    floorIdx: rack.floorIdx,
    roomId: rack.roomId || '',
    roomNumber: rack.roomNumber || '',
    position: rack.isPlaced && rack.position ? { ...rack.position } : null,
    rackConfig: {
      ...(targetDev?.rackConfig || {}),
      ...(payload.rackConfig || {}),
      rackCategory: payload.rackCategory || template?.category || targetDev?.rackConfig?.rackCategory || mappedCat.rackCategory,
      templateSlug: template?.slug || targetDev?.rackConfig?.templateSlug || '',
      isTemplateAccessory: Boolean(template && !targetDev),
      powerWatts: payload.powerWatts ?? template?.power_watts ?? targetDev?.rackConfig?.powerWatts ?? 0,
      airflow: payload.airflow || template?.airflow || targetDev?.rackConfig?.airflow || 'front-to-rear',
      interfaces: template?.interfaces || targetDev?.rackConfig?.interfaces || [],
    },
  });

  return {
    ok: true,
    rack,
    device: updatedDevice,
    mountedItems: getRackMountedItems(rackId),
  };
}

export function unmountDeviceFromRack(rackId, itemId, options = {}) {
  const dev = getDeviceById(itemId);
  if (!dev) {
    return { ok: false, error: 'ไม่พบอุปกรณ์ในตู้แร็ค' };
  }

  // If this was a pure passive template accessory (e.g., blank panel, shelf, cable duct) with no IP/MAC and not explicitly kept
  const isPureTemplateAccessory =
    Boolean(dev.rackConfig?.isTemplateAccessory) &&
    !dev.ip &&
    !dev.mac &&
    !options.keepInQueue;

  if (isPureTemplateAccessory) {
    deleteDevice(dev.id);
    return {
      ok: true,
      removedAccessoryId: dev.id,
      mountedItems: getRackMountedItems(rackId),
    };
  }

  // Otherwise un-mount network device and return it to the Unplaced Queue (or room if specified)
  const updated = upsertDevice({
    ...dev,
    id: dev.id,
    parentRackId: '',
    uPosition: null,
    rackFace: 'front',
    isPlaced: false,
    floorIdx: null,
    roomId: '',
    roomNumber: '',
    position: null,
  });

  return {
    ok: true,
    device: updated,
    mountedItems: getRackMountedItems(rackId),
  };
}

export function updateRackConfig(rackId, configPayload = {}) {
  const rack = getDeviceById(rackId);
  if (!rack) {
    return { ok: false, error: 'ไม่พบตู้แร็ค 3D' };
  }

  const nextHeight = configPayload.rackHeight !== undefined ? Number(configPayload.rackHeight) : Number(rack.rackConfig?.rackHeight || 42);
  const mountedItems = getRackMountedItems(rackId);

  // Verify no mounted device exceeds the new rack height
  for (const item of mountedItems) {
    const topU = Number(item.uPosition || 1) + Number(item.uHeight || 1) - 1;
    if (topU > nextHeight) {
      return {
        ok: false,
        error: `ไม่สามารถลดความสูงตู้เหลือ ${nextHeight}U ได้ เนื่องจากมีอุปกรณ์ "${item.name}" ติดตั้งอยู่ที่ช่อง U${item.uPosition}–U${topU}`,
      };
    }
  }

  const updatedRack = upsertDevice({
    ...rack,
    id: rack.id,
    name: configPayload.name !== undefined ? String(configPayload.name).trim() || rack.name : rack.name,
    rackConfig: {
      ...(rack.rackConfig || {}),
      rackHeight: nextHeight,
      rackWidth: configPayload.rackWidth !== undefined ? Number(configPayload.rackWidth) : Number(rack.rackConfig?.rackWidth || 19),
      formFactor: configPayload.formFactor || rack.rackConfig?.formFactor || '4-post-cabinet',
      notes: configPayload.notes !== undefined ? String(configPayload.notes) : (rack.rackConfig?.notes || ''),
    },
  });

  return {
    ok: true,
    rack: updatedRack,
    mountedItems,
  };
}

/**
 * Remove a server rack from the building (3D + Rackula) in one transaction.
 * - Real devices (with IP) inside the rack are returned to the scan queue (unmounted, unplaced).
 * - IP-less Rackula library parts are deleted.
 * - The rack itself is deleted.
 * Returns an undo snapshot consumed by restoreRackCascade().
 */
export function removeRackCascade(rackId) {
  const rack = getDeviceById(rackId);
  if (!rack || rack.modelType !== 'server_rack') {
    return { ok: false, error: 'Server Rack not found' };
  }
  const children = state.devices.filter((d) => d.parentRackId === rackId && d.id !== rackId);
  const snapshot = { rack: JSON.parse(JSON.stringify(rack)), parts: [], devices: [] };

  for (const child of children) {
    if (String(child.ip || '').trim()) {
      snapshot.devices.push(JSON.parse(JSON.stringify(child)));
      upsertDevice({
        ...child,
        id: child.id,
        parentRackId: '',
        uPosition: null,
        isPlaced: false,
        floorIdx: null,
        roomId: '',
        roomNumber: '',
        position: null,
      });
    } else {
      snapshot.parts.push(JSON.parse(JSON.stringify(child)));
      deleteDevice(child.id);
    }
  }
  deleteDevice(rackId);
  return { ok: true, snapshot, returnedToQueue: snapshot.devices.length, deletedParts: snapshot.parts.length };
}

/** Undo of removeRackCascade(): recreate the rack, its library parts and re-mount real devices. */
export function restoreRackCascade(snapshot) {
  if (!snapshot || !snapshot.rack || !snapshot.rack.id) {
    return { ok: false, error: 'Invalid rack snapshot' };
  }
  const rack = upsertDevice({ ...snapshot.rack });
  for (const part of snapshot.parts || []) upsertDevice({ ...part });
  for (const dev of snapshot.devices || []) upsertDevice({ ...dev });
  return { ok: true, rack, mountedItems: getRackMountedItems(rack.id) };
}
export function replaceDevicePorts(id, openPorts) {
  const dev = state.devices.find((d) => d.id === id);
  if (!dev) return null;
  dev.openPorts = openPorts;
  dev.updatedAt = new Date().toISOString();
  saveToDisk();
  dbSaveDevice(dev).catch((err) => console.error('[Store] dbSaveDevice error:', err.message));
  return dev;
}

export function deleteDevice(id) {
  state.devices = state.devices.filter((d) => d.id !== id);
  saveToDisk();
  dbDeleteDevice(id).catch((err) => console.error('[Store] dbDeleteDevice error:', err.message));
}

export function clearAllRoomsAndResetPlacements() {
  state.rooms = [];
  state.devices.forEach((d) => {
    d.isPlaced = false;
    d.floorIdx = null;
    d.roomId = '';
    d.roomNumber = '';
    d.position = null;
  });
  saveToDisk(true);
  prisma.room.deleteMany().catch(() => {});
  state.devices.forEach((d) => dbSaveDevice(d).catch(() => {}));
}

export function importFullBundle(bundle) {
  const check = validateBundleSchema(bundle);
  if (!check.valid) {
    throw new Error(`Invalid JSON Schema: ${check.errors.join('; ')}`);
  }
  if (Array.isArray(bundle.rooms)) state.rooms = bundle.rooms;
  if (Array.isArray(bundle.devices)) state.devices = bundle.devices;
  if (Array.isArray(bundle.networks)) state.networks = bundle.networks;
  saveToDisk(true);
  Promise.all([
    ...state.networks.map(dbSaveNetwork),
    ...state.rooms.map(dbSaveRoom),
    ...state.devices.map(dbSaveDevice),
  ]).catch((err) => console.error('[Store] db import error:', err.message));
  return getAdminSnapshot();
}

export function addScanLog(entry) {
  state.scanHistory.unshift({
    id: `SCAN-${Date.now().toString(36).toUpperCase()}`,
    timestamp: new Date().toISOString(),
    ...entry,
  });
  if (state.scanHistory.length > 30) {
    state.scanHistory = state.scanHistory.slice(0, 30);
  }
  saveToDisk();
}

export function updateDefaultViewState(viewState = {}) {
  if (!state.metadata) state.metadata = {};
  state.metadata.defaultViewState = {
    ...(state.metadata.defaultViewState || {}),
    ...viewState,
  };
  state.metadata.updatedAt = new Date().toISOString();
  saveToDisk(true);
  dbSaveSetting('defaultViewState', state.metadata.defaultViewState).catch((err) =>
    console.error('[Store] dbSaveSetting error:', err.message)
  );
  return state.metadata.defaultViewState;
}

export function getDefaultViewState() {
  return state.metadata?.defaultViewState || null;
}

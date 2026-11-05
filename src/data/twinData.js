// =============================================================================
// LUDUS BUILDING DIGITAL TWIN — ARCHITECTURAL & NETWORK CONFIGURATION
// =============================================================================

export const FLOORS = [
  { id: '00_ground',  index: 0, label: '00_Ground_Floor', shortLabel: 'G',  elevation: 0.0,  height: 4.0,  planImage: '/plans/floor_00.png' },
  { id: '01_first',   index: 1, label: '01_First_Floor',  shortLabel: '1F', elevation: 4.0,  height: 4.0,  planImage: '/plans/floor_01.png' },
  { id: '02_second',  index: 2, label: '02_Second_Floor', shortLabel: '2F', elevation: 8.0,  height: 4.0,  planImage: '/plans/floor_02.png' },
  { id: '03_rooftop', index: 3, label: '03_Rooftop',      shortLabel: 'RF', elevation: 12.0, height: 3.2,  planImage: '/plans/floor_03.png' },
];

export const OVERLAY_BOUNDS = {
  minX: -52.917,
  maxX: 65.969,
  minY: -35.278,
  maxY: 48.824,
  width: 118.886,
  depth: 84.102,
};

export const DEVICE_CATEGORIES = [
  { id: 'Router',         label: 'Router / Gateway',     color: '#f97316', icon: '🌐' },
  { id: 'Switch',         label: 'Network Switch',       color: '#38bdf8', icon: '🔀' },
  { id: 'Access Point',   label: 'Wireless AP',          color: '#06b6d4', icon: '📶' },
  { id: 'Server',         label: 'Server / NAS / VM',    color: '#a855f7', icon: '🖥️' },
  { id: 'CCTV',           label: 'CCTV / IP Camera',     color: '#ec4899', icon: '📹' },
  { id: 'Access Control', label: 'Access Control',       color: '#eab308', icon: '🔐' },
  { id: 'HVAC',           label: 'HVAC / BMS',           color: '#22c55e', icon: '❄️' },
  { id: 'Sensor',         label: 'IoT / Sensor',         color: '#14b8a6', icon: '📡' },
  { id: 'Printer',        label: 'Network Printer',      color: '#facc15', icon: '🖨️' },
  { id: 'Lighting',       label: 'Smart Lighting',       color: '#fde047', icon: '💡' },
  { id: 'Audio',          label: 'PA / Audio System',    color: '#8b5cf6', icon: '🔊' },
  { id: 'Power',          label: 'UPS / Power Meter',    color: '#ef4444', icon: '⚡' },
  { id: 'Network',        label: 'Generic Network Host', color: '#60a5fa', icon: '🔌' },
  { id: 'Custom',         label: 'Custom Device...',     color: '#f43f5e', icon: '🔧' },
];

export const ROOM_TYPES = [
  { id: 'NOC',       label: 'NOC / Server / MDF-IDF', color: '#38bdf8', icon: '🖥️', defaultWidth: 12, defaultDepth: 10 },
  { id: 'Office',    label: 'Office / Meeting Room',  color: '#60a5fa', icon: '🏢', defaultWidth: 12, defaultDepth: 10 },
  { id: 'Classroom', label: 'Classroom / Studio',     color: '#a855f7', icon: '🎓', defaultWidth: 14, defaultDepth: 12 },
  { id: 'Lobby',     label: 'Lobby / Common Area',    color: '#14b8a6', icon: '🏛️', defaultWidth: 18, defaultDepth: 14 },
  { id: 'ME',        label: 'M&E / Electrical / UPS', color: '#f97316', icon: '⚡', defaultWidth: 10, defaultDepth: 8 },
  { id: 'Sport',     label: 'Sport / Activity Court', color: '#22c55e', icon: '🏀', defaultWidth: 24, defaultDepth: 16 },
  { id: 'Security',  label: 'Security / Control',     color: '#ec4899', icon: '🛡️', defaultWidth: 10, defaultDepth: 8 },
  { id: 'Custom',    label: 'General / Custom Zone',  color: '#eab308', icon: '📍', defaultWidth: 12, defaultDepth: 10 },
];

export const MODEL_CATALOG = [
  {
    id: 'pin',
    name: '3D Glowing Pin (Default)',
    type: 'procedural',
    icon: '📍',
    description: 'หมุดเรืองแสงทรงกลมมาตรฐานพร้อมเสาแกน 3D',
  },
  {
    id: 'server_rack',
    name: 'Server Rack Cabinet (1K Web)',
    type: 'glb',
    path: '/models/server_rack.glb',
    icon: '🖥️',
    description: 'ตู้ Server Rack Cabinet พร้อมประตูกระจกและตะแกรงระบายความร้อน',
    scale: [1, 1, 1],
    yOffset: 0.0,
  },
];

export function getModelCatalogMeta(modelId = 'pin') {
  return MODEL_CATALOG.find((m) => m.id === modelId) || MODEL_CATALOG[0];
}

/**
 * Clamp a 3D coordinate (x, z) to be strictly inside a room's bounding perimeter.
 * Works for both Rectangle zones and Polygon zones.
 * @param {object} room
 * @param {number} x
 * @param {number} z
 * @param {number} margin - Safety padding in meters from wall
 * @returns {{x: number, z: number}}
 */
export function clampPointToRoomBounds(room, x = 0, z = 0, margin = 0.4) {
  if (!room) return { x, z };

  // 1. Polygon Zone Clamping
  if (Array.isArray(room.polygon) && room.polygon.length >= 3) {
    let minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
    for (const pt of room.polygon) {
      const px = Number(pt.x ?? 0);
      const pz = Number(pt.z ?? 0);
      if (px < minX) minX = px;
      if (px > maxX) maxX = px;
      if (pz < minZ) minZ = pz;
      if (pz > maxZ) maxZ = pz;
    }
    const safeMinX = minX + margin <= maxX - margin ? minX + margin : (minX + maxX) / 2;
    const safeMaxX = minX + margin <= maxX - margin ? maxX - margin : (minX + maxX) / 2;
    const safeMinZ = minZ + margin <= maxZ - margin ? minZ + margin : (minZ + maxZ) / 2;
    const safeMaxZ = minZ + margin <= maxZ - margin ? maxZ - margin : (minZ + maxZ) / 2;

    const clampedX = Math.min(safeMaxX, Math.max(safeMinX, Number(x)));
    const clampedZ = Math.min(safeMaxZ, Math.max(safeMinZ, Number(z)));
    return { x: Number(clampedX.toFixed(2)), z: Number(clampedZ.toFixed(2)) };
  }

  // 2. Rectangle Zone Clamping
  const rx = Number(room.position?.x ?? 0);
  const rz = Number(room.position?.z ?? 0);
  const totalW = Number(room.zoneSize?.width ?? 12);
  const totalD = Number(room.zoneSize?.depth ?? 10);

  const halfW = Math.max(0.2, (totalW / 2) - margin);
  const halfD = Math.max(0.2, (totalD / 2) - margin);

  const clampedX = Math.min(rx + halfW, Math.max(rx - halfW, Number(x)));
  const clampedZ = Math.min(rz + halfD, Math.max(rz - halfD, Number(z)));

  return { x: Number(clampedX.toFixed(2)), z: Number(clampedZ.toFixed(2)) };
}

/**
 * Compute polygon area in square meters using the Shoelace formula.
 * @param {Array<{x: number, z: number}>} poly
 */
export function computePolygonArea(poly = []) {
  if (!Array.isArray(poly) || poly.length < 3) return 0;
  let sum = 0;
  for (let i = 0; i < poly.length; i++) {
    const p1 = poly[i];
    const p2 = poly[(i + 1) % poly.length];
    sum += Number(p1.x || 0) * Number(p2.z || 0) - Number(p2.x || 0) * Number(p1.z || 0);
  }
  return Math.abs(sum) / 2;
}

/**
 * Compute polygon centroid (or bounding box center fallback) in {x, z}.
 * @param {Array<{x: number, z: number}>} poly
 */
export function computePolygonCentroid(poly = []) {
  if (!Array.isArray(poly) || poly.length === 0) return { x: 0, z: 0 };
  let sumX = 0;
  let sumZ = 0;
  for (const pt of poly) {
    sumX += Number(pt.x || 0);
    sumZ += Number(pt.z || 0);
  }
  return {
    x: Number((sumX / poly.length).toFixed(2)),
    z: Number((sumZ / poly.length).toFixed(2)),
  };
}

/**
 * Point-in-Polygon test (Ray-Casting algorithm in XZ plane).
 * @param {number} x
 * @param {number} z
 * @param {Array<{x: number, z: number}>} poly
 */
export function isPointInPolygonXZ(x, z, poly = []) {
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

/**
 * Find the room on the given floor whose 3D Floor Zone (Polygon or Rectangle) contains (x, z),
 * or the closest room within snapRadiusMeters.
 */
export function findMatchingRoomForPoint(rooms = [], floorIdx = 0, x = 0, z = 0, snapRadiusMeters = 14) {
  const floorRooms = (rooms || []).filter((r) => Number(r.floorIdx ?? 0) === Number(floorIdx));
  if (floorRooms.length === 0) return null;

  // 1. Check exact Polygon (if >= 3 vertices) or Rectangle containment first (smallest area wins if overlapping)
  const containing = floorRooms
    .filter((r) => {
      if (Array.isArray(r.polygon) && r.polygon.length >= 3) {
        return isPointInPolygonXZ(x, z, r.polygon);
      }
      const rx = Number(r.position?.x ?? 0);
      const rz = Number(r.position?.z ?? 0);
      const halfW = Number(r.zoneSize?.width ?? 12) / 2;
      const halfD = Number(r.zoneSize?.depth ?? 10) / 2;
      return Math.abs(x - rx) <= halfW && Math.abs(z - rz) <= halfD;
    })
    .sort((a, b) => {
      const areaA =
        Array.isArray(a.polygon) && a.polygon.length >= 3
          ? computePolygonArea(a.polygon)
          : Number(a.zoneSize?.width ?? 12) * Number(a.zoneSize?.depth ?? 10);
      const areaB =
        Array.isArray(b.polygon) && b.polygon.length >= 3
          ? computePolygonArea(b.polygon)
          : Number(b.zoneSize?.width ?? 12) * Number(b.zoneSize?.depth ?? 10);
      return areaA - areaB;
    });

  if (containing.length > 0) return containing[0];

  // 2. Fallback: nearest room center within snapRadiusMeters
  let best = null;
  let bestDist = Infinity;
  for (const r of floorRooms) {
    const rx = Number(r.position?.x ?? 0);
    const rz = Number(r.position?.z ?? 0);
    const dist = Math.hypot(x - rx, z - rz);
    if (dist <= snapRadiusMeters && dist < bestDist) {
      bestDist = dist;
      best = r;
    }
  }
  return best;
}


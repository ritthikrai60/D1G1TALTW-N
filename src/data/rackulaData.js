// =============================================================================
// RACKULA NATIVE ENGINE — PORTED FROM https://github.com/RackulaLives/Rackula
// Includes Dracula Muted Palette, NetBox Starter Device Library,
// EIA-310 Whole-U Collision Detection, Blocked Slots & YAML Serializer
// =============================================================================

/**
 * Default colours for each device category
 * From Rackula BRAND.md v0.6.0 - Muted Dracula palette for WCAG AA compliance
 */
export const RACKULA_CATEGORY_COLOURS = {
  server: '#4A7A8A',           // muted cyan
  network: '#7968A6',          // muted purple
  firewall: '#C0392B',         // alert red
  storage: '#3D7A4A',          // muted green
  power: '#A84A4A',            // muted red
  kvm: '#926A40',              // muted orange
  'av-media': '#A85A7A',       // muted pink
  cooling: '#75753F',          // muted yellow
  chassis: '#5A6A8A',          // muted blue-gray
  shelf: '#6272A4',            // Dracula comment neutral
  blank: '#44475A',            // Dracula selection neutral
  'cable-management': '#6272A4',
  'patch-panel': '#6272A4',
  other: '#6272A4',
};

export const RACKULA_CATEGORIES = [
  { id: 'all', label: 'ทั้งหมด (All)', color: '#BD93F9' },
  { id: 'server', label: 'Server / Compute', color: RACKULA_CATEGORY_COLOURS.server },
  { id: 'network', label: 'Network Switch', color: RACKULA_CATEGORY_COLOURS.network },
  { id: 'firewall', label: 'Router / Firewall', color: RACKULA_CATEGORY_COLOURS.firewall },
  { id: 'patch-panel', label: 'Patch Panel', color: RACKULA_CATEGORY_COLOURS['patch-panel'] },
  { id: 'power', label: 'UPS / PDU Power', color: RACKULA_CATEGORY_COLOURS.power },
  { id: 'storage', label: 'Storage / NAS / SAN', color: RACKULA_CATEGORY_COLOURS.storage },
  { id: 'kvm', label: 'KVM / Console', color: RACKULA_CATEGORY_COLOURS.kvm },
  { id: 'cooling', label: 'Cooling / Fan Panel', color: RACKULA_CATEGORY_COLOURS.cooling },
  { id: 'shelf', label: 'Rack Shelf / Tray', color: RACKULA_CATEGORY_COLOURS.shelf },
  { id: 'cable-management', label: 'Cable Management', color: RACKULA_CATEGORY_COLOURS['cable-management'] },
  { id: 'blank', label: 'Blanking Panel', color: RACKULA_CATEGORY_COLOURS.blank },
];

export const COMMON_RACK_HEIGHTS = [12, 18, 24, 42, 48];

/**
 * SVG Geometry Constants from Rackula (src/lib/components/RackFrame.svelte)
 */
export const RACK_SVG_METRICS = {
  rackWidth: 256,
  railWidth: 20,
  interiorWidth: 216, // 256 - 2 * 20
  uHeightPx: 26,
  rackPadding: 22,
};

function makePortInterfaces(count, type = '1000base-t') {
  return Array.from({ length: count }, (_, i) => ({
    name: String(i + 1),
    type,
  }));
}

/**
 * Official Starter Device Type Library from Rackula (src/lib/data/starterLibrary.ts)
 * Enhanced with common NetBox enterprise templates
 */
export const RACKULA_STARTER_LIBRARY = [
  // Servers
  {
    slug: '1u-server',
    manufacturer: 'Dell / HP / Supermicro',
    model: '1U Rackmount Server (R650 / DL360)',
    u_height: 1,
    category: 'server',
    is_full_depth: true,
    power_watts: 350,
    airflow: 'front-to-rear',
    colour: RACKULA_CATEGORY_COLOURS.server,
    interfaces: makePortInterfaces(4, '10gbase-x-sfpp'),
  },
  {
    slug: '2u-server',
    manufacturer: 'Dell / HP / Proxmox',
    model: '2U Hypervisor Server (R750 / DL380)',
    u_height: 2,
    category: 'server',
    is_full_depth: true,
    power_watts: 550,
    airflow: 'front-to-rear',
    colour: RACKULA_CATEGORY_COLOURS.server,
    interfaces: makePortInterfaces(8, '10gbase-x-sfpp'),
  },
  {
    slug: '4u-server',
    manufacturer: 'Supermicro / GPU Node',
    model: '4U High-Density Compute / AI Server',
    u_height: 4,
    category: 'server',
    is_full_depth: true,
    power_watts: 1200,
    airflow: 'front-to-rear',
    colour: RACKULA_CATEGORY_COLOURS.server,
    interfaces: makePortInterfaces(8, '25gbase-x-sfp28'),
  },

  // Firewalls & Routers
  {
    slug: '1u-router-firewall',
    manufacturer: 'Fortinet / Huawei / MikroTik',
    model: '1U Core Router / NGFW Firewall',
    u_height: 1,
    category: 'firewall',
    is_full_depth: false,
    power_watts: 120,
    airflow: 'front-to-rear',
    colour: RACKULA_CATEGORY_COLOURS.firewall,
    interfaces: makePortInterfaces(12, '1000base-t'),
  },
  {
    slug: '2u-router-firewall',
    manufacturer: 'Palo Alto / Cisco',
    model: '2U Enterprise Edge Gateway',
    u_height: 2,
    category: 'firewall',
    is_full_depth: true,
    power_watts: 280,
    airflow: 'front-to-rear',
    colour: RACKULA_CATEGORY_COLOURS.firewall,
    interfaces: makePortInterfaces(16, '10gbase-x-sfpp'),
  },

  // Network Switches
  {
    slug: '24-port-switch',
    manufacturer: 'Ruijie / Reyee / Cisco',
    model: '24-Port Managed PoE+ Switch (1U)',
    u_height: 1,
    category: 'network',
    is_full_depth: false,
    power_watts: 240,
    airflow: 'side-to-rear',
    colour: RACKULA_CATEGORY_COLOURS.network,
    interfaces: makePortInterfaces(24, '1000base-t'),
  },
  {
    slug: '48-port-switch',
    manufacturer: 'Ruijie / Ubiquiti / Aruba',
    model: '48-Port Core Distribution Switch (1U)',
    u_height: 1,
    category: 'network',
    is_full_depth: true,
    power_watts: 420,
    airflow: 'front-to-rear',
    colour: RACKULA_CATEGORY_COLOURS.network,
    interfaces: makePortInterfaces(48, '1000base-t'),
  },
  {
    slug: '1u-sfp-aggregation',
    manufacturer: 'MikroTik / Ruijie',
    model: '10G/25G SFP+ Aggregation Switch (1U)',
    u_height: 1,
    category: 'network',
    is_full_depth: false,
    power_watts: 150,
    airflow: 'front-to-rear',
    colour: RACKULA_CATEGORY_COLOURS.network,
    interfaces: makePortInterfaces(16, '10gbase-x-sfpp'),
  },

  // Patch Panels
  {
    slug: '24-port-patch-panel',
    manufacturer: 'Panduit / CommScope',
    model: '24-Port CAT6A Patch Panel (1U)',
    u_height: 1,
    category: 'patch-panel',
    is_full_depth: false,
    power_watts: 0,
    colour: RACKULA_CATEGORY_COLOURS['patch-panel'],
    interfaces: makePortInterfaces(24, '1000base-t'),
  },
  {
    slug: '48-port-patch-panel',
    manufacturer: 'Panduit / CommScope',
    model: '48-Port CAT6A Patch Panel (2U)',
    u_height: 2,
    category: 'patch-panel',
    is_full_depth: false,
    power_watts: 0,
    colour: RACKULA_CATEGORY_COLOURS['patch-panel'],
    interfaces: makePortInterfaces(48, '1000base-t'),
  },
  {
    slug: '1u-fiber-patch-panel',
    manufacturer: 'Corning / FS',
    model: '24-Core LC Duplex Fiber ODF (1U)',
    u_height: 1,
    category: 'patch-panel',
    is_full_depth: false,
    power_watts: 0,
    colour: RACKULA_CATEGORY_COLOURS['patch-panel'],
    interfaces: makePortInterfaces(12, '1000base-x-sfp'),
  },

  // Storage / NAS
  {
    slug: '2u-storage',
    manufacturer: 'Synology / QNAP',
    model: '2U 8-Bay RackStation NAS',
    u_height: 2,
    category: 'storage',
    is_full_depth: true,
    power_watts: 260,
    airflow: 'front-to-rear',
    colour: RACKULA_CATEGORY_COLOURS.storage,
    interfaces: makePortInterfaces(4, '1000base-t'),
  },
  {
    slug: '4u-storage',
    manufacturer: 'TrueNAS / Enterprise SAN',
    model: '4U 24-Bay Storage Array',
    u_height: 4,
    category: 'storage',
    is_full_depth: true,
    power_watts: 680,
    airflow: 'front-to-rear',
    colour: RACKULA_CATEGORY_COLOURS.storage,
    interfaces: makePortInterfaces(4, '10gbase-x-sfpp'),
  },

  // Power (PDU & UPS)
  {
    slug: '1u-pdu',
    manufacturer: 'APC / CyberPower',
    model: '1U Rack PDU 8-Outlet Metered',
    u_height: 1,
    category: 'power',
    is_full_depth: false,
    power_watts: 15,
    colour: RACKULA_CATEGORY_COLOURS.power,
  },
  {
    slug: '2u-ups',
    manufacturer: 'APC / Eaton',
    model: '2U Smart-UPS 3000VA LCD (RM)',
    u_height: 2,
    category: 'power',
    is_full_depth: true,
    power_watts: 45,
    va_rating: 3000,
    colour: RACKULA_CATEGORY_COLOURS.power,
  },
  {
    slug: '4u-ups',
    manufacturer: 'APC Symmetra / Vertiv',
    model: '4U Online Double-Conversion UPS 6000VA',
    u_height: 4,
    category: 'power',
    is_full_depth: true,
    power_watts: 90,
    va_rating: 6000,
    colour: RACKULA_CATEGORY_COLOURS.power,
  },

  // KVM, Shelves, Cable Management & Blanks
  {
    slug: '1u-console-drawer',
    manufacturer: 'ATEN / StarTech',
    model: '1U 19" LCD KVM Console Drawer',
    u_height: 1,
    category: 'kvm',
    is_full_depth: true,
    power_watts: 35,
    colour: RACKULA_CATEGORY_COLOURS.kvm,
  },
  {
    slug: '1u-cable-manager',
    manufacturer: 'Panduit',
    model: '1U Horizontal Finger Duct Cable Manager',
    u_height: 1,
    category: 'cable-management',
    is_full_depth: false,
    power_watts: 0,
    colour: RACKULA_CATEGORY_COLOURS['cable-management'],
  },
  {
    slug: '1u-shelf',
    manufacturer: 'Generic',
    model: '1U Cantilever Vented Equipment Shelf (Modem/MiniPC)',
    u_height: 1,
    category: 'shelf',
    is_full_depth: false,
    power_watts: 0,
    colour: RACKULA_CATEGORY_COLOURS.shelf,
  },
  {
    slug: '1u-fan-panel',
    manufacturer: 'AC Infinity',
    model: '1U Cloudplate Intelligent Exhaust Fan Panel',
    u_height: 1,
    category: 'cooling',
    is_full_depth: false,
    power_watts: 25,
    colour: RACKULA_CATEGORY_COLOURS.cooling,
  },
  {
    slug: '1u-blank',
    manufacturer: 'Generic',
    model: '1U Snap-In Blanking Panel',
    u_height: 1,
    category: 'blank',
    is_full_depth: false,
    power_watts: 0,
    colour: RACKULA_CATEGORY_COLOURS.blank,
  },
  {
    slug: '2u-blank',
    manufacturer: 'Generic',
    model: '2U Blanking Panel',
    u_height: 2,
    category: 'blank',
    is_full_depth: false,
    power_watts: 0,
    colour: RACKULA_CATEGORY_COLOURS.blank,
  },
];

/**
 * Map a Digital Twin device category to a Rackula category & colour
 */
export function mapTwinCategoryToRackula(category = 'Network') {
  const c = String(category).toLowerCase();
  if (c.includes('router') || c.includes('firewall') || c.includes('gateway')) {
    return { rackCategory: 'firewall', colour: RACKULA_CATEGORY_COLOURS.firewall, defaultUHeight: 1, isFullDepth: false };
  }
  if (c.includes('switch')) {
    return { rackCategory: 'network', colour: RACKULA_CATEGORY_COLOURS.network, defaultUHeight: 1, isFullDepth: false };
  }
  if (c.includes('server') || c.includes('vm') || c.includes('hypervisor')) {
    return { rackCategory: 'server', colour: RACKULA_CATEGORY_COLOURS.server, defaultUHeight: 2, isFullDepth: true };
  }
  if (c.includes('storage') || c.includes('nas')) {
    return { rackCategory: 'storage', colour: RACKULA_CATEGORY_COLOURS.storage, defaultUHeight: 2, isFullDepth: true };
  }
  if (c.includes('power') || c.includes('ups')) {
    return { rackCategory: 'power', colour: RACKULA_CATEGORY_COLOURS.power, defaultUHeight: 2, isFullDepth: true };
  }
  if (c.includes('audio') || c.includes('av')) {
    return { rackCategory: 'av-media', colour: RACKULA_CATEGORY_COLOURS['av-media'], defaultUHeight: 2, isFullDepth: false };
  }
  return { rackCategory: 'network', colour: RACKULA_CATEGORY_COLOURS.network, defaultUHeight: 1, isFullDepth: false };
}

/**
 * Compute inclusive U range [bottom, top] occupied by a device at uPosition with uHeight.
 * Matches Rackula EIA-310 whole-U standard (e.g. position=40, uHeight=2 -> occupies U40 and U41).
 */
export function getDeviceURange(uPosition, uHeight = 1) {
  const pos = Math.max(1, Math.round(Number(uPosition) || 1));
  const h = Math.max(1, Math.ceil(Number(uHeight) || 1));
  return {
    bottom: pos,
    top: pos + h - 1,
  };
}

/**
 * Check if two U ranges [bottom, top] overlap
 */
export function doURangesOverlap(rangeA, rangeB) {
  return rangeA.bottom <= rangeB.top && rangeB.bottom <= rangeA.top;
}

/**
 * Check if two mounted items conflict on face/depth:
 * - Same face always conflicts
 * - If EITHER item is full-depth (`isFullDepth: true` or `face === 'both'`), it occupies both Front and Rear at those U-slots!
 */
export function doFacesConflict(faceA = 'front', isFullDepthA = true, faceB = 'front', isFullDepthB = true) {
  if (faceA === 'both' || faceB === 'both') return true;
  if (isFullDepthA || isFullDepthB) return true;
  return faceA === faceB;
}

/**
 * Validate whether a device of `uHeight`, `face`, `isFullDepth` can be mounted at `uPosition`
 * inside a rack of `rackHeight` containing `mountedItems`.
 *
 * @param {object} params
 * @param {number} params.rackHeight - Total U height of rack (e.g. 42)
 * @param {number} params.uPosition - Target bottom U position (1..rackHeight)
 * @param {number} params.uHeight - Device height in U (1..42)
 * @param {'front'|'rear'|'both'} params.face - Mounting face
 * @param {boolean} params.isFullDepth - Whether device occupies full depth
 * @param {Array} params.mountedItems - Existing mounted items in the rack
 * @param {string|null} params.excludeId - Optional item ID to exclude (when moving an already mounted item)
 * @returns {{ valid: boolean, reason?: string, conflictingItem?: object }}
 */
export function canMountInRack({
  rackHeight = 42,
  uPosition = 1,
  uHeight = 1,
  face = 'front',
  isFullDepth = true,
  mountedItems = [],
  excludeId = null,
}) {
  const totalU = Math.max(1, Number(rackHeight) || 42);
  const pos = Math.round(Number(uPosition) || 1);
  const h = Math.max(1, Math.ceil(Number(uHeight) || 1));

  if (pos < 1) {
    return { valid: false, reason: 'ตำแหน่ง U ต้องเริ่มตั้งแต่ U1 ขึ้นไป' };
  }
  const targetRange = getDeviceURange(pos, h);
  if (targetRange.top > totalU) {
    return {
      valid: false,
      reason: `อุปกรณ์ขนาด ${h}U ที่ตำแหน่ง U${pos} (กินพื้นที่ U${targetRange.bottom}–U${targetRange.top}) เกินความสูงตู้ ${totalU}U`,
    };
  }

  for (const item of mountedItems) {
    if (excludeId && item.id === excludeId) continue;
    const itemPos = Number(item.uPosition);
    if (!itemPos || itemPos < 1) continue;
    const itemRange = getDeviceURange(itemPos, item.uHeight || 1);

    if (doURangesOverlap(targetRange, itemRange)) {
      const itemFace = item.rackFace || item.face || 'front';
      const itemFullDepth = item.isFullDepth !== undefined ? Boolean(item.isFullDepth) : true;
      if (doFacesConflict(face, isFullDepth, itemFace, itemFullDepth)) {
        return {
          valid: false,
          reason: `ชนกับ "${item.name}" ที่ติดตั้งอยู่ในช่อง U${itemRange.bottom}${itemRange.top > itemRange.bottom ? `–U${itemRange.top}` : ''} (${itemFullDepth ? 'Full-Depth ทะลุหน้า-หลัง' : itemFace.toUpperCase()})`,
          conflictingItem: item,
        };
      }
    }
  }

  return { valid: true };
}

/**
 * Find the highest (top-down) or lowest (bottom-up) available U-slot for a given device height & face.
 */
export function findFirstAvailableUSlot({
  rackHeight = 42,
  uHeight = 1,
  face = 'front',
  isFullDepth = true,
  mountedItems = [],
  preferTopDown = true,
}) {
  const totalU = Math.max(1, Number(rackHeight) || 42);
  const h = Math.max(1, Math.ceil(Number(uHeight) || 1));
  const maxStartU = totalU - h + 1;

  if (preferTopDown) {
    for (let u = maxStartU; u >= 1; u--) {
      const check = canMountInRack({ rackHeight: totalU, uPosition: u, uHeight: h, face, isFullDepth, mountedItems });
      if (check.valid) return u;
    }
  } else {
    for (let u = 1; u <= maxStartU; u++) {
      const check = canMountInRack({ rackHeight: totalU, uPosition: u, uHeight: h, face, isFullDepth, mountedItems });
      if (check.valid) return u;
    }
  }
  return null;
}

/**
 * Compute blocked slots on `viewFace` caused by full-depth devices mounted on the opposite face.
 * Ported from Rackula's `src/lib/utils/blocked-slots.ts`.
 */
export function computeBlockedSlots(mountedItems = [], viewFace = 'front') {
  const blocked = [];
  for (const item of mountedItems) {
    const itemFace = item.rackFace || item.face || 'front';
    const isFullDepth = item.isFullDepth !== undefined ? Boolean(item.isFullDepth) : true;
    if (itemFace !== viewFace && (isFullDepth || itemFace === 'both')) {
      const range = getDeviceURange(item.uPosition, item.uHeight || 1);
      blocked.push({
        bottom: range.bottom,
        top: range.top,
        deviceName: item.name,
        otherFace: itemFace,
        colour: item.color || item.colour || '#4A7A8A',
        item,
      });
    }
  }
  return blocked;
}

/**
 * Serialize a rack and its mounted items into an authentic Rackula v1.0.0 YAML layout string
 */
export function serializeToRackulaYaml(rackDevice, mountedItems = []) {
  const rackHeight = Number(rackDevice?.rackConfig?.rackHeight || 42);
  const rackWidth = Number(rackDevice?.rackConfig?.rackWidth || 19);
  const rackName = rackDevice?.name || 'LUDUS Server Rack';

  const deviceTypesMap = new Map();
  const placedYamlList = [];

  for (const item of mountedItems) {
    const slug =
      item.slug ||
      item.deviceType ||
      `${String(item.category || 'device').toLowerCase().replace(/[^a-z0-9]+/g, '-')}-${item.uHeight || 1}u`;

    if (!deviceTypesMap.has(slug)) {
      const mapped = mapTwinCategoryToRackula(item.category);
      deviceTypesMap.set(slug, {
        slug,
        manufacturer: item.vendor || item.manufacturer || 'Generic',
        model: item.model || item.name || slug,
        u_height: Number(item.uHeight || 1),
        is_full_depth: item.isFullDepth !== undefined ? Boolean(item.isFullDepth) : true,
        colour: item.color || item.colour || mapped.colour,
        category: item.rackCategory || mapped.rackCategory,
      });
    }

    placedYamlList.push({
      id: item.id,
      device_type: slug,
      position: Number(item.uPosition || 1),
      face: item.rackFace || item.face || 'front',
      name: item.name,
      ip: item.ip || undefined,
      notes: item.notes || (item.ip ? `IP: ${item.ip} | MAC: ${item.mac || '-'}` : undefined),
    });
  }

  const lines = [
    `# Generated by LUDUS Digital Twin (Rackula Schema v1.0.0 Compatible)`,
    `version: "1.0.0"`,
    `metadata:`,
    `  schema_version: "1.0"`,
    `name: "${rackName.replace(/"/g, '\\"')}"`,
    ``,
    `rack:`,
    `  id: "${rackDevice?.id || 'rack-0'}"`,
    `  name: "${rackName.replace(/"/g, '\\"')}"`,
    `  height: ${rackHeight}`,
    `  width: ${rackWidth}`,
    `  desc_units: false`,
    `  form_factor: "4-post-cabinet"`,
    `  starting_unit: 1`,
    `  position: 0`,
    `  devices:`,
  ];

  if (placedYamlList.length === 0) {
    lines[lines.length - 1] = `  devices: []`;
  } else {
    for (const pd of placedYamlList) {
      lines.push(`    - id: "${pd.id}"`);
      lines.push(`      device_type: "${pd.device_type}"`);
      lines.push(`      position: ${pd.position}`);
      lines.push(`      face: "${pd.face}"`);
      lines.push(`      name: "${String(pd.name || '').replace(/"/g, '\\"')}"`);
      if (pd.notes) {
        lines.push(`      notes: "${String(pd.notes).replace(/"/g, '\\"')}"`);
      }
    }
  }

  lines.push(``);
  lines.push(`device_types:`);
  if (deviceTypesMap.size === 0) {
    lines[lines.length - 1] = `device_types: []`;
  } else {
    for (const dt of deviceTypesMap.values()) {
      lines.push(`  - slug: "${dt.slug}"`);
      lines.push(`    manufacturer: "${String(dt.manufacturer).replace(/"/g, '\\"')}"`);
      lines.push(`    model: "${String(dt.model).replace(/"/g, '\\"')}"`);
      lines.push(`    u_height: ${dt.u_height}`);
      lines.push(`    is_full_depth: ${dt.is_full_depth}`);
      lines.push(`    colour: "${dt.colour}"`);
      lines.push(`    category: "${dt.category}"`);
    }
  }

  lines.push(``);
  lines.push(`settings:`);
  lines.push(`  display_mode: "label"`);
  lines.push(`  show_labels_on_images: true`);

  return lines.join('\n');
}


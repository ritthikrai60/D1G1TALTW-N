import { PrismaClient } from '@prisma/client';
import fs from 'node:fs';
import path from 'node:path';

export const prisma = new PrismaClient();
export let isPostgresAvailable = false;

const DATA_DIR = path.resolve(process.cwd(), 'data');
const JSON_DB_PATH = path.join(DATA_DIR, 'digital_twin_db.json');

/**
 * Transforms a Prisma Device record into the standard JSON API format
 */
export function formatDeviceFromDb(record) {
  if (!record) return null;
  const isPlaced = Boolean(record.isPlaced);
  const position =
    isPlaced && record.posX !== null && record.posZ !== null
      ? {
          x: Number(record.posX || 0),
          y: Number(record.posY ?? 1.2),
          z: Number(record.posZ || 0),
        }
      : null;

  return {
    id: record.id,
    name: record.name,
    category: record.category,
    customType: record.customType || '',
    color: record.color || '#38bdf8',
    status: record.status || 'Online',
    value: record.value || '',
    ip: record.ip || '',
    subnet: record.subnet || '',
    mac: record.mac || '',
    vendor: record.vendor || 'Generic Network Device',
    hostname: record.hostname || '',
    osFirmware: record.osFirmware || '',
    serialNumber: record.serialNumber || '',
    assetTag: record.assetTag || '',
    connectedSwitch: record.connectedSwitch || '',
    switchPort: record.switchPort || '',
    vlan: record.vlan || 'VLAN 1',
    isPlaced,
    floorIdx: isPlaced && record.floorIdx !== null && record.floorIdx !== undefined ? Number(record.floorIdx) : null,
    floorLabel: record.floorLabel || '00_Ground_Floor',
    roomId: record.roomId || '',
    roomNumber: record.roomNumber || '',
    position,
    modelType: record.modelType || 'pin',
    rotationY: Number(record.rotationY || 0),
    parentRackId: record.parentRackId || '',
    uPosition: record.uPosition !== null && record.uPosition !== undefined ? Number(record.uPosition) : null,
    uHeight: record.uHeight !== null && record.uHeight !== undefined ? Number(record.uHeight) : 1,
    rackFace: record.rackFace || 'front',
    isFullDepth: record.isFullDepth !== undefined ? Boolean(record.isFullDepth) : true,
    rackConfig: record.rackConfig && typeof record.rackConfig === 'object' ? record.rackConfig : {},
    hierarchy: record.hierarchy && typeof record.hierarchy === 'object' ? record.hierarchy : {},
    networkInfo: record.networkInfo && typeof record.networkInfo === 'object' ? record.networkInfo : {},
    hardwareInfo: record.hardwareInfo && typeof record.hardwareInfo === 'object' ? record.hardwareInfo : {},
    spatialInfo: record.spatialInfo && typeof record.spatialInfo === 'object' ? record.spatialInfo : {},
    telemetry: record.telemetry && typeof record.telemetry === 'object' ? record.telemetry : {},
    openPorts: Array.isArray(record.openPorts) ? record.openPorts : [],
    snmpInfo: record.snmpInfo && typeof record.snmpInfo === 'object' ? record.snmpInfo : {},
    switchInterfaces: Array.isArray(record.switchInterfaces) ? record.switchInterfaces : [],
    credentials:
      record.credentials && typeof record.credentials === 'object'
        ? record.credentials
        : {
            username: 'admin',
            password: '',
            loginUrl: '',
            defaultPort: '',
            notes: '',
          },
    latencyMs: record.latencyMs !== null && record.latencyMs !== undefined ? Number(record.latencyMs) : null,
    latencyHistory: Array.isArray(record.latencyHistory) ? record.latencyHistory : [],
    lastSeen: record.lastSeen ? record.lastSeen.toISOString() : new Date().toISOString(),
    createdAt: record.createdAt ? record.createdAt.toISOString() : undefined,
    updatedAt: record.updatedAt ? record.updatedAt.toISOString() : new Date().toISOString(),
  };
}

/**
 * Transforms a Prisma Room record into the standard JSON API format
 */
export function formatRoomFromDb(record) {
  if (!record) return null;
  return {
    id: record.id,
    roomNumber: record.roomNumber,
    name: record.name,
    roomType: record.roomType || 'Office',
    floorIdx: Number(record.floorIdx ?? 0),
    floorLabel: record.floorLabel || '00_Ground_Floor',
    color: record.color || '#38bdf8',
    vlan: record.vlan || '',
    description: record.description || '',
    zoneSize: {
      width: Number(record.width || 12),
      depth: Number(record.depth || 10),
    },
    polygon: Array.isArray(record.polygon) ? record.polygon : [],
    position: {
      x: Number(record.posX || 0),
      y: Number(record.posY ?? 1.5),
      z: Number(record.posZ || 0),
    },
    createdAt: record.createdAt ? record.createdAt.toISOString() : undefined,
    updatedAt: record.updatedAt ? record.updatedAt.toISOString() : new Date().toISOString(),
  };
}

/**
 * Transforms a Prisma Network record into the standard JSON API format
 */
export function formatNetworkFromDb(record) {
  if (!record) return null;
  return {
    id: record.id,
    name: record.name,
    cidr: record.cidr,
    gateway: record.gateway || '',
    dnsServers: Array.isArray(record.dnsServers) ? record.dnsServers : [],
    dhcpServer: record.dhcpServer || '',
    interfaceName: record.interfaceName || 'Custom VLAN/Subnet',
    description: record.description || '',
    localIp: record.localIp || '',
    mac: record.mac || '',
    vlanId: record.vlanId || '',
    isAutoDetected: Boolean(record.isAutoDetected),
    isConnectedNow: Boolean(record.isConnectedNow),
    lastScannedAt: record.lastScannedAt ? record.lastScannedAt.toISOString() : null,
  };
}

/**
 * Auto-seeds PostgreSQL database from data/digital_twin_db.json if empty
 */
export async function autoSeedFromDiskJsonIfEmpty() {
  try {
    if (!fs.existsSync(JSON_DB_PATH)) {
      console.log('[PostgreSQL] No seed JSON found at', JSON_DB_PATH);
      return false;
    }

    const raw = fs.readFileSync(JSON_DB_PATH, 'utf-8');
    const parsed = JSON.parse(raw);

    const devCount = await prisma.device.count();
    const roomCount = await prisma.room.count();
    const netCount = await prisma.network.count();

    // 1. Seed Networks if empty
    if (netCount === 0 && Array.isArray(parsed.networks)) {
      for (const net of parsed.networks) {
        if (!net.cidr) continue;
        await prisma.network.upsert({
          where: { cidr: net.cidr },
          update: {},
          create: {
            id: net.id || `NET-${Math.random().toString(36).slice(2, 8).toUpperCase()}`,
            name: net.name || net.cidr,
            cidr: net.cidr,
            gateway: net.gateway || '',
            dnsServers: Array.isArray(net.dnsServers) ? net.dnsServers : [],
            dhcpServer: net.dhcpServer || '',
            interfaceName: net.interfaceName || 'Custom VLAN/Subnet',
            description: net.description || '',
            localIp: net.localIp || '',
            mac: net.mac || '',
            vlanId: net.vlanId !== undefined ? String(net.vlanId) : '',
            isAutoDetected: Boolean(net.isAutoDetected),
            isConnectedNow: Boolean(net.isConnectedNow),
            lastScannedAt: net.lastScannedAt ? new Date(net.lastScannedAt) : null,
          },
        });
      }
    }

    // 2. Seed Rooms if empty
    if (roomCount === 0 && Array.isArray(parsed.rooms)) {
      for (const r of parsed.rooms) {
        if (!r.id) continue;
        await prisma.room.upsert({
          where: { id: r.id },
          update: {},
          create: {
            id: r.id,
            roomNumber: String(r.roomNumber || 'UNASSIGNED'),
            name: String(r.name || 'Room'),
            roomType: r.roomType || 'Office',
            floorIdx: Number(r.floorIdx ?? 0),
            floorLabel: r.floorLabel || '00_Ground_Floor',
            color: r.color || '#38bdf8',
            vlan: r.vlan || '',
            description: r.description || '',
            width: Number(r.zoneSize?.width ?? 12),
            depth: Number(r.zoneSize?.depth ?? 10),
            posX: Number(r.position?.x ?? 0),
            posY: Number(r.position?.y ?? 1.5),
            posZ: Number(r.position?.z ?? 0),
            polygon: Array.isArray(r.polygon) ? r.polygon : [],
          },
        });
      }
    }

    // 3. Seed Devices if empty
    if (devCount === 0 && Array.isArray(parsed.devices)) {
      const validRoomIds = new Set((await prisma.room.findMany({ select: { id: true } })).map((rm) => rm.id));

      for (const d of parsed.devices) {
        if (!d.id) continue;
        const isPlaced = Boolean(d.isPlaced);
        const roomId = d.roomId && validRoomIds.has(d.roomId) ? d.roomId : null;

        await prisma.device.upsert({
          where: { id: d.id },
          update: {},
          create: {
            id: d.id,
            name: d.name || 'Device',
            category: d.category || 'Network',
            customType: d.customType || '',
            color: d.color || '#38bdf8',
            status: d.status || 'Online',
            value: d.value || '',
            ip: d.ip || '',
            subnet: d.subnet || '',
            mac: (d.mac || '').toUpperCase(),
            vendor: d.vendor || 'Generic Network Device',
            hostname: d.hostname || '',
            osFirmware: d.osFirmware || '',
            serialNumber: d.serialNumber || '',
            assetTag: d.assetTag || '',
            connectedSwitch: d.connectedSwitch || '',
            switchPort: d.switchPort || '',
            vlan: d.vlan || 'VLAN 1',
            isPlaced,
            floorIdx: isPlaced && d.floorIdx !== null && d.floorIdx !== undefined ? Number(d.floorIdx) : null,
            floorLabel: d.floorLabel || '00_Ground_Floor',
            roomId,
            roomNumber: d.roomNumber || '',
            posX: isPlaced && d.position ? Number(d.position.x || 0) : null,
            posY: isPlaced && d.position ? Number(d.position.y ?? 1.2) : null,
            posZ: isPlaced && d.position ? Number(d.position.z || 0) : null,
            modelType: d.modelType || 'pin',
            rotationY: Number(d.rotationY || 0),
            parentRackId: d.parentRackId || '',
            uPosition: d.uPosition !== null && d.uPosition !== undefined ? Number(d.uPosition) : null,
            uHeight: d.uHeight !== null && d.uHeight !== undefined ? Number(d.uHeight) : 1,
            rackFace: d.rackFace || 'front',
            isFullDepth: d.isFullDepth !== undefined ? Boolean(d.isFullDepth) : true,
            rackConfig: d.rackConfig && typeof d.rackConfig === 'object' ? d.rackConfig : {},
            hierarchy: d.hierarchy || {},
            networkInfo: d.networkInfo || {},
            hardwareInfo: d.hardwareInfo || {},
            spatialInfo: d.spatialInfo || {},
            telemetry: d.telemetry || {},
            openPorts: Array.isArray(d.openPorts) ? d.openPorts : [],
            snmpInfo: d.snmpInfo || {},
            switchInterfaces: d.switchInterfaces || [],
            credentials: d.credentials || {},
            latencyMs: d.latencyMs !== null && d.latencyMs !== undefined ? Number(d.latencyMs) : null,
            latencyHistory: d.latencyHistory || [],
            lastSeen: d.lastSeen ? new Date(d.lastSeen) : new Date(),
          },
        });
      }
    }

    // 4. Seed Settings if empty
    if (parsed.metadata?.defaultViewState) {
      await prisma.systemSetting.upsert({
        where: { key: 'defaultViewState' },
        update: { value: parsed.metadata.defaultViewState },
        create: { key: 'defaultViewState', value: parsed.metadata.defaultViewState },
      });
    }

    isPostgresAvailable = true;
    return true;
  } catch (err) {
    isPostgresAvailable = false;
    console.error('[PostgreSQL] Failed during autoSeedFromDiskJsonIfEmpty:', err.message);
    return false;
  }
}

/**
 * Load all entities from PostgreSQL into memory objects
 */
export async function dbLoadAll() {
  try {
    await autoSeedFromDiskJsonIfEmpty();

    const [dbNetworks, dbRooms, dbDevices, dbSettings, dbScanHistory] = await Promise.all([
      prisma.network.findMany({ orderBy: { createdAt: 'asc' } }),
      prisma.room.findMany({ orderBy: { floorIdx: 'asc' } }),
      prisma.device.findMany({ orderBy: { createdAt: 'asc' } }),
      prisma.systemSetting.findMany(),
      prisma.scanHistory.findMany({ take: 50, orderBy: { timestamp: 'desc' } }),
    ]);

    const settingsMap = new Map(dbSettings.map((s) => [s.key, s.value]));
    isPostgresAvailable = true;

    return {
      networks: dbNetworks.map(formatNetworkFromDb),
      rooms: dbRooms.map(formatRoomFromDb),
      devices: dbDevices.map(formatDeviceFromDb),
      defaultViewState: settingsMap.get('defaultViewState') || null,
      adminPassword: settingsMap.get('adminPassword') || null,
      scanHistory: dbScanHistory.map((s) => ({
        id: s.id,
        timestamp: s.timestamp.toISOString(),
        cidr: s.cidr || '',
        scanMode: s.scanMode,
        devicesFound: s.devicesFound,
        portsScanned: s.portsScanned,
        ...(s.summary || {}),
      })),
    };
  } catch (err) {
    isPostgresAvailable = false;
    console.error('[PostgreSQL] Failed in dbLoadAll, fallback will be used:', err.message);
    return null;
  }
}

/**
 * Persist device to PostgreSQL asynchronously
 */
export async function dbSaveDevice(dev) {
  if (!isPostgresAvailable) return null;
  try {
    if (!dev || !dev.id) return null;
    const isPlaced = Boolean(dev.isPlaced);

    // Validate roomId relation
    let roomId = isPlaced && dev.roomId ? String(dev.roomId) : null;
    if (roomId) {
      const exists = await prisma.room.findUnique({ where: { id: roomId }, select: { id: true } });
      if (!exists) roomId = null;
    }

    const data = {
      name: dev.name || 'Device',
      category: dev.category || 'Network',
      customType: dev.customType || '',
      color: dev.color || '#38bdf8',
      status: dev.status || 'Online',
      value: dev.value !== undefined ? String(dev.value) : '',
      ip: dev.ip !== undefined ? String(dev.ip) : '',
      subnet: dev.subnet !== undefined ? String(dev.subnet) : '',
      mac: (dev.mac !== undefined ? String(dev.mac) : '').toUpperCase(),
      vendor: dev.vendor || 'Generic Network Device',
      hostname: dev.hostname || '',
      osFirmware: dev.osFirmware || '',
      serialNumber: dev.serialNumber !== undefined ? String(dev.serialNumber) : '',
      assetTag: dev.assetTag !== undefined ? String(dev.assetTag) : '',
      connectedSwitch: dev.connectedSwitch !== undefined ? String(dev.connectedSwitch) : '',
      switchPort: dev.switchPort !== undefined ? String(dev.switchPort) : '',
      vlan: dev.vlan !== undefined ? String(dev.vlan) : 'VLAN 1',
      isPlaced,
      floorIdx: isPlaced && dev.floorIdx !== null && dev.floorIdx !== undefined ? Number(dev.floorIdx) : null,
      floorLabel: dev.floorLabel || '00_Ground_Floor',
      roomId,
      roomNumber: dev.roomNumber !== undefined ? String(dev.roomNumber) : '',
      posX: isPlaced && dev.position ? Number(dev.position.x || 0) : null,
      posY: isPlaced && dev.position ? Number(dev.position.y ?? 1.2) : null,
      posZ: isPlaced && dev.position ? Number(dev.position.z || 0) : null,
      modelType: dev.modelType || 'pin',
      rotationY: Number(dev.rotationY || 0),
      parentRackId: dev.parentRackId !== undefined ? String(dev.parentRackId || '') : '',
      uPosition: dev.uPosition !== null && dev.uPosition !== undefined ? Number(dev.uPosition) : null,
      uHeight: dev.uHeight !== null && dev.uHeight !== undefined ? Number(dev.uHeight) : 1,
      rackFace: dev.rackFace || 'front',
      isFullDepth: dev.isFullDepth !== undefined ? Boolean(dev.isFullDepth) : true,
      rackConfig: dev.rackConfig && typeof dev.rackConfig === 'object' ? dev.rackConfig : {},
      hierarchy: dev.hierarchy || {},
      networkInfo: dev.networkInfo || {},
      hardwareInfo: dev.hardwareInfo || {},
      spatialInfo: dev.spatialInfo || {},
      telemetry: dev.telemetry || {},
      openPorts: Array.isArray(dev.openPorts) ? dev.openPorts : [],
      snmpInfo: dev.snmpInfo || {},
      switchInterfaces: Array.isArray(dev.switchInterfaces) ? dev.switchInterfaces : [],
      credentials: dev.credentials || {},
      latencyMs: dev.latencyMs !== null && dev.latencyMs !== undefined ? Number(dev.latencyMs) : null,
      latencyHistory: Array.isArray(dev.latencyHistory) ? dev.latencyHistory : [],
      lastSeen: dev.lastSeen ? new Date(dev.lastSeen) : new Date(),
    };

    return await prisma.device.upsert({
      where: { id: dev.id },
      update: data,
      create: { id: dev.id, ...data },
    });
  } catch (err) {
    console.error(`[PostgreSQL] Error dbSaveDevice for ${dev?.id}:`, err.message);
    return null;
  }
}

/**
 * Delete device from PostgreSQL
 */
export async function dbDeleteDevice(id) {
  if (!isPostgresAvailable) return false;
  try {
    if (!id) return false;
    await prisma.device.delete({ where: { id } }).catch(() => {});
    return true;
  } catch (err) {
    console.error(`[PostgreSQL] Error dbDeleteDevice for ${id}:`, err.message);
    return false;
  }
}

/**
 * Persist room to PostgreSQL asynchronously
 */
export async function dbSaveRoom(room) {
  if (!isPostgresAvailable) return null;
  try {
    if (!room || !room.id) return null;
    const data = {
      roomNumber: String(room.roomNumber || 'UNASSIGNED'),
      name: String(room.name || 'Room'),
      roomType: room.roomType || 'Office',
      floorIdx: Number(room.floorIdx ?? 0),
      floorLabel: room.floorLabel || '00_Ground_Floor',
      color: room.color || '#38bdf8',
      vlan: room.vlan || '',
      description: room.description || '',
      width: Number(room.zoneSize?.width ?? room.width ?? 12),
      depth: Number(room.zoneSize?.depth ?? room.depth ?? 10),
      posX: Number(room.position?.x ?? 0),
      posY: Number(room.position?.y ?? 1.5),
      posZ: Number(room.position?.z ?? 0),
      polygon: Array.isArray(room.polygon) ? room.polygon : [],
    };

    return await prisma.room.upsert({
      where: { id: room.id },
      update: data,
      create: { id: room.id, ...data },
    });
  } catch (err) {
    console.error(`[PostgreSQL] Error dbSaveRoom for ${room?.id}:`, err.message);
    return null;
  }
}

/**
 * Delete room from PostgreSQL
 */
export async function dbDeleteRoom(id) {
  if (!isPostgresAvailable) return false;
  try {
    if (!id) return false;
    await prisma.room.delete({ where: { id } }).catch(() => {});
    return true;
  } catch (err) {
    console.error(`[PostgreSQL] Error dbDeleteRoom for ${id}:`, err.message);
    return false;
  }
}

/**
 * Persist network to PostgreSQL asynchronously
 */
export async function dbSaveNetwork(net) {
  if (!isPostgresAvailable) return null;
  try {
    if (!net || !net.cidr) return null;
    const cidr = String(net.cidr).trim();
    const data = {
      name: net.name || cidr,
      cidr,
      gateway: net.gateway || '',
      dnsServers: Array.isArray(net.dnsServers) ? net.dnsServers : [],
      dhcpServer: net.dhcpServer || '',
      interfaceName: net.interfaceName || 'Custom VLAN/Subnet',
      description: net.description || '',
      localIp: net.localIp || '',
      mac: net.mac || '',
      vlanId: net.vlanId !== undefined ? String(net.vlanId) : '',
      isAutoDetected: Boolean(net.isAutoDetected),
      isConnectedNow: Boolean(net.isConnectedNow),
      lastScannedAt: net.lastScannedAt ? new Date(net.lastScannedAt) : null,
    };

    return await prisma.network.upsert({
      where: { cidr },
      update: data,
      create: {
        id: net.id || `NET-${Math.random().toString(36).slice(2, 8).toUpperCase()}`,
        ...data,
      },
    });
  } catch (err) {
    console.error(`[PostgreSQL] Error dbSaveNetwork for ${net?.cidr}:`, err.message);
    return null;
  }
}

/**
 * Delete network from PostgreSQL
 */
export async function dbDeleteNetwork(id) {
  if (!isPostgresAvailable) return false;
  try {
    if (!id) return false;
    await prisma.network.delete({ where: { id } }).catch(() => {});
    return true;
  } catch (err) {
    console.error(`[PostgreSQL] Error dbDeleteNetwork for ${id}:`, err.message);
    return false;
  }
}

/**
 * Persist key/value setting to PostgreSQL
 */
export async function dbSaveSetting(key, value) {
  if (!isPostgresAvailable) return null;
  try {
    if (!key) return null;
    return await prisma.systemSetting.upsert({
      where: { key },
      update: { value },
      create: { key, value },
    });
  } catch (err) {
    console.error(`[PostgreSQL] Error dbSaveSetting for ${key}:`, err.message);
    return null;
  }
}

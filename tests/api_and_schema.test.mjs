import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import express from 'express';

import { lookupMacVendor, inferDeviceCategory, getHierarchyTierAndRole } from '../server/oui.js';
import { validateBundleSchema, getHierarchy } from '../server/store.js';
import { createApiRouterAndWs } from '../server/api.js';
import { prisma } from '../server/db.js';
import { MODEL_CATALOG, clampPointToRoomBounds } from '../src/data/twinData.js';

const DB_PATH = path.resolve(process.cwd(), 'data', 'digital_twin_db.json');
const FRS_PATH = path.resolve(process.cwd(), 'docs', 'FEATURES_REQUIREMENTS.md');
const SKILL_ROOT_PATH = path.resolve(process.cwd(), 'SKILL.md');
const SKILL_AGENT_PATH = path.resolve(process.cwd(), '.agents', 'skills', 'building-digital-twin', 'SKILL.md');
const APP_PATH = path.resolve(process.cwd(), 'src', 'App.jsx');
const VIEWPORT_PATH = path.resolve(process.cwd(), 'src', 'components', 'ThreeViewport.jsx');
const MODAL_PATH = path.resolve(process.cwd(), 'src', 'components', 'DeviceModal.jsx');
const ROOM_MODAL_PATH = path.resolve(process.cwd(), 'src', 'components', 'RoomModal.jsx');
const VIEWER_MENU_PATH = path.resolve(process.cwd(), 'src', 'components', 'ViewerMenu.jsx');
const ADMIN_TOOLBAR_PATH = path.resolve(process.cwd(), 'src', 'components', 'AdminToolbar.jsx');

test('1. Scanned JSON Database (data/digital_twin_db.json) conforms to Schema v2.0.0 & Unplaced Default Rules', () => {
  assert.ok(fs.existsSync(DB_PATH), 'data/digital_twin_db.json must exist');
  const raw = JSON.parse(fs.readFileSync(DB_PATH, 'utf-8'));

  assert.equal(raw.schemaVersion, '2.0.0');
  assert.ok(raw.metadata, 'metadata object must exist');
  assert.equal(raw.metadata.buildingModel, 'LUDUS_Building_No_Glass.igz');

  const check = validateBundleSchema(raw);
  assert.equal(check.valid, true, `Schema validation errors: ${check.errors.join(', ')}`);

  assert.ok(Array.isArray(raw.networks) && raw.networks.length >= 2, 'Must contain discovered networks');
  assert.ok(Array.isArray(raw.rooms), 'rooms must be an array');
  assert.ok(Array.isArray(raw.devices) && raw.devices.length >= 30, 'Must contain all discovered network devices');

  // Verify all scanned devices have explicit boolean isPlaced flag and unplaced queue exists
  assert.ok(
    raw.devices.every((d) => typeof d.isPlaced === 'boolean'),
    'All scanned devices must have explicit boolean isPlaced property'
  );
  assert.ok(
    raw.devices.filter((d) => !d.isPlaced).length >= 20,
    'Unplaced devices queue must contain unorganized scanned devices'
  );

  const devIdSet = new Set(raw.devices.map((d) => d.id));

  for (const dev of raw.devices) {
    assert.ok(dev.id, 'Device must have id');
    assert.ok(dev.name, 'Device must have name');
    assert.ok(dev.ip || dev.id.startsWith('RACKITEM-') || dev.modelType === 'server_rack', 'Device must have IP address');
    assert.ok(dev.hierarchy, `Device ${dev.id} must have hierarchy object`);
    assert.ok(dev.networkInfo, `Device ${dev.id} must have networkInfo object`);
    assert.ok(dev.hardwareInfo, `Device ${dev.id} must have hardwareInfo object`);
    assert.ok(dev.spatialInfo, `Device ${dev.id} must have spatialInfo object`);
    assert.ok(dev.telemetry, `Device ${dev.id} must have telemetry object`);
    assert.ok(Array.isArray(dev.openPorts), `Device ${dev.id} must have openPorts array`);

    const hPath = dev.hierarchy.path;
    assert.ok(Array.isArray(hPath) && hPath.length >= 2, `Device ${dev.id} must have valid hierarchy.path`);
    assert.equal(hPath[0], 'WAN-ROOT', 'Root of hierarchy path must be WAN-ROOT');
    assert.equal(hPath[hPath.length - 1], dev.id, 'Leaf of hierarchy path must be device id');
    assert.equal(new Set(hPath).size, hPath.length, 'Hierarchy path must not contain cycles');

    const pid = dev.hierarchy.parentDeviceId;
    assert.ok(pid === 'WAN-ROOT' || devIdSet.has(pid), `Parent ${pid} of ${dev.id} must exist`);
  }

  const h = getHierarchy();
  assert.ok(h.networkTopologyTree, 'networkTopologyTree must exist');
  assert.equal(h.networkTopologyTree.id, 'WAN-ROOT');
  assert.ok(h.discoveredTopologyTree.children.length >= 1, 'discoveredTopologyTree must hold full scanned hierarchy');

  assert.ok(h.spatialBuildingTree, 'spatialBuildingTree must exist');
  assert.equal(h.spatialBuildingTree.floors.length, 4, 'Spatial tree must have 4 building floors (G, 1F, 2F, RF)');
});

test('2. OUI MAC Vendor Lookup & Device Category / Hierarchy Classifier works accurately', () => {
  assert.equal(lookupMacVendor('C4:B2:5B:F3:C4:9C'), 'Huawei / Ruijie Enterprise Gateway');
  assert.equal(lookupMacVendor('E0:5D:54:F0:A5:EA'), 'Ruijie / Reyee Managed PoE Switch');
  assert.equal(lookupMacVendor('C8:CD:55:61:88:55'), 'Ruijie / Reyee Managed Wireless AP');
  assert.equal(lookupMacVendor('00:15:5D:82:0D:1F'), 'Microsoft Hyper-V Virtual Machine');

  const gwCat = inferDeviceCategory({
    ip: '192.168.110.50',
    mac: 'C4:B2:5B:F3:C4:9C',
    vendor: 'Huawei / Ruijie Enterprise Gateway',
    openPorts: [{ port: 80 }, { port: 443 }, { port: 1883 }],
    isGateway: true,
  });
  assert.equal(gwCat, 'Router');
  assert.deepEqual(getHierarchyTierAndRole(gwCat, true), { tier: 1, role: 'Core Gateway / Router' });

  const swCat = inferDeviceCategory({
    ip: '192.168.110.52',
    mac: 'E0:5D:54:F0:A5:EA',
    vendor: 'Ruijie / Reyee Managed PoE Switch',
    openPorts: [{ port: 80 }, { port: 443 }, { port: 6379 }],
  });
  assert.equal(swCat, 'Switch');
  assert.deepEqual(getHierarchyTierAndRole(swCat, false), { tier: 2, role: 'Distribution / PoE Switch' });

  const printerCat = inferDeviceCategory({
    ip: '192.168.110.141',
    mac: 'A4:D7:3C:8A:9A:7D',
    vendor: 'Smart Terminal',
    openPorts: [{ port: 80 }, { port: 515 }, { port: 631 }, { port: 9100 }],
  });
  assert.equal(printerCat, 'Printer');
});

test('3. REST API Enforces Strict Unplaced Filtering on Public Views & Supports Admin Place/Unplace Lifecycle', async () => {
  const app = express();
  const server = http.createServer(app);
  const { router, attachWebSocket } = createApiRouterAndWs();
  app.use('/api', router);
  attachWebSocket(server);

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const { port } = server.address();
  const baseUrl = `http://127.0.0.1:${port}`;

  try {
    // 3.1 GET /api/health
    const healthRes = await fetch(`${baseUrl}/api/health`);
    assert.equal(healthRes.status, 200);

    // 3.2 GET /api/public/state must NOT expose any unplaced devices
    const pubRes1 = await fetch(`${baseUrl}/api/public/state`);
    assert.equal(pubRes1.status, 200);
    const pubState1 = await pubRes1.json();
    const initialPlacedCount = pubState1.devices.length;
    assert.ok(
      pubState1.devices.every((d) => d.isPlaced === true),
      'Public state must hide all unplaced devices'
    );

    // 3.3 Admin Login
    const loginRes = await fetch(`${baseUrl}/api/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: process.env.ADMIN_PASSWORD || 'admin123' }),
    });
    assert.equal(loginRes.status, 200);
    const { token } = await loginRes.json();

    // 3.4 Admin State sees all discovered unplaced devices in the queue
    const admRes = await fetch(`${baseUrl}/api/admin/state`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    assert.equal(admRes.status, 200);
    const admState = await admRes.json();
    assert.ok(admState.devices.length >= 30, 'Admin state must include all discovered devices in queue');

    // 3.5 Admin places an unplaced device -> it immediately becomes visible in /api/public/state
    const targetDev = admState.devices.find((d) => !d.isPlaced) || admState.devices[0];
    const placeRes = await fetch(`${baseUrl}/api/admin/devices`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        ...targetDev,
        isPlaced: true,
        floorIdx: 0,
        roomNumber: 'G-101',
        position: { x: -10, y: 1.5, z: -5 },
      }),
    });
    assert.equal(placeRes.status, 200);

    const pubRes2 = await fetch(`${baseUrl}/api/public/state`);
    const pubState2 = await pubRes2.json();
    assert.equal(pubState2.devices.length, initialPlacedCount + 1, 'Placed device must now appear in public state');
    assert.ok(pubState2.devices.some((d) => d.id === targetDev.id));

    // 3.6 Admin unplaces the device -> it disappears from /api/public/state again
    const unplaceRes = await fetch(`${baseUrl}/api/admin/devices/${targetDev.id}/unplace`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    assert.equal(unplaceRes.status, 200);

    const pubRes3 = await fetch(`${baseUrl}/api/public/state`);
    const pubState3 = await pubRes3.json();
    assert.equal(pubState3.devices.length, initialPlacedCount, 'Unplaced device must be hidden from public state again');
    assert.ok(!pubState3.devices.some((d) => d.id === targetDev.id));
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('4. Features Requirement Specification (FRS v2.0.0) Regression Guard prevents missing UI layers & features', () => {
  assert.ok(fs.existsSync(FRS_PATH), 'docs/FEATURES_REQUIREMENTS.md must exist');
  assert.ok(fs.existsSync(SKILL_ROOT_PATH), 'SKILL.md must exist at workspace root');
  assert.ok(fs.existsSync(SKILL_AGENT_PATH), '.agents/skills/building-digital-twin/SKILL.md must exist for auto-discovery');

  const skillCode = fs.readFileSync(SKILL_ROOT_PATH, 'utf-8');
  assert.ok(skillCode.includes('FEATURES_REQUIREMENTS.md'), 'SKILL.md must reference docs/FEATURES_REQUIREMENTS.md');
  assert.ok(skillCode.includes('showGlass'), 'SKILL.md must document the 8 mandatory display layers');

  // App shell + extracted Viewer menu are checked together (source-grep guards follow code across modules)
  const appCode = fs.readFileSync(APP_PATH, 'utf-8') + '\n' + fs.readFileSync(VIEWER_MENU_PATH, 'utf-8');
  const viewportCode = fs.readFileSync(VIEWPORT_PATH, 'utf-8');
  const modalCode = fs.readFileSync(MODAL_PATH, 'utf-8');

  // Verify all 8 mandatory 3D Display Layer Switches exist in App.jsx and ThreeViewport.jsx
  const requiredLayerKeys = [
    'exploded',
    'showGlass',
    'showWalls',
    'showRoof',
    'showBasketball',
    'showArrows',
    'showPlans',
    'showRooms',
  ];

  for (const key of requiredLayerKeys) {
    assert.ok(
      appCode.includes(key),
      `App.jsx must include layer switch for "${key}" in Section 2 (Display Layers)`
    );
    assert.ok(
      viewportCode.includes(key),
      `ThreeViewport.jsx must support layer visibility for "${key}"`
    );
  }

  // Verify Category Filter toggles & Status/Subnet filters exist in App.jsx
  assert.ok(appCode.includes('toggleCategoryFilter'), 'App.jsx must include interactive Category Filter chips');
  assert.ok(appCode.includes('filterSubnet'), 'App.jsx must include Subnet CIDR filter');
  assert.ok(appCode.includes('filterStatus'), 'App.jsx must include Device Status filter');

  // Verify DeviceModal includes HTTP :80, HTTPS :443, Reverse Proxy, Switch Matrix, and Port Scanner
  assert.ok(modalCode.includes('HTTP :80'), 'DeviceModal.jsx must include HTTP :80 quick access button');
  assert.ok(modalCode.includes('HTTPS :443'), 'DeviceModal.jsx must include HTTPS :443 quick access button');
  assert.ok(modalCode.includes('/api/proxy'), 'DeviceModal.jsx must include Reverse Proxy preview');
  assert.ok(modalCode.includes('scan-ports'), 'DeviceModal.jsx must include Fast & Full Port Scanner');
  assert.ok(modalCode.includes('switchInterfaces'), 'DeviceModal.jsx must include Switch/Router Port Matrix');

  // Verify RoomModal & 3D Room Zone / Auto-Snap / Polygon Vertex Drawer / Undo-Redo features exist
  assert.ok(fs.existsSync(ROOM_MODAL_PATH), 'src/components/RoomModal.jsx must exist');
  const roomModalCode = fs.readFileSync(ROOM_MODAL_PATH, 'utf-8');
  assert.ok(roomModalCode.includes('Smart Room Cascade'), 'RoomModal.jsx must support Smart Room Cascade renumbering');
  assert.ok(viewportCode.includes('roomZoneMeshesMap'), 'ThreeViewport.jsx must render 3D Floor Zone Highlight pads');
  assert.ok(viewportCode.includes('TransformControls'), 'ThreeViewport.jsx must include Three.js TransformControls CAD Gizmo');
  assert.ok(viewportCode.includes('drawRoomZoneMode'), 'ThreeViewport.jsx must support 3D zone drawing');
  assert.ok(viewportCode.includes('polyDraftVertices'), 'ThreeViewport.jsx must support point-by-point Polygon vertex drawing');
  assert.ok(viewportCode.includes('isPolygonVertexHandle'), 'ThreeViewport.jsx must support per-vertex Polygon handle dragging');
  assert.ok(appCode.includes('placingRoom'), 'App.jsx must support interactive 3D Room Placement mode');
  assert.ok(appCode.includes('handleUndo'), 'App.jsx must support transactional Undo (Ctrl+Z)');
  assert.ok(appCode.includes('handleRedo'), 'App.jsx must support transactional Redo (Ctrl+Y)');
  assert.ok(appCode.includes('handleDeleteRoomZone'), 'App.jsx must support Room Zone deletion (Delete/Backspace)');
  assert.ok(fs.existsSync(ADMIN_TOOLBAR_PATH), 'src/components/AdminToolbar.jsx must exist');
  assert.ok(appCode.includes('AdminToolbar'), 'App.jsx must render AdminToolbar on /admin');
});

test('5. Spatial Room Numbering, 3D Zone Highlight, Auto-Snap & Smart Room Cascade Lifecycle', async () => {
  const app = express();
  const server = http.createServer(app);
  const { router } = createApiRouterAndWs(server);
  app.use('/api', router);

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;
  const baseUrl = `http://127.0.0.1:${port}`;

  try {
    // 5.1 Admin Login
    const loginRes = await fetch(`${baseUrl}/api/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: process.env.ADMIN_PASSWORD || 'admin123' }),
    });
    const { token } = await loginRes.json();
    assert.ok(token);

    // 5.2 Create an Angled / Custom Polygon Room on Floor 1
    const createRoomRes = await fetch(`${baseUrl}/api/admin/rooms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        roomNumber: '199-TEST',
        name: 'Test Polygon NOC Zone',
        roomType: 'NOC',
        floorIdx: 1,
        polygon: [
          { x: 4, z: -14 },
          { x: 18, z: -12 },
          { x: 16, z: -2 },
          { x: 4, z: -2 },
        ],
        position: { x: 10, y: 5.6, z: -8 },
      }),
    });
    assert.equal(createRoomRes.status, 200);
    const { room: createdRoom } = await createRoomRes.json();
    assert.equal(createdRoom.roomNumber, '199-TEST');
    assert.equal(createdRoom.polygon.length, 4, 'Room must persist custom 4-vertex polygon');

    // 5.3 Place a device inside the room's 3D Zone (11, 5.2, -7) with autoSnapRoom: true
    const adminRes = await fetch(`${baseUrl}/api/admin/state`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const adminData = await adminRes.json();
    const targetDev = adminData.devices[0];

    const placeRes = await fetch(`${baseUrl}/api/admin/devices/${targetDev.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        ...targetDev,
        isPlaced: true,
        floorIdx: 1,
        roomId: '',
        roomNumber: '',
        autoSnapRoom: true,
        position: { x: 11, y: 5.2, z: -7 },
      }),
    });
    assert.equal(placeRes.status, 200);
    const { device: snappedDev } = await placeRes.json();
    assert.equal(snappedDev.roomNumber, '199-TEST', 'Device placed inside 3D Room Zone must auto-snap roomNumber');
    assert.equal(snappedDev.roomId, createdRoom.id, 'Device placed inside 3D Room Zone must auto-snap roomId');

    // 5.4 Rename/Renumber the Room (199-TEST -> 188-RENAMED) and verify Smart Cascade updates the device
    const renameRes = await fetch(`${baseUrl}/api/admin/rooms/${createdRoom.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        roomNumber: '188-RENAMED',
        name: 'Renamed NOC Zone',
        roomType: 'NOC',
        floorIdx: 1,
        zoneSize: { width: 16, depth: 12 },
        position: { x: 10, y: 5.6, z: -8 },
      }),
    });
    assert.equal(renameRes.status, 200);

    const pubRes = await fetch(`${baseUrl}/api/public/state`);
    const pubState = await pubRes.json();
    const updatedDevInPub = pubState.devices.find((d) => d.id === targetDev.id);
    assert.ok(updatedDevInPub, 'Placed device must be in public state');
    assert.equal(
      updatedDevInPub.roomNumber,
      '188-RENAMED',
      'Smart Room Cascade must update roomNumber on devices inside the room when renamed'
    );

    // 5.5 Clean up: unplace test device & delete test room
    await fetch(`${baseUrl}/api/admin/devices/${targetDev.id}/unplace`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    await fetch(`${baseUrl}/api/admin/rooms/${createdRoom.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('6. 3D Model Catalog Registry, Room Boundary Clamping & Server Rack Placement with Rotation Lifecycle', async () => {
  // 6.1 Verify MODEL_CATALOG registry
  assert.ok(Array.isArray(MODEL_CATALOG), 'MODEL_CATALOG must be an array');
  const pinMeta = MODEL_CATALOG.find((m) => m.id === 'pin');
  const rackMeta = MODEL_CATALOG.find((m) => m.id === 'server_rack');
  assert.ok(pinMeta, 'Pin model must exist in MODEL_CATALOG');
  assert.ok(rackMeta, 'Server rack model must exist in MODEL_CATALOG');
  assert.equal(rackMeta.type, 'glb');
  assert.equal(rackMeta.path, '/models/server_rack.glb');

  // 6.2 Verify physical GLB exists on disk and has valid glTF magic header
  const rackDiskPath = path.resolve(process.cwd(), 'public', 'models', 'server_rack.glb');
  assert.ok(fs.existsSync(rackDiskPath), 'public/models/server_rack.glb must exist on disk');
  const fd = fs.openSync(rackDiskPath, 'r');
  const magicBuf = Buffer.alloc(4);
  fs.readSync(fd, magicBuf, 0, 4, 0);
  fs.closeSync(fd);
  assert.equal(magicBuf.toString('ascii'), 'glTF', 'File must have valid binary glTF header');

  // 6.3 Verify clampPointToRoomBounds for Rectangle Room
  const rectRoom = {
    position: { x: 10, y: 0, z: 20 },
    zoneSize: { width: 10, depth: 8 },
  };
  // Inside room -> stays inside
  const insidePt = clampPointToRoomBounds(rectRoom, 11, 21, 0.5);
  assert.equal(insidePt.x, 11);
  assert.equal(insidePt.z, 21);

  // Far outside room (x = 50, z = 100) -> strictly clamped to room perimeter
  const outsidePt = clampPointToRoomBounds(rectRoom, 50, 100, 0.5);
  assert.ok(outsidePt.x <= 10 + 4.5, 'X coordinate must be clamped within room width');
  assert.ok(outsidePt.x >= 10 - 4.5, 'X coordinate must be clamped within room width');
  assert.ok(outsidePt.z <= 20 + 3.5, 'Z coordinate must be clamped within room depth');
  assert.ok(outsidePt.z >= 20 - 3.5, 'Z coordinate must be clamped within room depth');

  // 6.4 Verify clampPointToRoomBounds for Polygon Room
  const polyRoom = {
    polygon: [
      { x: 0, z: 0 },
      { x: 10, z: 0 },
      { x: 10, z: 10 },
      { x: 0, z: 10 },
    ],
  };
  const clampedPolyPt = clampPointToRoomBounds(polyRoom, -20, 50, 0.5);
  assert.ok(clampedPolyPt.x >= 0.5 && clampedPolyPt.x <= 9.5, 'Polygon X clamped');
  assert.ok(clampedPolyPt.z >= 0.5 && clampedPolyPt.z <= 9.5, 'Polygon Z clamped');

  // 6.5 End-to-end API Test: Place Server Rack with modelType and rotationY
  const app = express();
  const server = http.createServer(app);
  const { router } = createApiRouterAndWs(server);
  app.use('/api', router);

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;
  const baseUrl = `http://127.0.0.1:${port}`;

  try {
    const loginRes = await fetch(`${baseUrl}/api/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: process.env.ADMIN_PASSWORD || 'admin123' }),
    });
    const { token } = await loginRes.json();
    assert.ok(token);

    const adminStateRes = await fetch(`${baseUrl}/api/admin/state`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const { devices } = await adminStateRes.json();
    const targetDev = devices.find((d) => d.category === 'Server') || devices[0];

    // Place device with modelType: 'server_rack' and rotationY: 90
    const placeRes = await fetch(`${baseUrl}/api/admin/devices`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        ...targetDev,
        isPlaced: true,
        floorIdx: 1,
        roomNumber: '101-NOC',
        modelType: 'server_rack',
        rotationY: 90,
        position: { x: 5.5, y: 0.05, z: -4.2 },
      }),
    });
    assert.equal(placeRes.status, 200);
    const { device: placedDev } = await placeRes.json();
    assert.equal(placedDev.modelType, 'server_rack', 'modelType must persist as server_rack');
    assert.equal(placedDev.rotationY, 90, 'rotationY must persist as 90');

    // Verify public state exposes placed server rack with modelType & rotationY
    const pubRes = await fetch(`${baseUrl}/api/public/state`);
    const pubState = await pubRes.json();
    const devInPub = pubState.devices.find((d) => d.id === targetDev.id);
    assert.ok(devInPub, 'Server rack must appear in public state');
    assert.equal(devInPub.modelType, 'server_rack');
    assert.equal(devInPub.rotationY, 90);

    // Clean up
    await fetch(`${baseUrl}/api/admin/devices/${targetDev.id}/unplace`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('7. Active Device & Server Rack Move, Rotate, Unplace & Permanent Delete Lifecycle', async () => {
  const app = express();
  const server = http.createServer(app);
  const { router } = createApiRouterAndWs(server);
  app.use('/api', router);

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;
  const baseUrl = `http://127.0.0.1:${port}`;

  try {
    // 7.1 Login as Admin
    const loginRes = await fetch(`${baseUrl}/api/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: process.env.ADMIN_PASSWORD || 'admin123' }),
    });
    const { token } = await loginRes.json();
    assert.ok(token);

    // 7.2 Create a test Server Rack device
    const createRes = await fetch(`${baseUrl}/api/admin/devices`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        name: 'Test MDF Server Rack Unit',
        category: 'Server',
        modelType: 'server_rack',
        rotationY: 0,
        floorIdx: 1,
        roomNumber: '101-NOC',
        isPlaced: true,
        position: { x: 10, y: 0.05, z: 15 },
      }),
    });
    assert.equal(createRes.status, 200);
    const { device: rack } = await createRes.json();
    assert.equal(rack.modelType, 'server_rack');
    assert.equal(rack.rotationY, 0);

    // 7.3 Test MOVE: Update position within room
    const moveRes = await fetch(`${baseUrl}/api/admin/devices/${encodeURIComponent(rack.id)}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        ...rack,
        position: { x: 12.5, y: 0.05, z: 16.2 },
      }),
    });
    assert.equal(moveRes.status, 200);
    const { device: movedRack } = await moveRes.json();
    assert.equal(movedRack.position.x, 12.5);
    assert.equal(movedRack.position.z, 16.2);

    // 7.4 Test ROTATE: Update rotation angle to 180°
    const rotateRes = await fetch(`${baseUrl}/api/admin/devices/${encodeURIComponent(rack.id)}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        ...movedRack,
        rotationY: 180,
      }),
    });
    assert.equal(rotateRes.status, 200);
    const { device: rotatedRack } = await rotateRes.json();
    assert.equal(rotatedRack.rotationY, 180, 'Server rack must rotate to 180°');

    // Verify public view reflects the moved & rotated rack
    const pubRes1 = await fetch(`${baseUrl}/api/public/state`);
    const pubState1 = await pubRes1.json();
    const pubRack1 = pubState1.devices.find((d) => d.id === rack.id);
    assert.ok(pubRack1, 'Placed rack must appear on public state');
    assert.equal(pubRack1.position.x, 12.5);
    assert.equal(pubRack1.rotationY, 180);

    // 7.5 Test UNPLACE: Remove rack from room back to unplaced queue (safe delete)
    const unplaceRes = await fetch(`${baseUrl}/api/admin/devices/${encodeURIComponent(rack.id)}/unplace`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    assert.equal(unplaceRes.status, 200);

    // Verify unplaced rack disappeared from public state
    const pubRes2 = await fetch(`${baseUrl}/api/public/state`);
    const pubState2 = await pubRes2.json();
    assert.equal(
      pubState2.devices.some((d) => d.id === rack.id),
      false,
      'Unplaced rack must be hidden from public view'
    );

    // 7.6 Test PERMANENT DELETE: Remove device entirely
    const delRes = await fetch(`${baseUrl}/api/admin/devices/${encodeURIComponent(rack.id)}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    assert.equal(delRes.status, 200);

    // Verify admin queue no longer contains the deleted device
    const adminRes = await fetch(`${baseUrl}/api/admin/state`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const adminState = await adminRes.json();
    assert.equal(
      adminState.devices.some((d) => d.id === rack.id),
      false,
      'Deleted device must be completely removed from admin database'
    );
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('8. Device Badge/Label Layer Toggle, Global Admin Default View Persistence & Public Synchronization', async () => {
  // 8.1 Verify ThreeViewport source contains showDeviceLabels and showDevices in DEFAULT_VIEW_STATE and syncVisibility
  const viewportSrc = fs.readFileSync(VIEWPORT_PATH, 'utf-8');
  assert.ok(
    viewportSrc.includes('showDeviceLabels: true'),
    'DEFAULT_VIEW_STATE must define showDeviceLabels: true'
  );
  assert.ok(
    viewportSrc.includes('showDevices: true'),
    'DEFAULT_VIEW_STATE must define showDevices: true'
  );
  assert.ok(
    viewportSrc.includes('showLabels'),
    'ThreeViewport syncVisibility must decouple 3D mesh visibility from HTML text badges using showLabels'
  );

  // 8.2 Verify App.jsx contains layer-device-labels and layer-devices switch and default view controls
  const appSrc = fs.readFileSync(APP_PATH, 'utf-8') + '\n' + fs.readFileSync(VIEWER_MENU_PATH, 'utf-8');
  assert.ok(
    appSrc.includes('layer-device-labels'),
    'App.jsx must contain Switch id="layer-device-labels" for device badge layer'
  );
  assert.ok(
    appSrc.includes('layer-devices'),
    'App.jsx must contain Switch id="layer-devices" for 3D device layer'
  );
  assert.ok(
    appSrc.includes('handleSaveAsAdminDefaultView'),
    'App.jsx must implement handleSaveAsAdminDefaultView'
  );
  assert.ok(
    appSrc.includes('handleResetToAdminDefaultView'),
    'App.jsx must implement handleResetToAdminDefaultView'
  );

  // 8.3 Verify AdminToolbar.jsx contains buttons for device label toggle and save default view
  const adminToolbarSrc = fs.readFileSync(ADMIN_TOOLBAR_PATH, 'utf-8');
  assert.ok(
    adminToolbarSrc.includes('showDeviceLabels'),
    'AdminToolbar must contain toggle button for showDeviceLabels'
  );
  assert.ok(
    adminToolbarSrc.includes('onSaveAsDefaultView'),
    'AdminToolbar must support onSaveAsDefaultView callback'
  );

  // 8.4 REST API Lifecycle for PUT /api/admin/settings/default-view
  const app = express();
  const server = http.createServer(app);
  const { router, attachWebSocket } = createApiRouterAndWs();
  app.use('/api', router);
  attachWebSocket(server);

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const { port } = server.address();
  const baseUrl = `http://127.0.0.1:${port}`;

  try {
    // Unauthorized attempt must be rejected (401)
    const unauthRes = await fetch(`${baseUrl}/api/admin/settings/default-view`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ showDeviceLabels: false }),
    });
    assert.equal(unauthRes.status, 401, 'Unauthorized request must be rejected');

    // Admin login
    const loginRes = await fetch(`${baseUrl}/api/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: process.env.ADMIN_PASSWORD || 'admin123' }),
    });
    assert.equal(loginRes.status, 200);
    const { token } = await loginRes.json();
    assert.ok(token);

    // Save default view state: turn OFF device labels & glass
    const saveRes = await fetch(`${baseUrl}/api/admin/settings/default-view`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        showDeviceLabels: false,
        showGlass: false,
        showRooms: true,
      }),
    });
    assert.equal(saveRes.status, 200);
    const saveData = await saveRes.json();
    assert.equal(saveData.ok, true);
    assert.equal(saveData.defaultViewState.showDeviceLabels, false);
    assert.equal(saveData.defaultViewState.showGlass, false);

    // Verify GET /api/public/state exposes metadata.defaultViewState to public users
    const pubRes = await fetch(`${baseUrl}/api/public/state`);
    assert.equal(pubRes.status, 200);
    const pubState = await pubRes.json();
    assert.ok(pubState.metadata, 'Public state must contain metadata');
    assert.ok(pubState.metadata.defaultViewState, 'Public state metadata must include defaultViewState');
    assert.equal(pubState.metadata.defaultViewState.showDeviceLabels, false);
    assert.equal(pubState.metadata.defaultViewState.showGlass, false);

    // Reset default view state back to device labels ON
    const resetRes = await fetch(`${baseUrl}/api/admin/settings/default-view`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        showDeviceLabels: true,
        showGlass: true,
      }),
    });
    assert.equal(resetRes.status, 200);
    const resetData = await resetRes.json();
    assert.equal(resetData.defaultViewState.showDeviceLabels, true);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('9. PostgreSQL 16 & Prisma ORM Persistence: Hybrid Relational + JSONB, Auto-Seed, and Live Sync Lifecycle', async () => {
  const app = express();
  app.use(express.json());
  const { router } = createApiRouterAndWs();
  app.use('/api', router);

  const server = http.createServer(app);
  await new Promise((resolve) => server.listen(0, resolve));
  const port = server.address().port;
  const baseUrl = `http://localhost:${port}`;

  try {
    // 1. Verify /api/health reports PostgreSQL 16 database status via Prisma
    const healthRes = await fetch(`${baseUrl}/api/health`);
    assert.equal(healthRes.status, 200);
    const healthData = await healthRes.json();
    assert.equal(healthData.ok, true);
    assert.ok(healthData.database, 'Health check must report database info');
    assert.equal(healthData.database.type, 'PostgreSQL 16 (Prisma)');

    const isPgConnected = healthData.database.status === 'connected';
    if (!isPgConnected) {
      assert.equal(healthData.database.status, 'disconnected');
      return;
    }

    // 2. Direct Prisma queries: verify records exist in PostgreSQL
    const dbDevCount = await prisma.device.count();
    const dbRoomCount = await prisma.room.count();
    const dbNetCount = await prisma.network.count();
    assert.ok(dbDevCount >= 30, `PostgreSQL must contain all seeded devices (found ${dbDevCount})`);
    assert.ok(dbRoomCount >= 1, `PostgreSQL must contain seeded rooms (found ${dbRoomCount})`);
    assert.ok(dbNetCount >= 2, `PostgreSQL must contain seeded networks (found ${dbNetCount})`);

    // 3. Obtain Admin Bearer Token
    const loginRes = await fetch(`${baseUrl}/api/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: process.env.ADMIN_PASSWORD || 'admin' }),
    });
    const { token } = await loginRes.json();
    assert.ok(token, 'Must obtain valid token');

    // 4. Test live creation of a new device and verify persistence in PostgreSQL
    const testDevId = `TEST-PG-DEV-${Date.now()}`;
    const createRes = await fetch(`${baseUrl}/api/admin/devices`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        id: testDevId,
        name: 'PostgreSQL Test Server Unit',
        category: 'Server',
        ip: '192.168.110.222',
        isPlaced: true,
        floorIdx: 1,
        modelType: 'server_rack',
        rotationY: 1.57,
        position: { x: 5.5, y: 5.2, z: -3.2 },
        openPorts: [{ port: 80, service: 'HTTP' }, { port: 5432, service: 'PostgreSQL' }],
        hierarchy: { tier: 3, role: 'Database Server' },
      }),
    });
    assert.equal(createRes.status, 200);

    // Wait slightly for async Prisma write
    await new Promise((r) => setTimeout(r, 200));

    // Direct query PostgreSQL via Prisma to verify spatial and JSONB fields
    const pgDev = await prisma.device.findUnique({ where: { id: testDevId } });
    assert.ok(pgDev, 'Device must exist in PostgreSQL devices table');
    assert.equal(pgDev.name, 'PostgreSQL Test Server Unit');
    assert.equal(pgDev.modelType, 'server_rack');
    assert.equal(Number(pgDev.posX), 5.5);
    assert.equal(Number(pgDev.posY), 5.2);
    assert.equal(Number(pgDev.posZ), -3.2);
    assert.equal(Number(pgDev.rotationY), 1.57);
    assert.ok(Array.isArray(pgDev.openPorts), 'openPorts must be stored as JSONB array');
    assert.equal(pgDev.openPorts.length, 2);

    // 5. Test Room upsert and verify persistence in PostgreSQL
    const testRoomId = `TEST-PG-ROOM-${Date.now()}`;
    const roomRes = await fetch(`${baseUrl}/api/admin/rooms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        id: testRoomId,
        roomNumber: '401-LAB',
        name: 'Database Cluster Lab',
        roomType: 'NOC',
        floorIdx: 2,
        zoneSize: { width: 15, depth: 12 },
        position: { x: 0, y: 9.6, z: 0 },
      }),
    });
    assert.equal(roomRes.status, 200);

    await new Promise((r) => setTimeout(r, 200));

    const pgRoom = await prisma.room.findUnique({ where: { id: testRoomId } });
    assert.ok(pgRoom, 'Room must exist in PostgreSQL rooms table');
    assert.equal(pgRoom.roomNumber, '401-LAB');
    assert.equal(Number(pgRoom.width), 15);
    assert.equal(Number(pgRoom.depth), 12);

    // 6. Test delete cleanup in PostgreSQL
    const delDevRes = await fetch(`${baseUrl}/api/admin/devices/${testDevId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    assert.equal(delDevRes.status, 200);

    const delRoomRes = await fetch(`${baseUrl}/api/admin/rooms/${testRoomId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    assert.equal(delRoomRes.status, 200);

    await new Promise((r) => setTimeout(r, 200));

    const deletedDev = await prisma.device.findUnique({ where: { id: testDevId } });
    assert.equal(deletedDev, null, 'Deleted device must no longer exist in PostgreSQL');

    const deletedRoom = await prisma.room.findUnique({ where: { id: testRoomId } });
    assert.equal(deletedRoom, null, 'Deleted room must no longer exist in PostgreSQL');
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

// ============================================================================
// TEST 10: Rackula 19-Inch Rack Elevation Engine, Collision Detection & PostgreSQL Persistence
// ============================================================================
test('Test 10: Rackula 19-Inch Rack Elevation Engine, Collision Detection, Blocked Slots & PostgreSQL Persistence', async () => {
  const {
    RACKULA_STARTER_LIBRARY,
    canMountInRack,
    computeBlockedSlots,
    serializeToRackulaYaml,
  } = await import('../src/data/rackulaData.js');

  assert.ok(RACKULA_STARTER_LIBRARY.length >= 20, 'Starter library must have at least 20 templates');

  const app = express();
  const server = http.createServer(app);
  const { router } = createApiRouterAndWs(server);
  app.use('/api', router);

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;
  const baseUrl = `http://127.0.0.1:${port}`;

  const rackId = `TEST-RACK-${Date.now()}`;

  try {
    const loginRes = await fetch(`${baseUrl}/api/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: process.env.ADMIN_PASSWORD || 'admin123' }),
    });
    const { token } = await loginRes.json();
    assert.ok(token, 'Must obtain admin token');

    // 1. Create a 42U 3D Server Rack in NOC Room
    const createRackRes = await fetch(`${baseUrl}/api/admin/devices`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        id: rackId,
        name: 'NOC Core Cabinet RACK-01',
        category: 'Server',
        modelType: 'server_rack',
        isPlaced: true,
        floorIdx: 1,
        roomNumber: '101',
        position: { x: 4.0, y: 4.05, z: -2.0 },
        rackConfig: { rackHeight: 42, rackWidth: 19 },
      }),
    });
    assert.equal(createRackRes.status, 200);

    // 2. Mount a 2U Full-Depth Hypervisor Server at U40 (occupies U40-U41 Front & Rear)
    const mountServerRes = await fetch(`${baseUrl}/api/admin/racks/${rackId}/mount`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        templateSlug: '2u-server',
        name: 'Proxmox VE Node 01',
        ip: '192.168.110.210',
        uPosition: 40,
        face: 'front',
      }),
    });
    assert.equal(mountServerRes.status, 200);
    const mountServerData = await mountServerRes.json();
    assert.equal(mountServerData.ok, true);
    assert.equal(mountServerData.device.uPosition, 40);
    assert.equal(mountServerData.device.uHeight, 2);
    assert.equal(mountServerData.device.isFullDepth, true);
    assert.equal(mountServerData.device.parentRackId, rackId);

    // 3. Verify U-Slot Collision Detection:
    // Attempting to mount another device at U41 on Front OR Rear must be rejected because Proxmox Node (U40-U41) is Full-Depth!
    const collisionFrontRes = await fetch(`${baseUrl}/api/admin/racks/${rackId}/mount`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        templateSlug: '24p-switch',
        uPosition: 41,
        face: 'front',
      }),
    });
    assert.equal(collisionFrontRes.status, 400, 'Mounting at overlapping Front U41 must fail');

    const collisionRearRes = await fetch(`${baseUrl}/api/admin/racks/${rackId}/mount`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        templateSlug: '1u-pdu',
        uPosition: 40,
        face: 'rear',
      }),
    });
    assert.equal(collisionRearRes.status, 400, 'Mounting at Rear U40 behind a Full-Depth device must fail');

    // 4. Mount a Half-Depth 24-Port Switch at U42 Front AND a Half-Depth PDU at U42 Rear -> Both succeed!
    const mountSwRes = await fetch(`${baseUrl}/api/admin/racks/${rackId}/mount`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        templateSlug: '24p-switch',
        name: 'Cisco Catalyst 9300-24P',
        ip: '192.168.110.211',
        uPosition: 42,
        face: 'front',
        isFullDepth: false,
      }),
    });
    assert.equal(mountSwRes.status, 200);

    const mountPduRes = await fetch(`${baseUrl}/api/admin/racks/${rackId}/mount`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        templateSlug: '1u-pdu',
        name: 'APC Rack PDU U42-Rear',
        uPosition: 42,
        face: 'rear',
        isFullDepth: false,
      }),
    });
    assert.equal(mountPduRes.status, 200, 'Half-depth Rear U42 must succeed opposite half-depth Front U42');
    const pduData = await mountPduRes.json();

    // 5. Verify Blocked Slots & Rackula YAML v1.0.0 Serialization
    const rackStateRes = await fetch(`${baseUrl}/api/racks/${rackId}`);
    assert.equal(rackStateRes.status, 200);
    const { rack, mountedItems } = await rackStateRes.json();
    assert.equal(mountedItems.length, 3);

    const rearBlocked = computeBlockedSlots(mountedItems, 'rear');
    assert.equal(rearBlocked.length, 1, 'Rear face must have 1 blocked slot range from U40-U41 Full-Depth Server');
    assert.equal(rearBlocked[0].bottom, 40);
    assert.equal(rearBlocked[0].top, 41);

    const yamlOutput = serializeToRackulaYaml(rack, mountedItems);
    assert.ok(yamlOutput.includes('version: "1.0.0"'), 'YAML must include Rackula v1.0.0 version');
    assert.ok(yamlOutput.includes('Proxmox VE Node 01'), 'YAML must include mounted server');
    assert.ok(yamlOutput.includes('Cisco Catalyst 9300-24P'), 'YAML must include mounted switch');

    // 6. Verify PostgreSQL Persistence of parentRackId, uPosition, uHeight, rackFace
    let isPgConnected = false;
    try {
      await prisma.$queryRaw`SELECT 1`;
      isPgConnected = true;
    } catch {}

    if (isPgConnected) {
      await new Promise((r) => setTimeout(r, 200));
      const pgMountedServer = await prisma.device.findUnique({
        where: { id: mountServerData.device.id },
      });
      assert.ok(pgMountedServer, 'Mounted server must be persisted in PostgreSQL');
      assert.equal(pgMountedServer.parentRackId, rackId);
      assert.equal(pgMountedServer.uPosition, 40);
      assert.equal(pgMountedServer.uHeight, 2);
      assert.equal(pgMountedServer.rackFace, 'front');
    }

    // 6b. Test Drag-and-Drop Reordering within rack (Move Proxmox VE Node 01 from U40 to U10)
    const moveRes = await fetch(`${baseUrl}/api/admin/racks/${rackId}/mount`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        deviceId: mountServerData.device.id,
        uPosition: 10,
        face: 'front',
        uHeight: 2,
        isFullDepth: true,
      }),
    });
    assert.equal(moveRes.status, 200, 'Reordering mounted device within rack must succeed');
    const moveData = await moveRes.json();
    assert.equal(moveData.device.uPosition, 10, 'Device should now be moved to U10');

    // 7. Test Unmount & Cleanup
    for (const item of mountedItems) {
      await fetch(`${baseUrl}/api/admin/devices/${item.id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
    }
    await fetch(`${baseUrl}/api/admin/devices/${rackId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('11. Rackula Upstream REST Persistence API, YAML Schema v1.0.0 & Sub-App Integration', async () => {
  const testApp = express();
  const { router } = createApiRouterAndWs();
  testApp.use('/api', router);
  const server = http.createServer(testApp);
  await new Promise((resolve) => server.listen(0, resolve));
  const port = server.address().port;
  const baseUrl = `http://127.0.0.1:${port}`;

  try {
    // 1. Verify healthcheck matches Rackula isPersistenceHealthPayload schema
    const healthRes = await fetch(`${baseUrl}/api/health`);
    assert.equal(healthRes.status, 200, 'GET /api/health must respond with 200 OK');
    const healthJson = await healthRes.json();
    assert.equal(healthJson.ok, true, 'health.ok must be true');
    assert.equal(healthJson.status, 'ok', 'health.status must be "ok" for Rackula persistence health');
    assert.equal(healthJson.service, 'rackula-persistence-api', 'health.service must be "rackula-persistence-api"');
    assert.equal(typeof healthJson.version, 'number', 'health.version must be number');

    // 2. Verify layouts list endpoint
    const listRes = await fetch(`${baseUrl}/api/layouts`);
    assert.equal(listRes.status, 200, 'GET /api/layouts must respond with 200 OK');
    const listData = await listRes.json();
    assert.ok(Array.isArray(listData.layouts), 'layouts must be an array');

    // 3. Verify single rack layout retrieval if racks exist
    if (listData.layouts.length > 0) {
      const rackId = listData.layouts[0].id;
      const layoutRes = await fetch(`${baseUrl}/api/layouts/${encodeURIComponent(rackId)}`);
      assert.equal(layoutRes.status, 200, 'GET /api/layouts/:id must respond with 200 OK');
      assert.ok(
        (layoutRes.headers.get('content-type') || '').includes('text/yaml'),
        'Must return text/yaml Content-Type'
      );
      const yamlText = await layoutRes.text();
      assert.ok(yamlText.includes('version: 1.0.0') || yamlText.includes("version: '1.0.0'"), 'YAML must declare version 1.0.0');
      assert.ok(yamlText.includes('racks:'), 'YAML must declare racks array');
      assert.ok(yamlText.includes('settings:'), 'YAML must include settings section required by Rackula schema');
      assert.ok(yamlText.includes('display_mode:'), 'YAML settings must declare display_mode');

      // 4A. Verify Unauthorized PUT /api/layouts/:id (without admin token) is rejected with 401
      const unauthPut = await fetch(`${baseUrl}/api/layouts/${encodeURIComponent(rackId)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'text/yaml' },
        body: yamlText,
      });
      assert.equal(unauthPut.status, 401, 'PUT /api/layouts/:id without admin token must return 401 Unauthorized');

      // 4B. Verify Authorized PUT /api/layouts/:id with Admin Bearer token succeeds and synchronizes rack name
      const loginRes = await fetch(`${baseUrl}/api/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: 'admin123' }),
      });
      const loginData = await loginRes.json();
      const adminToken = loginData.token;

      // Update rack name in YAML to verify two-way synchronization
      const updatedYaml = yamlText.replace(
        /(name:\s*)(.+)/,
        `$1Updated-Rack-Name-${rackId}`
      );

      const authPut = await fetch(`${baseUrl}/api/layouts/${encodeURIComponent(rackId)}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'text/yaml',
          Authorization: `Bearer ${adminToken}`,
        },
        body: updatedYaml,
      });
      assert.equal(authPut.status, 200, 'PUT /api/layouts/:id with valid admin token must succeed');
      const putData = await authPut.json();
      assert.equal(putData.ok, true, 'PUT response must return ok: true');

      // 4D. Verify DELETE /api/layouts/:id removes the rack layout from Rackula
      const delLayoutRes = await fetch(`${baseUrl}/api/layouts/${encodeURIComponent(rackId)}`, {
        method: 'DELETE',
      });
      assert.equal(delLayoutRes.status, 200, 'DELETE /api/layouts/:id must respond with 200 OK');
      const delLayoutData = await delLayoutRes.json();
      assert.equal(delLayoutData.ok, true, 'DELETE /api/layouts/:id response must return ok: true');

      const afterDelRes = await fetch(`${baseUrl}/api/layouts/${encodeURIComponent(rackId)}`);
      assert.equal(afterDelRes.status, 404, 'GET /api/layouts/:id after deletion must respond with 404 Not Found');
      // 4C. Verify assets compatibility endpoint
      const assetsRes = await fetch(`${baseUrl}/api/assets/${encodeURIComponent(rackId)}`);
      assert.equal(assetsRes.status, 200, 'GET /api/assets/:id must return 200 OK');
      const assetsData = await assetsRes.json();
      assert.ok(Array.isArray(assetsData.assets), 'assetsData.assets must be an array');
    }

    // 5. Verify Rackula Sub-App assets build directory
    const distIndex = path.resolve(process.cwd(), 'rackula', 'dist', 'index.html');
    assert.ok(fs.existsSync(distIndex), 'rackula/dist/index.html must exist for sub-app serving');
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('12. Empty Rack Placement: named rack has no fake IP, library parts are hidden from public state until an IP is bound', async () => {
  const app = express();
  const server = http.createServer(app);
  const { router, attachWebSocket } = createApiRouterAndWs();
  app.use('/api', router);
  attachWebSocket(server);
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const { port } = server.address();
  const baseUrl = `http://127.0.0.1:${port}`;
  let rackId = '';
  let partId = '';
  let headers = {};

  try {
    const loginRes = await fetch(`${baseUrl}/api/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: process.env.ADMIN_PASSWORD || 'admin123' }),
    });
    const { token } = await loginRes.json();
    headers = { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` };

    // 12.1 Create an EMPTY named rack (no ip) and place it
    const rackRes = await fetch(`${baseUrl}/api/admin/devices`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        name: 'Test-Empty-Rack',
        category: 'Server',
        modelType: 'server_rack',
        vendor: 'Server Rack Cabinet',
        isPlaced: true,
        floorIdx: 0,
        position: { x: 0, y: 0.05, z: 0 },
      }),
    });
    assert.ok(rackRes.status < 300, 'creating an empty rack must succeed');
    const rackData = await rackRes.json();
    const rack = rackData.device || rackData;
    rackId = rack.id;
    assert.equal(rack.name, 'Test-Empty-Rack');
    assert.equal(rack.ip, '', 'empty rack must not carry a fake IP');

    // 12.2 Mount a Rackula library part (no IP) into the rack
    const mountRes = await fetch(`${baseUrl}/api/admin/racks/${rackId}/mount`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ templateSlug: '24-port-switch', name: 'Test-Part', category: 'Switch' }),
    });
    const mountData = await mountRes.json();
    assert.ok(mountRes.ok, 'mount of library part must succeed: ' + (mountData.error || ''));
    {
      partId = mountData.device.id;
      assert.equal(mountData.device.ip, '', 'library part has no IP');

      // 12.3 Public state hides the IP-less part but still exposes the rack itself
      const pub = await (await fetch(`${baseUrl}/api/public/state`)).json();
      assert.ok(pub.devices.some((d) => d.id === rackId), 'placed rack stays visible');
      assert.ok(!pub.devices.some((d) => d.id === partId), 'IP-less rack part must be hidden from public state');

      // 12.4 Rack detail still lists the part
      const detail = await (await fetch(`${baseUrl}/api/racks/${rackId}`)).json();
      assert.ok(detail.mountedItems.some((d) => d.id === partId), 'rack detail must list mounted library part');

      // 12.5 Binding a real IP makes it countable in public state
      await fetch(`${baseUrl}/api/admin/devices/${encodeURIComponent(partId)}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify({ ip: '10.254.254.77' }),
      });
      const pub2 = await (await fetch(`${baseUrl}/api/public/state`)).json();
      assert.ok(pub2.devices.some((d) => d.id === partId), 'part with bound IP must appear in public state');
    }

    // 12.6 UI guard: quick rack placement asks for a name and never hijacks a scanned device
    const appSrc = fs.readFileSync(APP_PATH, 'utf-8');
    assert.ok(appSrc.includes('RackNameDialog'), 'App.jsx must ask for rack name via RackNameDialog');
    assert.ok(!appSrc.includes("unplacedDevices.find((d) => d.category === 'Server')"), 'rack placement must not reuse scanned Server devices');
  } finally {
    for (const id of [partId, rackId].filter(Boolean)) {
      await fetch(`${baseUrl}/api/admin/devices/${encodeURIComponent(id)}`, { method: 'DELETE', headers }).catch(() => {});
    }
    await new Promise((resolve) => server.close(resolve));
    try {
      await prisma.$disconnect();
    } catch {}
  }
});
import * as React from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { TransformControls } from 'three/examples/jsm/controls/TransformControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import {
  FLOORS,
  OVERLAY_BOUNDS,
  DEVICE_CATEGORIES,
  ROOM_TYPES,
  computePolygonArea,
  computePolygonCentroid,
  clampPointToRoomBounds,
} from '../data/twinData.js';

const DEFAULT_CAM_POS = new THREE.Vector3(62, 54, 78);
const DEFAULT_CAM_TARGET = new THREE.Vector3(4, 6, -2);

export const DEFAULT_VIEW_STATE = {
  selectedFloor: 'all',
  exploded: false,
  showPlans: true,
  showRooms: true,
  showDevices: true,
  showDeviceLabels: true,
  showGlass: true,
  showRoof: true,
  showBasketball: true,
  showArrows: true,
  showWalls: true,
  filterSubnet: 'all',
  filterStatus: 'all',
  enabledCategories: DEVICE_CATEGORIES.map((c) => c.id),
};

function getCategoryMeta(catId) {
  return (
    DEVICE_CATEGORIES.find((c) => c.id === catId) || {
      id: catId || 'Network',
      label: catId || 'Network',
      color: '#38bdf8',
      icon: '🔌',
    }
  );
}

function getRoomTypeMeta(roomType) {
  return (
    ROOM_TYPES.find((r) => r.id === roomType) || {
      id: roomType || 'Office',
      label: roomType || 'Office',
      color: '#38bdf8',
      icon: '🏢',
    }
  );
}

function snapValue(val, enabled = true, step = 0.5) {
  if (!enabled) return Number(val.toFixed(2));
  return Number((Math.round(val / step) * step).toFixed(2));
}

function safeDisposeGroup(grp) {
  if (!grp) return;
  grp.traverse((child) => {
    if (child.userData?.isSharedModelInstance) return;
    if (child.isMesh || child.isLineSegments) {
      if (child.geometry && !child.userData?.isSharedGeometry) {
        child.geometry.dispose();
      }
      if (child.material && !child.userData?.isSharedMaterial) {
        if (Array.isArray(child.material)) {
          child.material.forEach((m) => m?.dispose?.());
        } else {
          child.material?.dispose?.();
        }
      }
    }
  });
  if (grp.parent) {
    grp.parent.remove(grp);
  }
}

export const ThreeViewport = React.forwardRef(function ThreeViewport(
  {
    theme = 'dark',
    viewState = DEFAULT_VIEW_STATE,
    rooms = [],
    placedDevices = [],
    placementMode = false,
    drawRoomZoneMode = false,
    drawShapeType = 'polygon',
    drawFloorIdx = 0,
    snapToGrid = true,
    magneticWallSnap = true,
    activeRoomId = null,
    roomTransformMode = null,
    onSurfacePick,
    onRoomZoneDrawn,
    onPolygonDraftChange,
    onRoomTransformCommit,
    onSelectDevice,
    activeAdminDeviceId = null,
    deviceTransformMode = 'translate',
    onDeviceTransformCommit,
    onSelectRoom,
    onAdminSelectRoom,
    onModelLoaded,
  },
  ref
) {
  const mountRef = React.useRef(null);
  const labelsRef = React.useRef(null);
  const [modelsLoaded, setModelsLoaded] = React.useState(false);
  const engineRef = React.useRef(null);

  const mergedViewState = React.useMemo(
    () => ({ ...DEFAULT_VIEW_STATE, ...(viewState || {}) }),
    [viewState]
  );

  const viewStateRef = React.useRef(mergedViewState);
  viewStateRef.current = mergedViewState;

  const placementModeRef = React.useRef(placementMode);
  placementModeRef.current = placementMode;

  const drawRoomZoneModeRef = React.useRef(drawRoomZoneMode);
  drawRoomZoneModeRef.current = drawRoomZoneMode;

  const drawShapeTypeRef = React.useRef(drawShapeType);
  drawShapeTypeRef.current = drawShapeType;

  const drawFloorIdxRef = React.useRef(drawFloorIdx);
  drawFloorIdxRef.current = drawFloorIdx;

  const snapToGridRef = React.useRef(snapToGrid);
  snapToGridRef.current = snapToGrid;

  const magneticWallSnapRef = React.useRef(magneticWallSnap);
  magneticWallSnapRef.current = magneticWallSnap;

  const activeRoomIdRef = React.useRef(activeRoomId);
  activeRoomIdRef.current = activeRoomId;

  const roomTransformModeRef = React.useRef(roomTransformMode);
  roomTransformModeRef.current = roomTransformMode;

  const onSurfacePickRef = React.useRef(onSurfacePick);
  onSurfacePickRef.current = onSurfacePick;

  const onRoomZoneDrawnRef = React.useRef(onRoomZoneDrawn);
  onRoomZoneDrawnRef.current = onRoomZoneDrawn;

  const onPolygonDraftChangeRef = React.useRef(onPolygonDraftChange);
  onPolygonDraftChangeRef.current = onPolygonDraftChange;

  const onRoomTransformCommitRef = React.useRef(onRoomTransformCommit);
  onRoomTransformCommitRef.current = onRoomTransformCommit;

  const onSelectDeviceRef = React.useRef(onSelectDevice);
  onSelectDeviceRef.current = onSelectDevice;

  const activeAdminDeviceIdRef = React.useRef(activeAdminDeviceId);
  activeAdminDeviceIdRef.current = activeAdminDeviceId;

  const deviceTransformModeRef = React.useRef(deviceTransformMode);
  deviceTransformModeRef.current = deviceTransformMode;

  const onDeviceTransformCommitRef = React.useRef(onDeviceTransformCommit);
  onDeviceTransformCommitRef.current = onDeviceTransformCommit;

  const placedDevicesRef = React.useRef(placedDevices);
  placedDevicesRef.current = placedDevices;

  const roomsRef = React.useRef(rooms);
  roomsRef.current = rooms;

  const onSelectRoomRef = React.useRef(onSelectRoom);
  onSelectRoomRef.current = onSelectRoom;

  const onAdminSelectRoomRef = React.useRef(onAdminSelectRoom);
  onAdminSelectRoomRef.current = onAdminSelectRoom;

  const onModelLoadedRef = React.useRef(onModelLoaded);
  onModelLoadedRef.current = onModelLoaded;

  // Expose flyTo, flyToTopDown, resetCamera, and Polygon Drawing Actions to parent
  React.useImperativeHandle(ref, () => ({
    flyTo(pos, floorIdx = 0) {
      const eng = engineRef.current;
      if (!eng || !pos) return;
      const fg = eng.floorGroups[floorIdx];
      const offsetY = fg ? fg.position.y : 0;
      const target = new THREE.Vector3(
        Number(pos.x || 0),
        Number(pos.y || 1.5) + offsetY,
        Number(pos.z || 0)
      );
      const endCamPos = target.clone().add(new THREE.Vector3(14, 12, 16));
      eng.cameraAnim = {
        startPos: eng.camera.position.clone(),
        endPos: endCamPos,
        startTarget: eng.controls.target.clone(),
        endTarget: target,
        progress: 0,
      };
    },
    flyToTopDown(floorIdx = 0) {
      const eng = engineRef.current;
      if (!eng) return;
      const flMeta = FLOORS.find((f) => f.index === Number(floorIdx)) || FLOORS[0];
      const fg = eng.floorGroups[flMeta.index];
      const offsetY = fg ? fg.position.y : 0;
      const centerTarget = new THREE.Vector3(4, flMeta.elevation + offsetY, -2);
      const topCamPos = new THREE.Vector3(4, flMeta.elevation + offsetY + 92, -1.95);
      eng.cameraAnim = {
        startPos: eng.camera.position.clone(),
        endPos: topCamPos,
        startTarget: eng.controls.target.clone(),
        endTarget: centerTarget,
        progress: 0,
      };
    },
    resetCamera() {
      const eng = engineRef.current;
      if (!eng) return;
      eng.cameraAnim = {
        startPos: eng.camera.position.clone(),
        endPos: DEFAULT_CAM_POS.clone(),
        startTarget: eng.controls.target.clone(),
        endTarget: DEFAULT_CAM_TARGET.clone(),
        progress: 0,
      };
    },
    finishPolygonDraft() {
      if (engineRef.current?.finishPolygonDraft) {
        return engineRef.current.finishPolygonDraft();
      }
      return false;
    },
    undoLastPolygonVertex() {
      if (engineRef.current?.undoLastPolygonVertex) {
        return engineRef.current.undoLastPolygonVertex();
      }
      return false;
    },
    cancelPolygonDraft() {
      if (engineRef.current?.cancelPolygonDraft) {
        engineRef.current.cancelPolygonDraft();
      }
    },
  }));

  // Initialize Three.js Scene once
  React.useEffect(() => {
    const container = mountRef.current;
    const labelsContainer = labelsRef.current;
    if (!container || !labelsContainer) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x060b14);
    scene.fog = new THREE.FogExp2(0x060b14, 0.0022);

    const camera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.5,
      1000
    );
    camera.position.copy(DEFAULT_CAM_POS);

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: 'high-performance',
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.12;
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.maxPolarAngle = Math.PI / 2 - 0.01;
    controls.minDistance = 4;
    controls.maxDistance = 260;
    controls.target.copy(DEFAULT_CAM_TARGET);

    scene.add(new THREE.AmbientLight(0xdbeafe, 0.85));
    scene.add(new THREE.HemisphereLight(0xe0f2fe, 0x1e293b, 0.65));

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.45);
    dirLight.position.set(65, 110, 55);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 10;
    dirLight.shadow.camera.far = 260;
    const d = 80;
    dirLight.shadow.camera.left = -d;
    dirLight.shadow.camera.right = d;
    dirLight.shadow.camera.top = d;
    dirLight.shadow.camera.bottom = -d;
    dirLight.shadow.bias = -0.0005;
    scene.add(dirLight);

    const gridHelper = new THREE.GridHelper(220, 110, 0x1e3a8a, 0x0f172a);
    gridHelper.position.y = -0.08;
    scene.add(gridHelper);

    const floorGroups = {};
    const planOverlayMeshes = {};
    const categoryMeshes = {
      Glass: [],
      Roof: [],
      Basketball: [],
      Arrow: [],
      Stair: [],
      Wall: [],
      Slab: [],
      Column: [],
      Parapet: [],
    };
    const pickableMeshes = [];

    const textureLoader = new THREE.TextureLoader();
    const overlayCenterX = (OVERLAY_BOUNDS.minX + OVERLAY_BOUNDS.maxX) / 2;
    const overlayCenterZ = -(OVERLAY_BOUNDS.minY + OVERLAY_BOUNDS.maxY) / 2;

    FLOORS.forEach((f) => {
      const fg = new THREE.Group();
      fg.name = `FloorGroup_${f.index}`;
      scene.add(fg);
      floorGroups[f.index] = fg;

      textureLoader.load(
        f.planImage,
        (tex) => {
          tex.colorSpace = THREE.SRGBColorSpace;
          const geo = new THREE.PlaneGeometry(OVERLAY_BOUNDS.width, OVERLAY_BOUNDS.depth);
          geo.rotateX(-Math.PI / 2);
          const mat = new THREE.MeshBasicMaterial({
            map: tex,
            transparent: true,
            opacity: 0.85,
            depthWrite: false,
            side: THREE.DoubleSide,
          });
          const mesh = new THREE.Mesh(geo, mat);
          mesh.position.set(overlayCenterX, f.elevation + 0.04, overlayCenterZ);
          mesh.visible = false;
          fg.add(mesh);
          planOverlayMeshes[f.index] = mesh;
          syncVisibility(eng, viewStateRef.current);
        },
        undefined,
        () => {}
      );
    });

    // 3D CAD TransformControls (Gizmo for Moving / Resizing Room Zones in XZ Plane)
    const transformControls = new TransformControls(camera, renderer.domElement);
    transformControls.showY = false;
    const tcHelper = transformControls.getHelper
      ? transformControls.getHelper()
      : transformControls;
    scene.add(tcHelper);

    // Live 3D Rectangle Marquee Preview Group (for Click & Drag Room Zone Drawing)
    const drawPreviewGroup = new THREE.Group();
    drawPreviewGroup.visible = false;
    const previewPadGeo = new THREE.PlaneGeometry(1, 1);
    previewPadGeo.rotateX(-Math.PI / 2);
    const previewPadMat = new THREE.MeshBasicMaterial({
      color: 0x10b981,
      transparent: true,
      opacity: 0.28,
      depthWrite: false,
      side: THREE.DoubleSide,
    });
    const previewPadMesh = new THREE.Mesh(previewPadGeo, previewPadMat);
    drawPreviewGroup.add(previewPadMesh);

    const previewBoxGeo = new THREE.BoxGeometry(1, 0.35, 1);
    const previewEdgesGeo = new THREE.EdgesGeometry(previewBoxGeo);
    const previewEdgesMat = new THREE.LineBasicMaterial({
      color: 0x34d399,
      transparent: true,
      opacity: 0.98,
    });
    const previewBorderLines = new THREE.LineSegments(previewEdgesGeo, previewEdgesMat);
    previewBorderLines.position.y = 0.18;
    drawPreviewGroup.add(previewBorderLines);
    scene.add(drawPreviewGroup);

    // Live 3D Polygon Point-by-Point Preview Group
    const polygonPreviewGroup = new THREE.Group();
    polygonPreviewGroup.visible = false;
    scene.add(polygonPreviewGroup);

    // Magnetic Snap Indicator Ring (Glowing Cyan Ring when snapping to Wall/Column corner)
    const snapRingGeo = new THREE.RingGeometry(0.28, 0.45, 24);
    snapRingGeo.rotateX(-Math.PI / 2);
    const snapRingMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.95,
      side: THREE.DoubleSide,
      depthWrite: false,
    });
    const snapIndicatorMesh = new THREE.Mesh(snapRingGeo, snapRingMat);
    snapIndicatorMesh.visible = false;
    scene.add(snapIndicatorMesh);

    // Selected Room Per-Vertex Editable Handles Group
    const vertexHandlesGroup = new THREE.Group();
    scene.add(vertexHandlesGroup);

    const eng = {
      scene,
      camera,
      renderer,
      controls,
      transformControls,
      tcHelper,
      drawPreviewGroup,
      polygonPreviewGroup,
      snapIndicatorMesh,
      vertexHandlesGroup,
      drawMeasureEl: null,
      gridHelper,
      floorGroups,
      planOverlayMeshes,
      categoryMeshes,
      pickableMeshes,
      floorSnapPoints: { 0: [], 1: [], 2: [], 3: [] },
      deviceMeshesMap: new Map(),
      deviceDomMap: new Map(),
      roomDomMap: new Map(),
      roomZoneMeshesMap: new Map(),
      cachedRackModel: null,
      cameraAnim: null,
      modelLoaded: false,
      finishPolygonDraft: null,
      undoLastPolygonVertex: null,
      cancelPolygonDraft: null,
    };
    engineRef.current = eng;

    transformControls.addEventListener('dragging-changed', (event) => {
      controls.enabled = !event.value;
      if (!event.value && transformControls.object) {
        const obj = transformControls.object;

        // Case 1: Dragging an individual Polygon Vertex Handle
        if (obj.userData?.isPolygonVertexHandle) {
          const roomId = obj.userData.roomId;
          const vIdx = obj.userData.vertexIdx;
          const rmInfo = roomId ? eng.roomDomMap.get(roomId) : null;
          if (roomId && rmInfo && onRoomTransformCommitRef.current) {
            const basePoly =
              Array.isArray(rmInfo.room.polygon) && rmInfo.room.polygon.length >= 3
                ? rmInfo.room.polygon
                : [];
            if (basePoly.length >= 3) {
              const newPoly = basePoly.map((pt, idx) =>
                idx === vIdx
                  ? {
                      x: snapValue(obj.position.x, snapToGridRef.current, 0.5),
                      z: snapValue(obj.position.z, snapToGridRef.current, 0.5),
                    }
                  : { x: Number(pt.x), z: Number(pt.z) }
              );
              const centroid = computePolygonCentroid(newPoly);
              const xs = newPoly.map((p) => p.x);
              const zs = newPoly.map((p) => p.z);
              const w = Math.max(2, Number((Math.max(...xs) - Math.min(...xs)).toFixed(2)));
              const d = Math.max(2, Number((Math.max(...zs) - Math.min(...zs)).toFixed(2)));
              const flMeta = FLOORS.find((f) => f.index === Number(rmInfo.floorIdx)) || FLOORS[0];
              onRoomTransformCommitRef.current({
                roomId,
                polygon: newPoly,
                position: {
                  x: centroid.x,
                  y: Number((flMeta.elevation + 1.6).toFixed(2)),
                  z: centroid.z,
                },
                zoneSize: { width: w, depth: d },
              });
            }
          }
          return;
        }

        // Case 2: Dragging / Scaling / Rotating the entire Room Zone Group
        const roomId = obj.userData?.roomId;
        const rmInfo = roomId ? eng.roomDomMap.get(roomId) : null;
        if (roomId && rmInfo && onRoomTransformCommitRef.current) {
          const flMeta = FLOORS.find((f) => f.index === Number(rmInfo.floorIdx)) || FLOORS[0];
          const baseX = Number(rmInfo.room.position?.x || 0);
          const baseZ = Number(rmInfo.room.position?.z || 0);
          const finalX = snapValue(obj.position.x, snapToGridRef.current, 0.5);
          const finalZ = snapValue(obj.position.z, snapToGridRef.current, 0.5);
          const dx = finalX - baseX;
          const dz = finalZ - baseZ;
          const sx = obj.scale.x || 1;
          const sz = obj.scale.z || 1;
          const rotY = obj.rotation.y || 0;
          const cosA = Math.cos(rotY);
          const sinA = Math.sin(rotY);

          let updatedPolygon = undefined;
          if (Array.isArray(rmInfo.room.polygon) && rmInfo.room.polygon.length >= 3) {
            updatedPolygon = rmInfo.room.polygon.map((pt) => {
              const relX = (Number(pt.x) - baseX) * sx;
              const relZ = (Number(pt.z) - baseZ) * sz;
              const rx = relX * cosA + relZ * sinA;
              const rz = -relX * sinA + relZ * cosA;
              return {
                x: Number((finalX + rx).toFixed(2)),
                z: Number((finalZ + rz).toFixed(2)),
              };
            });
          }

          const baseW = Number(rmInfo.room.zoneSize?.width ?? 12);
          const baseD = Number(rmInfo.room.zoneSize?.depth ?? 10);
          const rawW = Math.max(2, baseW * Math.abs(sx));
          const rawD = Math.max(2, baseD * Math.abs(sz));
          const finalW = snapValue(rawW, snapToGridRef.current, 0.5);
          const finalD = snapValue(rawD, snapToGridRef.current, 0.5);
          obj.scale.set(1, 1, 1);
          obj.rotation.set(0, 0, 0);
          onRoomTransformCommitRef.current({
            roomId,
            polygon: updatedPolygon,
            position: {
              x: finalX,
              y: Number((flMeta.elevation + 1.6).toFixed(2)),
              z: finalZ,
            },
            zoneSize: {
              width: Math.max(2, finalW),
              depth: Math.max(2, finalD),
            },
          });
          return;
        }

        // Case 3: Dragging / Rotating an existing placed Device or Server Rack
        if (obj.userData?.isDevicePin && obj.userData?.deviceId) {
          const devId = obj.userData.deviceId;
          const targetDev = (placedDevicesRef.current || []).find((d) => d.id === devId);
          if (targetDev && onDeviceTransformCommitRef.current) {
            const room = (roomsRef.current || []).find(
              (r) => r.id === targetDev.roomId || r.roomNumber === targetDev.roomNumber
            );
            const clamped = clampPointToRoomBounds(room, obj.position.x, obj.position.z, 0.4);
            obj.position.x = clamped.x;
            obj.position.z = clamped.z;

            let rotYDeg = Number(targetDev.rotationY ?? 0);
            if (obj.rotation.y !== 0) {
              rotYDeg = Math.round((obj.rotation.y * 180) / Math.PI) % 360;
              if (rotYDeg < 0) rotYDeg += 360;
            }

            onDeviceTransformCommitRef.current({
              deviceId: devId,
              position: {
                x: clamped.x,
                y: obj.position.y,
                z: clamped.z,
              },
              rotationY: rotYDeg,
            });
          }
          return;
        }
      }
    });

    // Realtime Room Boundary Clamping while dragging Device/Rack
    transformControls.addEventListener('change', () => {
      if (transformControls.object && transformControls.object.userData?.isDevicePin) {
        const obj = transformControls.object;
        const devId = obj.userData.deviceId;
        const targetDev = (placedDevicesRef.current || []).find((d) => d.id === devId);
        if (targetDev) {
          const room = (roomsRef.current || []).find(
            (r) => r.id === targetDev.roomId || r.roomNumber === targetDev.roomNumber
          );
          if (room) {
            const clamped = clampPointToRoomBounds(room, obj.position.x, obj.position.z, 0.4);
            obj.position.x = clamped.x;
            obj.position.z = clamped.z;
          }
        }
      }
    });

    const gltfLoader = new GLTFLoader();
    gltfLoader.load(
      '/models/building.glb',
      (gltf) => {
        const root = gltf.scene;
        const children = [...root.children];
        let meshCount = 0;

        children.forEach((obj) => {
          const name = obj.name || '';
          let floorIdx = 0;
          if (name.startsWith('F1_')) floorIdx = 1;
          else if (name.startsWith('F2_')) floorIdx = 2;
          else if (name.startsWith('F3_')) floorIdx = 3;

          const parts = name.split('_');
          const cat = parts[1] || 'Wall';
          if (categoryMeshes[cat]) {
            categoryMeshes[cat].push(obj);
          }

          obj.userData.floorIdx = floorIdx;
          obj.userData.category = cat;

          obj.traverse((child) => {
            if (child.isMesh) {
              meshCount++;
              child.userData.floorIdx = floorIdx;
              child.userData.category = cat;
              const isGlass = cat === 'Glass';
              child.castShadow = !isGlass;
              child.receiveShadow = true;
              if (isGlass && child.material) {
                child.material.transparent = true;
                child.material.opacity = 0.42;
                child.material.depthWrite = false;
              }
              if (cat !== 'Glass' && cat !== 'Arrow') {
                pickableMeshes.push(child);
              }
              if ((cat === 'Wall' || cat === 'Column') && child.geometry) {
                child.geometry.computeBoundingBox();
                const bb = child.geometry.boundingBox;
                if (bb && eng.floorSnapPoints[floorIdx]) {
                  const corners = [
                    { x: Number(bb.min.x.toFixed(2)), z: Number(bb.min.z.toFixed(2)) },
                    { x: Number(bb.min.x.toFixed(2)), z: Number(bb.max.z.toFixed(2)) },
                    { x: Number(bb.max.x.toFixed(2)), z: Number(bb.min.z.toFixed(2)) },
                    { x: Number(bb.max.x.toFixed(2)), z: Number(bb.max.z.toFixed(2)) },
                    {
                      x: Number(((bb.min.x + bb.max.x) / 2).toFixed(2)),
                      z: Number(((bb.min.z + bb.max.z) / 2).toFixed(2)),
                    },
                  ];
                  for (const c of corners) {
                    eng.floorSnapPoints[floorIdx].push(c);
                  }
                }
              }
            }
          });

          if (floorGroups[floorIdx]) {
            floorGroups[floorIdx].add(obj);
          } else {
            floorGroups[0].add(obj);
          }
        });

        eng.modelLoaded = true;
        syncVisibility(eng, viewStateRef.current);
        if (onModelLoadedRef.current) {
          onModelLoadedRef.current({ meshCount });
        }
      },
      undefined,
      (err) => {
        console.error('Failed to load building.glb:', err);
      }
    );

    // Preload & Cache Server Rack 3D GLB Model for fast instancing
    gltfLoader.load(
      '/models/server_rack.glb',
      (gltf) => {
        eng.cachedRackModel = gltf.scene;
        setModelsLoaded(true);
      },
      undefined,
      (err) => {
        console.warn('Server rack model not loaded yet:', err);
      }
    );

    // Pointer / Raycasting & 3D Polygon (Point-by-Point) + Rectangle Zone Drawing
    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    const drawPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    const planeHitPoint = new THREE.Vector3();
    let downPos = { x: 0, y: 0 };
    let isDrawingRect = false;
    let drawStartPt = null;
    let drawCurrentPt = null;
    let activeDrawFloorIdx = 0;

    // Point-by-Point Polygon Draft state
    let polyDraftVertices = [];
    let polyHoverPt = null;
    let lastClickTime = 0;

    // Create floating live measurement HUD badge for Polygon & Rectangle drawing
    const drawMeasureEl = document.createElement('div');
    drawMeasureEl.className = 'draw-measure-badge';
    drawMeasureEl.style.display = 'none';
    labelsContainer.appendChild(drawMeasureEl);
    eng.drawMeasureEl = drawMeasureEl;

    const rebuildPolygonPreview = () => {
      while (polygonPreviewGroup.children.length > 0) {
        polygonPreviewGroup.remove(polygonPreviewGroup.children[0]);
      }
      if (polyDraftVertices.length === 0) {
        polygonPreviewGroup.visible = false;
        return;
      }
      polygonPreviewGroup.visible = true;
      const worldY = polyDraftVertices[0].worldY;

      // 1. Render Vertex Pin Spheres (First vertex is larger & amber so user knows where to click to close)
      polyDraftVertices.forEach((v, idx) => {
        const isFirst = idx === 0;
        const vGeo = new THREE.SphereGeometry(isFirst ? 0.38 : 0.25, 16, 16);
        const vMat = new THREE.MeshBasicMaterial({
          color: isFirst ? 0xfbbf24 : 0x10b981,
        });
        const vMesh = new THREE.Mesh(vGeo, vMat);
        vMesh.position.set(v.x, worldY + 0.16, v.z);
        polygonPreviewGroup.add(vMesh);
      });

      // 2. Render Rubber-band Outline + Semi-transparent Polygon Fill
      const allPts = polyHoverPt ? [...polyDraftVertices, polyHoverPt] : [...polyDraftVertices];
      if (allPts.length >= 2) {
        const lineVecs = allPts.map((p) => new THREE.Vector3(p.x, worldY + 0.16, p.z));
        if (allPts.length >= 3) {
          lineVecs.push(new THREE.Vector3(allPts[0].x, worldY + 0.16, allPts[0].z));
        }
        const lineGeo = new THREE.BufferGeometry().setFromPoints(lineVecs);
        const lineMat = new THREE.LineBasicMaterial({ color: 0x34d399 });
        polygonPreviewGroup.add(new THREE.Line(lineGeo, lineMat));
      }

      if (allPts.length >= 3) {
        const shape = new THREE.Shape();
        shape.moveTo(allPts[0].x, -allPts[0].z);
        for (let i = 1; i < allPts.length; i++) {
          shape.lineTo(allPts[i].x, -allPts[i].z);
        }
        shape.closePath();
        const fillGeo = new THREE.ShapeGeometry(shape);
        fillGeo.rotateX(-Math.PI / 2);
        const fillMat = new THREE.MeshBasicMaterial({
          color: 0x10b981,
          transparent: true,
          opacity: 0.24,
          depthWrite: false,
          side: THREE.DoubleSide,
        });
        const fillMesh = new THREE.Mesh(fillGeo, fillMat);
        fillMesh.position.y = worldY + 0.04;
        polygonPreviewGroup.add(fillMesh);
      }
    };

    const notifyPolygonDraftChange = () => {
      if (onPolygonDraftChangeRef.current) {
        onPolygonDraftChangeRef.current(polyDraftVertices.length);
      }
    };

    const commitPolygonDraft = () => {
      if (polyDraftVertices.length < 3) return false;
      const cleanPoly = polyDraftVertices.map((v) => ({
        x: Number(v.x.toFixed(2)),
        z: Number(v.z.toFixed(2)),
      }));
      const area = computePolygonArea(cleanPoly);
      if (area < 1.0) return false;

      const centroid = computePolygonCentroid(cleanPoly);
      const xs = cleanPoly.map((p) => p.x);
      const zs = cleanPoly.map((p) => p.z);
      const w = Number(Math.max(2, Math.max(...xs) - Math.min(...xs)).toFixed(2));
      const d = Number(Math.max(2, Math.max(...zs) - Math.min(...zs)).toFixed(2));
      const localElev = polyDraftVertices[0].localElevation;
      const fIdx = activeDrawFloorIdx;

      polyDraftVertices = [];
      polyHoverPt = null;
      rebuildPolygonPreview();
      snapIndicatorMesh.visible = false;
      drawMeasureEl.style.display = 'none';
      notifyPolygonDraftChange();

      if (onRoomZoneDrawnRef.current) {
        onRoomZoneDrawnRef.current({
          floorIdx: fIdx,
          x: centroid.x,
          y: Number((localElev + 1.6).toFixed(2)),
          z: centroid.z,
          width: w,
          depth: d,
          polygon: cleanPoly,
          areaSqM: Number(area.toFixed(2)),
        });
      }
      return true;
    };

    eng.finishPolygonDraft = () => commitPolygonDraft();

    eng.undoLastPolygonVertex = () => {
      if (polyDraftVertices.length > 0) {
        polyDraftVertices.pop();
        rebuildPolygonPreview();
        notifyPolygonDraftChange();
        if (polyDraftVertices.length === 0) {
          drawMeasureEl.style.display = 'none';
        }
        return true;
      }
      return false;
    };

    eng.cancelPolygonDraft = () => {
      polyDraftVertices = [];
      polyHoverPt = null;
      rebuildPolygonPreview();
      snapIndicatorMesh.visible = false;
      drawMeasureEl.style.display = 'none';
      notifyPolygonDraftChange();
    };

    const getFloorPlaneIntersection = (e, fIdx, prevVertex = null) => {
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);

      const flMeta = FLOORS.find((f) => f.index === Number(fIdx)) || FLOORS[0];
      const fg = floorGroups[flMeta.index];
      const offsetY = fg ? fg.position.y : 0;
      const worldPlaneY = flMeta.elevation + offsetY + 0.08;
      drawPlane.set(new THREE.Vector3(0, 1, 0), -worldPlaneY);

      if (!raycaster.ray.intersectPlane(drawPlane, planeHitPoint)) {
        return null;
      }

      let x = planeHitPoint.x;
      let z = planeHitPoint.z;
      let snappedToCorner = false;

      // 1. Shift key Angle Constraint (0°, 45°, 90°, 135° relative to previous vertex)
      if (e.shiftKey && prevVertex) {
        const dx = x - prevVertex.x;
        const dz = z - prevVertex.z;
        const dist = Math.hypot(dx, dz);
        if (dist > 0.1) {
          const rawAngle = Math.atan2(dz, dx);
          const stepRad = Math.PI / 4; // 45 degrees
          const snappedAngle = Math.round(rawAngle / stepRad) * stepRad;
          x = prevVertex.x + dist * Math.cos(snappedAngle);
          z = prevVertex.z + dist * Math.sin(snappedAngle);
        }
      }

      // 2. Magnetic Wall / Column / Existing Room Vertex Snap (within 0.95m radius)
      if (magneticWallSnapRef.current && !e.shiftKey) {
        const candidates = [...(eng.floorSnapPoints[flMeta.index] || [])];
        for (const [, rmEntry] of eng.roomDomMap.entries()) {
          if (
            rmEntry.floorIdx === flMeta.index &&
            Array.isArray(rmEntry.room.polygon)
          ) {
            for (const v of rmEntry.room.polygon) {
              candidates.push({ x: Number(v.x), z: Number(v.z) });
            }
          }
        }
        let bestDist = 0.95;
        let bestPt = null;
        for (const c of candidates) {
          const d = Math.hypot(x - c.x, z - c.z);
          if (d < bestDist) {
            bestDist = d;
            bestPt = c;
          }
        }
        if (bestPt) {
          x = bestPt.x;
          z = bestPt.z;
          snappedToCorner = true;
        }
      }

      if (!snappedToCorner) {
        x = snapValue(x, snapToGridRef.current, 0.5);
        z = snapValue(z, snapToGridRef.current, 0.5);
      }

      return {
        x: Number(x.toFixed(2)),
        z: Number(z.toFixed(2)),
        worldY: worldPlaneY,
        localElevation: flMeta.elevation,
        snappedToCorner,
      };
    };

    const handlePointerDown = (e) => {
      downPos = { x: e.clientX, y: e.clientY };

      // Close any active 3D room rollout menus on canvas interaction
      if (eng.roomDomMap) {
        eng.roomDomMap.forEach((entry) => {
          if (entry.el) {
            entry.el.classList.remove('rollout-open');
            const sub = entry.el.querySelector('.room-rollout-menu');
            if (sub) sub.style.display = 'none';
          }
        });
      }

      // Only start Click-and-Drag Rectangle Marquee on pointerdown when drawShapeType === 'rectangle'
      if (
        drawRoomZoneModeRef.current &&
        drawShapeTypeRef.current === 'rectangle' &&
        e.button === 0
      ) {
        const vs = viewStateRef.current || DEFAULT_VIEW_STATE;
        activeDrawFloorIdx =
          vs.selectedFloor !== 'all'
            ? Number(vs.selectedFloor)
            : Number(drawFloorIdxRef.current ?? 0);
        const pt = getFloorPlaneIntersection(e, activeDrawFloorIdx);
        if (pt) {
          isDrawingRect = true;
          drawStartPt = pt;
          drawCurrentPt = pt;
          controls.enabled = false;
          drawPreviewGroup.position.set(pt.x, pt.worldY, pt.z);
          drawPreviewGroup.scale.set(0.5, 1, 0.5);
          drawPreviewGroup.visible = true;
          drawMeasureEl.style.display = 'block';
          drawMeasureEl.style.left = `${e.clientX}px`;
          drawMeasureEl.style.top = `${e.clientY}px`;
          drawMeasureEl.innerHTML = `📐 ลากเม้าส์วาดกรอบสี่เหลี่ยม: 0.5m × 0.5m`;
        }
      }
    };

    const handlePointerMove = (e) => {
      // Case A: Point-by-Point Polygon Drawing live rubber-band & measurement preview
      if (drawRoomZoneModeRef.current && drawShapeTypeRef.current === 'polygon') {
        const vs = viewStateRef.current || DEFAULT_VIEW_STATE;
        activeDrawFloorIdx =
          vs.selectedFloor !== 'all'
            ? Number(vs.selectedFloor)
            : Number(drawFloorIdxRef.current ?? 0);
        const prevV =
          polyDraftVertices.length > 0
            ? polyDraftVertices[polyDraftVertices.length - 1]
            : null;
        const pt = getFloorPlaneIntersection(e, activeDrawFloorIdx, prevV);
        if (!pt) return;

        // Show Magnetic Snap Ring when near a Wall/Column corner or First Vertex
        let closingFirst = false;
        if (polyDraftVertices.length >= 3) {
          const firstV = polyDraftVertices[0];
          if (Math.hypot(pt.x - firstV.x, pt.z - firstV.z) <= 1.25) {
            pt.x = firstV.x;
            pt.z = firstV.z;
            closingFirst = true;
          }
        }

        if (pt.snappedToCorner || closingFirst) {
          snapIndicatorMesh.position.set(pt.x, pt.worldY + 0.14, pt.z);
          snapIndicatorMesh.material.color.setHex(closingFirst ? 0xfbbf24 : 0x38bdf8);
          snapIndicatorMesh.visible = true;
        } else {
          snapIndicatorMesh.visible = false;
        }

        polyHoverPt = pt;
        if (polyDraftVertices.length > 0) {
          rebuildPolygonPreview();
          const segLen = Math.hypot(pt.x - prevV.x, pt.z - prevV.z).toFixed(2);
          const candidatePoly = [...polyDraftVertices, pt];
          const area =
            candidatePoly.length >= 3 ? computePolygonArea(candidatePoly).toFixed(1) : '0.0';
          drawMeasureEl.style.display = 'block';
          drawMeasureEl.style.left = `${e.clientX}px`;
          drawMeasureEl.style.top = `${e.clientY}px`;
          drawMeasureEl.innerHTML = closingFirst
            ? `✅ คลิกเพื่อปิดกรอบห้อง (${polyDraftVertices.length} มุม · พื้นที่ ${area} ตร.ม.)`
            : `📐 ด้านนี้ ${segLen}m · รวม ${polyDraftVertices.length + 1} มุม (${area} ตร.ม.)${
                pt.snappedToCorner ? ' · 🧲 Snap มุมเสา/ผนัง' : ''
              }`;
        } else {
          drawMeasureEl.style.display = 'block';
          drawMeasureEl.style.left = `${e.clientX}px`;
          drawMeasureEl.style.top = `${e.clientY}px`;
          drawMeasureEl.innerHTML = `📍 คลิกปักหมุดมุมที่ 1 บนพื้นห้อง (${pt.x}, ${pt.z})${
            pt.snappedToCorner ? ' · 🧲 Snap มุมเสา/ผนัง' : ''
          }`;
        }
        return;
      }

      // Case B: Rectangle Drag Marquee
      if (!isDrawingRect || !drawStartPt) return;
      const pt = getFloorPlaneIntersection(e, activeDrawFloorIdx);
      if (!pt) return;
      drawCurrentPt = pt;
      const cx = (drawStartPt.x + pt.x) / 2;
      const cz = (drawStartPt.z + pt.z) / 2;
      const w = Math.max(0.5, Math.abs(pt.x - drawStartPt.x));
      const d = Math.max(0.5, Math.abs(pt.z - drawStartPt.z));
      drawPreviewGroup.position.set(cx, pt.worldY, cz);
      drawPreviewGroup.scale.set(w, 1, d);
      const area = (w * d).toFixed(1);
      drawMeasureEl.style.left = `${e.clientX}px`;
      drawMeasureEl.style.top = `${e.clientY}px`;
      drawMeasureEl.innerHTML = `📐 ขนาดกรอบห้อง: ${w.toFixed(1)}m × ${d.toFixed(1)}m (${area} ตร.ม.)`;
    };

    const handlePointerUp = (e) => {
      if (isDrawingRect) {
        isDrawingRect = false;
        controls.enabled = true;
        drawPreviewGroup.visible = false;
        drawMeasureEl.style.display = 'none';

        if (drawStartPt && drawCurrentPt && onRoomZoneDrawnRef.current) {
          const rawW = Math.abs(drawCurrentPt.x - drawStartPt.x);
          const rawD = Math.abs(drawCurrentPt.z - drawStartPt.z);
          if (rawW >= 1.0 && rawD >= 1.0) {
            const cx = Number(((drawStartPt.x + drawCurrentPt.x) / 2).toFixed(2));
            const cz = Number(((drawStartPt.z + drawCurrentPt.z) / 2).toFixed(2));
            const w = Number(Math.max(2, rawW).toFixed(2));
            const d = Number(Math.max(2, rawD).toFixed(2));
            const minX = Number((cx - w / 2).toFixed(2));
            const maxX = Number((cx + w / 2).toFixed(2));
            const minZ = Number((cz - d / 2).toFixed(2));
            const maxZ = Number((cz + d / 2).toFixed(2));
            onRoomZoneDrawnRef.current({
              floorIdx: activeDrawFloorIdx,
              x: cx,
              y: Number((drawStartPt.localElevation + 1.6).toFixed(2)),
              z: cz,
              width: w,
              depth: d,
              polygon: [
                { x: minX, z: minZ },
                { x: maxX, z: minZ },
                { x: maxX, z: maxZ },
                { x: minX, z: maxZ },
              ],
            });
          }
        }
        drawStartPt = null;
        drawCurrentPt = null;
        return;
      }

      if (Math.hypot(e.clientX - downPos.x, e.clientY - downPos.y) > 5) return;

      // Point-by-Point Polygon Vertex Placement on Left Click
      if (
        drawRoomZoneModeRef.current &&
        drawShapeTypeRef.current === 'polygon' &&
        e.button === 0
      ) {
        const now = Date.now();
        const isDoubleClick = now - lastClickTime < 320;
        lastClickTime = now;

        const vs = viewStateRef.current || DEFAULT_VIEW_STATE;
        activeDrawFloorIdx =
          vs.selectedFloor !== 'all'
            ? Number(vs.selectedFloor)
            : Number(drawFloorIdxRef.current ?? 0);
        const prevV =
          polyDraftVertices.length > 0
            ? polyDraftVertices[polyDraftVertices.length - 1]
            : null;
        const pt = getFloorPlaneIntersection(e, activeDrawFloorIdx, prevV);
        if (!pt) return;

        // If user double-clicked or clicked near the first vertex (with >= 3 points), close & commit Polygon!
        if (polyDraftVertices.length >= 3) {
          const firstV = polyDraftVertices[0];
          const distToFirst = Math.hypot(pt.x - firstV.x, pt.z - firstV.z);
          if (distToFirst <= 1.25 || isDoubleClick) {
            commitPolygonDraft();
            return;
          }
        }

        // Prevent duplicate zero-length point
        if (prevV && Math.hypot(pt.x - prevV.x, pt.z - prevV.z) < 0.15) {
          return;
        }

        polyDraftVertices.push(pt);
        rebuildPolygonPreview();
        notifyPolygonDraftChange();
        return;
      }

      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);

      // Check if Admin clicked one of the Selected Room's Per-Vertex Handles
      if (vertexHandlesGroup.children.length > 0) {
        const handleHits = raycaster.intersectObjects(vertexHandlesGroup.children, false);
        if (handleHits.length > 0) {
          const hitHandle = handleHits[0].object;
          transformControls.setMode('translate');
          transformControls.showX = true;
          transformControls.showY = false;
          transformControls.showZ = true;
          transformControls.attach(hitHandle);
          return;
        }
      }

      if (placementModeRef.current) {
        const roomZoneMeshes = [];
        for (const [, grp] of eng.roomZoneMeshesMap.entries()) {
          if (grp.visible) {
            grp.traverse((c) => {
              if (c.isMesh) roomZoneMeshes.push(c);
            });
          }
        }
        const visibleTargets = [...pickableMeshes, ...roomZoneMeshes].filter((m) => {
          let cur = m;
          while (cur) {
            if (!cur.visible) return false;
            cur = cur.parent;
          }
          return true;
        });
        const hits = raycaster.intersectObjects(visibleTargets, false);
        if (hits.length > 0 && onSurfacePickRef.current) {
          const hit = hits[0];
          let roomId = null;
          let curObj = hit.object;
          while (curObj) {
            if (curObj.userData?.roomId) {
              roomId = curObj.userData.roomId;
              break;
            }
            curObj = curObj.parent;
          }
          const fIdx = hit.object.userData.floorIdx ?? 0;
          const fg = floorGroups[fIdx];
          const localY = hit.point.y - (fg ? fg.position.y : 0);
          onSurfacePickRef.current({
            floorIdx: fIdx,
            roomId,
            x: snapValue(hit.point.x, snapToGridRef.current, 0.5),
            y: Number((localY + 0.45).toFixed(2)),
            z: snapValue(hit.point.z, snapToGridRef.current, 0.5),
          });
        }
        return;
      }

      const pinObjects = [];
      for (const [, grp] of eng.deviceMeshesMap.entries()) {
        if (grp.visible) pinObjects.push(grp);
      }
      const pinHits = raycaster.intersectObjects(pinObjects, true);
      if (pinHits.length > 0) {
        let obj = pinHits[0].object;
        while (obj && !obj.userData?.deviceId) obj = obj.parent;
        if (obj?.userData?.deviceId && onSelectDeviceRef.current) {
          onSelectDeviceRef.current(obj.userData.deviceId);
        }
        return;
      }

      // Check 3D Room Zone click if no device pin was clicked
      const roomZoneObjects = [];
      for (const [, grp] of eng.roomZoneMeshesMap.entries()) {
        if (grp.visible) roomZoneObjects.push(grp);
      }
      const roomHits = raycaster.intersectObjects(roomZoneObjects, true);
      if (roomHits.length > 0) {
        let obj = roomHits[0].object;
        while (obj && !obj.userData?.roomId) obj = obj.parent;
        if (obj?.userData?.roomId) {
          if (onAdminSelectRoomRef.current) {
            onAdminSelectRoomRef.current(obj.userData.roomId);
          } else if (onSelectRoomRef.current) {
            onSelectRoomRef.current(obj.userData.roomId);
          }
        }
      }
    };

    renderer.domElement.addEventListener('pointerdown', handlePointerDown);
    renderer.domElement.addEventListener('pointermove', handlePointerMove);
    renderer.domElement.addEventListener('pointerup', handlePointerUp);

    eng.halfW = window.innerWidth / 2;
    eng.halfH = window.innerHeight / 2;

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
      eng.halfW = window.innerWidth / 2;
      eng.halfH = window.innerHeight / 2;
    };
    window.addEventListener('resize', handleResize);

    // Animation loop
    let animId;
    const tempVec = new THREE.Vector3();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const vs = viewStateRef.current || DEFAULT_VIEW_STATE;

      FLOORS.forEach((f) => {
        const fg = floorGroups[f.index];
        if (!fg) return;
        const targetY = vs.exploded ? f.index * 11.5 : 0;
        fg.position.y += (targetY - fg.position.y) * 0.1;
      });

      if (eng.cameraAnim) {
        eng.cameraAnim.progress += 0.06;
        const t = Math.min(1, eng.cameraAnim.progress);
        const ease = 1 - Math.pow(1 - t, 3);
        camera.position.lerpVectors(eng.cameraAnim.startPos, eng.cameraAnim.endPos, ease);
        controls.target.lerpVectors(eng.cameraAnim.startTarget, eng.cameraAnim.endTarget, ease);
        if (t >= 1) eng.cameraAnim = null;
      }

      controls.update();
      renderer.render(scene, camera);

      const halfW = eng.halfW || (window.innerWidth / 2);
      const halfH = eng.halfH || (window.innerHeight / 2);
      const showDevs = vs.showDevices !== undefined ? Boolean(vs.showDevices) : true;
      const showLabels = vs.showDeviceLabels !== undefined ? Boolean(vs.showDeviceLabels) : true;

      for (const [, info] of eng.deviceDomMap.entries()) {
        if (!showDevs || !info.pinGroup.visible || !showLabels) {
          info.el.style.display = 'none';
          continue;
        }
        info.pinGroup.getWorldPosition(tempVec);
        tempVec.project(camera);
        if (tempVec.z > 1) {
          info.el.style.opacity = '0';
        } else {
          info.el.style.display = 'flex';
          info.el.style.opacity = '1';
          info.el.style.left = `${tempVec.x * halfW + halfW}px`;
          info.el.style.top = `${-tempVec.y * halfH + halfH}px`;
        }
      }

      for (const [, info] of eng.roomDomMap.entries()) {
        if (info.el.style.display === 'none') continue;
        const fg = floorGroups[info.floorIdx];
        const offsetY = fg ? fg.position.y : 0;
        tempVec.set(
          Number(info.room.position?.x || 0),
          Number(info.room.position?.y || 1.5) + offsetY,
          Number(info.room.position?.z || 0)
        );
        tempVec.project(camera);
        if (tempVec.z > 1) {
          info.el.style.opacity = '0';
        } else {
          info.el.style.opacity = '1';
          info.el.style.left = `${tempVec.x * halfW + halfW}px`;
          info.el.style.top = `${-tempVec.y * halfH + halfH}px`;
        }
      }
    };
    animate();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', handleResize);
      renderer.domElement.removeEventListener('pointerdown', handlePointerDown);
      renderer.domElement.removeEventListener('pointermove', handlePointerMove);
      renderer.domElement.removeEventListener('pointerup', handlePointerUp);
      for (const [, grp] of eng.deviceMeshesMap.entries()) {
        safeDisposeGroup(grp);
      }
      for (const [, grp] of eng.roomZoneMeshesMap.entries()) {
        safeDisposeGroup(grp);
      }
      eng.deviceMeshesMap.clear();
      eng.roomZoneMeshesMap.clear();
      if (controls && controls.dispose) controls.dispose();
      if (transformControls && transformControls.dispose) transformControls.dispose();
      renderer.dispose();
    };
  }, []);

  // Update 3D Scene Background when Theme toggles between Dark & Light
  React.useEffect(() => {
    const eng = engineRef.current;
    if (!eng) return;
    const bgHex = theme === 'light' ? 0xe2e8f0 : 0x060b14;
    eng.scene.background = new THREE.Color(bgHex);
    eng.scene.fog = new THREE.FogExp2(bgHex, 0.002);
  }, [theme]);

  // Update cursor on placementMode or drawRoomZoneMode
  React.useEffect(() => {
    const eng = engineRef.current;
    if (!eng) return;
    eng.renderer.domElement.style.cursor =
      placementMode || drawRoomZoneMode ? 'crosshair' : 'default';
    if (!drawRoomZoneMode && eng.cancelPolygonDraft) {
      eng.cancelPolygonDraft();
    }
  }, [placementMode, drawRoomZoneMode, drawShapeType]);

  // Rebuild 3D Pins & Room Labels whenever placedDevices or rooms change
  React.useEffect(() => {
    const eng = engineRef.current;
    const labelsContainer = labelsRef.current;
    if (!eng || !labelsContainer) return;

    if (eng.transformControls) {
      eng.transformControls.detach();
    }

    for (const [, grp] of eng.deviceMeshesMap.entries()) {
      safeDisposeGroup(grp);
    }
    for (const [, grp] of eng.roomZoneMeshesMap.entries()) {
      safeDisposeGroup(grp);
    }
    eng.deviceMeshesMap.clear();
    eng.deviceDomMap.clear();
    eng.roomDomMap.clear();
    eng.roomZoneMeshesMap.clear();
    labelsContainer.innerHTML = '';
    if (eng.drawMeasureEl) {
      labelsContainer.appendChild(eng.drawMeasureEl);
    }

    // Rooms (3D Floor Zone Highlight + Interactive Room Tag with Live Health & Device Count)
    (rooms || []).forEach((rm) => {
      const fIdx = Number(rm.floorIdx ?? 0);
      const fg = eng.floorGroups[fIdx] || eng.floorGroups[0];
      const flMeta = FLOORS.find((f) => f.index === fIdx) || FLOORS[0];
      const rMeta = getRoomTypeMeta(rm.roomType);
      const roomColorHex = rm.color || rMeta.color || '#38bdf8';
      const roomColor = new THREE.Color(roomColorHex);

      // Compute placed devices belonging to this room (strictly isPlaced === true)
      const roomDevices = (placedDevices || []).filter(
        (d) =>
          d.isPlaced &&
          Number(d.floorIdx ?? 0) === fIdx &&
          (d.roomId === rm.id || (d.roomNumber && d.roomNumber === rm.roomNumber))
      );

      let roomHealthStatus = 'Idle';
      if (roomDevices.length > 0) {
        const hasOffline = roomDevices.some(
          (d) => String(d.status || '').toLowerCase() === 'offline'
        );
        const hasWarning = roomDevices.some(
          (d) => String(d.status || '').toLowerCase() === 'warning'
        );
        roomHealthStatus = hasOffline ? 'Offline' : hasWarning ? 'Warning' : 'Online';
      }

      // 1. 3D Floor Zone Highlight Pad + Glowing Border (Custom Polygon or Rectangle)
      const zoneW = Math.max(2, Number(rm.zoneSize?.width ?? 12));
      const zoneD = Math.max(2, Number(rm.zoneSize?.depth ?? 10));
      const rx = Number(rm.position?.x || 0);
      const rz = Number(rm.position?.z || 0);
      const zoneY = flMeta.elevation + 0.08;

      const zoneGroup = new THREE.Group();
      zoneGroup.position.set(rx, zoneY, rz);
      zoneGroup.userData = { isRoomZone: true, roomId: rm.id, floorIdx: fIdx };

      if (Array.isArray(rm.polygon) && rm.polygon.length >= 3) {
        const shape = new THREE.Shape();
        rm.polygon.forEach((pt, idx) => {
          const lx = Number(pt.x) - rx;
          const lz = Number(pt.z) - rz;
          if (idx === 0) shape.moveTo(lx, -lz);
          else shape.lineTo(lx, -lz);
        });
        shape.closePath();

        const padGeo = new THREE.ShapeGeometry(shape);
        padGeo.rotateX(-Math.PI / 2);
        const padMat = new THREE.MeshBasicMaterial({
          color: roomColor,
          transparent: true,
          opacity: 0.18,
          depthWrite: false,
          side: THREE.DoubleSide,
        });
        const padMesh = new THREE.Mesh(padGeo, padMat);
        padMesh.position.y = 0.02;
        padMesh.userData = { isRoomZone: true, roomId: rm.id, floorIdx: fIdx };
        zoneGroup.add(padMesh);

        const extrudeGeo = new THREE.ExtrudeGeometry(shape, {
          depth: 0.28,
          bevelEnabled: false,
        });
        extrudeGeo.rotateX(-Math.PI / 2);
        const edgesGeo = new THREE.EdgesGeometry(extrudeGeo);
        const edgesMat = new THREE.LineBasicMaterial({
          color: roomColor,
          transparent: true,
          opacity: 0.85,
        });
        const borderLines = new THREE.LineSegments(edgesGeo, edgesMat);
        borderLines.position.y = 0.28;
        borderLines.userData = { isRoomZone: true, roomId: rm.id, floorIdx: fIdx };
        zoneGroup.add(borderLines);
      } else {
        const padGeo = new THREE.PlaneGeometry(zoneW, zoneD);
        padGeo.rotateX(-Math.PI / 2);
        const padMat = new THREE.MeshBasicMaterial({
          color: roomColor,
          transparent: true,
          opacity: 0.16,
          depthWrite: false,
          side: THREE.DoubleSide,
        });
        const padMesh = new THREE.Mesh(padGeo, padMat);
        padMesh.userData = { isRoomZone: true, roomId: rm.id, floorIdx: fIdx };
        zoneGroup.add(padMesh);

        const boxGeo = new THREE.BoxGeometry(zoneW, 0.28, zoneD);
        const edgesGeo = new THREE.EdgesGeometry(boxGeo);
        const edgesMat = new THREE.LineBasicMaterial({
          color: roomColor,
          transparent: true,
          opacity: 0.78,
        });
        const borderLines = new THREE.LineSegments(edgesGeo, edgesMat);
        borderLines.position.y = 0.14;
        borderLines.userData = { isRoomZone: true, roomId: rm.id, floorIdx: fIdx };
        zoneGroup.add(borderLines);
      }

      if (fg) {
        fg.add(zoneGroup);
      }
      eng.roomZoneMeshesMap.set(rm.id, zoneGroup);

      // 2. Interactive 3D Floating Room Tag with Rollout Hierarchy (Room Number, Name > Roll Menu > Devices List)
      const el = document.createElement('div');
      el.className = `room-label-3d${activeRoomIdRef.current === rm.id ? ' selected-room' : ''}`;
      el.style.borderColor = roomColorHex;
      el.setAttribute('data-room-id', rm.id);

      const countBadgeHtml =
        roomDevices.length > 0
          ? `<span class="room-count-pill">${roomDevices.length} อุปกรณ์</span>`
          : '<span class="room-count-pill empty">0</span>';

      // 1. Header (Click to toggle roll menu)
      const headerEl = document.createElement('div');
      headerEl.className = 'room-label-header';
      headerEl.setAttribute('role', 'button');
      headerEl.setAttribute('title', `ห้อง [${rm.roomNumber}] ${rm.name || ''} - กดเพื่อดูรายการอุปกรณ์ในห้อง`);
      headerEl.innerHTML = `
        <span class="status-dot ${roomHealthStatus}" title="สถานะห้อง: ${roomHealthStatus}"></span>
        <span class="room-icon">${rMeta.icon}</span>
        <strong class="room-num">[${rm.roomNumber}]</strong>
        <span class="room-title">${rm.name || ''}</span>
        ${countBadgeHtml}
        <span class="room-roll-indicator">▼</span>
      `;

      // 2. Rollout Menu Container (Dropdown / Roll menu)
      const rolloutMenu = document.createElement('div');
      rolloutMenu.className = 'room-rollout-menu';
      rolloutMenu.style.display = 'none';

      // Rollout Menu Header with Room Details action
      const rolloutTop = document.createElement('div');
      rolloutTop.className = 'room-rollout-header';
      rolloutTop.innerHTML = `
        <div class="room-rollout-header-text" title="[${rm.roomNumber}] ${rm.name || ''}">
          <span class="status-dot ${roomHealthStatus}"></span>
          <strong>[${rm.roomNumber}]</strong>
          <span class="truncate-title">${rm.name || 'ห้อง'}</span>
          <span class="room-rollout-count font-mono">(${roomDevices.length})</span>
        </div>
        <button type="button" class="room-rollout-room-btn" title="เปิดหน้าต่างข้อมูลห้อง / แก้ไขห้อง">
          🏢 ข้อมูลห้อง
        </button>
      `;

      const roomBtn = rolloutTop.querySelector('.room-rollout-room-btn');
      if (roomBtn) {
        roomBtn.addEventListener('click', (ev) => {
          ev.stopPropagation();
          rolloutMenu.style.display = 'none';
          el.classList.remove('rollout-open');
          if (onAdminSelectRoomRef.current) {
            onAdminSelectRoomRef.current(rm.id);
          } else if (onSelectRoomRef.current) {
            onSelectRoomRef.current(rm.id);
          }
        });
      }

      rolloutMenu.appendChild(rolloutTop);

      // Rollout Device List
      const deviceListEl = document.createElement('div');
      deviceListEl.className = 'room-rollout-list';

      if (roomDevices.length === 0) {
        const emptyEl = document.createElement('div');
        emptyEl.className = 'room-rollout-empty';
        emptyEl.textContent = 'ยังไม่มีอุปกรณ์ติดตั้งในห้องนี้';
        deviceListEl.appendChild(emptyEl);
      } else {
        const racks = roomDevices.filter((d) => d.modelType === 'server_rack');
        const standalone = roomDevices.filter(
          (d) => d.modelType !== 'server_rack' && !d.parentRackId
        );

        // 1. Server Racks and their mounted devices (hierarchical)
        racks.forEach((rackDev) => {
          const mounted = roomDevices
            .filter((d) => d.parentRackId === rackDev.id)
            .sort((a, b) => Number(b.uPosition || 1) - Number(a.uPosition || 1));
          const rackStatus = String(rackDev.status || 'online').toLowerCase();
          const rackName = rackDev.name || rackDev.ip || 'Server Rack';

          const rackItemEl = document.createElement('div');
          rackItemEl.className = 'room-device-item is-rack';
          rackItemEl.setAttribute('role', 'button');
          rackItemEl.setAttribute(
            'title',
            `เปิดดูโครงสร้างผังตู้แร็ค 42U (${rackName})`
          );

          rackItemEl.innerHTML = `
            <span class="status-dot ${rackStatus}"></span>
            <span class="dev-type-icon">🗄️</span>
            <div class="device-meta">
              <div class="device-name">${rackName}</div>
              <div class="device-sub font-mono">
                ตู้แร็ค 42U · <span class="rack-badge">${mounted.length} อุปกรณ์</span>
              </div>
            </div>
            <span class="device-click-hint is-rack">
              ผังตู้ ➔
            </span>
          `;

          rackItemEl.addEventListener('click', (ev) => {
            ev.stopPropagation();
            rolloutMenu.style.display = 'none';
            el.classList.remove('rollout-open');
            if (onSelectDeviceRef.current) {
              onSelectDeviceRef.current(rackDev.id);
            }
          });

          deviceListEl.appendChild(rackItemEl);

          // Render nested mounted devices ordered by U
          mounted.forEach((mDev) => {
            const mMeta = getCategoryMeta(mDev.category);
            const mStatus = String(mDev.status || 'online').toLowerCase();
            const mName = mDev.name || mDev.ip || 'Device';
            const mIp = mDev.ip || '-';
            const uPos = mDev.uPosition || 1;

            const mItemEl = document.createElement('div');
            mItemEl.className = 'room-device-item is-nested-device';
            mItemEl.setAttribute('role', 'button');
            mItemEl.setAttribute(
              'title',
              `[U${uPos}] ${mName} (ติดตั้งในตู้ ${rackName})`
            );

            mItemEl.innerHTML = `
              <span class="u-badge-pill">U${uPos}</span>
              <span class="status-dot ${mStatus}"></span>
              <span class="dev-type-icon text-[11px]">${mMeta.icon || '📦'}</span>
              <div class="device-meta">
                <div class="device-name text-[10.5px]">${mName}</div>
                <div class="device-sub font-mono text-[9px]">${mIp}</div>
              </div>
            `;

            mItemEl.addEventListener('click', (ev) => {
              ev.stopPropagation();
              rolloutMenu.style.display = 'none';
              el.classList.remove('rollout-open');
              if (onSelectDeviceRef.current) {
                onSelectDeviceRef.current(mDev.id);
              }
            });

            deviceListEl.appendChild(mItemEl);
          });
        });

        // 2. Standalone Room Devices
        if (standalone.length > 0) {
          if (racks.length > 0) {
            const secTitle = document.createElement('div');
            secTitle.className = 'room-rollout-section-title';
            secTitle.innerHTML = `<span>อุปกรณ์ประจำห้อง (${standalone.length})</span>`;
            deviceListEl.appendChild(secTitle);
          }

          standalone.forEach((dev) => {
            const dMeta = getCategoryMeta(dev.category);
            const devStatusClass = String(dev.status || 'online').toLowerCase();
            const devName = dev.name || dev.ip || 'Device';
            const devIp = dev.ip || '-';

            const itemEl = document.createElement('div');
            itemEl.className = 'room-device-item';
            itemEl.setAttribute('role', 'button');
            itemEl.setAttribute('title', `เปิดรายละเอียดอุปกรณ์ (${devName})`);

            itemEl.innerHTML = `
              <span class="status-dot ${devStatusClass}"></span>
              <span class="dev-type-icon">${dMeta.icon || '📦'}</span>
              <div class="device-meta">
                <div class="device-name">${devName}</div>
                <div class="device-sub font-mono">${devIp}</div>
              </div>
              <span class="device-click-hint">➔</span>
            `;

            itemEl.addEventListener('click', (ev) => {
              ev.stopPropagation();
              rolloutMenu.style.display = 'none';
              el.classList.remove('rollout-open');
              if (onSelectDeviceRef.current) {
                onSelectDeviceRef.current(dev.id);
              }
            });

            deviceListEl.appendChild(itemEl);
          });
        }
      }

      rolloutMenu.appendChild(deviceListEl);

      el.appendChild(headerEl);
      el.appendChild(rolloutMenu);

      headerEl.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = rolloutMenu.style.display === 'block';

        // Close any other open room rollout menus in the viewport
        if (eng.roomDomMap) {
          eng.roomDomMap.forEach((entry) => {
            if (entry.el) {
              entry.el.classList.remove('rollout-open');
              const subMenu = entry.el.querySelector('.room-rollout-menu');
              if (subMenu) subMenu.style.display = 'none';
            }
          });
        }

        if (!isOpen) {
          rolloutMenu.style.display = 'block';
          el.classList.add('rollout-open');
          if (onAdminSelectRoomRef.current) {
            onAdminSelectRoomRef.current(rm.id);
          }
        }
      });

      labelsContainer.appendChild(el);
      eng.roomDomMap.set(rm.id, { el, room: rm, floorIdx: fIdx, zoneGroup, rolloutMenu });
    });

    // Placed Devices ONLY (Devices mounted inside a 3D Server Rack are consolidated inside their parent rack)
    (placedDevices || []).forEach((dev) => {
      if (!dev.isPlaced) return;
      if (dev.parentRackId) return;
      const fIdx = Number(dev.floorIdx ?? 0);
      const fg = eng.floorGroups[fIdx] || eng.floorGroups[0];
      const meta = getCategoryMeta(dev.category);
      const pinColor = new THREE.Color(dev.color || meta.color || '#38bdf8');

      const isRack = dev.modelType === 'server_rack';
      const rackChildren = isRack
        ? (placedDevices || []).filter(
            (d) => d.parentRackId === dev.id && d.uPosition !== null && Number(d.uPosition) >= 1
          )
        : [];
      const rackUsedU = isRack
        ? rackChildren.reduce((sum, item) => sum + Math.max(1, Number(item.uHeight || 1)), 0)
        : 0;
      const rackTotalU = isRack ? Math.max(1, Number(dev.rackConfig?.rackHeight || 42)) : 42;
      const rackStatus =
        isRack && rackChildren.some((c) => String(c.status || '').toLowerCase() === 'offline')
          ? 'Offline'
          : dev.status || 'Online';
      const pinGroup = new THREE.Group();
      const flMeta = FLOORS.find((f) => f.index === fIdx) || FLOORS[0];
      const floorElevation = flMeta.elevation;
      let posY = Number(dev.position?.y ?? (isRack ? 0.05 : 1.2));
      if (posY < floorElevation) {
        posY = floorElevation + (isRack ? 0.05 : 1.2);
      }
      pinGroup.position.set(
        Number(dev.position?.x || 0),
        posY,
        Number(dev.position?.z || 0)
      );
      pinGroup.userData = { isDevicePin: true, deviceId: dev.id, floorIdx: fIdx };

      if (isRack && eng.cachedRackModel) {
        const rackClone = eng.cachedRackModel.clone(true);
        rackClone.userData = { isSharedModelInstance: true };
        rackClone.scale.set(2.0, 2.0, 2.0);
        rackClone.position.set(0, 0.98, 0); // Ground the rack bottom on the floor
        const rotYDeg = Number(dev.rotationY ?? 0);
        rackClone.rotation.y = (rotYDeg * Math.PI) / 180;

        rackClone.traverse((child) => {
          if (child.isMesh) {
            child.userData = { isDevicePin: true, deviceId: dev.id };
            child.castShadow = true;
            child.receiveShadow = true;
          }
        });
        pinGroup.add(rackClone);

        // Status glowing ring at base of rack
        const ringGeo = new THREE.RingGeometry(0.55, 0.75, 24);
        ringGeo.rotateX(-Math.PI / 2);
        const ringMat = new THREE.MeshBasicMaterial({
          color: pinColor,
          transparent: true,
          opacity: 0.85,
          side: THREE.DoubleSide,
        });
        const ringMesh = new THREE.Mesh(ringGeo, ringMat);
        ringMesh.position.y = 0.02;
        pinGroup.add(ringMesh);
      } else {
        const sphereGeo = new THREE.SphereGeometry(0.45, 20, 20);
        const sphereMat = new THREE.MeshStandardMaterial({
          color: pinColor,
          emissive: pinColor,
          emissiveIntensity: String(dev.status).toLowerCase() === 'offline' ? 0.15 : 0.75,
          roughness: 0.25,
        });
        const sphere = new THREE.Mesh(sphereGeo, sphereMat);
        sphere.userData = { isDevicePin: true, deviceId: dev.id };
        pinGroup.add(sphere);

        const stemGeo = new THREE.CylinderGeometry(0.06, 0.06, 1.0, 8);
        stemGeo.translate(0, -0.5, 0);
        const stemMat = new THREE.MeshBasicMaterial({
          color: pinColor,
          transparent: true,
          opacity: 0.7,
        });
        pinGroup.add(new THREE.Mesh(stemGeo, stemMat));
      }

      fg.add(pinGroup);
      eng.deviceMeshesMap.set(dev.id, pinGroup);

      const badge = document.createElement('div');
      badge.className = 'device-pin-label';
      const roomTag = dev.roomNumber ? `[${dev.roomNumber}] ` : '';
      const rackInfoBadge = isRack
        ? `<span style="margin-left:5px;padding:1px 6px;border-radius:999px;background:rgba(189,147,249,0.24);border:1px solid rgba(189,147,249,0.5);color:#e2d4f0;font-size:10px;font-weight:700;">${rackChildren.length} ชิ้น • ${rackUsedU}/${rackTotalU}U</span>`
        : '';
      badge.innerHTML = `
        <span class="status-dot ${rackStatus}"></span>
        <span>${isRack ? '🗄️' : meta.icon}</span>
        <span>${roomTag}${dev.name || dev.ip}</span>
        ${rackInfoBadge}
      `;
      badge.addEventListener('click', (e) => {
        e.stopPropagation();
        if (onSelectDeviceRef.current) onSelectDeviceRef.current(dev.id);
      });
      labelsContainer.appendChild(badge);
      eng.deviceDomMap.set(dev.id, { el: badge, dev, pinGroup });
    });

    syncVisibility(eng, viewStateRef.current);
  }, [rooms, placedDevices, modelsLoaded]);

  // Attach/Detach TransformControls Gizmo, Per-Vertex Handles & Highlight Selected Room
  React.useEffect(() => {
    const eng = engineRef.current;
    if (!eng || !eng.transformControls) return;

    eng.transformControls.detach();

    // Priority 1: Attach to Active Device / Server Rack for 3D Move & Rotate
    if (activeAdminDeviceId && eng.deviceMeshesMap.has(activeAdminDeviceId)) {
      const devGroup = eng.deviceMeshesMap.get(activeAdminDeviceId);
      if (deviceTransformMode === 'rotate') {
        eng.transformControls.setMode('rotate');
        eng.transformControls.showX = false;
        eng.transformControls.showY = true;
        eng.transformControls.showZ = false;
      } else {
        eng.transformControls.setMode('translate');
        eng.transformControls.showX = true;
        eng.transformControls.showY = false;
        eng.transformControls.showZ = true;
      }
      eng.transformControls.attach(devGroup);
      return;
    }

    for (const [id, entry] of eng.roomDomMap.entries()) {
      if (id === activeRoomId) {
        entry.el.classList.add('selected-room');
      } else {
        entry.el.classList.remove('selected-room');
      }
    }

    while (eng.vertexHandlesGroup.children.length > 0) {
      eng.vertexHandlesGroup.remove(eng.vertexHandlesGroup.children[0]);
    }

    if (!activeRoomId || !roomTransformMode || !eng.roomZoneMeshesMap.has(activeRoomId)) {
      return;
    }

    const rmEntry = eng.roomDomMap.get(activeRoomId);
    const targetGroup = eng.roomZoneMeshesMap.get(activeRoomId);

    // Per-Vertex Polygon Editing Mode ('vertices')
    if (
      roomTransformMode === 'vertices' &&
      rmEntry &&
      Array.isArray(rmEntry.room.polygon) &&
      rmEntry.room.polygon.length >= 3
    ) {
      const flMeta = FLOORS.find((f) => f.index === Number(rmEntry.floorIdx)) || FLOORS[0];
      const fg = eng.floorGroups[flMeta.index];
      const offsetY = fg ? fg.position.y : 0;
      const worldY = flMeta.elevation + offsetY + 0.24;

      rmEntry.room.polygon.forEach((pt, idx) => {
        const hGeo = new THREE.SphereGeometry(0.42, 18, 18);
        const hMat = new THREE.MeshBasicMaterial({
          color: idx === 0 ? 0xfbbf24 : 0x38bdf8,
        });
        const handleMesh = new THREE.Mesh(hGeo, hMat);
        handleMesh.position.set(Number(pt.x), worldY, Number(pt.z));
        handleMesh.userData = {
          isPolygonVertexHandle: true,
          roomId: activeRoomId,
          vertexIdx: idx,
        };
        eng.vertexHandlesGroup.add(handleMesh);
      });

      if (eng.vertexHandlesGroup.children.length > 0) {
        eng.transformControls.setMode('translate');
        eng.transformControls.showX = true;
        eng.transformControls.showY = false;
        eng.transformControls.showZ = true;
        eng.transformControls.attach(eng.vertexHandlesGroup.children[0]);
      }
      return;
    }

    // Whole-Room Rotate Mode ('rotate' around Y axis)
    if (roomTransformMode === 'rotate') {
      eng.transformControls.setMode('rotate');
      eng.transformControls.showX = false;
      eng.transformControls.showY = true;
      eng.transformControls.showZ = false;
      eng.transformControls.attach(targetGroup);
      return;
    }

    // Whole-Room Scale or Translate Mode
    eng.transformControls.setMode(roomTransformMode === 'scale' ? 'scale' : 'translate');
    eng.transformControls.showX = true;
    eng.transformControls.showY = false;
    eng.transformControls.showZ = true;
    eng.transformControls.attach(targetGroup);
  }, [activeAdminDeviceId, deviceTransformMode, activeRoomId, roomTransformMode, rooms]);

  // Sync Layer & Filter Visibility whenever viewState changes
  React.useEffect(() => {
    const eng = engineRef.current;
    if (!eng) return;
    syncVisibility(eng, mergedViewState);
  }, [mergedViewState]);

  return (
    <>
      <div ref={mountRef} className="fixed inset-0 z-[1]" />
      <div ref={labelsRef} className="fixed inset-0 pointer-events-none z-[2]" />
    </>
  );
});

function syncVisibility(eng, rawVs) {
  const vs = { ...DEFAULT_VIEW_STATE, ...(rawVs || {}) };
  const selFloor = vs.selectedFloor;

  FLOORS.forEach((f) => {
    const fg = eng.floorGroups[f.index];
    if (!fg) return;
    fg.visible = selFloor === 'all' || Number(selFloor) === f.index;

    const overlay = eng.planOverlayMeshes[f.index];
    if (overlay) {
      overlay.visible = Boolean(vs.showPlans && fg.visible);
    }
  });

  eng.categoryMeshes.Glass.forEach((m) => (m.visible = Boolean(vs.showGlass)));
  eng.categoryMeshes.Roof.forEach((m) => (m.visible = Boolean(vs.showRoof)));
  eng.categoryMeshes.Basketball.forEach((m) => (m.visible = Boolean(vs.showBasketball)));
  eng.categoryMeshes.Arrow.forEach((m) => (m.visible = Boolean(vs.showArrows)));
  eng.categoryMeshes.Wall.forEach((m) => (m.visible = Boolean(vs.showWalls)));

  const enabledCats = Array.isArray(vs.enabledCategories)
    ? vs.enabledCategories
    : DEFAULT_VIEW_STATE.enabledCategories;

  const showDevs = vs.showDevices !== undefined ? Boolean(vs.showDevices) : true;
  const showLabels = vs.showDeviceLabels !== undefined ? Boolean(vs.showDeviceLabels) : true;

  for (const [, info] of eng.deviceDomMap.entries()) {
    const dev = info.dev;
    const floorMatch = selFloor === 'all' || Number(selFloor) === Number(dev.floorIdx ?? 0);
    const subMatch = vs.filterSubnet === 'all' || dev.subnet === vs.filterSubnet;
    const statusMatch =
      vs.filterStatus === 'all' ||
      String(dev.status || 'Online').toLowerCase() === String(vs.filterStatus).toLowerCase();
    const catKey = DEVICE_CATEGORIES.some((c) => c.id === dev.category)
      ? dev.category
      : 'Custom';
    const catMatch = enabledCats.includes(catKey);
    const visible = Boolean(showDevs && dev.isPlaced && floorMatch && subMatch && statusMatch && catMatch);
    info.pinGroup.visible = visible;
    info.el.style.display = (visible && showLabels) ? 'flex' : 'none';
  }

  for (const [, info] of eng.roomDomMap.entries()) {
    const floorMatch = selFloor === 'all' || Number(selFloor) === info.floorIdx;
    const show = Boolean(vs.showRooms && floorMatch);
    info.el.style.display = show ? '' : 'none';
    if (info.zoneGroup) {
      info.zoneGroup.visible = show;
    }
  }
}

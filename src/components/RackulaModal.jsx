import React, { useState, useMemo, useRef } from 'react';
import {
  RACKULA_CATEGORY_COLOURS,
  RACKULA_CATEGORIES,
  COMMON_RACK_HEIGHTS,
  RACK_SVG_METRICS,
  RACKULA_STARTER_LIBRARY,
  mapTwinCategoryToRackula,
  getDeviceURange,
  canMountInRack,
  findFirstAvailableUSlot,
  computeBlockedSlots,
  serializeToRackulaYaml,
} from '../data/rackulaData';

const PORT_COLOURS = {
  '1000base-t': '#10B981',     // Emerald
  '10gbase-t': '#3B82F6',      // Blue
  '10gbase-x-sfpp': '#8B5CF6', // Purple
  '25gbase-x-sfp28': '#F59E0B',// Amber
  '40gbase-x-qsfpp': '#EF4444',// Red
  default: '#6272A4',
};

/**
 * Ported from Rackula's PortIndicators.svelte & RackDevice.svelte
 * Renders a single mounted device faceplate inside the SVG Rack Frame
 */
function RackDeviceSVG({
  item,
  rackHeight,
  uHeightPx,
  rackWidth,
  railWidth,
  isSelected,
  isPendingMove,
  isAdmin,
  onSelect,
  onDragStartDevice,
}) {
  const uPos = Math.max(1, Number(item.uPosition || 1));
  const uH = Math.max(1, Number(item.uHeight || 1));
  const interiorWidth = rackWidth - railWidth * 2;
  const deviceHeightPx = uH * uHeightPx;
  const y = (rackHeight - uPos - uH + 1) * uHeightPx;
  const x = railWidth;

  const mapped = mapTwinCategoryToRackula(item.category);
  const baseColor = item.color || item.colour || mapped.colour || RACKULA_CATEGORY_COLOURS.server;
  const rackCat = item.rackConfig?.rackCategory || mapped.rackCategory || 'network';

  const statusLower = String(item.status || 'Online').toLowerCase();
  const isOnline = statusLower === 'online';
  const isWarning = statusLower === 'warning';
  const statusColor = isOnline ? '#50FA7B' : isWarning ? '#FFB86C' : '#FF5555';

  const openPorts = Array.isArray(item.openPorts) ? item.openPorts : [];
  const templateInterfaces = Array.isArray(item.rackConfig?.interfaces) ? item.rackConfig.interfaces : [];

  // Determine ports to render on faceplate
  const portCount = useMemo(() => {
    if (templateInterfaces.length > 0) return Math.min(48, templateInterfaces.length);
    if (rackCat === 'network' || String(item.category).toLowerCase() === 'switch') return 24;
    if (rackCat === 'patch-panel') return 24;
    if (rackCat === 'firewall' || String(item.category).toLowerCase() === 'router') return 8;
    if (rackCat === 'server') return 4;
    return 0;
  }, [templateInterfaces.length, rackCat, item.category]);

  const isBlank = rackCat === 'blank';
  const isCable = rackCat === 'cable-management';
  const isShelf = rackCat === 'shelf';
  const isPduOrUps = rackCat === 'power';

  return (
    <g
      transform={`translate(${x}, ${y})`}
      draggable={isAdmin}
      style={{ cursor: isAdmin ? 'grab' : 'pointer' }}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(item);
      }}
      onDragStart={(e) => {
        if (!isAdmin) return;
        e.stopPropagation();
        const payload = {
          type: 'mounted-device',
          deviceId: item.id,
          uHeight: uH,
          isFullDepth: item.isFullDepth !== undefined ? Boolean(item.isFullDepth) : true,
          currentFace: item.rackFace || item.face || 'front',
          currentU: uPos,
          name: item.name,
        };
        e.dataTransfer.setData('application/json', JSON.stringify(payload));
        e.dataTransfer.effectAllowed = 'move';
        onDragStartDevice?.(e, item);
      }}
    >
      {/* Device Main Body Rect */}
      <rect
        x={1}
        y={1}
        width={interiorWidth - 2}
        height={deviceHeightPx - 2}
        rx={3}
        ry={3}
        fill={baseColor}
        fillOpacity={isBlank ? 0.65 : 0.92}
        stroke={isPendingMove ? '#50FA7B' : isSelected ? '#FF79C6' : 'rgba(255,255,255,0.22)'}
        strokeWidth={isPendingMove ? 2.5 : isSelected ? 2.2 : 1}
        strokeDasharray={isPendingMove ? '5 3' : 'none'}
      />

      {/* Subtle Top Highlight Bevel */}
      <line
        x1={2}
        y1={2}
        x2={interiorWidth - 2}
        y2={2}
        stroke="rgba(255,255,255,0.25)"
        strokeWidth={1}
      />

      {/* Server / Cooling Vent Pattern for 2U+ Servers or Fan Panels */}
      {(rackCat === 'server' || rackCat === 'cooling' || rackCat === 'storage') && uH >= 2 && (
        <g opacity={0.22}>
          {Array.from({ length: 6 }, (_, idx) => (
            <rect
              key={idx}
              x={14 + idx * 32}
              y={deviceHeightPx - 14}
              width={26}
              height={8}
              rx={1.5}
              fill="#0f172a"
              stroke="rgba(255,255,255,0.3)"
              strokeWidth={0.6}
            />
          ))}
        </g>
      )}

      {/* Cable Management Finger Duct Pattern */}
      {isCable && (
        <g opacity={0.45}>
          {Array.from({ length: 18 }, (_, idx) => (
            <rect
              key={idx}
              x={10 + idx * 11}
              y={4}
              width={5}
              height={deviceHeightPx - 8}
              rx={1}
              fill="#1E1F29"
            />
          ))}
        </g>
      )}

      {/* Shelf Bottom Ledge */}
      {isShelf && (
        <line
          x1={4}
          y1={deviceHeightPx - 4}
          x2={interiorWidth - 4}
          y2={deviceHeightPx - 4}
          stroke="#F8F8F2"
          strokeWidth={2}
          strokeDasharray="6 3"
          opacity={0.6}
        />
      )}

      {/* Left Grip + Live Status LED (if active device) */}
      {!isBlank && !isCable && !isShelf && (
        <circle
          cx={10}
          cy={Math.min(13, deviceHeightPx / 2)}
          r={3.5}
          fill={statusColor}
          stroke="#0f172a"
          strokeWidth={1}
        />
      )}

      {/* Device Name Label */}
      <text
        x={!isBlank && !isCable && !isShelf ? 19 : 10}
        y={uH === 1 ? deviceHeightPx / 2 + 4 : 15}
        fill="#F8F8F2"
        fontSize={10.5}
        fontWeight="700"
        fontFamily="Inter, system-ui, sans-serif"
        style={{
          userSelect: 'none',
          paintOrder: 'stroke',
          stroke: 'rgba(15, 23, 42, 0.78)',
          strokeWidth: '2.5px',
          strokeLinecap: 'round',
          strokeLinejoin: 'round',
        }}
      >
        {String(item.name || 'Device').slice(0, item.ip ? 21 : 28)}
      </text>

      {/* Secondary Subtitle for 2U+ or IP badge */}
      {item.ip && (
        <g transform={`translate(${interiorWidth - 82}, ${uH === 1 ? 4 : 4})`}>
          <rect
            x={0}
            y={0}
            width={56}
            height={14}
            rx={3}
            fill="rgba(15, 23, 42, 0.78)"
            stroke="rgba(56, 189, 248, 0.45)"
            strokeWidth={0.8}
          />
          <text
            x={28}
            y={10}
            textAnchor="middle"
            fill="#38bdf8"
            fontSize={8.2}
            fontWeight="700"
            fontFamily="JetBrains Mono, monospace"
          >
            {item.ip}
          </text>
        </g>
      )}

      {/* U-Height Pill on Far Right */}
      <g transform={`translate(${interiorWidth - 23}, 4)`}>
        <rect
          x={0}
          y={0}
          width={19}
          height={14}
          rx={3}
          fill="rgba(15, 23, 42, 0.65)"
        />
        <text
          x={9.5}
          y={10}
          textAnchor="middle"
          fill="#CBD5E1"
          fontSize={8.5}
          fontWeight="700"
          fontFamily="JetBrains Mono, monospace"
        >
          {uH}U
        </text>
      </g>

      {/* PortIndicators SVG (Ported from Rackula PortIndicators.svelte) */}
      {portCount > 0 && (
        <g
          transform={`translate(${uH === 1 ? 128 : 18}, ${
            uH === 1 ? deviceHeightPx - 9 : deviceHeightPx - 12
          })`}
        >
          {Array.from({ length: Math.min(portCount, uH === 1 ? 12 : 24) }, (_, idx) => {
            const iface = templateInterfaces[idx];
            const hasLiveOpenPort = openPorts.length > 0 && idx < openPorts.length;
            const portColor = hasLiveOpenPort
              ? '#50FA7B'
              : iface?.type
              ? PORT_COLOURS[iface.type] || '#10B981'
              : '#10B981';
            return (
              <rect
                key={idx}
                x={idx * 5.2}
                y={0}
                width={3.8}
                height={4.5}
                rx={0.8}
                fill={portColor}
                stroke="#090D16"
                strokeWidth={0.5}
                opacity={0.9}
              />
            );
          })}
        </g>
      )}

      {/* PDU Outlets Visual */}
      {isPduOrUps && uH === 1 && (
        <g transform={`translate(115, ${deviceHeightPx / 2 - 4})`}>
          {Array.from({ length: 8 }, (_, idx) => (
            <rect
              key={idx}
              x={idx * 9}
              y={0}
              width={6}
              height={8}
              rx={1}
              fill="#1E1F29"
              stroke="#FFB86C"
              strokeWidth={0.7}
            />
          ))}
        </g>
      )}
    </g>
  );
}

/**
 * Ported from Rackula's RackFrame.svelte & ULabels.svelte
 * Renders a single 19-inch EIA-310 Rack Face (Front or Rear)
 */
function SingleRackElevationSVG({
  rack,
  face = 'front',
  rackHeight = 42,
  mountedItems = [],
  selectedItemId,
  pendingMoveItemId,
  onSelectItem,
  isAdmin,
  dragCandidate,
  onDropAtUSlot,
  onClickUSlot,
  onDragStartMountedDevice,
}) {
  const [hoveredU, setHoveredU] = useState(null);
  const { rackWidth, railWidth, interiorWidth, uHeightPx, rackPadding } = RACK_SVG_METRICS;

  const totalHeightPx = rackHeight * uHeightPx;
  const svgWidth = rackWidth;
  const svgHeight = totalHeightPx + rackPadding * 2;

  // Filter items mounted on this face (or 'both')
  const faceItems = useMemo(
    () =>
      mountedItems.filter((item) => {
        const f = item.rackFace || item.face || 'front';
        return f === face || f === 'both';
      }),
    [mountedItems, face]
  );

  // Compute blocked slots on this face caused by full-depth devices on the opposite face
  const blockedSlots = useMemo(
    () => computeBlockedSlots(mountedItems, face),
    [mountedItems, face]
  );

  // Evaluate drag or hover preview validity
  const previewEval = useMemo(() => {
    if (!hoveredU) return null;
    const candidateH = dragCandidate ? Math.max(1, Number(dragCandidate.uHeight || 1)) : 1;
    const candidateFullDepth =
      dragCandidate?.isFullDepth !== undefined ? Boolean(dragCandidate.isFullDepth) : true;
    const excludeId = dragCandidate?.excludeId || null;

    // Check if device height extends beyond rack top
    if (hoveredU + candidateH - 1 > rackHeight) {
      return {
        uPosition: hoveredU,
        uHeight: candidateH,
        valid: false,
        reason: `อุปกรณ์ขนาด ${candidateH}U ที่ตำแหน่ง U${hoveredU} เกินความสูงตู้ ${rackHeight}U`,
      };
    }

    const check = canMountInRack({
      rackHeight,
      uPosition: hoveredU,
      uHeight: candidateH,
      face,
      isFullDepth: candidateFullDepth,
      mountedItems,
      excludeId,
    });
    return {
      uPosition: hoveredU,
      uHeight: candidateH,
      valid: check.valid,
      reason: check.reason,
    };
  }, [hoveredU, dragCandidate, rackHeight, face, mountedItems]);

  const patternId = `rackula-blocked-hatch-${face}`;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      {/* Face Header Pill */}
      <div
        style={{
          marginBottom: 8,
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '4px 14px',
          borderRadius: 999,
          background: face === 'front' ? 'rgba(189, 147, 249, 0.16)' : 'rgba(56, 189, 248, 0.14)',
          border:
            face === 'front'
              ? '1px solid rgba(189, 147, 249, 0.45)'
              : '1px solid rgba(56, 189, 248, 0.4)',
          color: face === 'front' ? '#E2D4F0' : '#BAE6FD',
          fontSize: 12,
          fontWeight: 700,
          letterSpacing: '0.04em',
        }}
      >
        <span>{face === 'front' ? '🟦 FRONT ELEVATION (ด้านหน้าตู้)' : '🟧 REAR ELEVATION (ด้านหลังตู้)'}</span>
        <span style={{ opacity: 0.75, fontSize: 11 }}>({faceItems.length} ชิ้น)</span>
      </div>

      <svg
        width={svgWidth}
        height={svgHeight}
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        className="rackula-elevation-svg"
        style={{
          background: '#191A22',
          borderRadius: 10,
          border: pendingMoveItemId ? '2px dashed #50FA7B' : '1px solid #44475A',
          boxShadow: '0 12px 30px rgba(0,0,0,0.55)',
          userSelect: 'none',
          touchAction: 'none',
        }}
        onClick={() => {
          // Clicking empty rack canvas clears selection
          onSelectItem(null);
        }}
        onMouseLeave={() => setHoveredU(null)}
      >
        <defs>
          {/* Rackula 45-degree Crosshatch Pattern for Blocked Slots */}
          <pattern
            id={patternId}
            width="8"
            height="8"
            patternTransform="rotate(45 0 0)"
            patternUnits="userSpaceOnUse"
          >
            <rect width="8" height="8" fill="rgba(30, 31, 41, 0.72)" />
            <line x1="0" y1="0" x2="0" y2="8" stroke="#6272A4" strokeWidth="2.2" strokeOpacity="0.55" />
          </pattern>
        </defs>

        {/* Top & Bottom Cabinet Bezel Bars */}
        <rect x={0} y={0} width={svgWidth} height={rackPadding} fill="#282A36" />
        <text
          x={svgWidth / 2}
          y={15}
          textAnchor="middle"
          fill="#BD93F9"
          fontSize={10}
          fontWeight="700"
          fontFamily="JetBrains Mono, monospace"
        >
          {rack.name} • {rackHeight}U ({face.toUpperCase()})
        </text>

        <rect
          x={0}
          y={rackPadding + totalHeightPx}
          width={svgWidth}
          height={rackPadding}
          fill="#282A36"
        />
        <text
          x={svgWidth / 2}
          y={rackPadding + totalHeightPx + 14}
          textAnchor="middle"
          fill="#6272A4"
          fontSize={9.5}
          fontFamily="JetBrains Mono, monospace"
        >
          EIA-310 19&quot; STANDARD CABINET
        </text>

        {/* Main Rack Coordinate Space */}
        <g transform={`translate(0, ${rackPadding})`}>
          {/* Rack Interior Background */}
          <rect
            x={railWidth}
            y={0}
            width={interiorWidth}
            height={totalHeightPx}
            fill="#14151B"
          />

          {/* Left & Right Mounting Rails */}
          <rect x={0} y={0} width={railWidth} height={totalHeightPx} fill="#282A36" />
          <rect
            x={rackWidth - railWidth}
            y={0}
            width={railWidth}
            height={totalHeightPx}
            fill="#282A36"
          />

          {/* U-Slot Rows (U1 at bottom -> U_rackHeight at top) */}
          {Array.from({ length: rackHeight }, (_, idx) => {
            const uNumber = rackHeight - idx;
            const rowY = idx * uHeightPx;
            const isEven = uNumber % 2 === 0;

            return (
              <g
                key={uNumber}
                transform={`translate(0, ${rowY})`}
                onDragOver={(e) => {
                  if (!isAdmin) return;
                  e.preventDefault();
                  if (hoveredU !== uNumber) setHoveredU(uNumber);
                }}
                onDrop={(e) => {
                  if (!isAdmin) return;
                  e.preventDefault();
                  setHoveredU(null);
                  onDropAtUSlot?.(uNumber, face, e);
                }}
                onMouseEnter={() => {
                  if (isAdmin && dragCandidate) setHoveredU(uNumber);
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  if (isAdmin) onClickUSlot?.(uNumber, face);
                }}
                style={{ cursor: isAdmin ? 'pointer' : 'default' }}
              >
                {/* Interior U-Slot Band */}
                <rect
                  x={railWidth}
                  y={0}
                  width={interiorWidth}
                  height={uHeightPx}
                  fill={isEven ? 'rgba(68, 71, 90, 0.14)' : 'rgba(40, 42, 54, 0.06)'}
                  stroke="#282A36"
                  strokeWidth={0.7}
                />

                {/* Left Rail U-Number + 3 EIA Cage Nut Holes */}
                <text
                  x={10}
                  y={uHeightPx / 2 + 3.5}
                  textAnchor="middle"
                  fill={hoveredU === uNumber ? '#50FA7B' : '#8BE9FD'}
                  fontSize={8.5}
                  fontWeight="700"
                  fontFamily="JetBrains Mono, monospace"
                >
                  {uNumber}
                </text>
                {[4, 11.5, 19].map((hy, hIdx) => (
                  <rect
                    key={hIdx}
                    x={railWidth - 4}
                    y={hy}
                    width={2.5}
                    height={2.5}
                    fill="#14151B"
                    stroke="#6272A4"
                    strokeWidth={0.4}
                  />
                ))}

                {/* Right Rail U-Number + 3 EIA Cage Nut Holes */}
                <text
                  x={rackWidth - 9.5}
                  y={uHeightPx / 2 + 3.5}
                  textAnchor="middle"
                  fill={hoveredU === uNumber ? '#50FA7B' : '#6272A4'}
                  fontSize={8.5}
                  fontWeight="700"
                  fontFamily="JetBrains Mono, monospace"
                >
                  {uNumber}
                </text>
                {[4, 11.5, 19].map((hy, hIdx) => (
                  <rect
                    key={hIdx}
                    x={rackWidth - railWidth + 1.5}
                    y={hy}
                    width={2.5}
                    height={2.5}
                    fill="#14151B"
                    stroke="#6272A4"
                    strokeWidth={0.4}
                  />
                ))}
              </g>
            );
          })}

          {/* Blocked Slots Overlay (Full-Depth Devices Mounted on Opposite Face) */}
          {blockedSlots.map((b, idx) => {
            const spanU = b.top - b.bottom + 1;
            const blockY = (rackHeight - b.top) * uHeightPx;
            const blockH = spanU * uHeightPx;
            return (
              <g
                key={`blocked-${idx}`}
                transform={`translate(${railWidth}, ${blockY})`}
                style={{ pointerEvents: 'none' }}
              >
                <rect
                  x={1}
                  y={1}
                  width={interiorWidth - 2}
                  height={blockH - 2}
                  rx={3}
                  fill={`url(#${patternId})`}
                  stroke="#6272A4"
                  strokeWidth={1}
                  strokeDasharray="4 2"
                />
                <text
                  x={interiorWidth / 2}
                  y={blockH / 2 + 3.5}
                  textAnchor="middle"
                  fill="#94A3B8"
                  fontSize={9}
                  fontWeight="600"
                  fontFamily="Inter, system-ui, sans-serif"
                >
                  🔒 Full-Depth ({b.otherFace.toUpperCase()}): {String(b.deviceName).slice(0, 18)}
                </text>
              </g>
            );
          })}

          {/* Mounted Devices on this Face */}
          {faceItems.map((item) => (
            <RackDeviceSVG
              key={item.id}
              item={item}
              rackHeight={rackHeight}
              uHeightPx={uHeightPx}
              rackWidth={rackWidth}
              railWidth={railWidth}
              isSelected={selectedItemId === item.id}
              isPendingMove={pendingMoveItemId === item.id}
              isAdmin={isAdmin}
              onSelect={onSelectItem}
              onDragStartDevice={onDragStartMountedDevice}
            />
          ))}

          {/* Live Drag / Hover Slot Placement Preview */}
          {isAdmin && previewEval && (
            <g
              transform={`translate(${railWidth}, ${
                (rackHeight - previewEval.uPosition - previewEval.uHeight + 1) * uHeightPx
              })`}
              style={{ pointerEvents: 'none' }}
            >
              <rect
                x={1}
                y={1}
                width={interiorWidth - 2}
                height={previewEval.uHeight * uHeightPx - 2}
                rx={3}
                fill={
                  previewEval.valid
                    ? 'rgba(80, 250, 123, 0.22)'
                    : 'rgba(255, 85, 85, 0.26)'
                }
                stroke={previewEval.valid ? '#50FA7B' : '#FF5555'}
                strokeWidth={2}
                strokeDasharray="5 3"
              />
              <text
                x={interiorWidth / 2}
                y={(previewEval.uHeight * uHeightPx) / 2 + 4}
                textAnchor="middle"
                fill={previewEval.valid ? '#50FA7B' : '#FF5555'}
                fontSize={9.5}
                fontWeight="700"
                fontFamily="JetBrains Mono, monospace"
              >
                {previewEval.valid
                  ? `+ วางที่ช่อง U${previewEval.uPosition}${
                      previewEval.uHeight > 1
                        ? `–U${previewEval.uPosition + previewEval.uHeight - 1}`
                        : ''
                    } (${previewEval.uHeight}U)`
                  : `❌ ช่อง U${previewEval.uPosition} ติดตั้งไม่ได้`}
              </text>
            </g>
          )}
        </g>
      </svg>
    </div>
  );
}

/**
 * Main Rackula 19-Inch Rack Elevation Designer & Interactive Hardware Manager Modal
 */
export default function RackulaModal({
  open,
  rack,
  allDevices = [],
  rooms = [],
  isAdmin = false,
  adminToken = '',
  onClose,
  onRefreshState,
  onInspectMountedDevice,
  onStartMove3DRack,
  onUnplace3DRack,
  toast,
}) {
  const [viewMode, setViewMode] = useState('dual'); // 'dual' | 'front' | 'rear'
  const [paletteTab, setPaletteTab] = useState('scanned'); // 'scanned' | 'library'
  const [libCategory, setLibCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItemId, setSelectedItemId] = useState(null);
  const [pendingMoveItem, setPendingMoveItem] = useState(null); // Item queued for Tap-to-Move
  const [targetMountFace, setTargetMountFace] = useState('front');
  const [targetMountU, setTargetMountU] = useState('');
  const [dragCandidate, setDragCandidate] = useState(null);
  const [busy, setBusy] = useState(false);
  const [pingingId, setPingingId] = useState(null);
  const [scanningPortsId, setScanningPortsId] = useState(null);
  const [editIpInput, setEditIpInput] = useState('');
  const [editNameInput, setEditNameInput] = useState('');
  const [renamingRack, setRenamingRack] = useState(false);
  const [rackNameInput, setRackNameInput] = useState('');
  const [isUnmountHovered, setIsUnmountHovered] = useState(false);

  const svgExportContainerRef = useRef(null);

  const rackId = rack?.id || '';
  const rackRoomId = rack?.roomId || '';
  const rackHeight = Math.max(1, Number(rack?.rackConfig?.rackHeight || 42));

  // All devices mounted inside this rack
  const mountedItems = useMemo(
    () =>
      rackId
        ? allDevices
            .filter(
              (d) =>
                d.parentRackId === rackId &&
                d.uPosition !== null &&
                d.uPosition !== undefined &&
                Number(d.uPosition) >= 1
            )
            .sort((a, b) => Number(b.uPosition) - Number(a.uPosition))
        : [],
    [allDevices, rackId]
  );

  const selectedItem = useMemo(
    () => mountedItems.find((d) => d.id === selectedItemId) || null,
    [mountedItems, selectedItemId]
  );

  React.useEffect(() => {
    setEditIpInput(selectedItem?.ip || '');
    setEditNameInput(selectedItem?.name || '');
  }, [selectedItem?.id, selectedItem?.ip, selectedItem?.name]);

  // Scanned / Available Network Devices that can be mounted into this rack
  const mountableNetworkDevices = useMemo(() => {
    if (!rackId) return [];
    const q = searchQuery.trim().toLowerCase();
    return allDevices
      .filter((d) => {
        if (d.id === rackId) return false;
        if (d.modelType === 'server_rack') return false;
        if (d.parentRackId === rackId) return false;
        if (!q) return true;
        return (
          String(d.name || '').toLowerCase().includes(q) ||
          String(d.ip || '').toLowerCase().includes(q) ||
          String(d.mac || '').toLowerCase().includes(q) ||
          String(d.category || '').toLowerCase().includes(q) ||
          String(d.vendor || '').toLowerCase().includes(q)
        );
      })
      .sort((a, b) => {
        // Prioritize unplaced devices or devices in the same room
        const aSameRoom = a.roomId && a.roomId === rackRoomId ? 1 : 0;
        const bSameRoom = b.roomId && b.roomId === rackRoomId ? 1 : 0;
        if (aSameRoom !== bSameRoom) return bSameRoom - aSameRoom;
        const aUnplaced = !a.isPlaced ? 1 : 0;
        const bUnplaced = !b.isPlaced ? 1 : 0;
        return bUnplaced - aUnplaced;
      });
  }, [allDevices, rackId, rackRoomId, searchQuery]);

  // Filtered Rackula Starter Library templates
  const filteredStarterLibrary = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return RACKULA_STARTER_LIBRARY.filter((tpl) => {
      if (libCategory !== 'all' && tpl.category !== libCategory) return false;
      if (!q) return true;
      return (
        tpl.model.toLowerCase().includes(q) ||
        tpl.manufacturer.toLowerCase().includes(q) ||
        tpl.slug.toLowerCase().includes(q) ||
        tpl.category.toLowerCase().includes(q)
      );
    });
  }, [libCategory, searchQuery]);

  // Rack telemetry summary
  const rackStats = useMemo(() => {
    const occupiedUSet = new Set();
    let totalWatts = 0;
    let onlineCount = 0;
    let offlineCount = 0;

    for (const item of mountedItems) {
      const range = getDeviceURange(item.uPosition, item.uHeight || 1);
      for (let u = range.bottom; u <= range.top; u++) occupiedUSet.add(u);
      totalWatts += Number(item.rackConfig?.powerWatts || 120);
      if (String(item.status || 'Online').toLowerCase() === 'offline') offlineCount++;
      else onlineCount++;
    }

    const usedU = occupiedUSet.size;
    const utilizationPct = Math.min(100, Math.round((usedU / rackHeight) * 100));

    return {
      usedU,
      freeU: Math.max(0, rackHeight - usedU),
      utilizationPct,
      totalWatts,
      onlineCount,
      offlineCount,
    };
  }, [mountedItems, rackHeight]);

  // Listen for Escape key to clear selection or drag state
  React.useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape') {
        setSelectedItemId(null);
        setDragCandidate(null);
        setPendingMoveItem(null);
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (!open || !rack) return null;

  // API helper for mounting
  async function handleMountPayload(payload) {
    if (!isAdmin) return;
    setBusy(true);
    try {
      const res = await fetch(`/api/admin/racks/${rack.id}/mount`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        toast?.({
          title: 'ไม่สามารถติดตั้งลงช่อง U นี้ได้',
          description: data.error || 'เกิดข้อผิดพลาดในการตรวจสอบช่อง U',
          variant: 'destructive',
        });
        return null;
      }
      if (data.device?.id) {
        setSelectedItemId(data.device.id);
      }
      await onRefreshState?.();
      toast?.({
        title: 'ติดตั้งอุปกรณ์ในตู้แร็คสำเร็จ',
        description: `ติดตั้ง "${data.device?.name}" ที่ช่อง U${data.device?.uPosition} (${String(
          data.device?.rackFace || 'front'
        ).toUpperCase()})`,
        variant: 'success',
      });
      return data.device;
    } catch (err) {
      toast?.({
        title: 'เกิดข้อผิดพลาด',
        description: err.message,
        variant: 'destructive',
      });
      return null;
    } finally {
      setBusy(false);
      setDragCandidate(null);
    }
  }

  async function handleUnmountItem(item) {
    if (!isAdmin || !item) return;
    setBusy(true);
    try {
      const res = await fetch(`/api/admin/racks/${rack.id}/unmount`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify({ itemId: item.id }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        toast?.({
          title: 'ถอดอุปกรณ์ไม่สำเร็จ',
          description: data.error || 'Error unmounting device',
          variant: 'destructive',
        });
        return;
      }
      setSelectedItemId(null);
      await onRefreshState?.();
      toast?.({
        title: 'ถอดอุปกรณ์ออกจากช่อง U แล้ว',
        description: `"${item.name}" ถูกถอดออกจากตู้แร็คแล้ว`,
      });
    } catch (err) {
      toast?.({
        title: 'เกิดข้อผิดพลาด',
        description: err.message,
        variant: 'destructive',
      });
    } finally {
      setBusy(false);
    }
  }

  async function handleRenameRack() {
    const nextName = rackNameInput.trim();
    if (!isAdmin || !nextName || nextName === rack.name) {
      setRenamingRack(false);
      return;
    }
    setBusy(true);
    try {
      const res = await fetch(`/api/admin/racks/${rack.id}/config`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify({ name: nextName }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        toast?.({ title: 'เปลี่ยนชื่อตู้ไม่สำเร็จ', description: data.error, variant: 'destructive' });
        return;
      }
      await onRefreshState?.();
      toast?.({ title: `เปลี่ยนชื่อตู้เป็น "${nextName}" แล้ว` });
      setRenamingRack(false);
    } finally {
      setBusy(false);
    }
  }

  async function handleUpdateRackHeight(newHeight) {
    if (!isAdmin) return;
    setBusy(true);
    try {
      const res = await fetch(`/api/admin/racks/${rack.id}/config`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify({ rackHeight: Number(newHeight) }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        toast?.({
          title: 'เปลี่ยนขนาดตู้แร็คไม่สำเร็จ',
          description: data.error,
          variant: 'destructive',
        });
        return;
      }
      await onRefreshState?.();
      toast?.({
        title: `อัปเดตขนาดตู้แร็คเป็น ${newHeight}U สำเร็จ`,
      });
    } finally {
      setBusy(false);
    }
  }

  function handleExportRackulaYaml() {
    const yamlStr = serializeToRackulaYaml(rack, mountedItems);
    const blob = new Blob([yamlStr], { type: 'text/yaml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${String(rack.name || 'server-rack').replace(/\s+/g, '_')}_rackula.yaml`;
    a.click();
    URL.revokeObjectURL(url);
    toast?.({
      title: 'ดาวน์โหลดไฟล์ Rackula YAML (.yaml) สำเร็จ',
      description: 'สามารถนำไปใช้กับ Rackula หรือ NetBox ได้ทันที',
      variant: 'success',
    });
  }

  function handleExportRackSvg() {
    const svgEl = svgExportContainerRef.current?.querySelector('svg.rackula-elevation-svg');
    if (!svgEl) return;
    const serializer = new XMLSerializer();
    let source = serializer.serializeToString(svgEl);
    if (!source.match(/^<svg[^>]+xmlns="http:\/\/www\.w3\.org\/2000\/svg"/)) {
      source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
    }
    const blob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${String(rack.name || 'server-rack').replace(/\s+/g, '_')}_elevation.svg`;
    a.click();
    URL.revokeObjectURL(url);
    toast?.({
      title: 'ส่งออกแผนผังตู้แร็ค SVG สำเร็จ',
      variant: 'success',
    });
  }

  // (1) Open Web Login directly in a new browser tab
  function handleOpenWebLoginNewTab(item, forcedProto = null, forcedPort = null) {
    if (!item?.ip) {
      toast?.({
        title: 'ยังไม่ได้ระบุ IP Address',
        description: 'กรุณากรอก IP Address ของอุปกรณ์ในช่องด้านล่างก่อนเปิดหน้า Web Login',
        variant: 'destructive',
      });
      return;
    }

    if (!forcedProto && !forcedPort && item.credentials?.loginUrl) {
      window.open(item.credentials.loginUrl, '_blank', 'noopener');
      return;
    }

    const ports = Array.isArray(item.openPorts) ? item.openPorts : [];
    const portNums = new Set(ports.map((p) => Number(typeof p === 'object' ? p.port : p)));
    let proto = forcedProto;
    let port = forcedPort;

    if (!proto || !port) {
      if (portNums.has(443)) {
        proto = 'https';
        port = 443;
      } else if (portNums.has(80)) {
        proto = 'http';
        port = 80;
      } else if (portNums.has(8443)) {
        proto = 'https';
        port = 8443;
      } else if (portNums.has(8006)) {
        proto = 'https';
        port = 8006;
      } else if (portNums.has(8080)) {
        proto = 'http';
        port = 8080;
      } else {
        proto = 'http';
        port = 80;
      }
    }

    const targetUrl = `${proto}://${item.ip}:${port}`;
    window.open(targetUrl, '_blank', 'noopener');
  }

  // (2) Live Ping & Port Scan directly inside Rackula Right Panel
  async function handleLivePingSelected(item) {
    if (!item?.ip) {
      toast?.({
        title: 'ไม่มี IP Address สำหรับ Ping',
        description: 'กรุณาระบุ IP Address ของอุปกรณ์ก่อนทดสอบสัญญาณ',
        variant: 'destructive',
      });
      return;
    }
    setPingingId(item.id);
    try {
      const res = await fetch(`/api/devices/${encodeURIComponent(item.id)}/ping`, {
        method: 'POST',
      });
      const data = await res.json();
      if (res.ok && data.device) {
        await onRefreshState?.();
        toast?.({
          title: data.ping?.alive ? '⚡ อุปกรณ์ออนไลน์ (Ping ตอบกลับ)' : '⚠️ อุปกรณ์ไม่ตอบสนอง (Offline)',
          description: `${item.ip} • Latency: ${data.ping?.latencyMs ?? '-'} ms`,
          variant: data.ping?.alive ? 'success' : 'destructive',
        });
      } else {
        throw new Error(data.error || 'Ping failed');
      }
    } catch (err) {
      toast?.({
        title: 'Ping ทดสอบสัญญาณไม่สำเร็จ',
        description: err.message,
        variant: 'destructive',
      });
    } finally {
      setPingingId(null);
    }
  }

  async function handleLiveScanPortsSelected(item) {
    if (!item?.ip) {
      toast?.({
        title: 'ไม่มี IP Address สำหรับสแกนพอร์ต',
        description: 'กรุณาระบุ IP Address ของอุปกรณ์ก่อนสแกนพอร์ต',
        variant: 'destructive',
      });
      return;
    }
    setScanningPortsId(item.id);
    toast?.({
      title: `📡 กำลังสแกนพอร์ตมาตรฐาน (48 พอร์ต)...`,
      description: `เป้าหมาย: ${item.name} (${item.ip})`,
    });
    try {
      const res = await fetch(`/api/devices/${encodeURIComponent(item.id)}/scan-ports`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: 'fast' }),
      });
      const data = await res.json();
      if (res.ok && data.device) {
        await onRefreshState?.();
        toast?.({
          title: '✅ สแกนพอร์ตเสร็จสมบูรณ์',
          description: `พบพอร์ตเปิดใช้งาน ${(data.device.openPorts || []).length} พอร์ต บน ${item.ip}`,
          variant: 'success',
        });
      } else {
        throw new Error(data.error || 'Port scan failed');
      }
    } catch (err) {
      toast?.({
        title: 'สแกนพอร์ตไม่สำเร็จ',
        description: err.message,
        variant: 'destructive',
      });
    } finally {
      setScanningPortsId(null);
    }
  }

  // (3) Open Deep Device Dashboard in a NEW Browser Tab (no overlapping modals!)
  function handleOpenDeviceDashboardNewTab(item) {
    if (!item?.id) return;
    const basePath = window.location.pathname || '/';
    const url = `${basePath}?device=${encodeURIComponent(item.id)}`;
    window.open(url, '_blank', 'noopener');
  }

  return (
    <div
      className="modal-backdrop"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        background: 'rgba(6, 10, 19, 0.84)',
        backdropFilter: 'blur(10px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '18px',
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: 'min(1460px, 98vw)',
          height: 'min(910px, 94vh)',
          background: '#0F1420',
          border: '1px solid rgba(189, 147, 249, 0.35)',
          borderRadius: 16,
          boxShadow: '0 24px 70px rgba(0, 0, 0, 0.75)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          color: '#F8F8F2',
        }}
      >
        {/* ================= TOP HEADER BAR ================= */}
        <div
          style={{
            padding: '14px 20px',
            background: 'linear-gradient(90deg, #191A24 0%, #131B2E 100%)',
            borderBottom: '1px solid rgba(189, 147, 249, 0.25)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 12,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div
              style={{
                width: 42,
                height: 42,
                borderRadius: 10,
                background: 'rgba(189, 147, 249, 0.16)',
                border: '1px solid rgba(189, 147, 249, 0.45)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 22,
              }}
            >
              🗄️
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                {renamingRack ? (
                  <input
                    autoFocus
                    aria-label="Rack name"
                    value={rackNameInput}
                    disabled={busy}
                    onChange={(e) => setRackNameInput(e.target.value)}
                    onBlur={handleRenameRack}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleRenameRack();
                      if (e.key === 'Escape') setRenamingRack(false);
                    }}
                    style={{
                      fontSize: 17,
                      fontWeight: 800,
                      color: '#F8F8F2',
                      background: 'rgba(255,255,255,0.08)',
                      border: '1px solid rgba(189, 147, 249, 0.6)',
                      borderRadius: 8,
                      padding: '2px 8px',
                      minWidth: 180,
                    }}
                  />
                ) : (
                  <>
                    <span style={{ fontSize: 17, fontWeight: 800, color: '#F8F8F2' }}>
                      {rack.name}
                    </span>
                    {isAdmin && (
                      <button
                        type="button"
                        aria-label="Rename rack"
                        title="เปลี่ยนชื่อตู้"
                        onClick={() => {
                          setRackNameInput(rack.name || '');
                          setRenamingRack(true);
                        }}
                        style={{
                          background: 'transparent',
                          border: '1px solid rgba(189, 147, 249, 0.4)',
                          color: '#BD93F9',
                          borderRadius: 8,
                          padding: '1px 8px',
                          fontSize: 11,
                          cursor: 'pointer',
                        }}
                      >
                        ✎ แก้ชื่อ
                      </button>
                    )}
                  </>
                )}
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: 999,
                    background: 'rgba(189, 147, 249, 0.2)',
                    color: '#BD93F9',
                    border: '1px solid rgba(189, 147, 249, 0.4)',
                  }}
                >
                  RACKULA {rackHeight}U ELEVATION
                </span>
                {rack.roomNumber && (
                  <span
                    style={{
                      fontSize: 11,
                      padding: '2px 8px',
                      borderRadius: 999,
                      background: 'rgba(56, 189, 248, 0.15)',
                      color: '#38bdf8',
                    }}
                  >
                    📍 ห้อง {rack.roomNumber} (ชั้น {Number(rack.floorIdx ?? 0) + 1})
                  </span>
                )}
              </div>
              <div style={{ fontSize: 12, color: '#94A3B8', marginTop: 2 }}>
                ระบบจัดผังตู้แร็ค 19 นิ้ว มาตรฐาน EIA-310 • ใช้พื้นที่แล้ว{' '}
                <strong style={{ color: '#50FA7B' }}>
                  {rackStats.usedU}U / {rackHeight}U ({rackStats.utilizationPct}%)
                </strong>{' '}
                • อุปกรณ์ทั้งหมด <strong style={{ color: '#38bdf8' }}>{mountedItems.length} ชิ้น</strong> • พลังงานรวมประมาณ{' '}
                <strong style={{ color: '#FFB86C' }}>{rackStats.totalWatts} W</strong>
              </div>
            </div>
          </div>

          {/* Right Header Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            {/* View Mode Switcher */}
            <div
              style={{
                display: 'flex',
                background: '#090D16',
                padding: 3,
                borderRadius: 8,
                border: '1px solid #282A36',
              }}
            >
              {[
                { id: 'dual', label: 'คู่หน้า-หลัง (Dual)' },
                { id: 'front', label: 'เฉพาะด้านหน้า (Front)' },
                { id: 'rear', label: 'เฉพาะด้านหลัง (Rear)' },
              ].map((m) => (
                <button
                  key={m.id}
                  onClick={() => setViewMode(m.id)}
                  style={{
                    padding: '5px 10px',
                    fontSize: 11.5,
                    fontWeight: 700,
                    borderRadius: 6,
                    border: 'none',
                    cursor: 'pointer',
                    background: viewMode === m.id ? '#BD93F9' : 'transparent',
                    color: viewMode === m.id ? '#090D16' : '#94A3B8',
                  }}
                >
                  {m.label}
                </button>
              ))}
            </div>

            {/* Rack Height Selector (Admin) */}
            {isAdmin && (
              <select
                value={rackHeight}
                onChange={(e) => handleUpdateRackHeight(Number(e.target.value))}
                style={{
                  background: '#191A24',
                  color: '#F8F8F2',
                  border: '1px solid #44475A',
                  borderRadius: 8,
                  padding: '6px 10px',
                  fontSize: 12,
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
                title="ความสูงของตู้แร็ค (Rack Height U)"
              >
                {COMMON_RACK_HEIGHTS.map((h) => (
                  <option key={h} value={h}>
                    ขนาดตู้ {h}U
                  </option>
                ))}
              </select>
            )}

            <button
              onClick={handleExportRackulaYaml}
              style={{
                background: 'rgba(189, 147, 249, 0.14)',
                color: '#BD93F9',
                border: '1px solid rgba(189, 147, 249, 0.4)',
                borderRadius: 8,
                padding: '6px 11px',
                fontSize: 12,
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              📥 Export .YAML
            </button>

            <button
              onClick={handleExportRackSvg}
              style={{
                background: 'rgba(56, 189, 248, 0.14)',
                color: '#38bdf8',
                border: '1px solid rgba(56, 189, 248, 0.4)',
                borderRadius: 8,
                padding: '6px 11px',
                fontSize: 12,
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              🖼️ Export .SVG
            </button>

            {isAdmin && onStartMove3DRack && (
              <button
                onClick={() => {
                  onClose?.();
                  onStartMove3DRack(rack);
                }}
                style={{
                  background: 'rgba(245, 158, 11, 0.15)',
                  color: '#FBBF24',
                  border: '1px solid rgba(245, 158, 11, 0.4)',
                  borderRadius: 8,
                  padding: '6px 11px',
                  fontSize: 12,
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                ✥ ย้ายจุดวางตู้ 3D
              </button>
            )}

            <button
              onClick={onClose}
              style={{
                background: 'rgba(239, 68, 68, 0.16)',
                color: '#F87171',
                border: '1px solid rgba(239, 68, 68, 0.35)',
                borderRadius: 8,
                padding: '6px 12px',
                fontSize: 12,
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              ✕ ปิดหน้าต่าง
            </button>
          </div>
        </div>

        {/* ================= 3-COLUMN WORKSPACE ================= */}
        <div
          style={{
            flex: 1,
            display: 'grid',
            gridTemplateColumns: isAdmin ? '340px 1fr 350px' : '1fr 370px',
            overflow: 'hidden',
          }}
        >
          {/* -------- LEFT COLUMN: HARDWARE & SCANNED DEVICE PALETTE (ADMIN) -------- */}
          {isAdmin && (
            <div
              onDragOver={(e) => {
                if (dragCandidate?.source === 'rack') {
                  e.preventDefault();
                  e.dataTransfer.dropEffect = 'move';
                  if (!isUnmountHovered) setIsUnmountHovered(true);
                }
              }}
              onDragLeave={() => {
                if (isUnmountHovered) setIsUnmountHovered(false);
              }}
              onDrop={(e) => {
                if (dragCandidate?.source === 'rack' && dragCandidate.item) {
                  e.preventDefault();
                  setIsUnmountHovered(false);
                  handleUnmountItem(dragCandidate.item);
                }
              }}
              style={{
                borderRight: '1px solid #282A36',
                background: '#121623',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
                position: 'relative',
              }}
            >
              {/* Highlight Drop Zone to Unmount Mounted Devices */}
              {dragCandidate?.source === 'rack' && (
                <div
                  style={{
                    padding: '12px 14px',
                    margin: '8px 10px',
                    borderRadius: 10,
                    border: isUnmountHovered
                      ? '2px dashed #FF5555'
                      : '2px dashed #FFB86C',
                    background: isUnmountHovered
                      ? 'rgba(255, 85, 85, 0.25)'
                      : 'rgba(255, 184, 108, 0.16)',
                    color: isUnmountHovered ? '#FF5555' : '#FFB86C',
                    textAlign: 'center',
                    fontSize: 12,
                    fontWeight: 800,
                    boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
                    transition: 'all 0.15s ease',
                    userSelect: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 8,
                  }}
                >
                  <span style={{ fontSize: 16 }}>📥</span>
                  <span>
                    {isUnmountHovered
                      ? `ปล่อยเพื่อถอด "${dragCandidate.item?.name}" ออกจากตู้ทันที`
                      : `ลากมาปล่อยที่นี่เพื่อถอดอุปกรณ์ออกจากตู้ (Unmount)`}
                  </span>
                </div>
              )}

              {/* Palette Tabs */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  padding: 10,
                  gap: 6,
                  borderBottom: '1px solid #282A36',
                }}
              >
                <button
                  onClick={() => setPaletteTab('scanned')}
                  style={{
                    padding: '8px 10px',
                    borderRadius: 8,
                    border:
                      paletteTab === 'scanned'
                        ? '1px solid #38bdf8'
                        : '1px solid rgba(255,255,255,0.08)',
                    background:
                      paletteTab === 'scanned'
                        ? 'rgba(56, 189, 248, 0.16)'
                        : 'rgba(15, 23, 42, 0.6)',
                    color: paletteTab === 'scanned' ? '#38bdf8' : '#94A3B8',
                    fontSize: 12,
                    fontWeight: 700,
                    cursor: 'pointer',
                  }}
                >
                  📡 อุปกรณ์ในระบบ ({mountableNetworkDevices.length})
                </button>
                <button
                  onClick={() => setPaletteTab('library')}
                  style={{
                    padding: '8px 10px',
                    borderRadius: 8,
                    border:
                      paletteTab === 'library'
                        ? '1px solid #BD93F9'
                        : '1px solid rgba(255,255,255,0.08)',
                    background:
                      paletteTab === 'library'
                        ? 'rgba(189, 147, 249, 0.16)'
                        : 'rgba(15, 23, 42, 0.6)',
                    color: paletteTab === 'library' ? '#BD93F9' : '#94A3B8',
                    fontSize: 12,
                    fontWeight: 700,
                    cursor: 'pointer',
                  }}
                >
                  🧰 คลัง Rackula ({RACKULA_STARTER_LIBRARY.length})
                </button>
              </div>

              {/* Search & Target Slot Bar */}
              <div
                style={{
                  padding: '10px 12px',
                  borderBottom: '1px solid #282A36',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 8,
                }}
              >
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={
                    paletteTab === 'scanned'
                      ? 'ค้นหาชื่ออุปกรณ์, IP, MAC, ประเภท...'
                      : 'ค้นหา Server, Switch, Patch Panel, UPS...'
                  }
                  style={{
                    width: '100%',
                    padding: '7px 10px',
                    borderRadius: 8,
                    border: '1px solid #334155',
                    background: '#090D16',
                    color: '#F8F8F2',
                    fontSize: 12,
                  }}
                />

                {/* Target U-Slot & Face Selector for 1-Click Mount */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    fontSize: 11.5,
                    color: '#CBD5E1',
                  }}
                >
                  <span>เป้าหมาย:</span>
                  <select
                    value={targetMountFace}
                    onChange={(e) => setTargetMountFace(e.target.value)}
                    style={{
                      background: '#090D16',
                      color: '#F8F8F2',
                      border: '1px solid #334155',
                      borderRadius: 6,
                      padding: '4px 6px',
                      fontSize: 11.5,
                    }}
                  >
                    <option value="front">ด้านหน้า (Front)</option>
                    <option value="rear">ด้านหลัง (Rear)</option>
                  </select>
                  <input
                    type="number"
                    min={1}
                    max={rackHeight}
                    value={targetMountU}
                    onChange={(e) => setTargetMountU(e.target.value)}
                    placeholder="Auto U"
                    style={{
                      width: 68,
                      background: '#090D16',
                      color: '#50FA7B',
                      border: '1px solid #334155',
                      borderRadius: 6,
                      padding: '4px 6px',
                      fontSize: 11.5,
                      fontWeight: 700,
                    }}
                  />
                  <span style={{ fontSize: 10.5, color: '#64748B' }}>
                    (ลากวางที่ช่อง U ได้เลย)
                  </span>
                </div>

                {/* Category Filter Pills for Starter Library */}
                {paletteTab === 'library' && (
                  <div
                    style={{
                      display: 'flex',
                      gap: 5,
                      overflowX: 'auto',
                      paddingBottom: 4,
                    }}
                  >
                    {RACKULA_CATEGORIES.map((cat) => (
                      <button
                        key={cat.id}
                        onClick={() => setLibCategory(cat.id)}
                        style={{
                          whiteSpace: 'nowrap',
                          padding: '3px 8px',
                          borderRadius: 999,
                          fontSize: 10.5,
                          fontWeight: 700,
                          border:
                            libCategory === cat.id
                              ? `1px solid ${cat.color}`
                              : '1px solid rgba(255,255,255,0.1)',
                          background:
                            libCategory === cat.id
                              ? 'rgba(189, 147, 249, 0.2)'
                              : 'rgba(15, 23, 42, 0.6)',
                          color: libCategory === cat.id ? '#F8F8F2' : '#94A3B8',
                          cursor: 'pointer',
                        }}
                      >
                        {cat.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Scrollable Palette Items List */}
              <div
                style={{
                  flex: 1,
                  overflowY: 'auto',
                  padding: 10,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 8,
                }}
              >
                {paletteTab === 'scanned' ? (
                  mountableNetworkDevices.length === 0 ? (
                    <div
                      style={{
                        padding: 20,
                        textAlign: 'center',
                        color: '#64748B',
                        fontSize: 12.5,
                      }}
                    >
                      ไม่พบอุปกรณ์เครือข่ายที่พร้อมติดตั้งเพิ่ม
                    </div>
                  ) : (
                    mountableNetworkDevices.map((dev) => {
                      const mapped = mapTwinCategoryToRackula(dev.category);
                      const defaultH = dev.uHeight || mapped.defaultUHeight || 1;
                      return (
                        <div
                          key={dev.id}
                          draggable
                          onDragStart={(e) => {
                            e.dataTransfer.setData(
                              'application/json',
                              JSON.stringify({
                                type: 'existing-device',
                                deviceId: dev.id,
                                uHeight: defaultH,
                                isFullDepth:
                                  dev.isFullDepth !== undefined
                                    ? dev.isFullDepth
                                    : mapped.isFullDepth,
                              })
                            );
                            setDragCandidate({
                              uHeight: defaultH,
                              isFullDepth:
                                dev.isFullDepth !== undefined
                                  ? dev.isFullDepth
                                  : mapped.isFullDepth,
                              excludeId: dev.id,
                            });
                          }}
                          onDragEnd={() => setDragCandidate(null)}
                          style={{
                            padding: '9px 11px',
                            borderRadius: 10,
                            background: '#181D2E',
                            border: '1px solid rgba(56, 189, 248, 0.22)',
                            borderLeft: `4px solid ${dev.color || mapped.colour}`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            gap: 8,
                            cursor: 'grab',
                          }}
                        >
                          <div style={{ minWidth: 0, flex: 1 }}>
                            <div
                              style={{
                                fontSize: 12.5,
                                fontWeight: 700,
                                color: '#F8F8F2',
                                whiteSpace: 'nowrap',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                              }}
                            >
                              {dev.name}
                            </div>
                            <div
                              style={{
                                fontSize: 11,
                                color: '#94A3B8',
                                display: 'flex',
                                alignItems: 'center',
                                gap: 6,
                                marginTop: 2,
                              }}
                            >
                              <span style={{ color: '#38bdf8', fontFamily: 'monospace' }}>
                                {dev.ip || 'No IP'}
                              </span>
                              <span>• {dev.category}</span>
                              <span>• {defaultH}U</span>
                              {!dev.isPlaced ? (
                                <span style={{ color: '#FBBF24' }}>• ในคิว</span>
                              ) : (
                                <span style={{ color: '#4ADE80' }}>
                                  • ห้อง {dev.roomNumber || '-'}
                                </span>
                              )}
                            </div>
                          </div>
                          <button
                            disabled={busy}
                            onClick={() =>
                              handleMountPayload({
                                deviceId: dev.id,
                                face: targetMountFace,
                                uPosition: targetMountU ? Number(targetMountU) : null,
                                uHeight: defaultH,
                              })
                            }
                            style={{
                              padding: '5px 9px',
                              borderRadius: 7,
                              border: '1px solid rgba(80, 250, 123, 0.45)',
                              background: 'rgba(80, 250, 123, 0.14)',
                              color: '#50FA7B',
                              fontSize: 11,
                              fontWeight: 700,
                              cursor: 'pointer',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            + ติดตั้ง
                          </button>
                        </div>
                      );
                    })
                  )
                ) : (
                  filteredStarterLibrary.map((tpl) => (
                    <div
                      key={tpl.slug}
                      draggable
                      onDragStart={(e) => {
                        e.dataTransfer.setData(
                          'application/json',
                          JSON.stringify({
                            type: 'starter-template',
                            templateSlug: tpl.slug,
                            uHeight: tpl.u_height,
                            isFullDepth: tpl.is_full_depth,
                          })
                        );
                        setDragCandidate({
                          uHeight: tpl.u_height,
                          isFullDepth: tpl.is_full_depth,
                        });
                      }}
                      onDragEnd={() => setDragCandidate(null)}
                      style={{
                        padding: '9px 11px',
                        borderRadius: 10,
                        background: '#181D2E',
                        border: '1px solid rgba(189, 147, 249, 0.22)',
                        borderLeft: `4px solid ${tpl.colour}`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: 8,
                        cursor: 'grab',
                      }}
                    >
                      <div style={{ minWidth: 0, flex: 1 }}>
                        <div
                          style={{
                            fontSize: 12.5,
                            fontWeight: 700,
                            color: '#F8F8F2',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}
                        >
                          {tpl.model}
                        </div>
                        <div
                          style={{
                            fontSize: 11,
                            color: '#94A3B8',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 6,
                            marginTop: 2,
                          }}
                        >
                          <span
                            style={{
                              padding: '1px 5px',
                              borderRadius: 4,
                              background: 'rgba(189, 147, 249, 0.2)',
                              color: '#BD93F9',
                              fontWeight: 700,
                            }}
                          >
                            {tpl.u_height}U
                          </span>
                          <span>{tpl.manufacturer}</span>
                          <span>
                            • {tpl.is_full_depth ? 'Full-Depth' : 'Half-Depth'}
                          </span>
                        </div>
                      </div>
                      <button
                        disabled={busy}
                        onClick={() =>
                          handleMountPayload({
                            templateSlug: tpl.slug,
                            face: targetMountFace,
                            uPosition: targetMountU ? Number(targetMountU) : null,
                          })
                        }
                        style={{
                          padding: '5px 9px',
                          borderRadius: 7,
                          border: '1px solid rgba(189, 147, 249, 0.45)',
                          background: 'rgba(189, 147, 249, 0.16)',
                          color: '#E2D4F0',
                          fontSize: 11,
                          fontWeight: 700,
                          cursor: 'pointer',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        + ใส่ตู้
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* -------- CENTER COLUMN: RACKULA INTERACTIVE SVG ELEVATION CANVAS -------- */}
          <div
            ref={svgExportContainerRef}
            style={{
              background:
                'radial-gradient(circle at 50% 25%, rgba(40, 42, 54, 0.65) 0%, #090D16 100%)',
              overflowY: 'auto',
              padding: '20px 24px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <div
              style={{
                display: 'flex',
                gap: 32,
                alignItems: 'flex-start',
                justifyContent: 'center',
                flexWrap: 'wrap',
              }}
            >
              {(viewMode === 'dual' || viewMode === 'front') && (
                <SingleRackElevationSVG
                  rack={rack}
                  face="front"
                  rackHeight={rackHeight}
                  mountedItems={mountedItems}
                  selectedItemId={selectedItemId}
                  pendingMoveItemId={pendingMoveItem?.id || null}
                  onSelectItem={(item) => {
                    setSelectedItemId(item ? item.id : null);
                    if (item && pendingMoveItem && pendingMoveItem.id !== item.id) {
                      setPendingMoveItem(null);
                    }
                  }}
                  isAdmin={isAdmin}
                  dragCandidate={dragCandidate}
                  onDragStartMountedDevice={(e, item) => {
                    const uH = Math.max(1, Number(item.uHeight || 1));
                    const isFullDepth = item.isFullDepth !== undefined ? Boolean(item.isFullDepth) : true;
                    setDragCandidate({
                      uHeight: uH,
                      isFullDepth,
                      excludeId: item.id,
                      source: 'rack',
                      item,
                    });
                  }}
                  onClickUSlot={(uNumber, face) => {
                    // Tap-to-Move handler: If an item is pending move, execute move to this slot
                    if (pendingMoveItem && isAdmin) {
                      const uH = Math.max(1, Number(pendingMoveItem.uHeight || 1));
                      const isFullDepth = pendingMoveItem.isFullDepth !== undefined ? Boolean(pendingMoveItem.isFullDepth) : true;
                      handleMountPayload({
                        deviceId: pendingMoveItem.id,
                        uPosition: uNumber,
                        face,
                        uHeight: uH,
                        isFullDepth,
                      });
                      setPendingMoveItem(null);
                      return;
                    }
                    setTargetMountU(String(uNumber));
                    setTargetMountFace(face);
                  }}
                  onDropAtUSlot={(uNumber, face, e) => {
                    try {
                      const raw = e.dataTransfer.getData('application/json');
                      if (!raw) return;
                      const parsed = JSON.parse(raw);
                      if (parsed.type === 'mounted-device' && parsed.deviceId) {
                        handleMountPayload({
                          deviceId: parsed.deviceId,
                          uPosition: uNumber,
                          face,
                          uHeight: parsed.uHeight,
                          isFullDepth: parsed.isFullDepth,
                        });
                      } else if (parsed.type === 'existing-device' && parsed.deviceId) {
                        handleMountPayload({
                          deviceId: parsed.deviceId,
                          uPosition: uNumber,
                          face,
                          uHeight: parsed.uHeight,
                        });
                      } else if (parsed.type === 'starter-template' && parsed.templateSlug) {
                        handleMountPayload({
                          templateSlug: parsed.templateSlug,
                          uPosition: uNumber,
                          face,
                        });
                      }
                    } catch {}
                  }}
                />
              )}

              {(viewMode === 'dual' || viewMode === 'rear') && (
                <SingleRackElevationSVG
                  rack={rack}
                  face="rear"
                  rackHeight={rackHeight}
                  mountedItems={mountedItems}
                  selectedItemId={selectedItemId}
                  pendingMoveItemId={pendingMoveItem?.id || null}
                  onSelectItem={(item) => {
                    setSelectedItemId(item ? item.id : null);
                    if (item && pendingMoveItem && pendingMoveItem.id !== item.id) {
                      setPendingMoveItem(null);
                    }
                  }}
                  isAdmin={isAdmin}
                  dragCandidate={dragCandidate}
                  onDragStartMountedDevice={(e, item) => {
                    const uH = Math.max(1, Number(item.uHeight || 1));
                    const isFullDepth = item.isFullDepth !== undefined ? Boolean(item.isFullDepth) : true;
                    setDragCandidate({
                      uHeight: uH,
                      isFullDepth,
                      excludeId: item.id,
                      source: 'rack',
                      item,
                    });
                  }}
                  onClickUSlot={(uNumber, face) => {
                    // Tap-to-Move handler: If an item is pending move, execute move to this slot
                    if (pendingMoveItem && isAdmin) {
                      const uH = Math.max(1, Number(pendingMoveItem.uHeight || 1));
                      const isFullDepth = pendingMoveItem.isFullDepth !== undefined ? Boolean(pendingMoveItem.isFullDepth) : true;
                      handleMountPayload({
                        deviceId: pendingMoveItem.id,
                        uPosition: uNumber,
                        face,
                        uHeight: uH,
                        isFullDepth,
                      });
                      setPendingMoveItem(null);
                      return;
                    }
                    setTargetMountU(String(uNumber));
                    setTargetMountFace(face);
                  }}
                  onDropAtUSlot={(uNumber, face, e) => {
                    try {
                      const raw = e.dataTransfer.getData('application/json');
                      if (!raw) return;
                      const parsed = JSON.parse(raw);
                      if (parsed.type === 'mounted-device' && parsed.deviceId) {
                        handleMountPayload({
                          deviceId: parsed.deviceId,
                          uPosition: uNumber,
                          face,
                          uHeight: parsed.uHeight,
                          isFullDepth: parsed.isFullDepth,
                        });
                      } else if (parsed.type === 'existing-device' && parsed.deviceId) {
                        handleMountPayload({
                          deviceId: parsed.deviceId,
                          uPosition: uNumber,
                          face,
                          uHeight: parsed.uHeight,
                        });
                      } else if (parsed.type === 'starter-template' && parsed.templateSlug) {
                        handleMountPayload({
                          templateSlug: parsed.templateSlug,
                          uPosition: uNumber,
                          face,
                        });
                      }
                    } catch {}
                  }}
                />
              )}
            </div>
          </div>

          {/* -------- RIGHT COLUMN: SELECTED DEVICE / RACK INSPECTOR -------- */}
          <div
            style={{
              borderLeft: '1px solid #282A36',
              background: '#121623',
              padding: 16,
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: 14,
            }}
          >
            {selectedItem ? (
              <>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    borderBottom: '1px solid #282A36',
                    paddingBottom: 10,
                  }}
                >
                  <div>
                    <div style={{ fontSize: 11, color: '#BD93F9', fontWeight: 700 }}>
                      อุปกรณ์ในช่อง U{selectedItem.uPosition}
                      {Number(selectedItem.uHeight || 1) > 1
                        ? `–U${Number(selectedItem.uPosition) + Number(selectedItem.uHeight) - 1}`
                        : ''}{' '}
                      ({String(selectedItem.rackFace || 'front').toUpperCase()})
                    </div>
                    <div style={{ fontSize: 15, fontWeight: 800, color: '#F8F8F2', marginTop: 2 }}>
                      {selectedItem.name}
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setSelectedItemId(null);
                      setPendingMoveItem(null);
                      setDragCandidate(null);
                    }}
                    style={{
                      background: 'rgba(239, 68, 68, 0.15)',
                      border: '1px solid rgba(239, 68, 68, 0.4)',
                      color: '#F87171',
                      borderRadius: 6,
                      padding: '4px 10px',
                      fontSize: 11,
                      fontWeight: 700,
                      cursor: 'pointer',
                    }}
                    title="ปลดการเลือกอุปกรณ์นี้ (Esc)"
                  >
                    ✕ ยกเลิกเลือก (Esc)
                  </button>
                </div>

                {/* Live Telemetry & Identity Card */}
                <div
                  style={{
                    background: '#090D16',
                    borderRadius: 10,
                    padding: 12,
                    border: '1px solid #282A36',
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: 8,
                    fontSize: 12,
                  }}
                >
                  <div>
                    <div style={{ color: '#64748B', fontSize: 10.5 }}>IP Address</div>
                    <div style={{ color: '#38bdf8', fontWeight: 700, fontFamily: 'monospace' }}>
                      {selectedItem.ip || 'ไม่ได้ระบุ (Passive)'}
                    </div>
                  </div>
                  <div>
                    <div style={{ color: '#64748B', fontSize: 10.5 }}>สถานะ</div>
                    <div
                      style={{
                        color:
                          String(selectedItem.status).toLowerCase() === 'offline'
                            ? '#FF5555'
                            : '#50FA7B',
                        fontWeight: 700,
                      }}
                    >
                      ● {selectedItem.status || 'Online'}{' '}
                      {selectedItem.latencyMs !== null && selectedItem.latencyMs !== undefined
                        ? `(${selectedItem.latencyMs}ms)`
                        : ''}
                    </div>
                  </div>
                  <div>
                    <div style={{ color: '#64748B', fontSize: 10.5 }}>MAC Address</div>
                    <div style={{ color: '#CBD5E1', fontFamily: 'monospace', fontSize: 11 }}>
                      {selectedItem.mac || '-'}
                    </div>
                  </div>
                  <div>
                    <div style={{ color: '#64748B', fontSize: 10.5 }}>ผู้ผลิต / รุ่น</div>
                    <div style={{ color: '#CBD5E1', fontSize: 11.5 }}>
                      {selectedItem.vendor || '-'}
                    </div>
                  </div>
                </div>

                {/* Inline IP & Name Quick Edit (Admin) */}
                {isAdmin && (
                  <div
                    style={{
                      background: '#090D16',
                      borderRadius: 10,
                      padding: 10,
                      border: '1px solid #282A36',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 6,
                    }}
                  >
                    <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8' }}>
                      ✏️ กำหนดชื่อและ IP Address ของอุปกรณ์ในช่อง U{selectedItem.uPosition}
                    </div>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <input
                        type="text"
                        value={editNameInput}
                        onChange={(e) => setEditNameInput(e.target.value)}
                        placeholder="ชื่ออุปกรณ์..."
                        style={{
                          flex: 1,
                          minWidth: 0,
                          padding: '5px 8px',
                          borderRadius: 6,
                          border: '1px solid #334155',
                          background: '#121623',
                          color: '#F8F8F2',
                          fontSize: 11.5,
                        }}
                      />
                      <input
                        type="text"
                        value={editIpInput}
                        onChange={(e) => setEditIpInput(e.target.value)}
                        placeholder="IP เช่น 192.168.110.10"
                        style={{
                          width: 125,
                          padding: '5px 8px',
                          borderRadius: 6,
                          border: '1px solid #334155',
                          background: '#121623',
                          color: '#38bdf8',
                          fontFamily: 'monospace',
                          fontSize: 11.5,
                        }}
                      />
                      <button
                        disabled={busy}
                        onClick={() =>
                          handleMountPayload({
                            deviceId: selectedItem.id,
                            name: editNameInput.trim() || selectedItem.name,
                            ip: editIpInput.trim(),
                            uPosition: selectedItem.uPosition,
                            uHeight: selectedItem.uHeight || 1,
                            face: selectedItem.rackFace || 'front',
                            isFullDepth: selectedItem.isFullDepth,
                          })
                        }
                        style={{
                          padding: '5px 10px',
                          borderRadius: 6,
                          border: '1px solid rgba(80, 250, 123, 0.45)',
                          background: 'rgba(80, 250, 123, 0.16)',
                          color: '#50FA7B',
                          fontSize: 11,
                          fontWeight: 700,
                          cursor: 'pointer',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        บันทึก
                      </button>
                    </div>
                  </div>
                )}

                {/* ================= ACTION 1: WEB LOGIN (NEW BROWSER TAB) ================= */}
                <div
                  style={{
                    background: '#141A29',
                    borderRadius: 10,
                    padding: 12,
                    border: '1px solid rgba(56, 189, 248, 0.35)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 8,
                  }}
                >
                  <div
                    style={{
                      fontSize: 11.5,
                      fontWeight: 700,
                      color: '#38bdf8',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <span>1️⃣ เข้าหน้าควบคุมอุปกรณ์ผ่านเว็บ (Web Login)</span>
                    <span style={{ fontSize: 10, color: '#94A3B8' }}>เปิดแท็บใหม่ ↗</span>
                  </div>

                  <button
                    onClick={() => handleOpenWebLoginNewTab(selectedItem)}
                    disabled={!selectedItem.ip}
                    style={{
                      width: '100%',
                      padding: '9px 12px',
                      borderRadius: 8,
                      border: selectedItem.ip
                        ? '1px solid rgba(56, 189, 248, 0.6)'
                        : '1px solid #334155',
                      background: selectedItem.ip
                        ? 'linear-gradient(135deg, rgba(56, 189, 248, 0.28), rgba(37, 99, 235, 0.28))'
                        : '#090D16',
                      color: selectedItem.ip ? '#F8F8F2' : '#64748B',
                      fontSize: 12.5,
                      fontWeight: 800,
                      cursor: selectedItem.ip ? 'pointer' : 'not-allowed',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 6,
                    }}
                  >
                    <span>🌐 เปิด Web Login ในแท็บใหม่</span>
                    {selectedItem.ip && (
                      <span style={{ fontFamily: 'monospace', color: '#7DD3FC' }}>
                        ({selectedItem.ip}) ↗
                      </span>
                    )}
                  </button>

                  {selectedItem.ip && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      <button
                        onClick={() => handleOpenWebLoginNewTab(selectedItem, 'http', 80)}
                        style={{
                          flex: 1,
                          padding: '5px 8px',
                          borderRadius: 6,
                          border: '1px solid #334155',
                          background: '#090D16',
                          color: '#BAE6FD',
                          fontSize: 11,
                          fontWeight: 700,
                          fontFamily: 'monospace',
                          cursor: 'pointer',
                        }}
                      >
                        🌐 HTTP :80 ↗
                      </button>
                      <button
                        onClick={() => handleOpenWebLoginNewTab(selectedItem, 'https', 443)}
                        style={{
                          flex: 1,
                          padding: '5px 8px',
                          borderRadius: 6,
                          border: '1px solid #334155',
                          background: '#090D16',
                          color: '#A7F3D0',
                          fontSize: 11,
                          fontWeight: 700,
                          fontFamily: 'monospace',
                          cursor: 'pointer',
                        }}
                      >
                        🔒 HTTPS :443 ↗
                      </button>
                      {(selectedItem.openPorts || [])
                        .map((p) => Number(typeof p === 'object' ? p.port : p))
                        .filter((port) =>
                          [8080, 8443, 8006, 8291, 3000, 5000, 5001, 9000, 9090, 9443, 10000].includes(
                            port
                          )
                        )
                        .map((port) => {
                          const proto = [8443, 8006, 5001, 9443, 10000].includes(port)
                            ? 'https'
                            : 'http';
                          return (
                            <button
                              key={port}
                              onClick={() => handleOpenWebLoginNewTab(selectedItem, proto, port)}
                              style={{
                                padding: '5px 8px',
                                borderRadius: 6,
                                border: '1px solid rgba(189, 147, 249, 0.45)',
                                background: 'rgba(189, 147, 249, 0.15)',
                                color: '#E2D4F0',
                                fontSize: 11,
                                fontWeight: 700,
                                fontFamily: 'monospace',
                                cursor: 'pointer',
                              }}
                            >
                              {proto.toUpperCase()} :{port} ↗
                            </button>
                          );
                        })}
                    </div>
                  )}
                </div>

                {/* ================= ACTION 2: LIVE PING & PORT SCAN (INLINE) ================= */}
                <div
                  style={{
                    background: '#141A29',
                    borderRadius: 10,
                    padding: 12,
                    border: '1px solid rgba(80, 250, 123, 0.3)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 8,
                  }}
                >
                  <div
                    style={{
                      fontSize: 11.5,
                      fontWeight: 700,
                      color: '#50FA7B',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <span>2️⃣ ตรวจสอบสถานะสด & สแกนพอร์ต</span>
                    <span style={{ fontSize: 10, color: '#94A3B8' }}>
                      พอร์ตที่เปิด: {(selectedItem.openPorts || []).length}
                    </span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                    <button
                      disabled={!selectedItem.ip || pingingId === selectedItem.id}
                      onClick={() => handleLivePingSelected(selectedItem)}
                      style={{
                        padding: '8px 10px',
                        borderRadius: 8,
                        border: '1px solid rgba(80, 250, 123, 0.45)',
                        background: 'rgba(80, 250, 123, 0.14)',
                        color: '#50FA7B',
                        fontSize: 11.5,
                        fontWeight: 700,
                        cursor: selectedItem.ip ? 'pointer' : 'not-allowed',
                      }}
                    >
                      {pingingId === selectedItem.id
                        ? '⏳ กำลัง Ping...'
                        : '⚡ Ping เช็คสถานะสด'}
                    </button>

                    <button
                      disabled={!selectedItem.ip || scanningPortsId === selectedItem.id}
                      onClick={() => handleLiveScanPortsSelected(selectedItem)}
                      style={{
                        padding: '8px 10px',
                        borderRadius: 8,
                        border: '1px solid rgba(56, 189, 248, 0.45)',
                        background: 'rgba(56, 189, 248, 0.14)',
                        color: '#38bdf8',
                        fontSize: 11.5,
                        fontWeight: 700,
                        cursor: selectedItem.ip ? 'pointer' : 'not-allowed',
                      }}
                    >
                      {scanningPortsId === selectedItem.id
                        ? '📡 กำลังสแกน...'
                        : '📡 สแกนพอร์ต (48 พอร์ต)'}
                    </button>
                  </div>

                  {Array.isArray(selectedItem.openPorts) && selectedItem.openPorts.length > 0 && (
                    <div
                      style={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: 5,
                        paddingTop: 4,
                      }}
                    >
                      {selectedItem.openPorts.map((p, idx) => {
                        const portNum = typeof p === 'object' ? p.port : p;
                        const svc = typeof p === 'object' ? p.service || 'TCP' : 'TCP';
                        return (
                          <span
                            key={idx}
                            onClick={() => {
                              if (selectedItem.ip) {
                                const proto = [443, 8443, 8006, 9443].includes(Number(portNum))
                                  ? 'https'
                                  : 'http';
                                handleOpenWebLoginNewTab(selectedItem, proto, portNum);
                              }
                            }}
                            title="คลิกเพื่อเปิดพอร์ตนี้ในแท็บใหม่"
                            style={{
                              padding: '2px 7px',
                              borderRadius: 999,
                              background: '#090D16',
                              border: '1px solid #334155',
                              color: '#50FA7B',
                              fontSize: 10.5,
                              fontFamily: 'monospace',
                              fontWeight: 700,
                              cursor: selectedItem.ip ? 'pointer' : 'default',
                            }}
                          >
                            :{portNum} ({svc})
                          </span>
                        );
                      })}
                    </div>
                  )}
                </div>

                {/* ================= ACTION 3: DEEP INSPECTOR IN NEW TAB ================= */}
                <button
                  onClick={() => handleOpenDeviceDashboardNewTab(selectedItem)}
                  style={{
                    width: '100%',
                    padding: '9px 12px',
                    borderRadius: 10,
                    border: '1px solid rgba(189, 147, 249, 0.45)',
                    background: 'rgba(189, 147, 249, 0.14)',
                    color: '#E2D4F0',
                    fontSize: 12,
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 6,
                  }}
                >
                  <span>3️⃣ 📋 ดูรายละเอียดเชิงลึก / SNMP / Topology (เปิดแท็บใหม่)</span>
                  <span>↗</span>
                </button>

                {/* Admin Rack Slot Controls */}
                {isAdmin && (
                  <div
                    style={{
                      background: '#181D2E',
                      borderRadius: 10,
                      padding: 12,
                      border: '1px solid rgba(189, 147, 249, 0.25)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 10,
                    }}
                  >
                    <div style={{ fontSize: 12, fontWeight: 700, color: '#BD93F9' }}>
                      ⚙️ ปรับตำแหน่งและขนาดในตู้แร็ค (EIA-310)
                    </div>

                    {/* Tap-to-Move Button for Touch Screens */}
                    <button
                      onClick={() => {
                        if (pendingMoveItem?.id === selectedItem.id) {
                          setPendingMoveItem(null);
                        } else {
                          setPendingMoveItem(selectedItem);
                          toast?.({
                            title: `📍 เลือก "${selectedItem.name}" เตรียมย้ายแล้ว`,
                            description: `แตะที่ช่อง U บนผังตู้เพื่อย้ายไปตำแหน่งนั้นได้ทันที (หรือกดแตะซ้ำเพื่อยกเลิก)`,
                          });
                        }
                      }}
                      style={{
                        padding: '8px 12px',
                        borderRadius: 8,
                        border: pendingMoveItem?.id === selectedItem.id
                          ? '1px solid #50FA7B'
                          : '1px solid rgba(189, 147, 249, 0.5)',
                        background: pendingMoveItem?.id === selectedItem.id
                          ? 'rgba(80, 250, 123, 0.22)'
                          : 'rgba(189, 147, 249, 0.16)',
                        color: pendingMoveItem?.id === selectedItem.id ? '#50FA7B' : '#E2D4F0',
                        fontSize: 12,
                        fontWeight: 800,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: 6,
                      }}
                    >
                      <span>{pendingMoveItem?.id === selectedItem.id ? '🎯 กำลังเลือกช่อง U ปลายทาง... (แตะช่อง U ได้เลย)' : '👆 แตะเพื่อย้ายตำแหน่ง (Tap-to-Move)'}</span>
                    </button>

                    {/* Move Up / Down 1U */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                      <button
                        disabled={busy}
                        onClick={() =>
                          handleMountPayload({
                            deviceId: selectedItem.id,
                            uPosition: Number(selectedItem.uPosition) + 1,
                            uHeight: selectedItem.uHeight || 1,
                            face: selectedItem.rackFace || 'front',
                            isFullDepth: selectedItem.isFullDepth,
                          })
                        }
                        style={{
                          padding: '7px 10px',
                          borderRadius: 8,
                          border: '1px solid #334155',
                          background: '#090D16',
                          color: '#50FA7B',
                          fontSize: 12,
                          fontWeight: 700,
                          cursor: 'pointer',
                        }}
                      >
                        ⬆️ ขยับขึ้น +1U (U{Number(selectedItem.uPosition) + 1})
                      </button>
                      <button
                        disabled={busy || Number(selectedItem.uPosition) <= 1}
                        onClick={() =>
                          handleMountPayload({
                            deviceId: selectedItem.id,
                            uPosition: Number(selectedItem.uPosition) - 1,
                            uHeight: selectedItem.uHeight || 1,
                            face: selectedItem.rackFace || 'front',
                            isFullDepth: selectedItem.isFullDepth,
                          })
                        }
                        style={{
                          padding: '7px 10px',
                          borderRadius: 8,
                          border: '1px solid #334155',
                          background: '#090D16',
                          color: '#38bdf8',
                          fontSize: 12,
                          fontWeight: 700,
                          cursor: 'pointer',
                        }}
                      >
                        ⬇️ ขยับลง -1U (U{Math.max(1, Number(selectedItem.uPosition) - 1)})
                      </button>
                    </div>

                    {/* Change U-Height (1U..4U) */}
                    <div>
                      <div style={{ fontSize: 11, color: '#94A3B8', marginBottom: 4 }}>
                        ความสูงของอุปกรณ์ (U-Height):
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 6 }}>
                        {[1, 2, 3, 4].map((h) => (
                          <button
                            key={h}
                            disabled={busy}
                            onClick={() =>
                              handleMountPayload({
                                deviceId: selectedItem.id,
                                uPosition: selectedItem.uPosition,
                                uHeight: h,
                                face: selectedItem.rackFace || 'front',
                                isFullDepth: selectedItem.isFullDepth,
                              })
                            }
                            style={{
                              padding: '5px',
                              borderRadius: 6,
                              border:
                                Number(selectedItem.uHeight || 1) === h
                                  ? '1px solid #BD93F9'
                                  : '1px solid #334155',
                              background:
                                Number(selectedItem.uHeight || 1) === h
                                  ? 'rgba(189, 147, 249, 0.22)'
                                  : '#090D16',
                              color: '#F8F8F2',
                              fontSize: 11.5,
                              fontWeight: 700,
                              cursor: 'pointer',
                            }}
                          >
                            {h}U
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Flip Front/Rear & Toggle Full-Depth */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                      <button
                        disabled={busy}
                        onClick={() =>
                          handleMountPayload({
                            deviceId: selectedItem.id,
                            uPosition: selectedItem.uPosition,
                            uHeight: selectedItem.uHeight || 1,
                            face:
                              (selectedItem.rackFace || 'front') === 'front' ? 'rear' : 'front',
                            isFullDepth: selectedItem.isFullDepth,
                          })
                        }
                        style={{
                          padding: '6px 8px',
                          borderRadius: 7,
                          border: '1px solid #334155',
                          background: '#090D16',
                          color: '#E2D4F0',
                          fontSize: 11.5,
                          fontWeight: 700,
                          cursor: 'pointer',
                        }}
                      >
                        🔄 สลับเป็นด้าน{' '}
                        {(selectedItem.rackFace || 'front') === 'front' ? 'หลัง (Rear)' : 'หน้า (Front)'}
                      </button>

                      <button
                        disabled={busy}
                        onClick={() =>
                          handleMountPayload({
                            deviceId: selectedItem.id,
                            uPosition: selectedItem.uPosition,
                            uHeight: selectedItem.uHeight || 1,
                            face: selectedItem.rackFace || 'front',
                            isFullDepth: !selectedItem.isFullDepth,
                          })
                        }
                        style={{
                          padding: '6px 8px',
                          borderRadius: 7,
                          border: '1px solid #334155',
                          background: '#090D16',
                          color: '#FFB86C',
                          fontSize: 11.5,
                          fontWeight: 700,
                          cursor: 'pointer',
                        }}
                      >
                        📐 {selectedItem.isFullDepth ? 'Full-Depth (ทะลุ)' : 'Half-Depth (ครึ่งตู้)'}
                      </button>
                    </div>

                    {/* Unmount Button */}
                    <button
                      disabled={busy}
                      onClick={() => handleUnmountItem(selectedItem)}
                      style={{
                        marginTop: 4,
                        padding: '8px 12px',
                        borderRadius: 8,
                        border: '1px solid rgba(245, 158, 11, 0.45)',
                        background: 'rgba(245, 158, 11, 0.14)',
                        color: '#FBBF24',
                        fontSize: 12,
                        fontWeight: 700,
                        cursor: 'pointer',
                      }}
                    >
                      📤 ถอดอุปกรณ์ออกจากช่อง U (Unmount)
                    </button>
                  </div>
                )}
              </>
            ) : (
              /* Rack Summary & Mounted Inventory List when no specific U-item is clicked */
              <>
                <div style={{ fontSize: 14, fontWeight: 800, color: '#F8F8F2' }}>
                  📋 รายการอุปกรณ์ที่ติดตั้งในตู้แร็คนี้ ({mountedItems.length})
                </div>
                <div style={{ fontSize: 11.5, color: '#94A3B8' }}>
                  คลิกที่อุปกรณ์บนผังตู้แร็ค SVG หรือจากรายการด้านล่างเพื่อดูสถานะ, เปิดหน้าเว็บ Login (:80/:443) หรือปรับช่อง U
                </div>

                <div
                  style={{
                    flex: 1,
                    overflowY: 'auto',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 6,
                  }}
                >
                  {mountedItems.length === 0 ? (
                    <div
                      style={{
                        padding: 24,
                        textAlign: 'center',
                        background: '#090D16',
                        borderRadius: 10,
                        border: '1px dashed #334155',
                        color: '#64748B',
                        fontSize: 12.5,
                      }}
                    >
                      ยังไม่มีอุปกรณ์ติดตั้งในตู้แร็คนี้
                      {isAdmin && (
                        <div style={{ marginTop: 6, color: '#BD93F9' }}>
                          ลากอุปกรณ์จากแถบซ้ายมือมาวางในช่อง U1–U{rackHeight} ได้ทันที
                        </div>
                      )}
                    </div>
                  ) : (
                    mountedItems.map((item) => {
                      const range = getDeviceURange(item.uPosition, item.uHeight || 1);
                      return (
                        <div
                          key={item.id}
                          onClick={() => setSelectedItemId(item.id)}
                          style={{
                            padding: '8px 10px',
                            borderRadius: 8,
                            background: '#090D16',
                            border: '1px solid #282A36',
                            borderLeft: `4px solid ${item.color || '#BD93F9'}`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            cursor: 'pointer',
                          }}
                        >
                          <div>
                            <div style={{ fontSize: 12, fontWeight: 700, color: '#F8F8F2' }}>
                              <span style={{ color: '#50FA7B', fontFamily: 'monospace', marginRight: 6 }}>
                                [U{range.bottom}
                                {range.top > range.bottom ? `–U${range.top}` : ''}]
                              </span>
                              {item.name}
                            </div>
                            <div style={{ fontSize: 10.5, color: '#94A3B8', marginTop: 2 }}>
                              {item.ip ? `IP: ${item.ip} • ` : ''}
                              {item.uHeight || 1}U • {String(item.rackFace || 'front').toUpperCase()}
                            </div>
                          </div>
                          <span style={{ fontSize: 11, color: '#38bdf8', fontWeight: 700 }}>
                            ดูข้อมูล →
                          </span>
                        </div>
                      );
                    })
                  )}
                </div>

                {isAdmin && onUnplace3DRack && (
                  <button
                    onClick={() => {
                      onClose?.();
                      onUnplace3DRack(rack);
                    }}
                    style={{
                      padding: '8px 12px',
                      borderRadius: 8,
                      border: '1px solid rgba(245, 158, 11, 0.4)',
                      background: 'rgba(245, 158, 11, 0.12)',
                      color: '#FBBF24',
                      fontSize: 12,
                      fontWeight: 700,
                      cursor: 'pointer',
                    }}
                  >
                    📦 เอาโมเดลตู้แร็คออกจากพื้นที่ห้อง (เก็บเข้าคิว)
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


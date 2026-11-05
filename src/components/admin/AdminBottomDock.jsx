import React from "react"
import { M3IconButton, M3SegmentedButtonSet, M3SegmentedButton, M3Badge, M3Divider } from "@/components/m3"
import {
  ShieldCheck,
  Crosshair,
  Undo2,
  Redo2,
  Grid,
  Magnet,
  Maximize2,
  Trash2,
  X,
  Square,
  Pentagon,
} from "lucide-react"

/**
 * Bottom-Center Floating Admin Command Capsule
 * Symbol-first snapping, history, and active mode HUD.
 */
export function AdminBottomDock({
  activeTool,
  toggleTool,
  unplacedCount = 0,
  drawShapeType = "rectangle",
  setDrawShapeType,
  drawRoomZoneMode = false,
  placingDevice = null,
  placingRoom = null,
  cancelActiveMode,
  undoCount = 0,
  redoCount = 0,
  handleUndo,
  handleRedo,
  snapToGrid = true,
  setSnapToGrid,
  magneticWallSnap = true,
  setMagneticWallSnap,
  autoSnapRoomEnabled = true,
  setAutoSnapRoomEnabled,
  activeAdminRoomId = null,
  handleDeleteRoomZone,
  onOpenRackula,
}) {
  const isAnyActiveMode = drawRoomZoneMode || Boolean(placingDevice) || Boolean(placingRoom)

  return (
    <div
      role="toolbar"
      aria-label="Admin Command Toolbar"
      className="fixed bottom-3 left-1/2 -translate-x-1/2 z-30 max-w-[98vw] overflow-x-auto rounded-full border border-border/80 bg-card/90 backdrop-blur-2xl px-3.5 py-1.5 shadow-2xl pointer-events-auto flex items-center gap-2"
    >
      {/* 1. DOCK DRAWER TOGGLE & RACKULA EXTENDED FAB */}
      <div className="flex items-center gap-1.5 shrink-0">
        <M3IconButton
          variant={activeTool ? "filled" : "tonal"}
          onClick={() => toggleTool?.(activeTool ? null : "rooms")}
          ariaLabel="เปิด/ปิด แผงควบคุม Inspector"
          title="เปิด/ปิด แผงควบคุม Inspector (ห้อง, สแกนเนอร์, อุปกรณ์ที่วางแล้ว)"
          className={activeTool ? "bg-primary text-white" : ""}
        >
          <Crosshair className="h-4 w-4" />
        </M3IconButton>

        {onOpenRackula && (
          <button
            type="button"
            onClick={() => onOpenRackula?.()}
            className="flex items-center gap-1.5 px-3 h-8 rounded-full bg-primary/15 hover:bg-primary/25 border border-primary/30 text-primary font-medium text-xs transition-all shadow-sm hover:shadow active:scale-95 cursor-pointer shrink-0"
            title="เปิดจัดการผังตู้แร็ค 19 นิ้ว (Rackula Designer) ในแท็บแยก"
          >
            <span className="text-sm">🖥️</span>
            <span className="font-semibold whitespace-nowrap">ผังตู้แร็ค</span>
          </button>
        )}
      </div>

      <div className="h-6 w-2 flex items-center justify-center shrink-0">
        <M3Divider />
      </div>

      {/* 2. SHAPE MODE SELECTOR (Only relevant or emphasized when drawing) */}
      <div className="flex items-center shrink-0">
        <M3SegmentedButtonSet>
          <M3SegmentedButton
            label="Rect"
            icon={<Square className="h-3.5 w-3.5" />}
            selected={drawShapeType === "rectangle"}
            onClick={() => setDrawShapeType?.("rectangle")}
            ariaLabel="ทรงสี่เหลี่ยมผืนผ้า (Rectangle)"
            title="ทรงสี่เหลี่ยมผืนผ้า 4 จุด"
          />
          <M3SegmentedButton
            label="Poly"
            icon={<Pentagon className="h-3.5 w-3.5" />}
            selected={drawShapeType === "polygon"}
            onClick={() => setDrawShapeType?.("polygon")}
            ariaLabel="ทรงโพลีกอนอิสระ (Custom Polygon)"
            title="ทรงโพลีกอนปักหมุดทีละจุดอิสระ"
          />
        </M3SegmentedButtonSet>
      </div>

      <div className="h-6 w-2 flex items-center justify-center shrink-0">
        <M3Divider />
      </div>

      {/* 3. HISTORY CONTROLS (Undo / Redo / Delete) */}
      <div className="flex items-center gap-0.5 shrink-0">
        <div className="m3-badge-anchor">
          <M3IconButton
            variant="standard"
            disabled={undoCount === 0}
            onClick={handleUndo}
            ariaLabel={`ย้อนกลับคำสั่งล่าสุด [Ctrl+Z] (${undoCount} รายการ)`}
            title={`ย้อนกลับคำสั่งล่าสุด [Ctrl+Z] (${undoCount})`}
            className="text-amber-400"
          >
            <Undo2 className="h-4 w-4" />
          </M3IconButton>
          {undoCount > 0 && <M3Badge value={undoCount} />}
        </div>

        <div className="m3-badge-anchor">
          <M3IconButton
            variant="standard"
            disabled={redoCount === 0}
            onClick={handleRedo}
            ariaLabel={`ทำซ้ำคำสั่งที่ย้อนกลับ [Ctrl+Y] (${redoCount} รายการ)`}
            title={`ทำซ้ำคำสั่งที่ย้อนกลับ [Ctrl+Y] (${redoCount})`}
            className="text-primary"
          >
            <Redo2 className="h-4 w-4" />
          </M3IconButton>
          {redoCount > 0 && <M3Badge value={redoCount} />}
        </div>

        {activeAdminRoomId && (
          <M3IconButton
            variant="filled"
            onClick={() => handleDeleteRoomZone?.(activeAdminRoomId)}
            ariaLabel="ลบกรอบห้องที่เลือกอยู่ [Delete / Backspace]"
            title="ลบกรอบห้องที่เลือกอยู่ [Del]"
            className="bg-destructive text-destructive-foreground ml-1"
          >
            <Trash2 className="h-4 w-4" />
          </M3IconButton>
        )}
      </div>

      <div className="h-6 w-2 flex items-center justify-center shrink-0">
        <M3Divider />
      </div>

      {/* 4. SNAPPING TOGGLES (Symbolic Icon Buttons) */}
      <div className="flex items-center gap-1 shrink-0">
        <M3IconButton
          variant={snapToGrid ? "tonal" : "standard"}
          toggle
          selected={snapToGrid}
          onClick={() => setSnapToGrid?.(!snapToGrid)}
          ariaLabel="Snap to Grid 0.5m"
          title={`Snap to Grid 0.5m: ${snapToGrid ? "เปิดอยู่" : "ปิดอยู่"}`}
          className={snapToGrid ? "text-primary" : "text-muted-foreground"}
        >
          <Grid className="h-4 w-4" />
        </M3IconButton>

        <M3IconButton
          variant={magneticWallSnap ? "tonal" : "standard"}
          toggle
          selected={magneticWallSnap}
          onClick={() => setMagneticWallSnap?.(!magneticWallSnap)}
          ariaLabel="Magnetic Wall Snap (ดูดแนวกำแพง CAD)"
          title={`Magnetic Wall Snap: ${magneticWallSnap ? "เปิดอยู่" : "ปิดอยู่"}`}
          className={magneticWallSnap ? "text-emerald-400" : "text-muted-foreground"}
        >
          <Magnet className="h-4 w-4" />
        </M3IconButton>

        <M3IconButton
          variant={autoSnapRoomEnabled ? "tonal" : "standard"}
          toggle
          selected={autoSnapRoomEnabled}
          onClick={() => setAutoSnapRoomEnabled?.(!autoSnapRoomEnabled)}
          ariaLabel="Auto-Snap Room (ผูกห้องอัตโนมัติเมื่อวางหมุด)"
          title={`Auto-Snap Room: ${autoSnapRoomEnabled ? "เปิดอยู่" : "ปิดอยู่"}`}
          className={autoSnapRoomEnabled ? "text-sky-400" : "text-muted-foreground"}
        >
          <Maximize2 className="h-4 w-4" />
        </M3IconButton>
      </div>

      {/* 5. ACTIVE MODE HUD NOTIFICATION PILL */}
      {isAnyActiveMode && (
        <div className="flex items-center gap-1.5 pl-2 ml-1 border-l border-border animate-in fade-in zoom-in-95 duration-150 shrink-0">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
          </span>
          <span className="text-[11px] font-semibold text-emerald-400 whitespace-nowrap">
            {drawRoomZoneMode && "โหมดวาดกรอบห้อง"}
            {placingDevice && `กำลังวาง ${placingDevice.name || placingDevice.ip}`}
            {placingRoom && "กำลังปักเลขห้อง"}
          </span>
          <button
            type="button"
            onClick={cancelActiveMode}
            className="flex items-center gap-0.5 px-2 py-0.5 rounded-full bg-secondary hover:bg-muted text-[10px] font-mono text-muted-foreground hover:text-foreground cursor-pointer transition-colors"
            title="กด Esc เพื่อยกเลิกโหมดนี้"
          >
            <span>[Esc]</span>
            <X className="h-3 w-3" />
          </button>
        </div>
      )}
    </div>
  )
}


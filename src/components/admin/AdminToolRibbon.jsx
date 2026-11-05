import React from "react"
import { M3IconButton, M3Divider } from "@/components/m3"
import {
  MousePointer,
  Move,
  RotateCw,
  Maximize2,
  GitCommit,
  SquareDashed,
  MapPin,
  Server,
  Compass,
  Tag,
  Save,
  Layers,
} from "lucide-react"

/**
 * Symbolic CAD Left Ribbon for Admin 3D Manipulation
 * Standard 48px pro ribbon inspired by CAD/BIM tools.
 */
export function AdminToolRibbon({
  roomTransformMode = "scale",
  setRoomTransformMode,
  drawRoomZoneMode = false,
  toggleDrawRoomZoneMode,
  placingRoom,
  handleQuick3DRoomPin,
  onQuickPlaceServerRack,
  onFlyToTopDown,
  viewState = {},
  updateView,
  onSaveAsDefaultView,
}) {
  const showLabels = viewState.showDeviceLabels ?? true

  return (
    <aside
      aria-label="CAD Tool Ribbon"
      className="fixed left-3 top-1/2 -translate-y-1/2 z-30 flex flex-col items-center gap-1 p-1.5 rounded-2xl border border-border/80 bg-card/90 backdrop-blur-xl shadow-2xl pointer-events-auto"
    >
      {/* 1. SELECTION & TRANSFORM MODES */}
      <div className="flex flex-col gap-1 items-center">
        <M3IconButton
          variant={roomTransformMode === "translate" ? "tonal" : "standard"}
          toggle
          selected={roomTransformMode === "translate"}
          onClick={() => setRoomTransformMode?.("translate")}
          ariaLabel="โหมดย้ายตำแหน่ง [W] (Translate X/Z)"
          title="โหมดย้ายตำแหน่งวัตถุ/โซน [W]"
          className="text-primary"
        >
          <Move className="h-4 w-4" />
        </M3IconButton>

        <M3IconButton
          variant={roomTransformMode === "rotate" ? "tonal" : "standard"}
          toggle
          selected={roomTransformMode === "rotate"}
          onClick={() => setRoomTransformMode?.("rotate")}
          ariaLabel="โหมดหมุนวัตถุ [E] (Rotate Y)"
          title="โหมดหมุนวัตถุ [E]"
          className="text-amber-400"
        >
          <RotateCw className="h-4 w-4" />
        </M3IconButton>

        <M3IconButton
          variant={roomTransformMode === "scale" ? "tonal" : "standard"}
          toggle
          selected={roomTransformMode === "scale"}
          onClick={() => setRoomTransformMode?.("scale")}
          ariaLabel="โหมดปรับขนาดกรอบห้อง [R] (Scale Size)"
          title="โหมดปรับขนาดกรอบห้อง [R]"
          className="text-sky-400"
        >
          <Maximize2 className="h-4 w-4" />
        </M3IconButton>

        <M3IconButton
          variant={roomTransformMode === "vertices" ? "tonal" : "standard"}
          toggle
          selected={roomTransformMode === "vertices"}
          onClick={() => setRoomTransformMode?.("vertices")}
          ariaLabel="โหมดดัดจุดยอดมุมโพลีกอน [A] (Vertex Edit)"
          title="โหมดดัดจุดยอดมุมโพลีกอน [A]"
          className="text-emerald-400"
        >
          <GitCommit className="h-4 w-4" />
        </M3IconButton>
      </div>

      <div className="w-6 my-1">
        <M3Divider />
      </div>

      {/* 2. CREATION & DRAWING TOOLS */}
      <div className="flex flex-col gap-1 items-center">
        <M3IconButton
          variant={drawRoomZoneMode ? "filled" : "standard"}
          toggle
          selected={drawRoomZoneMode}
          onClick={toggleDrawRoomZoneMode}
          ariaLabel="โหมดวาดกรอบห้อง 3D [D] (Draw Zone)"
          title="โหมดวาดกรอบห้อง 3D (Polygon/Rectangle) [D]"
          className={drawRoomZoneMode ? "bg-emerald-600 text-white" : "text-emerald-400"}
        >
          <SquareDashed className="h-4 w-4" />
        </M3IconButton>

        <M3IconButton
          variant={placingRoom ? "filled" : "standard"}
          toggle
          selected={Boolean(placingRoom)}
          onClick={handleQuick3DRoomPin}
          ariaLabel="ปักหมุดหมายเลขห้อง [P] (Pin Room)"
          title="ปักหมุดกำหนดหมายเลขห้องลงบนโมเดล 3D"
          className={placingRoom ? "bg-primary text-white" : "text-primary"}
        >
          <MapPin className="h-4 w-4" />
        </M3IconButton>

        <M3IconButton
          variant="standard"
          onClick={onQuickPlaceServerRack}
          ariaLabel="วางตู้แร็ค Server Rack 3D"
          title="เลือกวางตู้ Server Rack 3D Model ในห้อง"
          className="text-purple-400"
        >
          <Server className="h-4 w-4" />
        </M3IconButton>
      </div>

      <div className="w-6 my-1">
        <M3Divider />
      </div>

      {/* 3. VIEW & UTILITY SHORTCUTS */}
      <div className="flex flex-col gap-1 items-center">
        <M3IconButton
          variant="standard"
          onClick={onFlyToTopDown}
          ariaLabel="มุมมองแปลนดิ่ง 90 องศา (Top-Down CAD View)"
          title="มุมมองแปลนดิ่ง 90° Top-Down"
          className="text-emerald-400"
        >
          <Compass className="h-4 w-4" />
        </M3IconButton>

        <M3IconButton
          variant={showLabels ? "tonal" : "standard"}
          toggle
          selected={showLabels}
          onClick={() => updateView?.({ showDeviceLabels: !showLabels })}
          ariaLabel="เปิด/ปิดป้ายชื่ออุปกรณ์ 3D"
          title="เปิด/ปิดป้ายชื่ออุปกรณ์ 3D"
          className="text-sky-400"
        >
          <Tag className="h-4 w-4" />
        </M3IconButton>

        {onSaveAsDefaultView && (
          <M3IconButton
            variant="standard"
            onClick={onSaveAsDefaultView}
            ariaLabel="บันทึกมุมมองนี้เป็นค่าเริ่มต้น"
            title="บันทึกมุมมองนี้เป็นค่าเริ่มต้นสำหรับผู้ใช้ทั่วไป"
            className="text-amber-400"
          >
            <Save className="h-4 w-4" />
          </M3IconButton>
        )}
      </div>
    </aside>
  )
}


import React, { useState } from "react"
import { FLOORS, DEVICE_CATEGORIES, ROOM_TYPES } from "@/data/twinData"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Input, SelectNative } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { M3IconButton, M3Badge, M3SegmentedButtonSet, M3SegmentedButton, M3Divider } from "@/components/m3"
import { AdminToolRibbon } from "@/components/admin/AdminToolRibbon"
import { AdminBottomDock } from "@/components/admin/AdminBottomDock"
import {
  ShieldCheck,
  Search,
  MapPin,
  Crosshair,
  Radar,
  Server,
  Plus,
  Trash2,
  Sparkles,
  Download,
  Layers,
  Building2,
  ChevronDown,
  Eye,
  FolderPlus,
  Wrench,
  SquareDashed,
  Undo2,
  Redo2,
  Compass,
  Move,
  Maximize2,
  Tag,
  Save,
} from "lucide-react"

/**
 * Studio-Grade Floating Admin Command Toolbar (Dock) + Contextual Tool Panel
 * Strictly rendered on /admin route when authenticated.
 */
export function AdminToolbar({
  unplacedDevices = [],
  filteredUnplacedDevices = [],
  placedDevices = [],
  rooms = [],
  filteredAdminRooms = [],
  networks = [],
  viewState,
  updateView,
  placingDevice,
  placingRoom,
  drawRoomZoneMode = false,
  toggleDrawRoomZoneMode,
  drawShapeType = "rectangle",
  setDrawShapeType,
  snapToGrid = true,
  setSnapToGrid,
  magneticWallSnap = true,
  setMagneticWallSnap,
  autoSnapRoomEnabled = true,
  setAutoSnapRoomEnabled,
  cancelActiveMode,
  activeAdminRoomId = null,
  setActiveAdminRoomId,
  roomTransformMode = "scale",
  setRoomTransformMode,
  undoCount = 0,
  redoCount = 0,
  handleUndo,
  handleRedo,
  handleDeleteRoomZone,
  onFlyToTopDown,
  startPlacingDevice,
  onQuickPlaceServerRack,
  startPlacingRoom,
  onSaveAsDefaultView,
  handleUnplaceDevice,
  onSelectDevice,
  onSelectRoom,
  onFlyTo,
  adminSearch,
  setAdminSearch,
  adminRoomSearch,
  setAdminRoomSearch,
  subnetInput,
  setSubnetInput,
  scanStatus,
  handleTriggerScan,
  singleIpInput,
  setSingleIpInput,
  scanningSingleIp,
  handleScanSingleIp,
  newDevForm,
  setNewDevForm,
  handleAddDevice,
  newRoomForm,
  setNewRoomForm,
  handleAddRoom,
  batchRoomForm,
  setBatchRoomForm,
  handleBatchGenerateRooms,
}) {
  // Active tool drawer: "queue" | "placed" | "rooms" | "scanner" | "add-device" | null (collapsed for full 3D view)
  const [activeTool, setActiveTool] = useState("rooms")

  const toggleTool = (toolId) => {
    setActiveTool((prev) => (prev === toolId ? null : toolId))
  }

  // Quick 1-Click 3D Room Pin Launcher from the Toolbar
  const handleQuick3DRoomPin = () => {
    const fIdx =
      viewState.selectedFloor === "all" ? Number(newRoomForm.floorIdx ?? 1) : Number(viewState.selectedFloor)
    const prefix = fIdx === 0 ? "G0" : fIdx === 3 ? "RF-0" : `${fIdx}0`
    const nextNum = rooms.filter((r) => Number(r.floorIdx) === fIdx).length + 1
    const suggestedRoomNo = `${prefix}${nextNum}`
    const draft = {
      ...newRoomForm,
      floorIdx: fIdx,
      roomNumber: newRoomForm.roomNumber || suggestedRoomNo,
      name: newRoomForm.name || `Room ${newRoomForm.roomNumber || suggestedRoomNo}`,
    }
    startPlacingRoom(draft)
  }

  return (
    <>
      {/* 1. CONTEXTUAL FLOATING TOOL DRAWER (Opens above the Bottom Dock when a tool is active) */}
      {activeTool && (
        <aside aria-label="Admin dock" className="fixed top-16 right-3 bottom-20 z-20 w-[420px] max-w-[95vw] flex flex-col pointer-events-auto animate-in fade-in slide-in-from-right-4 duration-150">
          <Card className="flex-1 flex flex-col overflow-hidden rounded-2xl border border-border bg-card/95 backdrop-blur-xl shadow-lg">
            <CardHeader className="p-4 pb-3 border-b border-border/60 bg-secondary/30 flex flex-row items-center justify-between gap-2 space-y-0">
              <div className="flex items-center gap-2 min-w-0">
                <div className="h-7 w-7 rounded-md bg-primary/15 border border-primary/30 flex items-center justify-center text-primary shrink-0">
                  <Wrench className="h-4 w-4" />
                </div>
                <div className="min-w-0">
                  <CardTitle className="text-xs sm:text-sm truncate">
                    {activeTool === "queue" && `คิวอุปกรณ์รอจัดวาง 3D (${unplacedDevices.length})`}
                    {activeTool === "placed" && `อุปกรณ์ที่วางบนตึกแล้ว (${placedDevices.length})`}
                    {activeTool === "rooms" && `จัดการหมายเลขห้อง & โซน 3D (${rooms.length})`}
                    {activeTool === "scanner" && "สแกนเครือข่าย Multi-Subnet & IP Probe"}
                    {activeTool === "add-device" && "เพิ่มอุปกรณ์ใหม่เข้าคิวรอจัดวาง"}
                    {activeTool === "view" && "มุมมอง เลเยอร์ และ Export"}
                  </CardTitle>
                  <CardDescription className="text-[11px] truncate">
                    {activeTool === "queue" && "เลือกอุปกรณ์แล้วคลิกวางลงบนพื้นห้องในโมเดล 3D"}
                    {activeTool === "placed" && "ตรวจสอบ ย้ายจุดติดตั้ง หรือถอนหมุดกลับเข้าคิว"}
                    {activeTool === "rooms" && "คลิกกำหนดเลขห้องบน 3D, ไฮไลต์กรอบห้อง และสร้างห้องตาม Pattern"}
                    {activeTool === "scanner" && "ค้นหาอุปกรณ์ในวง LAN/WAN/VLAN อัตโนมัติ"}
                    {activeTool === "add-device" && "บันทึกอุปกรณ์ใหม่เข้าสู่คิวรอจัดวางของ Admin"}
                    {activeTool === "view" && "สลับชั้น เลเยอร์ 3D และบันทึกค่าเริ่มต้นสำหรับผู้ใช้ทั่วไป"}
                  </CardDescription>
                </div>
              </div>

              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 shrink-0"
                onClick={() => setActiveTool(null)}
                aria-label="Collapse admin dock"
                title="พับเก็บแผงเครื่องมือเพื่อดูโมเดล 3D เต็มจอ"
              >
                <ChevronDown className="h-4 w-4" />
              </Button>
            </CardHeader>

            {/* DOCK TABS: switch between admin tools without returning to the bottom toolbar */}
            <div role="tablist" aria-label="Admin tools" className="flex gap-1 border-b border-border bg-card px-2 py-1.5 overflow-x-auto items-center">
              {[
                { id: "queue", label: "คิวรอวาง", icon: "📥", count: unplacedDevices.length },
                { id: "placed", label: "วางแล้ว", icon: "📌", count: placedDevices.length },
                { id: "rooms", label: "ห้อง", icon: "🏷️", count: rooms.length },
                { id: "scanner", label: "สแกน", icon: "📡" },
                { id: "add-device", label: "+อุปกรณ์", icon: "➕" },
                { id: "view", label: "มุมมอง", icon: "👁️" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  role="tab"
                  aria-selected={activeTool === tab.id}
                  onClick={() => setActiveTool(tab.id)}
                  className={`shrink-0 rounded-full px-3 h-8 text-xs font-medium transition-colors cursor-pointer flex items-center gap-1.5 ${
                    activeTool === tab.id
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.label}</span>
                  {tab.count !== undefined && (
                    <M3Badge value={tab.count} className="ml-0.5" />
                  )}
                </button>
              ))}
            <Button
              size="sm"
              variant="outline"
              className="h-8 shrink-0 rounded-full text-xs gap-1.5 border-primary/40 text-primary hover:bg-primary/15 cursor-pointer px-3"
              onClick={onQuickPlaceServerRack}
              title="เลือกวางตู้ Server Rack 3D Model ลงในตำแหน่งกรอบห้องที่กำหนดไว้"
            >
              <Server className="h-3.5 w-3.5 text-primary" />
              <span>วางตู้ Rack 3D</span>
            </Button>
              </div>

            <CardContent className="p-3 flex-1 overflow-y-auto flex flex-col space-y-3">
              {/* TOOL PANEL 1: UNPLACED DISCOVERED QUEUE */}
              {activeTool === "queue" && (
                <div className="flex-1 flex flex-col space-y-2.5 overflow-hidden">
                  <div className="relative">
                    <Search className="h-3.5 w-3.5 absolute left-2.5 top-2.5 text-muted-foreground" />
                    <Input
                      value={adminSearch}
                      onChange={(e) => setAdminSearch(e.target.value)}
                      placeholder="ค้นหา IP, ชื่อ, MAC, ยี่ห้อ ในคิวรอวาง..."
                      className="pl-8 h-8 text-xs"
                    />
                  </div>

                  <div className="text-[11px] text-muted-foreground bg-secondary/30 rounded-md px-2.5 py-1.5 border border-border">
                    อุปกรณ์ในคิวนี้จะ<strong>ยังไม่ปรากฏบนหน้าแสดงผลหลัก</strong> จนกว่าคุณจะกดปุ่ม{" "}
                    <span className="text-primary font-semibold">"วางบนตึก 3D"</span>{" "}
                    แล้วคลิกเลือกจุดติดตั้งบนอาคาร (รองรับ Auto-Snap เข้าเลขห้องอัตโนมัติ)
                  </div>

                  <div className="flex-1 overflow-y-auto space-y-2 pr-1">
                    {filteredUnplacedDevices.length === 0 ? (
                      <div className="text-center py-8 text-xs text-muted-foreground">
                        ไม่มีอุปกรณ์ค้างในคิวรอจัดวาง
                      </div>
                    ) : (
                      filteredUnplacedDevices.map((dev) => (
                        <div
                          key={dev.id}
                          className={`rounded-lg border p-2.5 transition space-y-2 ${
                            placingDevice?.id === dev.id
                              ? "border-primary bg-primary/10"
                              : "border-border bg-secondary/20 hover:bg-secondary/40"
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div className="min-w-0">
                              <div className="text-xs font-bold truncate flex items-center gap-1.5">
                                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                                {dev.name || dev.ip}
                              </div>
                              <div className="text-[11px] font-mono text-muted-foreground">
                                {dev.ip} · {dev.mac || "No MAC"}
                              </div>
                              <div className="text-[10px] text-muted-foreground truncate">
                                {dev.vendor || "Unknown Vendor"} · พอร์ตเปิด{" "}
                                {(dev.openPorts || []).length} พอร์ต
                              </div>
                            </div>
                            <Badge variant="info" className="text-[10px] uppercase shrink-0">
                              {dev.category || "Network"}
                            </Badge>
                          </div>

                          <div className="flex items-center gap-1.5">
                            <Button
                              size="sm"
                              variant={placingDevice?.id === dev.id ? "secondary" : "default"}
                              className="flex-1 h-7 text-xs"
                              onClick={() => startPlacingDevice(dev)}
                            >
                              <Crosshair className="h-3.5 w-3.5 mr-1" />
                              {placingDevice?.id === dev.id
                                ? "คลิกบนตึก 3D..."
                                : "วางบนตึก 3D"}
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              className="h-7 px-2 text-xs"
                              onClick={() => onSelectDevice(dev.id)}
                            >
                              ดูข้อมูล
                            </Button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}

              {/* TOOL PANEL 2: PLACED DEVICES MANAGER */}
              {activeTool === "placed" && (
                <div className="flex-1 overflow-y-auto space-y-2 pr-1">
                  {placedDevices.length === 0 ? (
                    <div className="text-center py-8 text-xs text-muted-foreground">
                      ยังไม่มีอุปกรณ์ที่จัดวางลงอาคาร 3D
                      <br />
                      เลือกเครื่องมือ <strong>"คิวรอวาง"</strong> บน Toolbar ด้านล่างเพื่อปักหมุด
                    </div>
                  ) : (
                    placedDevices.map((dev) => {
                      const fl = FLOORS.find((f) => f.index === Number(dev.floorIdx))
                      return (
                        <div
                          key={dev.id}
                          className="rounded-lg border border-border bg-secondary/20 p-2.5 space-y-2"
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div>
                              <div className="text-xs font-bold">{dev.name || dev.ip}</div>
                              <div className="text-[11px] font-mono text-muted-foreground">
                                {dev.ip} · {fl ? fl.shortLabel : `F${dev.floorIdx}`} · ห้อง{" "}
                                <span className="text-primary font-bold">
                                  [{dev.roomNumber || "-"}]
                                </span>
                              </div>
                            </div>
                            <Badge variant="success" className="text-[10px]">
                              Placed
                            </Badge>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <Button
                              size="sm"
                              variant="outline"
                              className="flex-1 h-7 text-xs"
                              onClick={() => {
                                updateView({ selectedFloor: String(dev.floorIdx ?? 0) })
                                onFlyTo(dev.position, Number(dev.floorIdx ?? 0))
                                onSelectDevice(dev.id)
                              }}
                            >
                              เปิดการ์ด / Login
                            </Button>
                            <Button
                              size="sm"
                              variant="secondary"
                              className="h-7 px-2 text-xs"
                              onClick={() => startPlacingDevice(dev)}
                            >
                              ย้ายจุด
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              className="h-7 px-2 text-xs"
                              onClick={() => handleUnplaceDevice(dev.id)}
                              title="ถอนหมุดกลับเข้าคิว"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </Button>
                          </div>
                        </div>
                      )
                    })
                  )}
                </div>
              )}

              {/* TOOL PANEL 3: ROOM NUMBERING, 3D FLOOR ZONE & PATTERN GENERATOR */}
              {activeTool === "rooms" && (
                <div className="space-y-3">
                  {/* 1. Interactive 3D Click-to-Place Room Creator */}
                  <form
                    onSubmit={handleAddRoom}
                    className="rounded-lg border border-primary/30 bg-secondary/25 p-3 space-y-2.5"
                  >
                    <div className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                      <MapPin className="h-4 w-4 text-primary" />
                      1. กำหนดเลขห้อง & ไฮไลต์กรอบพื้นที่ห้อง 3D
                    </div>

                    <div className="grid grid-cols-3 gap-2">
                      <SelectNative
                        value={newRoomForm.floorIdx}
                        onChange={(e) => {
                          const fIdx = Number(e.target.value)
                          const prefix =
                            fIdx === 0 ? "G0" : fIdx === 3 ? "RF-0" : `${fIdx}0`
                          const countOnFloor =
                            rooms.filter((r) => Number(r.floorIdx) === fIdx).length + 1
                          setNewRoomForm({
                            ...newRoomForm,
                            floorIdx: fIdx,
                            roomNumber: `${prefix}${countOnFloor}`,
                          })
                          updateView({ selectedFloor: String(fIdx), showRooms: true })
                        }}
                        className="h-8 text-xs"
                      >
                        {FLOORS.map((f) => (
                          <option key={f.index} value={f.index}>
                            ชั้น {f.shortLabel}
                          </option>
                        ))}
                      </SelectNative>

                      <Input
                        placeholder="เลขห้อง (101)"
                        value={newRoomForm.roomNumber}
                        onChange={(e) =>
                          setNewRoomForm({
                            ...newRoomForm,
                            roomNumber: e.target.value,
                          })
                        }
                        className="h-8 text-xs font-mono font-bold"
                      />

                      <SelectNative
                        value={newRoomForm.roomType}
                        onChange={(e) => {
                          const rt = e.target.value
                          const meta =
                            ROOM_TYPES.find((t) => t.id === rt) || ROOM_TYPES[1]
                          setNewRoomForm({
                            ...newRoomForm,
                            roomType: rt,
                            color: meta.color,
                            width: meta.defaultWidth,
                            depth: meta.defaultDepth,
                          })
                        }}
                        className="h-8 text-xs"
                      >
                        {ROOM_TYPES.map((rt) => (
                          <option key={rt.id} value={rt.id}>
                            {rt.icon} {rt.id}
                          </option>
                        ))}
                      </SelectNative>
                    </div>

                    <div className="grid grid-cols-3 gap-2">
                      <Input
                        placeholder="ชื่อห้อง (เช่น NOC, ห้องเรียน 101)"
                        value={newRoomForm.name}
                        onChange={(e) =>
                          setNewRoomForm({ ...newRoomForm, name: e.target.value })
                        }
                        className="col-span-2 h-8 text-xs"
                      />
                      <Input
                        placeholder="VLAN (เช่น VLAN 10)"
                        value={newRoomForm.vlan}
                        onChange={(e) =>
                          setNewRoomForm({ ...newRoomForm, vlan: e.target.value })
                        }
                        className="h-8 text-xs font-mono"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div className="flex items-center gap-1.5">
                        <Label className="text-[11px] shrink-0">กว้าง (m):</Label>
                        <Input
                          type="number"
                          min="2"
                          max="80"
                          value={newRoomForm.width}
                          onChange={(e) =>
                            setNewRoomForm({ ...newRoomForm, width: e.target.value })
                          }
                          className="h-7 text-xs font-mono"
                        />
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Label className="text-[11px] shrink-0">ลึก (m):</Label>
                        <Input
                          type="number"
                          min="2"
                          max="80"
                          value={newRoomForm.depth}
                          onChange={(e) =>
                            setNewRoomForm({ ...newRoomForm, depth: e.target.value })
                          }
                          className="h-7 text-xs font-mono"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-1.5 pt-1">
                      <Button
                        type="button"
                        size="sm"
                        variant={drawRoomZoneMode ? "default" : "secondary"}
                        className={`h-8 text-xs col-span-2 ${
                          drawRoomZoneMode ? "bg-emerald-600 text-white ring-2 ring-emerald-400" : ""
                        }`}
                        onClick={toggleDrawRoomZoneMode}
                      >
                        <SquareDashed className="h-3.5 w-3.5 mr-1 text-emerald-400" />
                        {drawRoomZoneMode
                          ? "กำลังเปิดโหมดปักหมุดวาดกรอบห้องทีละมุม (Polygon / Rectangle)"
                          : "ปักหมุดวาดกรอบห้องทีละมุม (Polygon Point-by-Point)"}
                      </Button>
                      <Button
                        type="button"
                        size="sm"
                        variant="default"
                        className="h-8 text-xs"
                        onClick={() => startPlacingRoom(newRoomForm)}
                      >
                        <Crosshair className="h-3.5 w-3.5 mr-1" />
                        คลิกวางห้องบนตึก 3D
                      </Button>
                      <Button
                        type="submit"
                        size="sm"
                        variant="secondary"
                        className="h-8 text-xs"
                      >
                        <Plus className="h-3.5 w-3.5 mr-1" />
                        บันทึกจุดกึ่งกลางชั้น
                      </Button>
                    </div>
                  </form>

                  {/* 2. Quick Pattern Room Number Generator */}
                  <form
                    onSubmit={handleBatchGenerateRooms}
                    className="rounded-lg border border-border bg-secondary/15 p-3 space-y-2"
                  >
                    <div className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                      <Sparkles className="h-4 w-4 text-primary" />
                      2. สร้างชุดเลขห้องอัตโนมัติตาม Pattern (เช่น 101–104)
                    </div>
                    <div className="grid grid-cols-4 gap-1.5">
                      <SelectNative
                        value={batchRoomForm.floorIdx}
                        onChange={(e) => {
                          const fIdx = Number(e.target.value)
                          const pref =
                            fIdx === 0 ? "G0" : fIdx === 3 ? "RF-0" : `${fIdx}0`
                          setBatchRoomForm({
                            ...batchRoomForm,
                            floorIdx: fIdx,
                            prefix: pref,
                          })
                        }}
                        className="h-7 text-xs"
                      >
                        {FLOORS.map((f) => (
                          <option key={f.index} value={f.index}>
                            {f.shortLabel}
                          </option>
                        ))}
                      </SelectNative>
                      <Input
                        value={batchRoomForm.prefix}
                        onChange={(e) =>
                          setBatchRoomForm({ ...batchRoomForm, prefix: e.target.value })
                        }
                        placeholder="Prefix (10)"
                        className="h-7 text-xs font-mono"
                      />
                      <Input
                        type="number"
                        min="1"
                        max="99"
                        value={batchRoomForm.startNumber}
                        onChange={(e) =>
                          setBatchRoomForm({
                            ...batchRoomForm,
                            startNumber: Number(e.target.value),
                          })
                        }
                        className="h-7 text-xs font-mono"
                      />
                      <Input
                        type="number"
                        min="1"
                        max="12"
                        value={batchRoomForm.count}
                        onChange={(e) =>
                          setBatchRoomForm({
                            ...batchRoomForm,
                            count: Number(e.target.value),
                          })
                        }
                        className="h-7 text-xs font-mono"
                      />
                    </div>
                    <Button
                      type="submit"
                      size="sm"
                      variant="outline"
                      className="w-full h-7 text-xs"
                    >
                      <Sparkles className="h-3.5 w-3.5 mr-1 text-primary" />
                      สร้างห้อง {batchRoomForm.prefix}
                      {batchRoomForm.startNumber} ถึง {batchRoomForm.prefix}
                      {Number(batchRoomForm.startNumber) + Number(batchRoomForm.count) - 1}{" "}
                      อัตโนมัติ
                    </Button>
                  </form>

                  {/* 3. Existing Rooms List */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label className="text-xs font-bold uppercase tracking-wider">
                        3. รายการห้องในระบบ ({filteredAdminRooms.length})
                      </Label>
                    </div>

                    <div className="relative">
                      <Search className="h-3.5 w-3.5 absolute left-2.5 top-2 text-muted-foreground" />
                      <Input
                        value={adminRoomSearch}
                        onChange={(e) => setAdminRoomSearch(e.target.value)}
                        placeholder="ค้นหาเลขห้อง, ชื่อห้อง..."
                        className="pl-8 h-7 text-xs"
                      />
                    </div>

                    <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
                      {filteredAdminRooms.length === 0 ? (
                        <div className="text-center py-4 text-xs text-muted-foreground">
                          ไม่พบรายการห้อง
                        </div>
                      ) : (
                        filteredAdminRooms.map((rm) => {
                          const fl = FLOORS.find(
                            (f) => f.index === Number(rm.floorIdx ?? 0)
                          )
                          const rMeta =
                            ROOM_TYPES.find((r) => r.id === rm.roomType) || ROOM_TYPES[1]
                          const rmDevCount = placedDevices.filter(
                            (d) =>
                              d.isPlaced &&
                              Number(d.floorIdx ?? 0) === Number(rm.floorIdx ?? 0) &&
                              (d.roomId === rm.id ||
                                (d.roomNumber && d.roomNumber === rm.roomNumber))
                          ).length

                          return (
                            <div
                              key={rm.id}
                              className={`rounded-lg border p-2.5 space-y-2 transition ${
                                placingRoom?.id === rm.id
                                  ? "border-emerald-400 bg-emerald-500/10"
                                  : "border-border bg-secondary/20"
                              }`}
                            >
                              <div className="flex items-start justify-between gap-2">
                                <div className="min-w-0">
                                  <div className="text-xs font-bold flex items-center gap-1.5 truncate">
                                    <span>{rMeta.icon}</span>
                                    <span className="font-mono text-primary">
                                      [{rm.roomNumber}]
                                    </span>
                                    <span className="truncate">{rm.name}</span>
                                  </div>
                                  <div className="text-[11px] font-mono text-muted-foreground">
                                    {fl ? fl.shortLabel : `F${rm.floorIdx}`} · โซน{" "}
                                    {rm.zoneSize?.width ?? 12}m×
                                    {rm.zoneSize?.depth ?? 10}m · อุปกรณ์ {rmDevCount}{" "}
                                    ตัว
                                  </div>
                                </div>
                                <Badge variant="outline" className="text-[10px] shrink-0">
                                  {rm.roomType || "Office"}
                                </Badge>
                              </div>

                              <div className="flex items-center gap-1.5">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="flex-1 h-7 text-xs"
                                  onClick={() => onSelectRoom(rm.id)}
                                >
                                  แก้ไขเลขห้อง / ดูอุปกรณ์
                                </Button>
                                <Button
                                  size="sm"
                                  variant={activeAdminRoomId === rm.id ? "default" : "secondary"}
                                  className="h-7 px-2 text-xs"
                                  onClick={() => {
                                    setActiveAdminRoomId(
                                      activeAdminRoomId === rm.id ? null : rm.id
                                    )
                                    setRoomTransformMode("scale")
                                    updateView({
                                      selectedFloor: String(rm.floorIdx ?? 0),
                                      showRooms: true,
                                    })
                                    onFlyTo(rm.position, Number(rm.floorIdx ?? 0))
                                  }}
                                  title="เลือกกรอบห้อง 3D เพื่อดึงขนาด/ย้ายตำแหน่งหรือลบกรอบ"
                                >
                                  <Maximize2 className="h-3 w-3 mr-1" />
                                  ดึงกรอบ 3D
                                </Button>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  className="h-7 px-2 text-xs"
                                  onClick={() => handleDeleteRoomZone(rm.id)}
                                  title="ลบกรอบสี่เหลี่ยมโซนห้องนี้ (รองรับ Ctrl+Z เพื่อกู้คืน)"
                                >
                                  <Trash2 className="h-3 w-3" />
                                </Button>
                              </div>
                            </div>
                          )
                        })
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* TOOL PANEL 4: NETWORK SCANNER (SUBNET CIDR & SINGLE IP) */}
              {activeTool === "scanner" && (
                <div className="space-y-3">
                  <div className="rounded-lg border border-border bg-secondary/20 p-3 space-y-2.5">
                    <div className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                      <Radar className="h-4 w-4 text-primary" />
                      1. สแกนทั้งวงเครือข่าย (Subnet CIDR Scanner)
                    </div>
                    <div className="flex gap-1.5">
                      <Input
                        value={subnetInput}
                        onChange={(e) => setSubnetInput(e.target.value)}
                        placeholder="192.168.110.0/24"
                        className="h-8 text-xs font-mono"
                      />
                      <Button
                        size="sm"
                        className="h-8 shrink-0"
                        disabled={scanStatus.running}
                        onClick={handleTriggerScan}
                      >
                        <Radar
                          className={`h-3.5 w-3.5 mr-1 ${
                            scanStatus.running ? "animate-spin" : ""
                          }`}
                        />
                        สแกนวงนี้
                      </Button>
                    </div>

                    {networks.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {networks.map((net, idx) => (
                          <button
                            key={net.id ? `${net.id}-${idx}` : net.cidr || idx}
                            onClick={() => setSubnetInput(net.cidr)}
                            className="text-[10px] font-mono px-2 py-0.5 rounded border border-border bg-background hover:border-primary cursor-pointer"
                          >
                            {net.cidr}
                          </button>
                        ))}
                      </div>
                    )}

                    {scanStatus.running && (
                      <div className="space-y-1 pt-1">
                        <div className="flex justify-between text-[10px] font-mono text-muted-foreground">
                          <span>กำลังสแกน {scanStatus.cidr}...</span>
                          <span>{scanStatus.progress || 0}%</span>
                        </div>
                        <Progress value={scanStatus.progress || 10} />
                      </div>
                    )}
                  </div>

                  <form
                    onSubmit={handleScanSingleIp}
                    className="rounded-lg border border-border bg-secondary/20 p-3 space-y-2"
                  >
                    <div className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                      <Crosshair className="h-4 w-4 text-primary" />
                      2. สแกนเจาะจง IP เดี่ยว (Single IP Deep Probe)
                    </div>
                    <div className="flex gap-1.5">
                      <Input
                        value={singleIpInput}
                        onChange={(e) => setSingleIpInput(e.target.value)}
                        placeholder="เช่น 192.168.110.1"
                        className="h-8 text-xs font-mono"
                      />
                      <Button
                        type="submit"
                        size="sm"
                        variant="secondary"
                        className="h-8 shrink-0"
                        disabled={scanningSingleIp}
                      >
                        {scanningSingleIp ? "กำลังสแกน..." : "สแกน IP"}
                      </Button>
                    </div>
                  </form>
                </div>
              )}

              {/* TOOL PANEL 5: ADD MANUAL DEVICE TO QUEUE */}
              {activeTool === "add-device" && (
                <form
                  onSubmit={handleAddDevice}
                  className="rounded-lg border border-border bg-secondary/20 p-3 space-y-3"
                >
                  <div className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <Server className="h-4 w-4 text-primary" />
                    เพิ่มอุปกรณ์ใหม่เข้าสู่คิวรอจัดวาง
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <Input
                      placeholder="ชื่ออุปกรณ์ (เช่น SW-FL2)"
                      value={newDevForm.name}
                      onChange={(e) =>
                        setNewDevForm({ ...newDevForm, name: e.target.value })
                      }
                      className="h-8 text-xs"
                    />
                    <Input
                      placeholder="IP (เช่น 192.168.110.50)"
                      value={newDevForm.ip}
                      onChange={(e) =>
                        setNewDevForm({ ...newDevForm, ip: e.target.value })
                      }
                      className="h-8 text-xs font-mono"
                    />
                    <SelectNative
                      value={newDevForm.category}
                      onChange={(e) =>
                        setNewDevForm({ ...newDevForm, category: e.target.value })
                      }
                      className="h-8 text-xs"
                    >
                      {DEVICE_CATEGORIES.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.icon} {c.label}
                        </option>
                      ))}
                    </SelectNative>
                    <SelectNative
                      value={newDevForm.networkType}
                      onChange={(e) =>
                        setNewDevForm({ ...newDevForm, networkType: e.target.value })
                      }
                      className="h-8 text-xs"
                    >
                      <option value="LAN">LAN</option>
                      <option value="WAN">WAN</option>
                      <option value="VLAN">VLAN</option>
                    </SelectNative>

                    <SelectNative
                      value={newDevForm.modelType || "pin"}
                      onChange={(e) =>
                        setNewDevForm({ ...newDevForm, modelType: e.target.value })
                      }
                      className="h-8 text-xs font-semibold"
                    >
                      <option value="pin">📍 หมุด 3D เรืองแสง (Default)</option>
                      <option value="server_rack">🖥️ ตู้ Server Rack (3D Model)</option>
                    </SelectNative>

                    <SelectNative
                      value={newDevForm.rotationY ?? 0}
                      onChange={(e) =>
                        setNewDevForm({ ...newDevForm, rotationY: Number(e.target.value) })
                      }
                      className="h-8 text-xs font-mono"
                    >
                      <option value={0}>หมุน: 0° (หน้าตรง)</option>
                      <option value={90}>หมุน: 90° (หันขวา)</option>
                      <option value={180}>หมุน: 180° (หันหลัง)</option>
                      <option value={270}>หมุน: 270° (หันซ้าย)</option>
                    </SelectNative>
                  </div>
                  <Button type="submit" size="sm" className="w-full h-8 text-xs">
                    <Plus className="h-3.5 w-3.5 mr-1" />
                    บันทึกเข้าคิวรอจัดวาง
                  </Button>
                </form>
              )}

              {/* TOOL PANEL 6: VIEW / LAYERS / EXPORT (moved from bottom toolbar) */}
              {activeTool === "view" && (
                <div className="space-y-3">
                  <div className="flex flex-wrap items-center gap-1.5">
                            <div className="flex items-center rounded-full border border-border bg-secondary/35 p-0.5">
                              <button
                                type="button"
                                onClick={() => updateView({ selectedFloor: "all" })}
                                className={`px-2.5 py-1 rounded-full text-[11px] font-bold transition cursor-pointer ${
                                  viewState.selectedFloor === "all"
                                    ? "bg-primary text-primary-foreground shadow"
                                    : "text-muted-foreground hover:text-foreground"
                                }`}
                              >
                                ALL
                              </button>
                              {FLOORS.map((fl) => (
                                <button
                                  key={fl.index}
                                  type="button"
                                  onClick={() => updateView({ selectedFloor: String(fl.index) })}
                                  className={`px-2.5 py-1 rounded-full text-[11px] font-mono font-bold transition cursor-pointer ${
                                    String(viewState.selectedFloor) === String(fl.index)
                                      ? "bg-primary text-primary-foreground shadow"
                                      : "text-muted-foreground hover:text-foreground"
                                  }`}
                                >
                                  {fl.shortLabel}
                                </button>
                              ))}
                            </div>
                  
                  
                            <Button
                              size="sm"
                              variant={viewState.showPlans ? "secondary" : "ghost"}
                              className="h-8 rounded-full px-2.5 text-[11px]"
                              onClick={() => updateView({ showPlans: !viewState.showPlans })}
                              title="สลับแปลนพื้นสถาปัตย์ 2D (CAD Blueprints)"
                            >
                              <Layers className="h-3.5 w-3.5 mr-1 text-primary" />
                              แปลน 2D
                            </Button>
                  
                            <Button
                              size="sm"
                              variant={viewState.showRooms ? "secondary" : "ghost"}
                              className="h-8 rounded-full px-2.5 text-[11px]"
                              onClick={() => updateView({ showRooms: !viewState.showRooms })}
                              title="สลับการแสดงผลป้ายเลขห้องและกรอบพื้นที่ห้อง 3D"
                            >
                              <Eye className="h-3.5 w-3.5 mr-1 text-emerald-400" />
                              โซนห้อง
                            </Button>
                  
                            <Button
                              size="sm"
                              variant={(viewState.showDevices ?? true) ? "secondary" : "ghost"}
                              className="h-8 rounded-full px-2.5 text-[11px]"
                              onClick={() => updateView({ showDevices: !(viewState.showDevices ?? true) })}
                              title="สลับการแสดงผลหมุดและโมเดลอุปกรณ์ 3D ทั้งหมด"
                            >
                              <Server className="h-3.5 w-3.5 mr-1 text-sky-400" />
                              อุปกรณ์ 3D
                            </Button>
                  
                            <Button
                              size="sm"
                              variant={(viewState.showDeviceLabels ?? true) ? "secondary" : "ghost"}
                              className="h-8 px-2 text-[11px]"
                              onClick={() => updateView({ showDeviceLabels: !(viewState.showDeviceLabels ?? true) })}
                              title="สลับการแสดงผลป้ายชื่ออุปกรณ์ 3D (Device Badges)"
                            >
                              <Tag className="h-3.5 w-3.5 mr-1 text-sky-400" />
                              ป้ายอุปกรณ์
                            </Button>
                  
                            <Button
                              size="sm"
                              variant={viewState.exploded ? "secondary" : "ghost"}
                              className="h-8 px-2 text-[11px]"
                              onClick={() => updateView({ exploded: !viewState.exploded })}
                              title="แยกชั้นอาคารแนวตั้ง (Explode Floors)"
                            >
                              <Sparkles className="h-3.5 w-3.5 mr-1 text-amber-400" />
                              แยกชั้น
                            </Button>
                  
                            <Button
                              size="sm"
                              variant="outline"
                              className="h-8 px-2 text-[11px] border-primary/40 text-primary hover:bg-primary/15 cursor-pointer ml-1"
                              onClick={onSaveAsDefaultView}
                              title="บันทึกการเปิด-ปิด Layer ปัจจุบันเป็นค่าเริ่มต้นสำหรับผู้ใช้ทั่วไป"
                            >
                              <Save className="h-3.5 w-3.5 mr-1" />
                              <span className="hidden xl:inline">บันทึกค่าเริ่มต้น</span>
                            </Button>
                          </div>
                  <Separator />
                  <Button
                              size="sm"
                              variant="ghost"
                              className="h-9 px-2.5 text-xs"
                              onClick={() => window.open("/api/export", "_blank", "noopener")}
                              title="Export ข้อมูล JSON Schema v2.0.0 ทั้งระบบ"
                            >
                              <Download className="h-3.5 w-3.5 mr-1 text-primary" />
                              <span className="hidden xl:inline">Export JSON</span>
                            </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </aside>
      )}

      {/* 2. SYMBOLIC CAD LEFT RIBBON (Vertical pro tools: Move, Rotate, Scale, Vertices, Draw, Top-Down) */}
      <AdminToolRibbon
        roomTransformMode={roomTransformMode}
        setRoomTransformMode={setRoomTransformMode}
        drawRoomZoneMode={drawRoomZoneMode}
        toggleDrawRoomZoneMode={toggleDrawRoomZoneMode}
        placingRoom={placingRoom}
        handleQuick3DRoomPin={handleQuick3DRoomPin}
        onQuickPlaceServerRack={onQuickPlaceServerRack}
        onFlyToTopDown={onFlyToTopDown}
        viewState={viewState}
        updateView={updateView}
        onSaveAsDefaultView={onSaveAsDefaultView}
      />

      {/* 3. SYMBOLIC BOTTOM COMMAND & SNAPPING CAPSULE */}
      <AdminBottomDock
        activeTool={activeTool}
        toggleTool={toggleTool}
        unplacedCount={unplacedDevices.length}
        drawShapeType={drawShapeType}
        setDrawShapeType={setDrawShapeType}
        drawRoomZoneMode={drawRoomZoneMode}
        placingDevice={placingDevice}
        placingRoom={placingRoom}
        cancelActiveMode={cancelActiveMode}
        undoCount={undoCount}
        redoCount={redoCount}
        handleUndo={handleUndo}
        handleRedo={handleRedo}
        snapToGrid={snapToGrid}
        setSnapToGrid={setSnapToGrid}
        magneticWallSnap={magneticWallSnap}
        setMagneticWallSnap={setMagneticWallSnap}
        autoSnapRoomEnabled={autoSnapRoomEnabled}
        setAutoSnapRoomEnabled={setAutoSnapRoomEnabled}
        activeAdminRoomId={activeAdminRoomId}
        handleDeleteRoomZone={handleDeleteRoomZone}
      />
    </>
  )
}


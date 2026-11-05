import React, { useState, useEffect, useMemo, useRef, useCallback } from "react"
import { ThreeViewport, DEFAULT_VIEW_STATE } from "@/components/ThreeViewport"
import { DeviceModal } from "@/components/DeviceModal"
import { RoomModal } from "@/components/RoomModal"
import RackulaModal from "@/components/RackulaModal"
import { AdminToolbar } from "@/components/AdminToolbar"
import {
  M3Button,
  M3IconButton,
  M3SegmentedButtonSet,
  M3SegmentedButton,
  M3Badge,
  M3Divider,
  M3Fab,
  M3Dialog,
  M3Tabs,
  M3PrimaryTab,
  M3ChipSet,
  M3FilterChip,
  M3AssistChip,
  M3TextField,
  M3Switch,
} from "@/components/m3"
import {
  FLOORS,
  DEVICE_CATEGORIES,
  ROOM_TYPES,
  MODEL_CATALOG,
  findMatchingRoomForPoint,
  computePolygonArea,
  clampPointToRoomBounds,
} from "@/data/twinData"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Input, SelectNative } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet"
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/components/ui/toaster"
import {
  Menu,
  Layers,
  Building2,
  Radar,
  ShieldCheck,
  Search,
  Sun,
  Moon,
  RotateCcw,
  MapPin,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Plus,
  Trash2,
  Crosshair,
  FolderTree,
  ListFilter,
  Sparkles,
  Lock,
  Wifi,
  Server,
  Download,
  SquareDashed,
  Undo2,
  Redo2,
  Compass,
  Move,
  Maximize2,
  Eye,
  Grid,
  Tag,
  Save,
  Pin,
  PinOff,
} from "lucide-react"

// Helper to auto-increment room number after drawing (e.g. "101" -> "102", "G01" -> "G02")

export function ViewerMenu({
  adminAuthenticated,
  devices,
  directorySearch,
  expandedDirectoryRoomId,
  filteredDirectoryRooms,
  filteredPlacedDevices,
  handleResetToAdminDefaultView,
  handleSaveAsAdminDefaultView,
  isAdminRoute,
  menuOpen,
  menuPinned,
  networks,
  onOpenRackula,
  placedDevices,
  roomDirectorySearch,
  rooms,
  setDirectorySearch,
  setExpandedDirectoryRoomId,
  setMainViewMode,
  setMenuOpen,
  setModalOpen,
  setRoomDirectorySearch,
  setRoomModalOpen,
  setSelectedDeviceId,
  setSelectedRackId,
  setSelectedRoomId,
  toggleAllCategories,
  toggleCategoryFilter,
  toggleMenuPinned,
  updateView,
  viewState,
  viewportRef,
}) {
  return (
    <>
      {/* 4. MATERIAL 3 NAVIGATION DRAWER (Organized Controls & Directory) */}
      <Sheet open={menuOpen} onOpenChange={setMenuOpen} modal={!menuPinned}>
        <SheetContent
          side="left"
          hideOverlay={menuPinned}
          onInteractOutside={(e) => { if (menuPinned) e.preventDefault() }}
          className="w-[360px] sm:w-[400px] p-0 flex flex-col rounded-r-2xl bg-card/95 backdrop-blur-xl border-r border-border shadow-lg"
        >
          <SheetHeader className="p-6 pb-4 border-b border-border/60 bg-secondary/30">
            <div className="flex items-center gap-2.5">
              <div className="h-9 w-9 rounded-2xl bg-primary/20 border border-primary/40 flex items-center justify-center text-primary">
                <Layers className="h-5 w-5" />
              </div>
              <div>
                <SheetTitle className="text-base font-bold">เมนูควบคุมอาคาร 3D</SheetTitle>
                <div className="text-[11px] text-muted-foreground mt-0.5">Navigation drawer · ปักหมุดเพื่อให้เมนูค้างไว้</div>
              </div>
              <M3IconButton
                variant="standard"
                className="ml-auto mr-7 hidden md:inline-flex"
                ariaLabel={menuPinned ? "ปลดหมุดเมนู" : "ปักหมุดเมนูค้างไว้"}
                title={menuPinned ? "ปลดหมุดเมนู" : "ปักหมุดเมนูค้างไว้"}
                toggle
                selected={menuPinned}
                onClick={toggleMenuPinned}
              >
                {menuPinned ? <PinOff className="h-4 w-4 text-primary" /> : <Pin className="h-4 w-4" />}
              </M3IconButton>
            </div>
            <SheetDescription className="text-xs text-muted-foreground mt-2">
              จัดการมุมมองโครงสร้างอาคาร เปิด/ปิดเลเยอร์ กรองเครือข่าย และค้นหาอุปกรณ์ที่จัดวางแล้ว
            </SheetDescription>
          </SheetHeader>

          <div className="flex-1 overflow-y-auto px-5 py-4">
            <Accordion
              type="multiple"
              defaultValue={["floors", "layers", "filters", "directory"]}
              className="w-full space-y-2"
            >
              {/* SECTION 1: FLOOR & CAMERA CONTROLS */}
              <AccordionItem value="floors" className="border border-border/60 rounded-2xl px-3.5 py-1 bg-secondary/20">
                <AccordionTrigger className="hover:no-underline py-2.5">
                  <span className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-primary">
                    <Building2 className="h-4 w-4" />
                    1. เลือกชั้นอาคาร & มุมกล้อง (Floors & View)
                  </span>
                </AccordionTrigger>
                <AccordionContent className="space-y-3 pb-3">
                  <div className="grid grid-cols-2 gap-1.5">
                    <Button
                      size="sm"
                      variant={viewState.selectedFloor === "all" ? "default" : "outline"}
                      className="col-span-2 justify-start text-xs h-9 rounded-full px-3.5 shadow-sm"
                      onClick={() => updateView({ selectedFloor: "all" })}
                    >
                      🏢 แสดงทุกชั้นรวมกัน (All Floors)
                    </Button>
                    {FLOORS.map((fl) => (
                      <Button
                        key={fl.index}
                        size="sm"
                        variant={
                          String(viewState.selectedFloor) === String(fl.index)
                            ? "default"
                            : "outline"
                        }
                        className="justify-start text-xs h-9 rounded-full px-3.5 shadow-sm"
                        onClick={() => updateView({ selectedFloor: String(fl.index) })}
                      >
                        {fl.shortLabel} · {fl.label}
                      </Button>
                    ))}
                  </div>
                  <Button
                    size="sm"
                    variant="secondary"
                    className="w-full text-xs rounded-full h-9 shadow-sm"
                    onClick={() => {
                      updateView({ selectedFloor: "all" })
                      viewportRef.current?.resetCamera()
                    }}
                  >
                    <RotateCcw className="h-3.5 w-3.5 mr-1.5 text-primary" />
                    รีเซ็ตมุมกล้องเริ่มต้น (Reset 3D Orbit)
                  </Button>
                </AccordionContent>
              </AccordionItem>

              {/* SECTION 2: 3D LAYER SWITCHES (Complete 8 Architectural & Spatial Layers) */}
              <AccordionItem value="layers">
                <AccordionTrigger>
                  <span className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider">
                    <Sparkles className="h-4 w-4 text-primary" />
                    2. เลเยอร์โครงสร้างอาคาร 3D (Display Layers)
                  </span>
                </AccordionTrigger>
                <AccordionContent className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label
                      className="text-xs cursor-pointer"
                      onClick={() => updateView({ exploded: !viewState.exploded })}
                    >
                      แยกชั้นอาคารแนวตั้ง (Explode Floors)
                    </Label>
                    <Switch
                      id="layer-exploded"
                      checked={viewState.exploded}
                      onCheckedChange={(v) => updateView({ exploded: v })}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label
                      className="text-xs cursor-pointer"
                      onClick={() => updateView({ showGlass: !viewState.showGlass })}
                    >
                      แสดงกระจกหน้าต่างอาคาร (Window Glass Layer)
                    </Label>
                    <Switch
                      id="layer-glass"
                      checked={viewState.showGlass}
                      onCheckedChange={(v) => updateView({ showGlass: v })}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label
                      className="text-xs cursor-pointer"
                      onClick={() => updateView({ showWalls: !viewState.showWalls })}
                    >
                      แสดงผนังอาคาร (Architectural Walls)
                    </Label>
                    <Switch
                      id="layer-walls"
                      checked={viewState.showWalls}
                      onCheckedChange={(v) => updateView({ showWalls: v })}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label
                      className="text-xs cursor-pointer"
                      onClick={() => updateView({ showRoof: !viewState.showRoof })}
                    >
                      แสดงหลังคาดาดฟ้า (Rooftop Canopies)
                    </Label>
                    <Switch
                      id="layer-roof"
                      checked={viewState.showRoof}
                      onCheckedChange={(v) => updateView({ showRoof: v })}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label
                      className="text-xs cursor-pointer"
                      onClick={() =>
                        updateView({ showBasketball: !viewState.showBasketball })
                      }
                    >
                      แสดงสนามบาสเกตบอลดาดฟ้า (Basketball Court)
                    </Label>
                    <Switch
                      id="layer-basketball"
                      checked={viewState.showBasketball}
                      onCheckedChange={(v) => updateView({ showBasketball: v })}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label
                      className="text-xs cursor-pointer"
                      onClick={() => updateView({ showArrows: !viewState.showArrows })}
                    >
                      แสดงลูกศรทิศทางจราจร (Traffic Flow Arrows)
                    </Label>
                    <Switch
                      id="layer-arrows"
                      checked={viewState.showArrows}
                      onCheckedChange={(v) => updateView({ showArrows: v })}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label
                      className="text-xs cursor-pointer"
                      onClick={() => updateView({ showPlans: !viewState.showPlans })}
                    >
                      แสดงแปลนพื้นสถาปัตย์ 2D (CAD Blueprints)
                    </Label>
                    <Switch
                      id="layer-plans"
                      checked={viewState.showPlans}
                      onCheckedChange={(v) => updateView({ showPlans: v })}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label
                      className="text-xs cursor-pointer"
                      onClick={() => updateView({ showRooms: !viewState.showRooms })}
                    >
                      แสดงป้ายหมายเลขห้อง (Room Number Tags)
                    </Label>
                    <Switch
                      id="layer-rooms"
                      checked={viewState.showRooms}
                      onCheckedChange={(v) => updateView({ showRooms: v })}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label
                      className="text-xs cursor-pointer"
                      onClick={() =>
                        updateView({
                          showDevices: !(viewState.showDevices ?? true),
                        })
                      }
                    >
                      แสดงอุปกรณ์และโมเดล 3D (All 3D Devices & Racks)
                    </Label>
                    <Switch
                      id="layer-devices"
                      checked={viewState.showDevices ?? true}
                      onCheckedChange={(v) => updateView({ showDevices: v })}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label
                      className="text-xs cursor-pointer"
                      onClick={() =>
                        updateView({
                          showDeviceLabels: !(viewState.showDeviceLabels ?? true),
                        })
                      }
                    >
                      แสดงป้ายชื่ออุปกรณ์ 3D (Device Badges)
                    </Label>
                    <Switch
                      id="layer-device-labels"
                      checked={viewState.showDeviceLabels ?? true}
                      onCheckedChange={(v) => updateView({ showDeviceLabels: v })}
                    />
                  </div>

                  <div className="pt-2 border-t border-border flex flex-col gap-1.5">
                    <Button
                      size="sm"
                      variant="outline"
                      className="w-full text-xs h-7 justify-center gap-1.5"
                      onClick={handleResetToAdminDefaultView}
                      title="คืนค่าการแสดงผลเลเยอร์กลับเป็นค่าเริ่มต้นกลาง"
                    >
                      <RotateCcw className="h-3 w-3" />
                      คืนค่าเริ่มต้น (Reset to Default)
                    </Button>
                    {isAdminRoute && adminAuthenticated && (
                      <Button
                        size="sm"
                        variant="secondary"
                        className="w-full text-xs h-7 justify-center gap-1.5 border border-primary/30 text-primary hover:bg-primary/10"
                        onClick={handleSaveAsAdminDefaultView}
                        title="บันทึกมุมมองและการเปิด-ปิดเลเยอร์ปัจจุบันเป็นค่าเริ่มต้นกลางสำหรับผู้ใช้งานทุกคน"
                      >
                        <Save className="h-3 w-3" />
                        บันทึกเป็นค่าเริ่มต้นกลางสำหรับทุกคน
                      </Button>
                    )}
                  </div>
                </AccordionContent>
              </AccordionItem>

              {/* SECTION 3: NETWORK, CATEGORY & STATUS FILTERS */}
              <AccordionItem value="filters">
                <AccordionTrigger>
                  <span className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider">
                    <ListFilter className="h-4 w-4 text-primary" />
                    3. กรองวงเครือข่าย หมวดหมู่ & สถานะ (Filters)
                  </span>
                </AccordionTrigger>
                <AccordionContent className="space-y-3">
                  <div className="space-y-1.5">
                    <Label className="text-xs text-muted-foreground">
                      กรองตามสถานะ (Device Status)
                    </Label>
                    <div className="grid grid-cols-4 gap-1.5">
                      {["all", "Online", "Warning", "Offline"].map((st) => (
                        <Button
                          key={st}
                          size="sm"
                          variant={viewState.filterStatus === st ? "default" : "outline"}
                          className="h-7 text-xs"
                          onClick={() => updateView({ filterStatus: st })}
                        >
                          {st === "all" ? "ALL" : st}
                        </Button>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <Label className="text-xs text-muted-foreground">
                      กรองวงเครือข่าย (Subnet CIDR)
                    </Label>
                    <SelectNative
                      value={viewState.filterSubnet}
                      onChange={(e) => updateView({ filterSubnet: e.target.value })}
                    >
                      <option value="all">ทุกวงเครือข่าย (All Subnets)</option>
                      {networks.map((net, idx) => (
                        <option key={net.id ? `${net.id}-${idx}` : net.cidr || idx} value={net.cidr}>
                          {net.name || net.cidr} ({net.cidr})
                        </option>
                      ))}
                    </SelectNative>
                  </div>

                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <Label className="text-xs text-muted-foreground">
                        หมวดหมู่อุปกรณ์ (Device Categories)
                      </Label>
                      <button
                        type="button"
                        onClick={toggleAllCategories}
                        className="text-[11px] text-primary hover:underline cursor-pointer"
                      >
                        {viewState.enabledCategories.length === DEVICE_CATEGORIES.length
                          ? "ซ่อนทั้งหมด"
                          : "เลือกทั้งหมด"}
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {DEVICE_CATEGORIES.map((cat) => {
                        const active = viewState.enabledCategories.includes(cat.id)
                        return (
                          <button
                            key={cat.id}
                            type="button"
                            onClick={() => toggleCategoryFilter(cat.id)}
                            className={`px-2 py-1 rounded-md border text-[11px] flex items-center gap-1 transition cursor-pointer ${
                              active
                                ? "border-primary/60 bg-primary/15 text-foreground font-medium"
                                : "border-border bg-secondary/20 text-muted-foreground opacity-60"
                            }`}
                          >
                            <span>{cat.icon}</span>
                            <span>{cat.id}</span>
                          </button>
                        )
                      })}
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>

              {/* SECTION 4: PLACED DEVICE DIRECTORY */}
              <AccordionItem value="directory">
                <AccordionTrigger>
                  <span className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider">
                    <FolderTree className="h-4 w-4 text-primary" />
                    4. รายการอุปกรณ์ที่จัดวางแล้ว ({filteredPlacedDevices.length})
                  </span>
                </AccordionTrigger>
                <AccordionContent className="space-y-3">
                  <div className="relative">
                    <Search className="h-3.5 w-3.5 absolute left-2.5 top-2.5 text-muted-foreground" />
                    <Input
                      value={directorySearch}
                      onChange={(e) => setDirectorySearch(e.target.value)}
                      placeholder="ค้นหาชื่อ, IP, ห้อง..."
                      className="pl-8 h-8 text-xs"
                    />
                  </div>

                  {filteredPlacedDevices.length === 0 ? (
                    <div className="rounded-lg border border-dashed border-border p-4 text-center text-xs text-muted-foreground">
                      ยังไม่มีอุปกรณ์ที่ถูกจัดวางในหมวดหมู่นี้
                      <br />
                      <span className="text-[11px] opacity-80">
                        (อุปกรณ์ที่ยังไม่ถูกจัดวางโดย Admin จะไม่ถูกนำมาแสดงผล)
                      </span>
                    </div>
                  ) : (
                    <div className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
                      {filteredPlacedDevices.map((dev) => {
                        const fl = FLOORS.find((f) => f.index === Number(dev.floorIdx))
                        const stLower = String(dev.status || "Online").toLowerCase()
                        return (
                          <button
                            key={dev.id}
                            onClick={() => {
                              updateView({ selectedFloor: String(dev.floorIdx ?? 0) })
                              viewportRef.current?.flyTo(dev.position, Number(dev.floorIdx ?? 0))
                              setSelectedDeviceId(dev.id)
                              setModalOpen(true)
                              if (!menuPinned) setMenuOpen(false)
                            }}
                            className="w-full text-left rounded-lg border border-border bg-secondary/20 hover:bg-secondary/50 p-2.5 transition flex items-center justify-between gap-2 cursor-pointer"
                          >
                            <div className="min-w-0">
                              <div className="text-xs font-semibold truncate flex items-center gap-1.5">
                                <span
                                  className={`h-2 w-2 rounded-full ${
                                    stLower === "online"
                                      ? "bg-emerald-400"
                                      : stLower === "warning"
                                      ? "bg-amber-400"
                                      : "bg-rose-400"
                                  }`}
                                />
                                {dev.name || dev.ip}
                              </div>
                              <div className="text-[11px] font-mono text-muted-foreground truncate">
                                {dev.ip} · {fl ? fl.shortLabel : `F${dev.floorIdx}`} · ห้อง{" "}
                                {dev.roomNumber || "-"}
                              </div>
                            </div>
                            <Badge variant="outline" className="text-[10px] shrink-0 uppercase">
                              {dev.category}
                            </Badge>
                          </button>
                        )
                      })}
                    </div>
                  )}
                </AccordionContent>
              </AccordionItem>

              {/* SECTION 5: SPATIAL ROOMS DIRECTORY (Fly-to-Room & Room Health Overview) */}
              <AccordionItem value="rooms-directory">
                <AccordionTrigger>
                  <span className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider">
                    <MapPin className="h-4 w-4 text-primary" />
                    5. สารบัญห้องแยกตามชั้น ({filteredDirectoryRooms.length})
                  </span>
                </AccordionTrigger>
                <AccordionContent className="space-y-3">
                  <div className="relative">
                    <Search className="h-3.5 w-3.5 absolute left-2.5 top-2.5 text-muted-foreground" />
                    <Input
                      value={roomDirectorySearch}
                      onChange={(e) => setRoomDirectorySearch(e.target.value)}
                      placeholder="ค้นหาเลขห้อง, ชื่อห้อง, ประเภท..."
                      className="pl-8 h-8 text-xs"
                    />
                  </div>

                  {filteredDirectoryRooms.length === 0 ? (
                    <div className="rounded-lg border border-dashed border-border p-4 text-center text-xs text-muted-foreground">
                      ยังไม่มีข้อมูลห้องในชั้นที่เลือก
                    </div>
                  ) : (
                    <div className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
                      {filteredDirectoryRooms.map((rm) => {
                        const fl = FLOORS.find((f) => f.index === Number(rm.floorIdx ?? 0))
                        const rMeta =
                          ROOM_TYPES.find((r) => r.id === rm.roomType) || ROOM_TYPES[1]
                        const rmDevices = placedDevices.filter(
                          (d) =>
                            d.isPlaced &&
                            Number(d.floorIdx ?? 0) === Number(rm.floorIdx ?? 0) &&
                            (d.roomId === rm.id ||
                              (d.roomNumber && d.roomNumber === rm.roomNumber))
                        )
                        const hasOffline = rmDevices.some(
                          (d) => String(d.status || "").toLowerCase() === "offline"
                        )
                        const hasWarning = rmDevices.some(
                          (d) => String(d.status || "").toLowerCase() === "warning"
                        )
                        const dotColor =
                          rmDevices.length === 0
                            ? "bg-border"
                            : hasOffline
                            ? "bg-rose-400"
                            : hasWarning
                            ? "bg-amber-400"
                            : "bg-emerald-400"

                        const isExpanded = expandedDirectoryRoomId === rm.id
                        return (
                          <div
                            key={rm.id}
                            className={`rounded-lg border transition ${
                              isExpanded
                                ? "border-primary/60 bg-secondary/40 shadow-md"
                                : "border-border bg-secondary/20 hover:bg-secondary/40"
                            }`}
                          >
                            <div
                              onClick={() => {
                                setExpandedDirectoryRoomId((prev) =>
                                  prev === rm.id ? null : rm.id
                                )
                                updateView({
                                  selectedFloor: String(rm.floorIdx ?? 0),
                                  showRooms: true,
                                })
                                viewportRef.current?.flyTo(
                                  rm.position,
                                  Number(rm.floorIdx ?? 0)
                                )
                              }}
                              className="p-2.5 flex items-center justify-between gap-2 cursor-pointer select-none"
                            >
                              <div className="min-w-0">
                                <div className="text-xs font-semibold truncate flex items-center gap-1.5">
                                  <span className={`h-2 w-2 rounded-full shrink-0 ${dotColor}`} />
                                  <span>{rMeta.icon}</span>
                                  <span className="font-mono text-primary font-bold">
                                    [{rm.roomNumber}]
                                  </span>
                                  <span className="truncate">{rm.name}</span>
                                </div>
                                <div className="text-[11px] font-mono text-muted-foreground truncate mt-0.5">
                                  {fl ? fl.shortLabel : `F${rm.floorIdx}`} · อุปกรณ์ {rmDevices.length} รายการ
                                </div>
                              </div>
                              <div className="flex items-center gap-1 shrink-0">
                                <Badge
                                  variant={rmDevices.length > 0 ? "secondary" : "outline"}
                                  className="text-[10px] px-1.5 py-0 font-mono"
                                >
                                  {rmDevices.length}
                                </Badge>
                                <span className={`text-xs text-muted-foreground transition-transform duration-200 ${isExpanded ? "rotate-180" : ""}`}>
                                  ▼
                                </span>
                              </div>
                            </div>

                            {/* Rollout Device List & Room Actions */}
                            {isExpanded && (
                              <div className="px-2.5 pb-2.5 pt-1 border-t border-border/50 animate-in fade-in duration-150 space-y-1.5">
                                <div className="flex items-center justify-between gap-2 text-[11px] text-muted-foreground">
                                  <span>รายการอุปกรณ์ในห้อง:</span>
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    className="h-6 px-2 text-[10px] text-primary hover:text-primary gap-1"
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      setSelectedRoomId(rm.id)
                                      setRoomModalOpen(true)
                                      if (!menuPinned) setMenuOpen(false)
                                    }}
                                  >
                                    <Building2 className="h-3 w-3" />
                                    <span>ข้อมูลห้อง</span>
                                  </Button>
                                </div>

                                {rmDevices.length === 0 ? (
                                  <div className="text-[11px] text-muted-foreground italic py-1 px-1 text-center bg-background/40 rounded border border-dashed border-border/60">
                                    ยังไม่มีอุปกรณ์ติดตั้งในห้องนี้
                                  </div>
                                ) : (
                                  <div className="space-y-1 max-h-40 overflow-y-auto pr-0.5">
                                    {rmDevices.map((dev) => {
                                      const isRack = dev.modelType === "server_rack"
                                      const dCatMeta = DEVICE_CATEGORIES.find((c) => c.id === dev.category)
                                      const devStatus = String(dev.status || "").toLowerCase()
                                      return (
                                        <div
                                          key={dev.id}
                                          onClick={(e) => {
                                            e.stopPropagation()
                                            if (!menuPinned) setMenuOpen(false)
                                            if (isRack) {
                                              setSelectedRackId(dev.id)
                                              if (onOpenRackula) {
                                                onOpenRackula(dev.id)
                                              } else if (setMainViewMode) {
                                                setMainViewMode(dev.id)
                                              }
                                            } else {
                                              setSelectedDeviceId(dev.id)
                                              setModalOpen(true)
                                            }
                                          }}
                                          className={`flex items-center justify-between gap-2 p-1.5 rounded-md text-xs transition cursor-pointer border ${
                                            isRack
                                              ? "bg-accent/30 hover:bg-accent/50 border-primary/40 text-primary"
                                              : "bg-background/60 hover:bg-background/90 border-border/50 text-foreground"
                                          }`}
                                          title={
                                            isRack
                                              ? `เปิดจัดการตู้แร็ค Rackula (${dev.name || dev.ip})`
                                              : `เปิดรายละเอียดอุปกรณ์ (${dev.name || dev.ip})`
                                          }
                                        >
                                          <div className="min-w-0 flex items-center gap-1.5">
                                            <span
                                              className={`h-1.5 w-1.5 rounded-full shrink-0 ${
                                                devStatus === "offline"
                                                  ? "bg-rose-400"
                                                  : devStatus === "warning"
                                                  ? "bg-amber-400"
                                                  : "bg-emerald-400"
                                              }`}
                                            />
                                            <span className="shrink-0">{isRack ? "🗄️" : (dCatMeta?.icon || "📦")}</span>
                                            <span className="font-semibold truncate">{dev.name || dev.ip}</span>
                                          </div>
                                          <div className="flex items-center gap-1 shrink-0">
                                            {isRack ? (
                                              <Badge className="text-[9px] px-1 py-0 bg-primary/20 text-primary border-primary/40 font-mono">
                                                🖥️ ตู้แร็ค
                                              </Badge>
                                            ) : (
                                              <span className="text-[10px] font-mono text-muted-foreground">{dev.ip || "-"}</span>
                                            )}
                                          </div>
                                        </div>
                                      )
                                    })}
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  )}
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        </SheetContent>
      </Sheet>
    </>
  )
}

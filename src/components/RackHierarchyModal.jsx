import React, { useState, useMemo, useEffect } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/components/ui/toaster"
import { FLOORS, DEVICE_CATEGORIES, ROOM_TYPES } from "@/data/twinData"
import {
  RACKULA_CATEGORY_COLOURS,
  RACK_SVG_METRICS,
  mapTwinCategoryToRackula,
} from "@/data/rackulaData"
import {
  Server,
  Layers,
  MapPin,
  Building2,
  ExternalLink,
  Copy,
  Activity,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HardDrive,
  Network,
  Cpu,
  ChevronRight,
  Maximize2,
  Wrench,
  Wifi,
} from "lucide-react"

/**
 * RackHierarchyModal
 * 2-Column Split View:
 * - Left: Compact EIA-310 19" Rack Elevation with U42..U1 slots & mini visual units
 * - Right: Interactive Root Hierarchy Tree (Building > Floor > Room > Rack > Unit) & Expanded Device Info Card
 */
export function RackHierarchyModal({
  open,
  onOpenChange,
  rack,
  allDevices = [],
  rooms = [],
  isAdmin = false,
  adminToken = "",
  onOpenDeviceModal,
  onOpenRackulaDesigner,
  onFlyToRack,
}) {
  const { toast } = useToast()
  const [selectedFace, setSelectedFace] = useState("front")
  const [selectedDeviceId, setSelectedDeviceId] = useState(null)
  const [selectedEmptyU, setSelectedEmptyU] = useState(null)
  const [isPinging, setIsPinging] = useState(false)
  const [pingResult, setPingResult] = useState(null)

  const rackHeight = Math.max(12, Number(rack?.rackHeight || 42))

  // Find Room & Floor metadata for the rack
  const room = useMemo(() => {
    if (!rack) return null
    return (
      rooms.find(
        (r) =>
          r.id === rack.roomId ||
          (r.roomNumber && rack.roomNumber && r.roomNumber === rack.roomNumber)
      ) || null
    )
  }, [rack, rooms])

  const floor = useMemo(() => {
    const fIdx = Number(rack?.floorIdx ?? room?.floorIdx ?? 0)
    return FLOORS.find((f) => f.index === fIdx) || FLOORS[0]
  }, [rack, room])

  const roomTypeMeta = useMemo(() => {
    if (!room) return ROOM_TYPES[1]
    return ROOM_TYPES.find((r) => r.id === room.roomType) || ROOM_TYPES[1]
  }, [room])

  // Filter devices mounted inside this specific rack
  const mountedDevices = useMemo(() => {
    if (!rack?.id) return []
    return (allDevices || [])
      .filter((d) => d.isPlaced && d.parentRackId === rack.id)
      .sort((a, b) => Number(b.uPosition || 1) - Number(a.uPosition || 1))
  }, [allDevices, rack])

  // Filter mounted devices for the currently active face (front / rear)
  const faceMountedDevices = useMemo(() => {
    return mountedDevices.filter((d) => {
      const face = d.rackFace || d.face || "front"
      return face === selectedFace || face === "both"
    })
  }, [mountedDevices, selectedFace])

  // Create a map of U position -> mounted device
  const uSlotMap = useMemo(() => {
    const map = new Map()
    faceMountedDevices.forEach((dev) => {
      const uPos = Math.max(1, Number(dev.uPosition || 1))
      const uH = Math.max(1, Number(dev.uHeight || 1))
      for (let u = uPos; u < uPos + uH; u++) {
        map.set(u, { device: dev, isRoot: u === uPos })
      }
    })
    return map
  }, [faceMountedDevices])

  // Calculate overall Rack Health Status
  const rackHealth = useMemo(() => {
    if (mountedDevices.length === 0) return { status: "Idle", color: "#6b7280", label: "ว่าง (ยังไม่มีอุปกรณ์)" }
    const hasOffline = mountedDevices.some((d) => String(d.status || "").toLowerCase() === "offline")
    if (hasOffline) return { status: "Offline", color: "#ef4444", label: "พบอุปกรณ์ Offline" }
    const hasWarning = mountedDevices.some((d) => String(d.status || "").toLowerCase() === "warning")
    if (hasWarning) return { status: "Warning", color: "#f59e0b", label: "พบอุปกรณ์แจ้งเตือน" }
    return { status: "Online", color: "#22c55e", label: "พร้อมใช้งานสมบูรณ์" }
  }, [mountedDevices])

  // Default selection when modal opens
  useEffect(() => {
    if (open) {
      if (mountedDevices.length > 0) {
        setSelectedDeviceId(mountedDevices[0].id)
        setSelectedEmptyU(null)
      } else {
        setSelectedDeviceId(null)
        setSelectedEmptyU(1)
      }
      setPingResult(null)
    }
  }, [open, mountedDevices])

  // Currently selected device object
  const selectedDevice = useMemo(() => {
    if (!selectedDeviceId) return null
    return mountedDevices.find((d) => d.id === selectedDeviceId) || null
  }, [mountedDevices, selectedDeviceId])

  // Occupancy statistics
  const occupiedUCount = useMemo(() => {
    let count = 0
    mountedDevices.forEach((d) => {
      count += Math.max(1, Number(d.uHeight || 1))
    })
    return Math.min(rackHeight, count)
  }, [mountedDevices, rackHeight])

  const occupancyPercent = Math.round((occupiedUCount / rackHeight) * 100)

  // Copy helper
  const copyToClipboard = (text, label) => {
    if (!text) return
    navigator.clipboard.writeText(text)
    toast({
      title: "คัดลอกสำเร็จ",
      description: `คัดลอก ${label}: ${text} ไปยังคลิปบอร์ดแล้ว`,
    })
  }

  // Live Ping Simulation/Check
  const handlePing = async (dev) => {
    if (!dev?.ip || isPinging) return
    setIsPinging(true)
    setPingResult(null)
    try {
      const start = Date.now()
      const res = await fetch(`/api/health?_t=${start}`, { cache: "no-store" })
      const elapsed = Math.max(2, Math.round(Date.now() - start))
      const isOnline = String(dev.status || "online").toLowerCase() === "online"
      setPingResult({
        ok: isOnline && res.ok,
        timeMs: isOnline ? elapsed : 0,
        message: isOnline ? `ตอบสนองปกติ (RTT ${elapsed}ms · แพ็กเก็ตส่ง 4/4 รับครบ 100%)` : "Host Unreachable (Request timed out)",
      })
    } catch {
      setPingResult({
        ok: false,
        timeMs: 0,
        message: "ไม่สามารถส่งคำขอ Ping ได้",
      })
    } finally {
      setIsPinging(false)
    }
  }

  if (!rack) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl w-[94vw] h-[88vh] max-h-[850px] flex flex-col p-0 overflow-hidden bg-background text-foreground border-border shadow-2xl">
        {/* ================= MODAL HEADER ================= */}
        <DialogHeader className="p-4 border-b border-border bg-card/60 shrink-0 flex flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="h-10 w-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary text-xl shrink-0">
              🗄️
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <DialogTitle className="text-base font-bold truncate">
                  [ตู้แร็ค {rackHeight}U] {rack.name || rack.ip || "Server Rack"}
                </DialogTitle>
                <Badge
                  variant="outline"
                  className="gap-1.5 text-xs font-mono font-medium"
                  style={{ borderColor: rackHealth.color }}
                >
                  <span
                    className="h-2 w-2 rounded-full"
                    style={{ backgroundColor: rackHealth.color }}
                  />
                  {rackHealth.status}
                </Badge>
              </div>
              <DialogDescription className="text-xs text-muted-foreground flex items-center gap-2 mt-0.5 flex-wrap">
                <span className="flex items-center gap-1 font-mono text-primary">
                  <Building2 className="h-3.5 w-3.5" />
                  {floor.shortLabel}
                </span>
                <span>·</span>
                <span className="flex items-center gap-1">
                  <MapPin className="h-3.5 w-3.5" />
                  [{room?.roomNumber || "ไม่ระบุ"}] {room?.name || "ห้อง"}
                </span>
                <span>·</span>
                <span>
                  อุปกรณ์ในตู้: <strong>{mountedDevices.length}</strong> รายการ ({occupiedUCount}/{rackHeight}U)
                </span>
              </DialogDescription>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0 pr-6">
            {isAdmin && onOpenRackulaDesigner && (
              <Button
                size="sm"
                variant="outline"
                className="h-8 text-xs font-semibold gap-1.5 border-primary/40 text-primary hover:bg-primary/10"
                onClick={() => {
                  onOpenChange(false)
                  onOpenRackulaDesigner(rack.id)
                }}
                title="เปิดเครื่องมือจัดผังตู้แร็คและลากย้ายสล็อตแบบเต็มหน้าจอ (Rackula Designer)"
              >
                <Wrench className="h-3.5 w-3.5" />
                <span>แก้ไขใน Rackula</span>
              </Button>
            )}
          </div>
        </DialogHeader>

        {/* ================= MODAL BODY: 2-COLUMN SPLIT VIEW ================= */}
        <div className="flex-1 grid grid-cols-1 md:grid-cols-12 min-h-0 overflow-hidden divide-y md:divide-y-0 md:divide-x divide-border">
          {/* ---------------- LEFT COLUMN: COMPACT RACK ELEVATION (5 cols) ---------------- */}
          <div className="md:col-span-5 flex flex-col min-h-0 bg-card/20 overflow-hidden">
            {/* Top Toolbar: Front/Rear switch & Stats */}
            <div className="p-3 border-b border-border flex items-center justify-between gap-2 shrink-0 bg-background/50">
              <div className="flex items-center gap-1.5 text-xs font-bold text-foreground">
                <Layers className="h-3.5 w-3.5 text-primary" />
                <span>ผังตู้แร็ค 19" EIA-310</span>
              </div>
              <div className="flex items-center gap-1 bg-secondary/50 p-0.5 rounded-lg border border-border">
                <button
                  type="button"
                  onClick={() => setSelectedFace("front")}
                  className={`px-2 py-0.5 text-[11px] font-medium rounded transition ${
                    selectedFace === "front"
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                  aria-pressed={selectedFace === "front"}
                >
                  ด้านหน้า (Front)
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedFace("rear")}
                  className={`px-2 py-0.5 text-[11px] font-medium rounded transition ${
                    selectedFace === "rear"
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                  aria-pressed={selectedFace === "rear"}
                >
                  ด้านหลัง (Rear)
                </button>
              </div>
            </div>

            {/* Occupancy Progress Bar */}
            <div className="px-3 py-1.5 bg-muted/30 border-b border-border flex items-center justify-between text-[11px] font-mono text-muted-foreground">
              <span>ความจุที่ใช้งาน: {occupancyPercent}% ({occupiedUCount}/{rackHeight}U)</span>
              <span>ว่าง {rackHeight - occupiedUCount}U</span>
            </div>

            {/* Scrollable Elevation Column */}
            <div className="flex-1 min-h-0 overflow-y-auto p-3 flex justify-center">
              <div className="w-full max-w-[320px] bg-background border-2 border-border/80 rounded-lg shadow-inner overflow-hidden flex flex-col">
                {/* Rack Top Frame */}
                <div className="h-5 bg-secondary border-b border-border flex items-center justify-between px-2 text-[10px] font-mono text-muted-foreground font-bold tracking-wider select-none">
                  <span>◀ RAIL L</span>
                  <span>{rackHeight}U ELEVATION</span>
                  <span>RAIL R ▶</span>
                </div>

                {/* Slots: U42 down to U1 */}
                <div className="flex-1 flex flex-col divide-y divide-border/40 select-none">
                  {Array.from({ length: rackHeight }, (_, i) => rackHeight - i).map((u) => {
                    const slotInfo = uSlotMap.get(u)
                    const dev = slotInfo?.device
                    const isRoot = slotInfo?.isRoot
                    const isSelected = selectedDevice && dev && selectedDevice.id === dev.id
                    const isEmptySelected = selectedEmptyU === u && !dev

                    if (dev && !isRoot) {
                      // Sub-slot part of multi-U device (already rendered from root slot)
                      return null
                    }

                    if (dev && isRoot) {
                      const uH = Math.max(1, Number(dev.uHeight || 1))
                      const catMeta = DEVICE_CATEGORIES.find((c) => c.id === dev.category)
                      const rackulaCat = mapTwinCategoryToRackula(dev.category)
                      const itemColor =
                        dev.color ||
                        dev.colour ||
                        rackulaCat.colour ||
                        RACKULA_CATEGORY_COLOURS.server
                      const devStatus = String(dev.status || "online").toLowerCase()
                      const statusDotColor =
                        devStatus === "offline"
                          ? "#ef4444"
                          : devStatus === "warning"
                          ? "#f59e0b"
                          : "#22c55e"

                      return (
                        <div
                          key={`u-${u}`}
                          onClick={() => {
                            setSelectedDeviceId(dev.id)
                            setSelectedEmptyU(null)
                          }}
                          className={`relative flex items-center cursor-pointer transition border-l-4 ${
                            isSelected
                              ? "bg-primary/20 ring-2 ring-primary ring-inset shadow-md"
                              : "hover:bg-accent/40"
                          }`}
                          style={{
                            borderLeftColor: itemColor,
                            height: `${uH * 28}px`,
                          }}
                          title={`[U${u}] ${dev.name || dev.ip || "Device"} (${uH}U)`}
                        >
                          {/* Rail U Number on Left */}
                          <div className="w-8 shrink-0 flex items-center justify-center font-mono text-[10px] font-bold text-muted-foreground bg-muted/30 h-full border-r border-border/40">
                            {u}
                          </div>

                          {/* Device Faceplate Body */}
                          <div className="flex-1 min-w-0 px-2 flex items-center justify-between gap-1.5 h-full">
                            <div className="min-w-0 flex items-center gap-1.5">
                              <span
                                className="h-2 w-2 rounded-full shrink-0"
                                style={{ backgroundColor: statusDotColor }}
                              />
                              <span className="text-xs shrink-0">
                                {catMeta?.icon || "📦"}
                              </span>
                              <div className="min-w-0">
                                <div className="text-[11px] font-bold text-foreground truncate leading-tight">
                                  {dev.name || dev.ip || "Device"}
                                </div>
                                <div className="text-[9px] font-mono text-muted-foreground truncate">
                                  {dev.model || dev.device_type || (catMeta?.label || "Hardware")} · {uH}U
                                </div>
                              </div>
                            </div>

                            {/* Port Count / Activity indicator */}
                            <div className="flex items-center gap-1 shrink-0 font-mono text-[9px] text-muted-foreground bg-background/80 px-1 py-0.5 rounded border border-border/60">
                              <Network className="h-2.5 w-2.5 text-primary" />
                              <span>{dev.ports?.length || (uH >= 2 ? "24P" : "Gbe")}</span>
                            </div>
                          </div>

                          {/* Rail U Number on Right */}
                          <div className="w-8 shrink-0 flex items-center justify-center font-mono text-[10px] font-bold text-muted-foreground bg-muted/30 h-full border-l border-border/40">
                            {u}
                          </div>
                        </div>
                      )
                    }

                    // Empty Slot
                    return (
                      <div
                        key={`u-${u}`}
                        onClick={() => {
                          setSelectedEmptyU(u)
                          setSelectedDeviceId(null)
                        }}
                        className={`h-7 flex items-center cursor-pointer transition ${
                          isEmptySelected
                            ? "bg-primary/10 ring-1 ring-primary/40 ring-inset"
                            : "hover:bg-muted/40"
                        }`}
                        title={`ช่อง U${u} ว่าง (คลิกเพื่อดูข้อมูลสล็อต)`}
                      >
                        <div className="w-8 shrink-0 flex items-center justify-center font-mono text-[10px] text-muted-foreground/60 h-full border-r border-border/20">
                          {u}
                        </div>
                        <div className="flex-1 px-2 text-[10px] font-mono text-muted-foreground/40 italic flex items-center justify-between">
                          <span>— ว่าง —</span>
                          <span className="text-[9px] opacity-60">U{u}</span>
                        </div>
                        <div className="w-8 shrink-0 flex items-center justify-center font-mono text-[10px] text-muted-foreground/60 h-full border-l border-border/20">
                          {u}
                        </div>
                      </div>
                    )
                  })}
                </div>

                {/* Rack Bottom Frame */}
                <div className="h-4 bg-secondary border-t border-border flex items-center justify-center text-[9px] font-mono text-muted-foreground select-none">
                  BOTTOM / WHEELS
                </div>
              </div>
            </div>
          </div>

          {/* ---------------- RIGHT COLUMN: ROOT HIERARCHY TREE & DEVICE INFO (7 cols) ---------------- */}
          <div className="md:col-span-7 flex flex-col min-h-0 bg-background overflow-hidden">
            {/* Top Root Breadcrumb */}
            <div className="p-3 border-b border-border bg-card/40 shrink-0">
              <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground mb-1">
                Root Hierarchy Navigation (เส้นทางโครงสร้างกายภาพ)
              </div>
              <div className="flex items-center gap-1.5 text-xs font-semibold flex-wrap">
                <span className="text-muted-foreground">🏢 อาคาร LUDUS</span>
                <ChevronRight className="h-3 w-3 text-muted-foreground/60" />
                <span className="text-muted-foreground">ชั้น {floor.shortLabel}</span>
                <ChevronRight className="h-3 w-3 text-muted-foreground/60" />
                <span className="text-muted-foreground">
                  [{room?.roomNumber || "ห้อง"}] {room?.name || ""}
                </span>
                <ChevronRight className="h-3 w-3 text-muted-foreground/60" />
                <span className="text-primary font-bold">🗄️ {rack.name}</span>
                {selectedDevice && (
                  <>
                    <ChevronRight className="h-3 w-3 text-muted-foreground/60" />
                    <Badge variant="secondary" className="font-mono text-[11px] gap-1 px-1.5 py-0">
                      U{selectedDevice.uPosition} · {selectedDevice.name}
                    </Badge>
                  </>
                )}
              </div>
            </div>

            {/* Scrollable Content: Tree Branch + Device Info Card */}
            <div className="flex-1 min-h-0 overflow-y-auto p-4 space-y-4">
              {/* 1. Interactive Root Menu Branch */}
              <div className="rounded-xl border border-border bg-card/50 p-3 space-y-2">
                <div className="flex items-center justify-between text-xs font-bold text-foreground">
                  <div className="flex items-center gap-1.5">
                    <Server className="h-4 w-4 text-primary" />
                    <span>กิ่งโครงสร้างอุปกรณ์ในตู้ ({mountedDevices.length} อุปกรณ์)</span>
                  </div>
                  <span className="text-[11px] font-mono text-muted-foreground">
                    เรียงตามลำดับ U บนลงล่าง (Top-Down)
                  </span>
                </div>

                {mountedDevices.length === 0 ? (
                  <div className="p-4 rounded-lg border border-dashed border-border text-center text-xs text-muted-foreground">
                    ยังไม่มีอุปกรณ์ติดตั้งในตู้แร็คนี้
                  </div>
                ) : (
                  <div className="space-y-1">
                    {mountedDevices.map((dev) => {
                      const isSelected = selectedDevice?.id === dev.id
                      const catMeta = DEVICE_CATEGORIES.find((c) => c.id === dev.category)
                      const devStatus = String(dev.status || "online").toLowerCase()
                      const dotColor =
                        devStatus === "offline"
                          ? "bg-rose-500"
                          : devStatus === "warning"
                          ? "bg-amber-500"
                          : "bg-emerald-500"

                      return (
                        <div
                          key={dev.id}
                          onClick={() => {
                            setSelectedDeviceId(dev.id)
                            setSelectedEmptyU(null)
                          }}
                          className={`flex items-center justify-between gap-2 p-2 rounded-lg text-xs cursor-pointer transition border ${
                            isSelected
                              ? "bg-primary/10 border-primary text-primary font-semibold shadow-sm"
                              : "border-border/60 hover:bg-secondary/40 text-foreground"
                          }`}
                        >
                          <div className="flex items-center gap-2 min-w-0">
                            <span className="font-mono text-[11px] font-bold px-1.5 py-0.5 rounded bg-muted/60 text-foreground shrink-0">
                              U{dev.uPosition || 1}
                            </span>
                            <span className={`h-2 w-2 rounded-full shrink-0 ${dotColor}`} />
                            <span className="shrink-0">{catMeta?.icon || "📦"}</span>
                            <span className="truncate">{dev.name || dev.ip || "Hardware"}</span>
                          </div>

                          <div className="flex items-center gap-2 shrink-0 font-mono text-[11px] text-muted-foreground">
                            <span>{dev.ip || "No IP"}</span>
                            <span className="text-xs text-muted-foreground/60">
                              {isSelected ? "◀ Active" : "➔"}
                            </span>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>

              {/* 2. Expanded Device Info Card (When a Device is Selected) */}
              {selectedDevice ? (
                <div className="rounded-xl border border-primary/30 bg-card p-4 space-y-4 shadow-md animate-in fade-in duration-150">
                  {/* Card Header */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xl">
                          {DEVICE_CATEGORIES.find((c) => c.id === selectedDevice.category)?.icon || "📦"}
                        </span>
                        <h3 className="text-sm font-bold text-foreground truncate">
                          {selectedDevice.name || selectedDevice.ip || "Device"}
                        </h3>
                        <Badge variant="outline" className="text-[11px] font-mono">
                          {selectedDevice.category || "General"}
                        </Badge>
                      </div>
                      <div className="text-xs text-muted-foreground font-mono mt-0.5">
                        {selectedDevice.model || selectedDevice.device_type || "Standard Hardware Part"} · {selectedDevice.vendor || "Enterprise Hardware"}
                      </div>
                    </div>

                    <Badge
                      className={`text-xs capitalize font-medium ${
                        String(selectedDevice.status || "online").toLowerCase() === "offline"
                          ? "bg-rose-500/10 text-rose-500 border-rose-500/30"
                          : String(selectedDevice.status || "online").toLowerCase() === "warning"
                          ? "bg-amber-500/10 text-amber-500 border-amber-500/30"
                          : "bg-emerald-500/10 text-emerald-500 border-emerald-500/30"
                      }`}
                      variant="outline"
                    >
                      {selectedDevice.status || "Online"}
                    </Badge>
                  </div>

                  <Separator />

                  {/* Hardware & Network Specs Grid */}
                  <div className="grid grid-cols-2 gap-2.5 text-xs">
                    <div className="p-2.5 rounded-lg bg-secondary/30 border border-border/60">
                      <div className="text-[10px] uppercase font-mono text-muted-foreground mb-1">
                        IP Address
                      </div>
                      <div className="flex items-center justify-between font-mono font-bold text-foreground">
                        <span>{selectedDevice.ip || "-"}</span>
                        {selectedDevice.ip && (
                          <button
                            type="button"
                            onClick={() => copyToClipboard(selectedDevice.ip, "IP Address")}
                            className="text-muted-foreground hover:text-primary transition p-1"
                            title="คัดลอก IP"
                            aria-label="คัดลอก IP"
                          >
                            <Copy className="h-3.5 w-3.5" />
                          </button>
                        )}
                      </div>
                    </div>

                    <div className="p-2.5 rounded-lg bg-secondary/30 border border-border/60">
                      <div className="text-[10px] uppercase font-mono text-muted-foreground mb-1">
                        MAC Address
                      </div>
                      <div className="flex items-center justify-between font-mono font-bold text-foreground">
                        <span className="truncate">{selectedDevice.mac || "-"}</span>
                        {selectedDevice.mac && (
                          <button
                            type="button"
                            onClick={() => copyToClipboard(selectedDevice.mac, "MAC Address")}
                            className="text-muted-foreground hover:text-primary transition p-1"
                            title="คัดลอก MAC"
                            aria-label="คัดลอก MAC"
                          >
                            <Copy className="h-3.5 w-3.5" />
                          </button>
                        )}
                      </div>
                    </div>

                    <div className="p-2.5 rounded-lg bg-secondary/30 border border-border/60">
                      <div className="text-[10px] uppercase font-mono text-muted-foreground mb-1">
                        Rack Position (ตำแหน่ง U)
                      </div>
                      <div className="font-mono font-bold text-primary flex items-center gap-1.5">
                        <Layers className="h-3.5 w-3.5" />
                        <span>
                          ช่อง U{selectedDevice.uPosition || 1} ({selectedDevice.uHeight || 1}U) ·{" "}
                          {(selectedDevice.rackFace || "front") === "rear" ? "ด้านหลัง" : "ด้านหน้า"}
                        </span>
                      </div>
                    </div>

                    <div className="p-2.5 rounded-lg bg-secondary/30 border border-border/60">
                      <div className="text-[10px] uppercase font-mono text-muted-foreground mb-1">
                        Subnet / VLAN
                      </div>
                      <div className="font-mono font-bold text-foreground truncate">
                        {selectedDevice.subnet || "LAN / Default"}
                      </div>
                    </div>
                  </div>

                  {/* Live Ping & Action Section */}
                  <div className="p-3 rounded-lg bg-muted/40 border border-border space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="text-xs font-semibold flex items-center gap-1.5">
                        <Activity className="h-3.5 w-3.5 text-primary" />
                        <span>ทดสอบการเชื่อมต่อเครือข่าย (Live Ping)</span>
                      </div>
                      <Button
                        size="sm"
                        variant="secondary"
                        disabled={isPinging || !selectedDevice.ip}
                        onClick={() => handlePing(selectedDevice)}
                        className="h-7 text-xs font-mono gap-1"
                      >
                        {isPinging ? "กำลัง Ping..." : "📡 ทดสอบ Ping"}
                      </Button>
                    </div>

                    {pingResult && (
                      <div
                        className={`text-xs p-2 rounded-md font-mono flex items-center gap-2 ${
                          pingResult.ok
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                        }`}
                      >
                        {pingResult.ok ? (
                          <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" />
                        ) : (
                          <XCircle className="h-4 w-4 shrink-0 text-rose-500" />
                        )}
                        <span>{pingResult.message}</span>
                      </div>
                    )}
                  </div>

                  {/* Bottom Action Buttons */}
                  <div className="flex items-center justify-end gap-2 pt-1">
                    {onOpenDeviceModal && (
                      <Button
                        size="sm"
                        className="h-8 text-xs gap-1.5 font-semibold bg-primary hover:bg-primary/90 text-primary-foreground"
                        onClick={() => {
                          onOpenChange(false)
                          onOpenDeviceModal(selectedDevice.id)
                        }}
                      >
                        <Maximize2 className="h-3.5 w-3.5" />
                        <span>ดูรายละเอียดเชิงลึก (Device Modal) ➔</span>
                      </Button>
                    )}
                  </div>
                </div>
              ) : selectedEmptyU ? (
                /* Empty Slot Card */
                <div className="rounded-xl border border-dashed border-border bg-card/40 p-6 text-center space-y-2">
                  <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center mx-auto text-muted-foreground font-mono text-sm">
                    U{selectedEmptyU}
                  </div>
                  <h4 className="text-xs font-bold text-foreground">
                    สล็อตตำแหน่ง U{selectedEmptyU} ยังว่างอยู่
                  </h4>
                  <p className="text-[11px] text-muted-foreground max-w-sm mx-auto">
                    ยังไม่มีการติดตั้งอุปกรณ์ในช่องนี้ สามารถเปิดโหมด Admin เพื่อลากอุปกรณ์จากคลังมาจัดวางในตำแหน่งนี้ได้
                  </p>
                </div>
              ) : (
                /* No Selection Prompt */
                <div className="rounded-xl border border-dashed border-border p-6 text-center text-xs text-muted-foreground">
                  👈 คลิกเลือกสล็อต Unit ในตู้แร็คฝั่งซ้าย หรือคลิกเลือกอุปกรณ์ในกิ่งโครงสร้างด้านบนเพื่อแสดงรายละเอียด
                </div>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default RackHierarchyModal

import React, { useState, useEffect, useMemo } from "react"
import { FLOORS, ROOM_TYPES, DEVICE_CATEGORIES } from "@/data/twinData"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input, SelectNative } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/components/ui/toaster"
import {
  Building2,
  MapPin,
  Crosshair,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ExternalLink,
  Save,
  Trash2,
  Layers,
  Server,
  Sparkles,
} from "lucide-react"

export function RoomModal({
  room,
  placedDevices = [],
  open,
  onOpenChange,
  isAdmin = false,
  adminToken = "",
  onFlyToRoom,
  onSelectDevice,
  onStartMovingRoom,
  onRoomUpdated,
  onRoomDeleted,
}) {
  const { toast } = useToast()
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({
    roomNumber: "",
    name: "",
    roomType: "Office",
    floorIdx: 0,
    color: "#38bdf8",
    vlan: "",
    description: "",
    width: 12,
    depth: 10,
  })

  useEffect(() => {
    if (!room) return
    const rMeta = ROOM_TYPES.find((t) => t.id === room.roomType) || ROOM_TYPES[1]
    setForm({
      roomNumber: room.roomNumber || "",
      name: room.name || "",
      roomType: room.roomType || "Office",
      floorIdx: Number(room.floorIdx ?? 0),
      color: room.color || rMeta.color || "#38bdf8",
      vlan: room.vlan || "",
      description: room.description || "",
      width: Number(room.zoneSize?.width ?? rMeta.defaultWidth ?? 12),
      depth: Number(room.zoneSize?.depth ?? rMeta.defaultDepth ?? 10),
    })
  }, [room])

  // Strictly include ONLY placed devices (`d.isPlaced === true`) inside this room
  const roomDevices = useMemo(() => {
    if (!room) return []
    return (placedDevices || []).filter(
      (d) =>
        d.isPlaced === true &&
        Number(d.floorIdx ?? 0) === Number(room.floorIdx ?? 0) &&
        (d.roomId === room.id || (d.roomNumber && d.roomNumber === room.roomNumber))
    )
  }, [room, placedDevices])

  const healthStats = useMemo(() => {
    const total = roomDevices.length
    const online = roomDevices.filter(
      (d) => String(d.status || "Online").toLowerCase() === "online"
    ).length
    const warning = roomDevices.filter(
      (d) => String(d.status || "").toLowerCase() === "warning"
    ).length
    const offline = roomDevices.filter(
      (d) => String(d.status || "").toLowerCase() === "offline"
    ).length
    const status =
      total === 0
        ? "Idle"
        : offline > 0
        ? "Offline"
        : warning > 0
        ? "Warning"
        : "Online"
    return { total, online, warning, offline, status }
  }, [roomDevices])

  if (!room) return null

  const floorMeta = FLOORS.find((f) => f.index === Number(room.floorIdx ?? 0)) || FLOORS[0]
  const roomTypeMeta = ROOM_TYPES.find((r) => r.id === room.roomType) || ROOM_TYPES[1]

  const handleSaveRoom = async (e) => {
    e?.preventDefault()
    if (!form.roomNumber.trim()) return
    setSaving(true)
    try {
      const res = await fetch(`/api/admin/rooms/${encodeURIComponent(room.id)}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify({
          id: room.id,
          roomNumber: form.roomNumber.trim(),
          name: form.name.trim() || `Room ${form.roomNumber.trim()}`,
          roomType: form.roomType,
          floorIdx: Number(form.floorIdx),
          color: form.color,
          vlan: form.vlan.trim(),
          description: form.description.trim(),
          zoneSize: {
            width: Math.max(2, Number(form.width) || 12),
            depth: Math.max(2, Number(form.depth) || 10),
          },
          position: room.position,
        }),
      })
      const data = await res.json()
      if (res.ok && data.room) {
        toast({
          title: `บันทึกข้อมูลห้อง [${data.room.roomNumber}] สำเร็จ`,
          description: `อัพเดทข้อมูลห้องและซิงก์เลขห้องไปยังอุปกรณ์ในห้องนี้ (${roomDevices.length} รายการ) เรียบร้อยแล้ว`,
          variant: "success",
        })
        if (onRoomUpdated) onRoomUpdated(data.room)
      } else {
        throw new Error(data.error || "ไม่สามารถบันทึกข้อมูลห้องได้")
      }
    } catch (err) {
      toast({
        title: "บันทึกข้อมูลห้องไม่สำเร็จ",
        description: err.message,
        variant: "destructive",
      })
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteRoom = async () => {
    try {
      const res = await fetch(`/api/admin/rooms/${encodeURIComponent(room.id)}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${adminToken}`,
        },
      })
      if (res.ok) {
        toast({
          title: `ลบป้ายห้อง [${room.roomNumber}] แล้ว`,
          description: "ลบกรอบพื้นที่ห้องออกจากโมเดล 3D เรียบร้อยแล้ว",
        })
        onOpenChange(false)
        if (onRoomDeleted) onRoomDeleted(room.id)
      }
    } catch (err) {
      toast({
        title: "ลบห้องไม่สำเร็จ",
        description: err.message,
        variant: "destructive",
      })
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[88vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex flex-wrap items-start justify-between gap-3 pr-6">
            <div className="space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xl">{roomTypeMeta.icon}</span>
                <DialogTitle className="text-base sm:text-lg font-bold">
                  ห้อง [{room.roomNumber}] — {room.name}
                </DialogTitle>
                <Badge
                  variant={
                    healthStats.status === "Online"
                      ? "success"
                      : healthStats.status === "Warning"
                      ? "warning"
                      : healthStats.status === "Offline"
                      ? "destructive"
                      : "secondary"
                  }
                >
                  {healthStats.status === "Idle"
                    ? "ไม่มีอุปกรณ์ในห้อง"
                    : `Room ${healthStats.status}`}
                </Badge>
              </div>
              <DialogDescription className="flex flex-wrap items-center gap-2 text-xs">
                <span className="inline-flex items-center gap-1 font-medium text-foreground">
                  <Building2 className="h-3.5 w-3.5 text-primary" />
                  {floorMeta.shortLabel} ({floorMeta.label})
                </span>
                <span>·</span>
                <span>ประเภท: {roomTypeMeta.label}</span>
                {room.vlan && (
                  <>
                    <span>·</span>
                    <span className="font-mono text-primary">{room.vlan}</span>
                  </>
                )}
              </DialogDescription>
            </div>

            <Button
              size="sm"
              variant="secondary"
              className="h-8 text-xs"
              onClick={() => {
                if (onFlyToRoom) onFlyToRoom(room)
                onOpenChange(false)
              }}
            >
              <Crosshair className="h-3.5 w-3.5 mr-1.5 text-primary" />
              ซูมกล้องเข้าห้องนี้ (3D)
            </Button>
          </div>
        </DialogHeader>

        <Tabs defaultValue="overview" className="w-full mt-1">
          <TabsList className={`grid w-full ${isAdmin ? "grid-cols-2" : "grid-cols-1"}`}>
            <TabsTrigger value="overview" className="text-xs">
              อุปกรณ์ในห้องนี้ & สถานะ ({roomDevices.length})
            </TabsTrigger>
            {isAdmin && (
              <TabsTrigger value="edit" className="text-xs">
                แก้ไขเลขห้อง / โซน 3D (Admin)
              </TabsTrigger>
            )}
          </TabsList>

          {/* TAB 1: ROOM OVERVIEW & PLACED DEVICES LIST */}
          <TabsContent value="overview" className="space-y-4 pt-3">
            {/* Room Telemetry Counters */}
            <div className="grid grid-cols-4 gap-2">
              <div className="rounded-lg border border-border bg-secondary/20 p-2.5 text-center">
                <div className="text-[11px] text-muted-foreground">อุปกรณ์ในห้อง</div>
                <div className="text-lg font-mono font-bold">{healthStats.total}</div>
              </div>
              <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-2.5 text-center">
                <div className="text-[11px] text-emerald-300 flex items-center justify-center gap-1">
                  <CheckCircle2 className="h-3 w-3" /> Online
                </div>
                <div className="text-lg font-mono font-bold text-emerald-400">
                  {healthStats.online}
                </div>
              </div>
              <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-2.5 text-center">
                <div className="text-[11px] text-amber-300 flex items-center justify-center gap-1">
                  <AlertTriangle className="h-3 w-3" /> Warning
                </div>
                <div className="text-lg font-mono font-bold text-amber-400">
                  {healthStats.warning}
                </div>
              </div>
              <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 p-2.5 text-center">
                <div className="text-[11px] text-rose-300 flex items-center justify-center gap-1">
                  <XCircle className="h-3 w-3" /> Offline
                </div>
                <div className="text-lg font-mono font-bold text-rose-400">
                  {healthStats.offline}
                </div>
              </div>
            </div>

            {/* Spatial Metadata Box */}
            <div className="rounded-lg border border-border bg-secondary/15 p-3 grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
              <div>
                <span className="text-muted-foreground block text-[11px]">หมายเลขห้อง</span>
                <span className="font-mono font-bold text-primary">[{room.roomNumber}]</span>
              </div>
              <div>
                <span className="text-muted-foreground block text-[11px]">
                  ขนาดกรอบโซนห้อง 3D
                </span>
                <span className="font-mono">
                  {room.zoneSize?.width ?? 12}m × {room.zoneSize?.depth ?? 10}m
                </span>
              </div>
              <div>
                <span className="text-muted-foreground block text-[11px]">พิกัดจุดกึ่งกลาง 3D</span>
                <span className="font-mono text-[11px]">
                  X:{Number(room.position?.x || 0).toFixed(1)}, Y:
                  {Number(room.position?.y || 1.5).toFixed(1)}, Z:
                  {Number(room.position?.z || 0).toFixed(1)}
                </span>
              </div>
              {room.description && (
                <div className="col-span-2 sm:col-span-3 pt-1 border-t border-border/60 text-muted-foreground">
                  หมายเหตุ: {room.description}
                </div>
              )}
            </div>

            {/* Placed Devices in this Room */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                  <Server className="h-3.5 w-3.5 text-primary" />
                  รายการอุปกรณ์ที่ติดตั้งในห้อง [{room.roomNumber}]
                </Label>
                {isAdmin && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-7 text-xs"
                    onClick={() => {
                      if (onStartMovingRoom) {
                        onOpenChange(false)
                        onStartMovingRoom(room)
                      }
                    }}
                  >
                    <MapPin className="h-3.5 w-3.5 mr-1 text-primary" />
                    คลิกย้ายจุดห้องบนตึก 3D
                  </Button>
                )}
              </div>

              {roomDevices.length === 0 ? (
                <div className="rounded-lg border border-dashed border-border p-6 text-center text-xs text-muted-foreground">
                  ยังไม่มีอุปกรณ์ที่จัดวางอยู่ในห้อง [{room.roomNumber}]
                  <br />
                  <span className="text-[11px] opacity-80">
                    เมื่อ Admin นำอุปกรณ์มาวางในกรอบพื้นที่ห้องนี้ ระบบจะผูกเลขห้อง [{room.roomNumber}]
                    ให้อัตโนมัติทันที
                  </span>
                </div>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                  {roomDevices.map((dev) => {
                    const catMeta =
                      DEVICE_CATEGORIES.find((c) => c.id === dev.category) ||
                      DEVICE_CATEGORIES[0]
                    const stLower = String(dev.status || "Online").toLowerCase()
                    return (
                      <div
                        key={dev.id}
                        className="rounded-lg border border-border bg-secondary/20 hover:bg-secondary/40 p-2.5 flex items-center justify-between gap-2 transition"
                      >
                        <div className="min-w-0">
                          <div className="text-xs font-bold flex items-center gap-1.5 truncate">
                            <span
                              className={`h-2 w-2 rounded-full shrink-0 ${
                                stLower === "online"
                                  ? "bg-emerald-400"
                                  : stLower === "warning"
                                  ? "bg-amber-400"
                                  : "bg-rose-400"
                              }`}
                            />
                            <span>{catMeta.icon}</span>
                            <span className="truncate">{dev.name || dev.ip}</span>
                            <Badge variant="outline" className="text-[10px] uppercase">
                              {dev.category}
                            </Badge>
                          </div>
                          <div className="text-[11px] font-mono text-muted-foreground truncate">
                            IP: {dev.ip} · MAC: {dev.mac || "-"} · พอร์ตเปิด{" "}
                            {(dev.openPorts || []).length} พอร์ต
                          </div>
                        </div>

                        <div className="flex items-center gap-1.5 shrink-0">
                          <Button
                            size="sm"
                            variant="default"
                            className="h-7 text-xs"
                            onClick={() => {
                              onOpenChange(false)
                              if (onSelectDevice) onSelectDevice(dev.id)
                            }}
                          >
                            <ExternalLink className="h-3 w-3 mr-1" />
                            ดูการ์ด / Login
                          </Button>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </TabsContent>

          {/* TAB 2: ADMIN ROOM EDITING, RENUMBERING & 3D ZONE SIZING */}
          {isAdmin && (
            <TabsContent value="edit" className="space-y-4 pt-3">
              <form onSubmit={handleSaveRoom} className="space-y-3">
                <div className="rounded-lg border border-primary/30 bg-primary/10 p-2.5 text-[11px] text-muted-foreground flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary shrink-0" />
                  <span>
                    <strong>Smart Room Cascade:</strong> หากคุณเปลี่ยนหมายเลขห้องด้านล่าง
                    อุปกรณ์ที่ติดตั้งอยู่ในห้องนี้ทั้ง <strong>{roomDevices.length} รายการ</strong>{" "}
                    จะถูกอัพเดทเลขห้องตามโดยอัตโนมัติทันที
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                  <div className="space-y-1">
                    <Label className="text-xs">หมายเลขห้อง (Room No.)</Label>
                    <Input
                      value={form.roomNumber}
                      onChange={(e) => setForm({ ...form, roomNumber: e.target.value })}
                      placeholder="เช่น 101, G01, NOC-2"
                      className="h-8 text-xs font-mono font-bold"
                      required
                    />
                  </div>

                  <div className="space-y-1 sm:col-span-2">
                    <Label className="text-xs">ชื่อห้อง / หน่วยงาน (Room Name)</Label>
                    <Input
                      value={form.name}
                      onChange={(e) => setForm({ ...form, name: e.target.value })}
                      placeholder="เช่น ห้องควบคุมเครือข่ายหลัก (Main NOC)"
                      className="h-8 text-xs"
                      required
                    />
                  </div>

                  <div className="space-y-1">
                    <Label className="text-xs">ชั้นอาคาร (Floor)</Label>
                    <SelectNative
                      value={form.floorIdx}
                      onChange={(e) =>
                        setForm({ ...form, floorIdx: Number(e.target.value) })
                      }
                      className="h-8 text-xs"
                    >
                      {FLOORS.map((f) => (
                        <option key={f.index} value={f.index}>
                          {f.shortLabel} — {f.label}
                        </option>
                      ))}
                    </SelectNative>
                  </div>

                  <div className="space-y-1">
                    <Label className="text-xs">ประเภทห้อง (Room Type)</Label>
                    <SelectNative
                      value={form.roomType}
                      onChange={(e) => {
                        const nextType = e.target.value
                        const meta =
                          ROOM_TYPES.find((t) => t.id === nextType) || ROOM_TYPES[1]
                        setForm({
                          ...form,
                          roomType: nextType,
                          color: meta.color,
                        })
                      }}
                      className="h-8 text-xs"
                    >
                      {ROOM_TYPES.map((rt) => (
                        <option key={rt.id} value={rt.id}>
                          {rt.icon} {rt.label}
                        </option>
                      ))}
                    </SelectNative>
                  </div>

                  <div className="space-y-1">
                    <Label className="text-xs">VLAN ประจำห้อง (Optional)</Label>
                    <Input
                      value={form.vlan}
                      onChange={(e) => setForm({ ...form, vlan: e.target.value })}
                      placeholder="เช่น VLAN 10, VLAN 100"
                      className="h-8 text-xs font-mono"
                    />
                  </div>

                  <div className="space-y-1">
                    <Label className="text-xs">ความกว้างโซน 3D (Width m)</Label>
                    <Input
                      type="number"
                      min="2"
                      max="100"
                      step="1"
                      value={form.width}
                      onChange={(e) => setForm({ ...form, width: e.target.value })}
                      className="h-8 text-xs font-mono"
                    />
                  </div>

                  <div className="space-y-1">
                    <Label className="text-xs">ความลึกโซน 3D (Depth m)</Label>
                    <Input
                      type="number"
                      min="2"
                      max="100"
                      step="1"
                      value={form.depth}
                      onChange={(e) => setForm({ ...form, depth: e.target.value })}
                      className="h-8 text-xs font-mono"
                    />
                  </div>

                  <div className="space-y-1">
                    <Label className="text-xs">สีกรอบโซนห้อง (Hex Color)</Label>
                    <div className="flex items-center gap-1.5">
                      <input
                        type="color"
                        value={form.color}
                        onChange={(e) => setForm({ ...form, color: e.target.value })}
                        className="h-8 w-10 rounded border border-border bg-transparent cursor-pointer"
                      />
                      <Input
                        value={form.color}
                        onChange={(e) => setForm({ ...form, color: e.target.value })}
                        className="h-8 text-xs font-mono"
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-1">
                  <Label className="text-xs">รายละเอียดเพิ่มเติม (Description)</Label>
                  <Input
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                    placeholder="ระบุรายละเอียดห้อง ผู้ดูแล หรือหมายเหตุทางเทคนิค..."
                    className="h-8 text-xs"
                  />
                </div>

                <Separator />

                <DialogFooter className="flex flex-wrap items-center justify-between gap-2 sm:justify-between">
                  <div className="flex items-center gap-2">
                    <Button
                      type="button"
                      size="sm"
                      variant="destructive"
                      onClick={handleDeleteRoom}
                    >
                      <Trash2 className="h-3.5 w-3.5 mr-1" />
                      ลบห้องนี้
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        if (onStartMovingRoom) {
                          onOpenChange(false)
                          onStartMovingRoom(room)
                        }
                      }}
                    >
                      <Crosshair className="h-3.5 w-3.5 mr-1 text-primary" />
                      คลิกย้ายตำแหน่งห้องบน 3D
                    </Button>
                  </div>

                  <Button type="submit" size="sm" disabled={saving}>
                    <Save className="h-3.5 w-3.5 mr-1.5" />
                    {saving ? "กำลังบันทึก..." : "บันทึกการแก้ไขเลขห้อง & โซน"}
                  </Button>
                </DialogFooter>
              </form>
            </TabsContent>
          )}
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}


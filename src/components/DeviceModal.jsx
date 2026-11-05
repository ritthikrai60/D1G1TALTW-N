import React, { useState, useEffect } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/components/ui/toaster"
import { FLOORS } from "@/data/twinData"
import { M3Button } from "@/components/m3"
import {
  Globe,
  Lock,
  ExternalLink,
  Copy,
  RefreshCw,
  Trash2,
  Undo2,
  Radar,
  ShieldAlert,
  Network,
  Server,
  Eye,
  EyeOff,
  ChevronRight,
  Cpu,
  Activity,
  Cable,
} from "lucide-react"

const HTTP_LIKE_PORTS = new Set([
  80, 443, 8080, 8443, 8000, 8006, 8008, 8081, 8291, 8888, 3000, 5000, 5001, 9000, 9090, 9443, 10000,
])

function getFloorLabel(floorIdx) {
  if (floorIdx === null || floorIdx === undefined) return "ยังไม่ได้วางตำแหน่ง"
  const found = FLOORS.find((f) => f.index === Number(floorIdx))
  return found ? found.label : `Floor ${floorIdx}`
}

export function DeviceModal({
  device,
  allDevices = [],
  open,
  onOpenChange,
  isAdmin = false,
  onDeviceUpdated,
  onUnplaceDevice,
  onOpenRackula,
}) {
  const { toast } = useToast()
  const [scanningMode, setScanningMode] = useState(null) // 'fast' | 'full' | 'ping' | null
  const [proxyPreviewUrl, setProxyPreviewUrl] = useState(null)
  const [proxyDirectUrl, setProxyDirectUrl] = useState(null)
  const [showPassword, setShowPassword] = useState(false)

  useEffect(() => {
    setProxyPreviewUrl(null)
    setProxyDirectUrl(null)
    setShowPassword(false)
  }, [device?.id, open])

  if (!device) return null

  const ports = device.openPorts || device.ports || []
  const portSet = new Set(ports.map((p) => (typeof p === "object" ? Number(p.port) : Number(p))))
  const has80 = portSet.has(80)
  const has443 = portSet.has(443)
  const customWebPorts = [...portSet].filter(
    (p) => p !== 80 && p !== 443 && HTTP_LIKE_PORTS.has(p)
  )

  // Switch / Router physical port matrix
  const swPorts =
    Array.isArray(device.switchInterfaces) && device.switchInterfaces.length > 0
      ? device.switchInterfaces
      : Array.from(
          { length: device.category === "Switch" ? 24 : 8 },
          (_, i) => ({
            portIndex: i + 1,
            name: `GE1/0/${i + 1}`,
            status: i < Math.max(2, ports.length) ? "up" : "down",
            speed: "1000 Mbps",
            vlan: `VLAN ${device.vlanId ?? device.vlan ?? 1}`,
          })
        )

  // Build hierarchy chain from parentDeviceId or hierarchy.path
  const buildHierarchyChain = () => {
    const byId = new Map(allDevices.map((d) => [d.id, d]))
    const chain = []
    let curr = device
    const visited = new Set()
    while (curr && !visited.has(curr.id)) {
      visited.add(curr.id)
      chain.unshift(curr)
      const parentId = curr.hierarchy?.parentDeviceId || curr.parentDeviceId
      curr = parentId ? byId.get(parentId) : null
    }
    return chain
  }

  const hierarchyChain = buildHierarchyChain()

  const copyText = async (text, label) => {
    try {
      await navigator.clipboard.writeText(text)
      toast({
        title: `คัดลอก ${label} สำเร็จ`,
        description: `${text}`,
        variant: "success",
      })
    } catch {
      toast({
        title: "ไม่สามารถคัดลอกได้",
        description: text,
        variant: "destructive",
      })
    }
  }

  const openDirectPort = (proto, port) => {
    window.open(`${proto}://${device.ip}:${port}`, "_blank", "noopener")
  }

  const openReverseProxy = (customTargetUrl) => {
    if (customTargetUrl) {
      setProxyPreviewUrl(`/api/proxy?url=${encodeURIComponent(customTargetUrl)}`)
      setProxyDirectUrl(customTargetUrl)
      return
    }
    const proto = has443 ? "https" : "http"
    const port = has443 ? 443 : has80 ? 80 : customWebPorts[0] || 80
    const targetUrl = `${proto}://${device.ip}:${port}/`
    const proxyUrl = `/api/proxy?url=${encodeURIComponent(targetUrl)}`
    setProxyPreviewUrl(proxyUrl)
    setProxyDirectUrl(targetUrl)
  }

  const handlePingDevice = async () => {
    setScanningMode("ping")
    try {
      const res = await fetch(`/api/devices/${encodeURIComponent(device.id)}/ping`, {
        method: "POST",
      })
      const data = await res.json()
      if (res.ok && data.device) {
        onDeviceUpdated?.(data.device)
        toast({
          title: data.ping?.alive ? "อุปกรณ์ออนไลน์ (Ping ตอบกลับ)" : "อุปกรณ์ไม่ตอบสนอง (Offline)",
          description: `${device.ip} · Latency: ${data.ping?.latencyMs ?? "-"} ms`,
          variant: data.ping?.alive ? "success" : "destructive",
        })
      }
    } catch (err) {
      toast({
        title: "ตรวจสอบสถานะล้มเหลว",
        description: err.message,
        variant: "destructive",
      })
    } finally {
      setScanningMode(null)
    }
  }

  const handlePortScan = async (fullRange = false) => {
    const mode = fullRange ? "full" : "fast"
    setScanningMode(mode)
    toast({
      title: fullRange
        ? "กำลังสแกนพอร์ตทั้งหมด (1–65535)..."
        : "กำลังสแกนพอร์ตมาตรฐาน (Fast 48 Ports)...",
      description: `เป้าหมาย: ${device.ip} (${device.name})`,
    })
    try {
      const res = await fetch(`/api/devices/${encodeURIComponent(device.id)}/scan-ports`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode }),
      })
      const data = await res.json()
      if (res.ok && data.device) {
        onDeviceUpdated?.(data.device)
        toast({
          title: "สแกนพอร์ตเสร็จสมบูรณ์",
          description: `พบพอร์ตเปิดทั้งหมด ${(data.device.openPorts || []).length} พอร์ต บน ${device.ip}`,
          variant: "success",
        })
      } else {
        throw new Error(data.error || "Port scan failed")
      }
    } catch (err) {
      toast({
        title: "สแกนพอร์ตล้มเหลว",
        description: err.message,
        variant: "destructive",
      })
    } finally {
      setScanningMode(null)
    }
  }

  const statusLower = String(device.status || "Online").toLowerCase()
  const statusVariant =
    statusLower === "online"
      ? "success"
      : statusLower === "warning"
      ? "warning"
      : "destructive"

  const username = device.credentials?.username || device.defaultUsername || "admin"
  const passwordHint =
    device.credentials?.password || device.credentials?.passwordHint || device.defaultPasswordHint || "admin"

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex flex-wrap items-center gap-2 pr-6">
            <Badge variant={statusVariant} className="uppercase tracking-wider">
              <span className="h-1.5 w-1.5 rounded-full bg-current animate-pulse mr-1" />
              {device.status || "Online"}
            </Badge>
            <Badge variant="info" className="uppercase">
              {device.category || device.type || "Network"}
            </Badge>
            <Badge variant="outline" className="font-mono">
              {device.networkType || "LAN"}
            </Badge>
            <Badge variant="secondary" className="font-mono">
              {getFloorLabel(device.floorIdx)} · ห้อง {device.roomNumber || "Unassigned"}
            </Badge>
          </div>
          <DialogTitle className="text-xl mt-1 flex items-center gap-2">
            <Cpu className="h-5 w-5 text-primary shrink-0" />
            <span>{device.name || device.ip}</span>
            <span className="text-sm font-mono font-normal text-muted-foreground">
              ({device.ip})
            </span>
          </DialogTitle>
          <DialogDescription>
            {device.vendor || "Unknown Vendor"} · {device.model || "Network Device"} · Subnet{" "}
            <span className="font-mono text-foreground">{device.subnet || "-"}</span>
          </DialogDescription>
        </DialogHeader>

        {/* 19-Inch Server Rack Special Action Banner */}
        {device.modelType === "server_rack" && (
          <div className="rounded-xl border border-primary/50 bg-accent/60 p-3.5 flex flex-wrap items-center justify-between gap-3 shadow-lg">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-primary/20 border border-primary/40 flex items-center justify-center text-primary shrink-0">
                <Server className="h-5 w-5" />
              </div>
              <div>
                <div className="text-sm font-bold text-foreground flex items-center gap-2">
                  <span>ตู้แร็คเซิร์ฟเวอร์ 19 นิ้ว (Server Rack Enclosure)</span>
                  <Badge variant="outline" className="text-[10px] bg-primary/20 text-primary border-primary/50 font-mono">
                    {device.rackConfig?.rackHeight || 42}U
                  </Badge>
                </div>
                <div className="text-xs text-muted-foreground mt-0.5">
                  จัดเรียงอุปกรณ์ในตู้แร็ค, ดูความจุ U-Slot, ลากย้ายตำแหน่ง, และจัดการแบบ Elevation ผ่าน Rackula Designer
                </div>
              </div>
            </div>
            <M3Button
              variant="filled"
              className="font-bold text-xs shadow-md"
              icon={<Server className="h-4 w-4" />}
              onClick={() => {
                onOpenChange(false)
                if (onOpenRackula) {
                  onOpenRackula(device.id)
                }
              }}
            >
              เปิดจัดการตู้แร็ค (Rackula Designer)
            </M3Button>
          </div>
        )}

        {/* Quick Web Access Bar (80, 443, Custom Web Ports, Reverse Proxy, Live Ping) */}
        <div className="rounded-lg border border-border bg-secondary/30 p-3">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Globe className="h-3.5 w-3.5 text-primary" />
              Direct Web Access (80 / 443 / Custom Ports) & Reverse Proxy Login
            </span>
            <Button
              size="sm"
              variant="ghost"
              className="h-6 px-2 text-xs"
              disabled={scanningMode !== null}
              onClick={handlePingDevice}
            >
              <Activity
                className={`h-3.5 w-3.5 mr-1 text-emerald-400 ${
                  scanningMode === "ping" ? "animate-spin" : ""
                }`}
              />
              Ping เช็คสถานะสด
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant={has80 ? "default" : "outline"}
              onClick={() => openDirectPort("http", 80)}
            >
              <Globe className="h-3.5 w-3.5" />
              HTTP :80 {has80 ? "(Open)" : ""}
              <ExternalLink className="h-3 w-3 opacity-70" />
            </Button>

            <Button
              size="sm"
              variant={has443 ? "default" : "outline"}
              onClick={() => openDirectPort("https", 443)}
            >
              <Lock className="h-3.5 w-3.5" />
              HTTPS :443 {has443 ? "(Open)" : ""}
              <ExternalLink className="h-3 w-3 opacity-70" />
            </Button>

            {customWebPorts.map((port) => {
              const proto = [8443, 9443, 8006, 5001, 10000].includes(port) ? "https" : "http"
              return (
                <Button
                  key={port}
                  size="sm"
                  variant="secondary"
                  onClick={() => openDirectPort(proto, port)}
                >
                  <Globe className="h-3.5 w-3.5 text-sky-400" />
                  {proto.toUpperCase()} :{port}
                  <ExternalLink className="h-3 w-3 opacity-70" />
                </Button>
              )
            })}

            <Button
              size="sm"
              variant={proxyPreviewUrl ? "secondary" : "outline"}
              onClick={() => (proxyPreviewUrl ? setProxyPreviewUrl(null) : openReverseProxy())}
            >
              <Server className="h-3.5 w-3.5 text-emerald-400" />
              {proxyPreviewUrl ? "ปิดหน้าต่าง Reverse Proxy" : "เปิดผ่าน Reverse Proxy (ในหน้านี้)"}
            </Button>
          </div>

          {proxyPreviewUrl && (
            <div className="mt-3 rounded-lg border border-border overflow-hidden bg-background">
              <div className="flex items-center justify-between px-3 py-2 bg-muted/60 border-b border-border text-xs">
                <span className="font-mono truncate">Proxy Target: {proxyDirectUrl}</span>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-6 px-2 text-xs"
                    onClick={() => window.open(proxyDirectUrl, "_blank", "noopener")}
                  >
                    เปิดแท็บใหม่ <ExternalLink className="h-3 w-3 ml-1" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-6 px-2 text-xs text-destructive"
                    onClick={() => setProxyPreviewUrl(null)}
                  >
                    ปิด
                  </Button>
                </div>
              </div>
              <iframe
                src={proxyPreviewUrl}
                title="Device Reverse Proxy Preview"
                className="w-full h-72 bg-white border-0"
              />
            </div>
          )}
        </div>

        {/* shadcn/ui Tabs for Device Details, Ports, Switch Matrix, Credentials & Hierarchy */}
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">ข้อมูลอุปกรณ์</TabsTrigger>
            <TabsTrigger value="ports">พอร์ต TCP ({ports.length})</TabsTrigger>
            <TabsTrigger value="switch">แผงพอร์ต Switch/SNMP</TabsTrigger>
            <TabsTrigger value="hierarchy">Hierarchy & Login</TabsTrigger>
          </TabsList>

          {/* TAB 1: OVERVIEW */}
          <TabsContent value="overview" className="space-y-3 pt-2">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
              <div className="rounded-lg border border-border bg-secondary/20 p-2.5">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  IPv4 Address
                </div>
                <div className="text-sm font-mono font-semibold mt-0.5 flex items-center justify-between">
                  <span>{device.ip || "-"}</span>
                  {device.ip && (
                    <button
                      onClick={() => copyText(device.ip, "IP Address")}
                      className="text-muted-foreground hover:text-foreground cursor-pointer"
                      title="คัดลอก IP"
                    >
                      <Copy className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/20 p-2.5">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  MAC Address
                </div>
                <div className="text-sm font-mono font-semibold mt-0.5 flex items-center justify-between">
                  <span>{device.mac || "Unknown"}</span>
                  {device.mac && (
                    <button
                      onClick={() => copyText(device.mac, "MAC Address")}
                      className="text-muted-foreground hover:text-foreground cursor-pointer"
                      title="คัดลอก MAC"
                    >
                      <Copy className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/20 p-2.5">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  Vendor / Manufacturer
                </div>
                <div className="text-sm font-semibold mt-0.5 truncate">
                  {device.vendor || "Unknown"}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/20 p-2.5">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  Model / Hardware
                </div>
                <div className="text-sm font-semibold mt-0.5 truncate">
                  {device.model || "-"}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/20 p-2.5">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  OS / Firmware
                </div>
                <div className="text-sm font-semibold mt-0.5 truncate">
                  {device.os || device.osFirmware || device.osVersion || device.firmware || "-"}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/20 p-2.5">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  Serial Number / Asset Tag
                </div>
                <div className="text-sm font-mono font-semibold mt-0.5 truncate">
                  {device.serialNumber || "-"} {device.assetTag ? `(${device.assetTag})` : ""}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/20 p-2.5">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  Network / Subnet
                </div>
                <div className="text-sm font-mono font-semibold mt-0.5 truncate">
                  {device.networkType || "LAN"} · {device.subnet || "-"}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/20 p-2.5">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  Gateway / VLAN
                </div>
                <div className="text-sm font-mono font-semibold mt-0.5 truncate">
                  GW {device.gateway || "-"} · VLAN {device.vlanId ?? device.vlan ?? 1}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/20 p-2.5">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  Latency / Uptime
                </div>
                <div className="text-sm font-mono font-semibold mt-0.5 truncate">
                  {device.latencyMs != null ? `${device.latencyMs} ms` : "-"} ·{" "}
                  {device.uptime || "-"}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/20 p-2.5">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  Topology Role & Tier
                </div>
                <div className="text-sm font-semibold mt-0.5 truncate">
                  Tier {device.hierarchy?.tier ?? "-"} ({device.hierarchy?.role || "endpoint"})
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/20 p-2.5">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  3D Coordinates & Model
                </div>
                <div className="text-xs font-mono font-semibold mt-0.5">
                  {device.isPlaced && device.position
                    ? `X:${device.position.x} Y:${device.position.y} Z:${device.position.z} · ${device.modelType === 'server_rack' ? '🖥️ Server Rack' : '📍 3D Pin'} (${device.rotationY || 0}°)`
                    : "ยังไม่ได้จัดวางบน 3D"}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/20 p-2.5">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  Last Seen
                </div>
                <div className="text-xs font-mono font-semibold mt-0.5">
                  {device.lastSeen
                    ? new Date(device.lastSeen).toLocaleTimeString("th-TH")
                    : "-"}
                </div>
              </div>
            </div>
          </TabsContent>

          {/* TAB 2: PORTS TABLE */}
          <TabsContent value="ports" className="space-y-3 pt-2">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="text-xs text-muted-foreground">
                แสดงรายการพอร์ตที่เปิดใช้งานพร้อมโปรโตคอลและ HTTP/TCP Banner
              </div>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  disabled={scanningMode !== null}
                  onClick={() => handlePortScan(false)}
                >
                  <RefreshCw
                    className={`h-3.5 w-3.5 ${scanningMode === "fast" ? "animate-spin" : ""}`}
                  />
                  Fast Scan (48 พอร์ต)
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  disabled={scanningMode !== null}
                  onClick={() => handlePortScan(true)}
                >
                  <Radar
                    className={`h-3.5 w-3.5 ${scanningMode === "full" ? "animate-spin" : ""}`}
                  />
                  Full Scan (1–65535)
                </Button>
              </div>
            </div>

            <div className="rounded-lg border border-border max-h-64 overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-20">Port</TableHead>
                    <TableHead className="w-24">Service</TableHead>
                    <TableHead className="w-20">State</TableHead>
                    <TableHead>Banner / Server Title</TableHead>
                    <TableHead className="text-right w-40">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {ports.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center text-muted-foreground py-6">
                        ไม่พบพอร์ตที่เปิด หรือยังไม่ได้สแกนพอร์ต
                      </TableCell>
                    </TableRow>
                  ) : (
                    ports.map((pItem, idx) => {
                      const pNum = typeof pItem === "object" ? Number(pItem.port) : Number(pItem)
                      const service =
                        typeof pItem === "object" ? pItem.service || "tcp" : "tcp"
                      const banner =
                        typeof pItem === "object"
                          ? pItem.httpTitle || pItem.banner || pItem.serverHeader || "-"
                          : "-"
                      const isWeb = HTTP_LIKE_PORTS.has(pNum)
                      const proto = [443, 8443, 9443, 8006, 5001, 10000].includes(pNum)
                        ? "https"
                        : "http"
                      const targetUrl = `${proto}://${device.ip}:${pNum}/`

                      return (
                        <TableRow key={idx}>
                          <TableCell className="font-mono font-bold text-primary">
                            :{pNum}
                          </TableCell>
                          <TableCell className="font-mono text-xs uppercase">{service}</TableCell>
                          <TableCell>
                            <Badge variant="success" className="text-[10px]">
                              OPEN
                            </Badge>
                          </TableCell>
                          <TableCell className="font-mono text-xs text-muted-foreground truncate max-w-[180px]">
                            {banner}
                          </TableCell>
                          <TableCell className="text-right space-x-1">
                            {isWeb ? (
                              <>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="h-7 px-2 text-xs text-primary"
                                  onClick={() => openDirectPort(proto, pNum)}
                                >
                                  เปิดเว็บ <ExternalLink className="h-3 w-3 ml-1" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="h-7 px-2 text-xs"
                                  onClick={() => openReverseProxy(targetUrl)}
                                >
                                  Proxy
                                </Button>
                              </>
                            ) : (
                              <span className="text-xs text-muted-foreground font-mono">TCP</span>
                            )}
                          </TableCell>
                        </TableRow>
                      )
                    })
                  )}
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          {/* TAB 3: SWITCH / ROUTER PORT MATRIX & SNMP */}
          <TabsContent value="switch" className="space-y-3 pt-2">
            <div className="rounded-lg border border-border bg-secondary/20 p-3 space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="text-xs font-semibold flex items-center gap-1.5">
                  <Cable className="h-4 w-4 text-primary" />
                  แผงพอร์ตเชื่อมต่อ ({device.name || device.ip} — {swPorts.length} Physical Ports)
                </div>
                <span className="text-[11px] font-mono text-muted-foreground">
                  SNMP: {device.snmpInfo?.sysDescr || "Standard MIB-II Interface Table"}
                </span>
              </div>

              <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-2">
                {swPorts.map((sp) => {
                  const isUp = sp.status === "up"
                  return (
                    <div
                      key={sp.portIndex}
                      title={`${sp.name} | ${sp.speed} | ${sp.vlan}`}
                      className={`rounded-md border p-2 text-center font-mono text-xs transition ${
                        isUp
                          ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-300"
                          : "border-border bg-background/60 text-muted-foreground"
                      }`}
                    >
                      <div className="font-bold">#{sp.portIndex}</div>
                      <div className="text-[10px] mt-0.5">
                        {isUp ? "🟢 UP" : "⚪ DN"}
                      </div>
                      <div className="text-[9px] opacity-75 truncate">{sp.vlan}</div>
                    </div>
                  )
                })}
              </div>
            </div>
          </TabsContent>

          {/* TAB 4: HIERARCHY & LOGIN CREDENTIALS */}
          <TabsContent value="hierarchy" className="space-y-4 pt-2">
            {/* Network Hierarchy Chain */}
            <div className="rounded-lg border border-border bg-secondary/20 p-3 space-y-2">
              <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <Network className="h-3.5 w-3.5 text-primary" />
                Network Topology Hierarchy Path (Tier {device.hierarchy?.tier ?? 3} ·{" "}
                {device.hierarchy?.role || "endpoint"})
              </div>
              <div className="flex flex-wrap items-center gap-1.5 pt-1">
                {hierarchyChain.map((node, index) => (
                  <React.Fragment key={node.id}>
                    {index > 0 && <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />}
                    <div
                      className={`px-2.5 py-1 rounded-md border text-xs font-mono flex items-center gap-1.5 ${
                        node.id === device.id
                          ? "border-primary bg-primary/15 text-foreground font-bold"
                          : "border-border bg-background text-muted-foreground"
                      }`}
                    >
                      <span>{node.name || node.ip}</span>
                      <span className="text-[10px] opacity-75">({node.ip})</span>
                    </div>
                  </React.Fragment>
                ))}
              </div>
              {device.hierarchy?.pathNames?.length > 0 && (
                <div className="text-[11px] font-mono text-muted-foreground pt-1">
                  Full Path: {device.hierarchy.pathNames.join(" → ")}
                </div>
              )}
            </div>

            {/* Login Helper Card */}
            <div className="rounded-lg border border-border bg-secondary/20 p-3 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <ShieldAlert className="h-3.5 w-3.5 text-amber-400" />
                  Device Login Credential Helper
                </span>
                <Badge variant="outline" className="text-[10px]">
                  Auto-Copy พร้อมใช้งาน
                </Badge>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2">
                  <div>
                    <div className="text-[10px] uppercase text-muted-foreground">Username</div>
                    <div className="font-mono text-sm font-semibold">{username}</div>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => copyText(username, "Username")}
                  >
                    <Copy className="h-3.5 w-3.5" />
                    คัดลอก
                  </Button>
                </div>

                <div className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2">
                  <div>
                    <div className="text-[10px] uppercase text-muted-foreground">
                      Password / Default Hint
                    </div>
                    <div className="font-mono text-sm font-semibold">
                      {showPassword ? passwordHint : "••••••••"}
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-8 w-8"
                      onClick={() => setShowPassword((v) => !v)}
                    >
                      {showPassword ? (
                        <EyeOff className="h-3.5 w-3.5" />
                      ) : (
                        <Eye className="h-3.5 w-3.5" />
                      )}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => copyText(passwordHint, "Password Hint")}
                    >
                      <Copy className="h-3.5 w-3.5" />
                      คัดลอก
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>

        <Separator />

        <DialogFooter className="flex items-center justify-between sm:justify-between gap-2">
          <div>
            {isAdmin && device.isPlaced && (
              <Button
                variant="destructive"
                size="sm"
                onClick={() => onUnplaceDevice?.(device.id)}
                title="เอาโมเดลออกจากพื้นที่ 3D ส่งกลับเข้าคิวรอจัดวาง (ปลอดภัย ไม่ลบข้อมูล Network/IP)"
              >
                <Undo2 className="h-3.5 w-3.5 mr-1" />
                เอาโมเดลออกจากพื้นที่ (ส่งกลับคิว)
              </Button>
            )}
          </div>
          <Button variant="outline" size="sm" onClick={() => onOpenChange(false)}>
            ปิดหน้าต่าง
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

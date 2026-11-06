import React, { useState, useEffect, useMemo, useRef, useCallback } from "react"
import { ThreeViewport, DEFAULT_VIEW_STATE } from "@/components/ThreeViewport"
import { DeviceModal } from "@/components/DeviceModal"
import { RoomModal } from "@/components/RoomModal"
import RackulaModal from "@/components/RackulaModal"
import { RackHierarchyModal } from "@/components/RackHierarchyModal"
import { AdminToolbar } from "@/components/AdminToolbar"
import { ViewerMenu } from "@/components/ViewerMenu"
import { RackNameDialog } from "@/components/RackNameDialog"
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
/** IP-less Rackula library part mounted in a rack: not a real network device (hidden from stats, queue, directory). */
function isUnboundRackPart(d) {
  return Boolean(d && d.parentRackId && !String(d.ip || "").trim())
}

function incrementRoomNumber(str) {
  const s = String(str || "101").trim()
  const match = s.match(/^(.*?)(\d+)$/)
  if (!match) return `${s}-2`
  const prefix = match[1]
  const numStr = match[2]
  const nextVal = String(Number(numStr) + 1).padStart(numStr.length, "0")
  return `${prefix}${nextVal}`
}

export default function App() {
  const { toast } = useToast()
  const viewportRef = useRef(null)

  // Route detection: strictly separate Public Viewer (/) vs Admin Backoffice (/admin)
  const isAdminRoute = useMemo(() => {
    const path = window.location.pathname.replace(/\/+$/, "")
    return path === "/admin"
  }, [])

  // Theme state (Dark Slate default, Light mode optional)
  const [theme, setTheme] = useState(() => localStorage.getItem("dt_theme") || "dark")
  useEffect(() => {
    const root = document.documentElement
    if (theme === "light") {
      root.classList.add("light")
    } else {
      root.classList.remove("light")
    }
    localStorage.setItem("dt_theme", theme)
  }, [theme])

  // Hamburger Sheet state
  const [menuOpen, setMenuOpen] = useState(false)
  const [menuPinned, setMenuPinned] = useState(() => {
    try { return localStorage.getItem("ludus.menuPinned") === "1" } catch { return false }
  })
  const toggleMenuPinned = useCallback(() => {
    setMenuPinned((prev) => {
      const next = !prev
      try { localStorage.setItem("ludus.menuPinned", next ? "1" : "0") } catch { /* storage unavailable */ }
      return next
    })
  }, [])

  // Data state
  const [devices, setDevices] = useState([])
  const [rooms, setRooms] = useState([])
  const [networks, setNetworks] = useState([])
  const [activeInterfaces, setActiveInterfaces] = useState([])
  const [scanStatus, setScanStatus] = useState({ running: false, progress: 0, cidr: "" })
  const [modelStats, setModelStats] = useState({ loaded: false, meshCount: 0 })

  // 3D Viewer Layer & Filter State (passed to ThreeViewport as viewState)
  const [viewState, setViewState] = useState(() => {
    try {
      const saved = sessionStorage.getItem("ludus_user_view_state")
      if (saved) return { ...DEFAULT_VIEW_STATE, ...JSON.parse(saved) }
    } catch (_) {}
    return DEFAULT_VIEW_STATE
  })
  const [adminDefaultViewState, setAdminDefaultViewState] = useState(null)
  const [directorySearch, setDirectorySearch] = useState("")

  const updateView = useCallback((patch) => {
    setViewState((prev) => {
      const next = { ...prev, ...patch }
      try {
        sessionStorage.setItem("ludus_user_view_state", JSON.stringify(next))
      } catch (_) {}
      return next
    })
  }, [])

  const toggleCategoryFilter = useCallback((catId) => {
    setViewState((prev) => {
      const exists = prev.enabledCategories.includes(catId)
      const next = exists
        ? prev.enabledCategories.filter((id) => id !== catId)
        : [...prev.enabledCategories, catId]
      return { ...prev, enabledCategories: next }
    })
  }, [])

  const toggleAllCategories = useCallback(() => {
    setViewState((prev) => {
      const allIds = DEVICE_CATEGORIES.map((c) => c.id)
      const next = prev.enabledCategories.length === allIds.length ? [] : allIds
      return { ...prev, enabledCategories: next }
    })
  }, [])

  // Selected Device for Inspection Modal
  const [selectedDeviceId, setSelectedDeviceId] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)

  // Selected 3D Server Rack for Rackula 19-Inch Elevation Designer
  const [selectedRackId, setSelectedRackId] = useState(null)
  const [rackModalOpen, setRackModalOpen] = useState(false)
  const [rackHierarchyModalOpen, setRackHierarchyModalOpen] = useState(false)

  const serverRacks = useMemo(
    () => devices.filter((d) => d.modelType === "server_rack" && d.isPlaced === true),
    [devices]
  )

  // Keep selectedRackId synchronized with active 3D server racks
  useEffect(() => {
    if (serverRacks.length === 0) {
      if (selectedRackId !== null) setSelectedRackId(null);
    } else if (selectedRackId && !serverRacks.some((r) => r.id === selectedRackId)) {
      setSelectedRackId(serverRacks[0].id);
    }
  }, [serverRacks, selectedRackId])

  const notifyRackulaOfRemoval = useCallback((removedRackId) => {
    try {
      const iframe = document.getElementById("rackula-designer-iframe");
      if (iframe?.contentWindow) {
        iframe.contentWindow.postMessage(
          { type: "LUDUS_RACK_REMOVED", rackId: removedRackId },
          "*"
        );
      }
    } catch {
      // ignore cross-origin safely
    }
  }, [])

  const rackulaRefreshTimeoutRef = useRef(null)
  const refreshRackulaIframe = useCallback((targetRackId) => {
    if (rackulaRefreshTimeoutRef.current) {
      clearTimeout(rackulaRefreshTimeoutRef.current)
    }
    rackulaRefreshTimeoutRef.current = setTimeout(() => {
      try {
        const iframe = document.getElementById("rackula-designer-iframe")
        if (iframe && iframe.contentWindow) {
          iframe.contentWindow.postMessage(
            { type: "LUDUS_RACK_UPDATED", rackId: targetRackId },
            "*"
          )
          iframe.src = iframe.src
        }
      } catch {
        // ignore cross-origin or detached iframe safely
      }
    }, 250)
  }, [])
  const selectedRackDevice = useMemo(
    () => devices.find((d) => d.id === selectedRackId) || serverRacks[0] || null,
    [devices, selectedRackId, serverRacks]
  )

  // Selected Room for Inspection & Renumbering Modal
  const [selectedRoomId, setSelectedRoomId] = useState(null)
  const [roomModalOpen, setRoomModalOpen] = useState(false)
  const [roomDirectorySearch, setRoomDirectorySearch] = useState("")
  const [expandedDirectoryRoomId, setExpandedDirectoryRoomId] = useState(null)

  // Admin Auth & Backoffice state
  const [adminToken, setAdminToken] = useState(
    () => sessionStorage.getItem("dt_admin_token") || ""
  )
  const [adminAuthenticated, setAdminAuthenticated] = useState(false)

  // Open Rack Hierarchy & Elevation Inspector Modal (In-place modal, no new tab)
  const openRackHierarchy = useCallback((rackId) => {
    const targetId = rackId || selectedRackId || serverRacks[0]?.id;
    if (!targetId) {
      toast({
        title: "ไม่พบตู้แร็ค",
        description: "ยังไม่มีตู้แร็คที่จัดวางบนอาคาร 3D",
        variant: "destructive",
      });
      return;
    }
    setSelectedRackId(targetId);
    setRackHierarchyModalOpen(true);
  }, [selectedRackId, serverRacks, toast]);

  // Open Rackula 19-Inch Elevation Designer in a dedicated full-screen tab
  const openRackulaWindow = useCallback((rackId) => {
    const targetId = rackId || selectedRackId || serverRacks[0]?.id;
    if (!targetId) {
      toast({
        title: "ไม่พบตู้แร็ค",
        description: "ยังไม่มีตู้แร็คที่จัดวางบนอาคาร 3D",
        variant: "destructive",
      });
      return;
    }
    setSelectedRackId(targetId);
    const params = new URLSearchParams({ layout: targetId });
    if (isAdminRoute && adminToken) {
      params.set("token", adminToken);
    } else {
      params.set("readonly", "1");
    }
    window.open(`/rackula/?${params.toString()}`, "_blank");
    toast({
      title: "🚀 เปิดผังตู้แร็คในแท็บแยกแล้ว",
      description: `เปิด Rackula Designer สำหรับตู้แร็ค [${targetId}] เต็มจอเรียบร้อย`,
    });
  }, [selectedRackId, serverRacks, isAdminRoute, adminToken, toast]);
  const [loginDialogOpen, setLoginDialogOpen] = useState(false)
  const [passwordInput, setPasswordInput] = useState("")
  const [loginError, setLoginError] = useState("")

  // Admin Placement & Management state
  const [adminSearch, setAdminSearch] = useState("")
  const [adminRoomSearch, setAdminRoomSearch] = useState("")
  const [placingDevice, setPlacingDevice] = useState(null)
  const [placingRoom, setPlacingRoom] = useState(null)
  const [placementFloorIdx, setPlacementFloorIdx] = useState(0)
  const [placementRoom, setPlacementRoom] = useState("G01")
  const [autoSnapRoomEnabled, setAutoSnapRoomEnabled] = useState(true)
  const [placingModelType, setPlacingModelType] = useState("pin") // "pin" | "server_rack"
  const [placingRotationY, setPlacingRotationY] = useState(0) // 0, 90, 180, 270
  const [clampToRoomBoundsEnabled, setClampToRoomBoundsEnabled] = useState(true)
  const [activeAdminDeviceId, setActiveAdminDeviceId] = useState(null)
  const [deviceTransformMode, setDeviceTransformMode] = useState("translate") // "translate" | "rotate"
  const [subnetInput, setSubnetInput] = useState("192.168.110.0/24")
  const [singleIpInput, setSingleIpInput] = useState("")
  const [scanningSingleIp, setScanningSingleIp] = useState(false)

  // 3D Polygon (Point-by-Point) & Rectangle Zone Drawing, CAD Gizmo & Transactional Undo/Redo Stack (Ctrl+Z / Ctrl+Y)
  const [drawRoomZoneMode, setDrawRoomZoneMode] = useState(false)
  const [drawShapeType, setDrawShapeType] = useState("polygon") // "polygon" | "rectangle"
  const [polygonDraftCount, setPolygonDraftCount] = useState(0)
  const [snapToGrid, setSnapToGrid] = useState(true)
  const [magneticWallSnap, setMagneticWallSnap] = useState(true)
  const [activeAdminRoomId, setActiveAdminRoomId] = useState(null)
  const [roomTransformMode, setRoomTransformMode] = useState("vertices") // "vertices" | "translate" | "rotate" | "scale"
  const [undoStack, setUndoStack] = useState([])
  const [redoStack, setRedoStack] = useState([])

  // New Device / Room / Batch Room form state
  const [newDevForm, setNewDevForm] = useState({
    name: "",
    ip: "",
    category: "Switch",
    networkType: "LAN",
    vendor: "Cisco",
    model: "Catalyst",
  })
  const [newRoomForm, setNewRoomForm] = useState({
    roomNumber: "101",
    name: "",
    roomType: "Office",
    floorIdx: 1,
    color: "#60a5fa",
    vlan: "",
    width: 12,
    depth: 10,
  })
  const [batchRoomForm, setBatchRoomForm] = useState({
    floorIdx: 1,
    prefix: "10",
    startNumber: 1,
    count: 4,
    roomType: "Office",
    namePrefix: "ห้องปฏิบัติการ",
  })

  // Fetch initial state (Public vs Admin)
  const fetchState = useCallback(
    async (tokenOverride) => {
      const tok = tokenOverride !== undefined ? tokenOverride : adminToken
      try {
        if (isAdminRoute && tok) {
          const res = await fetch("/api/admin/state", {
            headers: { Authorization: `Bearer ${tok}` },
          })
          if (res.ok) {
            const data = await res.json()
            setDevices(data.devices || [])
            setRooms(data.rooms || [])
            setNetworks(data.networks || [])
            setActiveInterfaces(data.activeInterfaces || [])
            if (data.scanStatus) setScanStatus(data.scanStatus)
            if (data.networks?.[0]?.cidr) {
              setSubnetInput(data.networks[0].cidr)
            }
            const defView = data.metadata?.defaultViewState
            if (defView) {
              setAdminDefaultViewState(defView)
              if (!sessionStorage.getItem("ludus_user_view_state")) {
                setViewState((prev) => ({ ...prev, ...defView }))
              }
            }
            setAdminAuthenticated(true)
            setLoginDialogOpen(false)
            return
          } else if (res.status === 401) {
            sessionStorage.removeItem("dt_admin_token")
            setAdminToken("")
            setAdminAuthenticated(false)
            setLoginDialogOpen(true)
          }
        }

        // Public state (strictly returns ONLY isPlaced === true devices)
        const pubRes = await fetch("/api/public/state")
        if (pubRes.ok) {
          const pubData = await pubRes.json()
          setDevices(pubData.devices || [])
          setRooms(pubData.rooms || [])
          setNetworks(pubData.networks || [])
          setActiveInterfaces(pubData.activeInterfaces || [])
          const defView = pubData.metadata?.defaultViewState
          if (defView) {
            setAdminDefaultViewState(defView)
            if (!sessionStorage.getItem("ludus_user_view_state")) {
              setViewState((prev) => ({ ...prev, ...defView }))
            }
          }
        }
      } catch (err) {
        console.error("Failed to fetch state:", err)
      }
    },
    [isAdminRoute, adminToken]
  )

  useEffect(() => {
    if (isAdminRoute && !adminToken) {
      setLoginDialogOpen(true)
    }
    fetchState()
  }, [isAdminRoute, adminToken, fetchState])

  // Auto-open DeviceModal if navigated via new tab with ?device=<id>
  const handledUrlDeviceRef = useRef(false)
  useEffect(() => {
    if (handledUrlDeviceRef.current || devices.length === 0) return
    const params = new URLSearchParams(window.location.search)
    const targetDevId = params.get("device")
    if (targetDevId) {
      const found = devices.find((d) => d.id === targetDevId)
      if (found) {
        handledUrlDeviceRef.current = true
        setSelectedDeviceId(found.id)
        setModalOpen(true)
        if (found.position && found.floorIdx !== null && found.floorIdx !== undefined) {
          setViewState((prev) => ({ ...prev, selectedFloor: String(found.floorIdx) }))
          setTimeout(() => {
            viewportRef.current?.flyTo(found.position, Number(found.floorIdx))
          }, 350)
        }
      }
    }
  }, [devices])

  // WebSocket live telemetry connection with auto-reconnect (StrictMode-safe)
  useEffect(() => {
    let ws = null
    let isDisposed = false
    let reconnectTimer = null
    let retryDelay = 1000

    const connect = () => {
      if (isDisposed) return
      const proto = window.location.protocol === "https:" ? "wss" : "ws"
      ws = new WebSocket(`${proto}://${window.location.host}/ws`)

      ws.onopen = () => {
        retryDelay = 1000
      }

      ws.onmessage = (event) => {
        if (isDisposed) return
        try {
          const msg = JSON.parse(event.data)
          if (msg.type === "scan_progress") {
            const pct = msg.totalHosts
              ? Math.min(98, Math.round((msg.scannedHosts / msg.totalHosts) * 100))
              : msg.progress || msg.percent || 15
            setScanStatus({
              running: true,
              progress: pct,
              cidr: msg.cidr || msg.subnet || "",
            })
          } else if (msg.type === "scan_completed" || msg.type === "scan_complete") {
            setScanStatus({ running: false, progress: 100, cidr: "" })
            fetchState()
          } else if (msg.type === "default_view_updated" && msg.defaultViewState) {
            setAdminDefaultViewState(msg.defaultViewState)
          } else if (
            msg.type === "device_updated" ||
            msg.type === "device_discovered" ||
            msg.type === "state_changed" ||
            msg.type === "rack_updated" ||
            msg.type === "monitor_cycle"
          ) {
            fetchState()
            refreshRackulaIframe(msg.rackId)
          }
        } catch {
          // ignore malformed WS messages
        }
      }

      ws.onclose = () => {
        if (isDisposed) return
        reconnectTimer = setTimeout(() => {
          connect()
        }, retryDelay)
        retryDelay = Math.min(retryDelay * 1.5, 10000)
      }

      ws.onerror = () => {
        // ws.onclose will schedule reconnect
      }
    }

    // Cross-tab Zero-Latency BroadcastChannel listener
    let syncChannel = null
    if (typeof BroadcastChannel !== "undefined") {
      try {
        syncChannel = new BroadcastChannel("ludus_digital_twin_sync")
        syncChannel.onmessage = (event) => {
          if (event.data?.type === "rack_updated" || event.data?.type === "state_changed") {
            fetchState()
            refreshRackulaIframe(event.data?.rackId)
          }
        }
      } catch {}
    }

    const connectTimer = setTimeout(() => {
      connect()
    }, 60)

    return () => {
      isDisposed = true
      clearTimeout(connectTimer)
      if (syncChannel) {
        syncChannel.close()
        syncChannel = null
      }
      if (reconnectTimer) clearTimeout(reconnectTimer)
      if (rackulaRefreshTimeoutRef.current) clearTimeout(rackulaRefreshTimeoutRef.current)
      if (ws) {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close()
        } else if (ws.readyState === WebSocket.CONNECTING) {
          ws.onopen = () => ws.close()
        }
      }
    }
  }, [fetchState, refreshRackulaIframe])

  // Strictly separate Placed vs Unplaced devices
  // Rule: Any device that has NOT been placed/organized by Admin (isPlaced === false)
  // MUST NOT be shown on 3D view, top stats, or directory!
  const placedDevices = useMemo(
    () =>
      devices.filter(
        (d) =>
          !isUnboundRackPart(d) &&
          d.isPlaced === true &&
          d.position !== null &&
          d.position !== undefined &&
          d.floorIdx !== null &&
          d.floorIdx !== undefined
      ),
    [devices]
  )

  const unplacedDevices = useMemo(
    () =>
      devices.filter(
        (d) =>
          !isUnboundRackPart(d) &&
          (!d.isPlaced ||
          d.position === null ||
          d.position === undefined ||
          d.floorIdx === null ||
          d.floorIdx === undefined)
      ),
    [devices]
  )

  // Filtered placed devices for Hamburger Directory
  const filteredPlacedDevices = useMemo(() => {
    return placedDevices.filter((d) => {
      if (
        viewState.selectedFloor !== "all" &&
        Number(d.floorIdx) !== Number(viewState.selectedFloor)
      ) {
        return false
      }
      if (viewState.filterSubnet !== "all" && d.subnet !== viewState.filterSubnet) {
        return false
      }
      if (
        viewState.filterStatus !== "all" &&
        String(d.status || "Online").toLowerCase() !==
          String(viewState.filterStatus).toLowerCase()
      ) {
        return false
      }
      const catKey = DEVICE_CATEGORIES.some((c) => c.id === d.category)
        ? d.category
        : "Custom"
      if (!viewState.enabledCategories.includes(catKey)) {
        return false
      }
      if (directorySearch.trim()) {
        const q = directorySearch.toLowerCase()
        const match =
          (d.name || "").toLowerCase().includes(q) ||
          (d.ip || "").toLowerCase().includes(q) ||
          (d.roomNumber || "").toLowerCase().includes(q) ||
          (d.vendor || "").toLowerCase().includes(q) ||
          (d.category || "").toLowerCase().includes(q)
        if (!match) return false
      }
      return true
    })
  }, [placedDevices, viewState, directorySearch])

  const activeAdminDevice = useMemo(() => {
    return devices.find((d) => d.id === activeAdminDeviceId) || null
  }, [devices, activeAdminDeviceId])

  // Filtered unplaced queue for Admin Backoffice
  const filteredUnplacedDevices = useMemo(() => {
    if (!adminSearch.trim()) return unplacedDevices
    const q = adminSearch.toLowerCase()
    return unplacedDevices.filter(
      (d) =>
        (d.name || "").toLowerCase().includes(q) ||
        (d.ip || "").toLowerCase().includes(q) ||
        (d.mac || "").toLowerCase().includes(q) ||
        (d.vendor || "").toLowerCase().includes(q) ||
        (d.category || "").toLowerCase().includes(q)
    )
  }, [unplacedDevices, adminSearch])

  // Telemetry stats (ONLY counting placedDevices)
  const stats = useMemo(() => {
    // Racks are physical cabinets and IP-less rack parts are not network devices: not counted
    const statDevices = placedDevices.filter(
      (d) => d.modelType !== "server_rack" && !(d.parentRackId && !String(d.ip || "").trim())
    )
    const total = statDevices.length
    const online = statDevices.filter(
      (d) => String(d.status || "Online").toLowerCase() === "online"
    ).length
    const warning = statDevices.filter(
      (d) => String(d.status || "").toLowerCase() === "warning"
    ).length
    const offline = statDevices.filter(
      (d) => String(d.status || "").toLowerCase() === "offline"
    ).length
    return { total, online, warning, offline }
  }, [placedDevices])

  const selectedDevice = useMemo(
    () => devices.find((d) => d.id === selectedDeviceId) || null,
    [devices, selectedDeviceId]
  )

  const selectedRack = useMemo(
    () => devices.find((d) => d.id === selectedRackId) || null,
    [devices, selectedRackId]
  )

  const selectedRoom = useMemo(
    () => rooms.find((r) => r.id === selectedRoomId) || null,
    [rooms, selectedRoomId]
  )

  const filteredDirectoryRooms = useMemo(() => {
    return (rooms || []).filter((rm) => {
      if (
        viewState.selectedFloor !== "all" &&
        Number(rm.floorIdx ?? 0) !== Number(viewState.selectedFloor)
      ) {
        return false
      }
      if (roomDirectorySearch.trim()) {
        const q = roomDirectorySearch.toLowerCase()
        const match =
          (rm.roomNumber || "").toLowerCase().includes(q) ||
          (rm.name || "").toLowerCase().includes(q) ||
          (rm.roomType || "").toLowerCase().includes(q) ||
          (rm.vlan || "").toLowerCase().includes(q)
        if (!match) return false
      }
      return true
    })
  }, [rooms, viewState.selectedFloor, roomDirectorySearch])

  const filteredAdminRooms = useMemo(() => {
    return (rooms || []).filter((rm) => {
      if (!adminRoomSearch.trim()) return true
      const q = adminRoomSearch.toLowerCase()
      return (
        (rm.roomNumber || "").toLowerCase().includes(q) ||
        (rm.name || "").toLowerCase().includes(q) ||
        (rm.roomType || "").toLowerCase().includes(q) ||
        (rm.vlan || "").toLowerCase().includes(q)
      )
    })
  }, [rooms, adminRoomSearch])

  const roomsOnPlacementFloor = useMemo(() => {
    return (rooms || []).filter(
      (r) => Number(r.floorIdx ?? 0) === Number(placementFloorIdx)
    )
  }, [rooms, placementFloorIdx])

  // Admin Login handler
  const handleAdminLogin = async (e) => {
    e?.preventDefault()
    setLoginError("")
    try {
      const res = await fetch("/api/admin/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: passwordInput }),
      })
      const data = await res.json()
      if (res.ok && data.token) {
        sessionStorage.setItem("dt_admin_token", data.token)
        setAdminToken(data.token)
        setAdminAuthenticated(true)
        setLoginDialogOpen(false)
        toast({
          title: "เข้าสู่ระบบ Admin สำเร็จ",
          description: "พร้อมจัดการตำแหน่งอุปกรณ์บนอาคาร 3D และสแกนเครือข่าย",
          variant: "success",
        })
        fetchState(data.token)
      } else {
        setLoginError(data.error || "รหัสผ่านไม่ถูกต้อง")
      }
    } catch (err) {
      setLoginError(err.message)
    }
  }

  // Start placing a device on the 3D building
  const startPlacingDevice = (dev, forcedModelType = null) => {
    setPlacingRoom(null)
    setDrawRoomZoneMode(false)
    setActiveAdminRoomId(null)

    // Smart-resolve the target room and floor if rooms exist in the project:
    let targetFloorIdx =
      viewState.selectedFloor === "all"
        ? (dev.floorIdx !== null && dev.floorIdx !== undefined ? Number(dev.floorIdx) : null)
        : Number(viewState.selectedFloor)

    const candidateRoom =
      (activeAdminRoomId && rooms.find((r) => r.id === activeAdminRoomId)) ||
      (dev.roomId && rooms.find((r) => r.id === dev.roomId)) ||
      (dev.roomNumber && rooms.find((r) => r.roomNumber === dev.roomNumber)) ||
      (targetFloorIdx !== null ? rooms.find((r) => Number(r.floorIdx) === Number(targetFloorIdx)) : null) ||
      (rooms.length > 0 ? rooms[0] : null)

    if (candidateRoom) {
      targetFloorIdx = Number(candidateRoom.floorIdx ?? 0)
      setPlacementRoom(candidateRoom.roomNumber)
    } else {
      targetFloorIdx = targetFloorIdx ?? 0
      const defaultRoomPrefix =
        targetFloorIdx === 0 ? "G" : targetFloorIdx === 3 ? "RF-" : `${targetFloorIdx}`
      setPlacementRoom(dev.roomNumber || `${defaultRoomPrefix}01`)
    }

    setPlacementFloorIdx(targetFloorIdx)
    if (viewState.selectedFloor !== "all" && Number(viewState.selectedFloor) !== targetFloorIdx) {
      updateView({ selectedFloor: String(targetFloorIdx) })
    }

    const resolvedModelType =
      forcedModelType || dev.modelType || (dev.category === 'Server' ? 'server_rack' : 'pin')
    setPlacingModelType(resolvedModelType)
    setPlacingRotationY(Number(dev.rotationY ?? 0))
    setPlacingDevice(dev)
    toast({
      title: `โหมดจัดวางอุปกรณ์ 3D: ${dev.name || dev.ip}`,
      description: candidateRoom
        ? `บังคับจัดวางในกรอบห้อง [${candidateRoom.roomNumber}] ${candidateRoom.name} บน ${FLOORS.find((f) => f.index === targetFloorIdx)?.shortLabel || 'Floor'}`
        : "คลิกบนพื้นห้องในอาคาร 3D ได้เลย ระบบจะล็อกให้อยู่ในกรอบห้องเสมอ",
    })
  }

  // Quick Server Rack 3D Placement Launcher from Toolbar:
  // always an EMPTY rack (never hijacks a scanned device). Ask for the name first, then place.
  const [rackNameDialogOpen, setRackNameDialogOpen] = useState(false)
  const rackSuggestedName = useMemo(() => {
    const racks = devices.filter((d) => d.modelType === 'server_rack')
    const taken = new Set(racks.map((d) => d.name))
    let n = racks.length + 1
    while (taken.has(`Rack-${String(n).padStart(2, '0')}`)) n += 1
    return `Rack-${String(n).padStart(2, '0')}`
  }, [devices])

  const handleQuickPlaceServerRack = () => setRackNameDialogOpen(true)

  const handleConfirmRackName = (rackName) => {
    setRackNameDialogOpen(false)
    const candidateRoom =
      (activeAdminRoomId && rooms.find((r) => r.id === activeAdminRoomId)) ||
      (rooms.length > 0 ? rooms[0] : null)
    const targetFloorIdx = candidateRoom
      ? Number(candidateRoom.floorIdx ?? 0)
      : viewState.selectedFloor === "all"
      ? 0
      : Number(viewState.selectedFloor)

    startPlacingDevice(
      {
        name: rackName,
        category: 'Server',
        modelType: 'server_rack',
        rotationY: 0,
        floorIdx: targetFloorIdx,
        isPlaced: false,
        color: '#38bdf8',
        status: 'Online',
        vendor: 'Server Rack Cabinet',
        rackConfig: { rackHeight: 42 },
      },
      'server_rack'
    )
  }
  // Start placing or moving a Room on the 3D building
  const startPlacingRoom = (roomDraft) => {
    setPlacingDevice(null)
    setDrawRoomZoneMode(false)
    setActiveAdminRoomId(null)
    const targetFloorIdx = Number(
      roomDraft.floorIdx ??
        (viewState.selectedFloor === "all" ? 0 : Number(viewState.selectedFloor))
    )
    const rMeta =
      ROOM_TYPES.find((r) => r.id === roomDraft.roomType) || ROOM_TYPES[1]
    setPlacementFloorIdx(targetFloorIdx)
    updateView({ selectedFloor: String(targetFloorIdx), showRooms: true })
    setPlacingRoom({
      id: roomDraft.id || "",
      roomNumber: (roomDraft.roomNumber || "101").trim() || "101",
      name: (roomDraft.name || `Room ${roomDraft.roomNumber || "101"}`).trim(),
      roomType: roomDraft.roomType || "Office",
      floorIdx: targetFloorIdx,
      color: roomDraft.color || rMeta.color || "#38bdf8",
      vlan: roomDraft.vlan || "",
      description: roomDraft.description || "",
      width: Number(roomDraft.zoneSize?.width ?? roomDraft.width ?? rMeta.defaultWidth ?? 12),
      depth: Number(roomDraft.zoneSize?.depth ?? roomDraft.depth ?? rMeta.defaultDepth ?? 10),
    })
    toast({
      title: `โหมดปักหมุดพื้นที่ห้อง 3D: [${roomDraft.roomNumber || "101"}]`,
      description: "คลิกบนพื้นอาคาร 3D ในจุดกึ่งกลางห้องที่ต้องการวางป้ายและไฮไลต์กรอบห้อง",
    })
  }

  // Toggle 3D Polygon / Rectangle Zone Drawing Mode
  const toggleDrawRoomZoneMode = useCallback(() => {
    setPlacingDevice(null)
    setPlacingRoom(null)
    const next = !drawRoomZoneMode
    setDrawRoomZoneMode(next)
    if (next) {
      const targetFl =
        viewState.selectedFloor === "all"
          ? Number(newRoomForm.floorIdx ?? 1)
          : Number(viewState.selectedFloor)
      setPlacementFloorIdx(targetFl)
      updateView({ selectedFloor: String(targetFl), showRooms: true, showPlans: true })
      setNewRoomForm((f) => ({ ...f, floorIdx: targetFl }))
      toast({
        title: "เปิดโหมดปักหมุดวาดกรอบห้องทีละมุม (Polygon Point-by-Point)",
        description:
          "คลิกปักหมุดตามมุมห้องทีละจุด (รองรับ Snap มุมเสา/ผนัง และกด Shift ล็อกมุม 45°/90°) คลิกจุดแรกหรือกด Enter เพื่อปิดกรอบห้อง",
        variant: "success",
      })
    }
  }, [drawRoomZoneMode, viewState.selectedFloor, newRoomForm.floorIdx, updateView, toast])

  // Active Admin Room object (selected on 3D for CAD Gizmo Resize/Move or Quick Edit)
  const activeAdminRoom = useMemo(
    () => rooms.find((r) => r.id === activeAdminRoomId) || null,
    [rooms, activeAdminRoomId]
  )

  // Push a transactional command onto the Undo Stack (clears Redo Stack)
  const pushUndoCommand = useCallback((cmd) => {
    setUndoStack((prev) => [...prev.slice(-29), cmd])
    setRedoStack([])
  }, [])

  // Handle 3D Polygon or Rectangle Zone Drawn
  const handleRoomZoneDrawn = useCallback(
    async ({ floorIdx, x, y, z, width, depth, polygon, areaSqM }) => {
      const fIdx = Number(floorIdx ?? placementFloorIdx ?? 0)
      const fl = FLOORS.find((f) => f.index === fIdx) || FLOORS[0]
      const rMeta =
        ROOM_TYPES.find((r) => r.id === newRoomForm.roomType) || ROOM_TYPES[1]
      const roomNo = (newRoomForm.roomNumber || "101").trim() || "101"
      const roomName = (newRoomForm.name || "").trim() || `Room ${roomNo}`

      try {
        const res = await fetch("/api/admin/rooms", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${adminToken}`,
          },
          body: JSON.stringify({
            roomNumber: roomNo,
            name: roomName,
            roomType: newRoomForm.roomType || "Office",
            floorIdx: fIdx,
            color: newRoomForm.color || rMeta.color || "#38bdf8",
            vlan: (newRoomForm.vlan || "").trim(),
            zoneSize: {
              width: Math.max(2, Number(width) || 6),
              depth: Math.max(2, Number(depth) || 6),
            },
            polygon: Array.isArray(polygon) && polygon.length >= 3 ? polygon : [],
            position: { x, y, z },
          }),
        })
        const data = await res.json()
        if (res.ok && data.room) {
          pushUndoCommand({
            type: "CREATE_ROOM",
            room: data.room,
          })
          setActiveAdminRoomId(data.room.id)
          setRoomTransformMode(
            Array.isArray(data.room.polygon) && data.room.polygon.length >= 3
              ? "vertices"
              : "scale"
          )
          const nextNo = incrementRoomNumber(roomNo)
          setNewRoomForm((prev) => ({
            ...prev,
            floorIdx: fIdx,
            roomNumber: nextNo,
            name: "",
            width: Math.round(width),
            depth: Math.round(depth),
          }))
          const calcArea =
            areaSqM !== undefined
              ? areaSqM
              : Array.isArray(polygon) && polygon.length >= 3
              ? computePolygonArea(polygon).toFixed(1)
              : (width * depth).toFixed(1)
          toast({
            title:
              Array.isArray(polygon) && polygon.length >= 3
                ? `ปักหมุดกรอบห้อง [${data.room.roomNumber}] (${polygon.length} มุม · ${calcArea} ตร.ม.) สำเร็จ!`
                : `วาดกรอบห้อง [${data.room.roomNumber}] (${width}m × ${depth}m) สำเร็จ!`,
            description: `ชั้น ${fl.shortLabel} — เลขห้องถัดไปพร้อมวาด: [${nextNo}] (คลิกหมุดมุมเพื่อดัดรูปทรง หรือกด Ctrl+Z เพื่อ Undo)`,
            variant: "success",
          })
          fetchState()
        } else {
          throw new Error(data.error || "ไม่สามารถสร้างกรอบโซนห้องได้")
        }
      } catch (err) {
        toast({
          title: "สร้างกรอบโซนห้องไม่สำเร็จ",
          description: err.message,
          variant: "destructive",
        })
      }
    },
    [placementFloorIdx, newRoomForm, adminToken, pushUndoCommand, toast, fetchState]
  )

  // Handle Three.js TransformControls Gizmo commit (Vertex Drag, Resize, Move, or Rotate Room Zone in 3D)
  const handleRoomTransformCommit = useCallback(
    async ({ roomId, position, zoneSize, polygon }) => {
      const target = rooms.find((r) => r.id === roomId)
      if (!target) return
      const beforeRoom = JSON.parse(JSON.stringify(target))
      const updatedPayload = {
        ...target,
        position: {
          x: position.x,
          y: position.y,
          z: position.z,
        },
        zoneSize: {
          width: zoneSize.width,
          depth: zoneSize.depth,
        },
        polygon: polygon !== undefined ? polygon : target.polygon || [],
      }
      try {
        const res = await fetch(`/api/admin/rooms/${encodeURIComponent(roomId)}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${adminToken}`,
          },
          body: JSON.stringify(updatedPayload),
        })
        const data = await res.json()
        if (res.ok && data.room) {
          pushUndoCommand({
            type: "UPDATE_ROOM",
            beforeRoom,
            afterRoom: data.room,
          })
          toast({
            title: `อัปเดตรูปทรง/ตำแหน่งกรอบห้อง [${data.room.roomNumber}] สำเร็จ`,
            description:
              Array.isArray(data.room.polygon) && data.room.polygon.length >= 3
                ? `Polygon ${data.room.polygon.length} มุม · พื้นที่ ${computePolygonArea(
                    data.room.polygon
                  ).toFixed(1)} ตร.ม. (กด Ctrl+Z เพื่อย้อนกลับ)`
                : `ขนาดโซนใหม่: ${data.room.zoneSize.width}m × ${data.room.zoneSize.depth}m (กด Ctrl+Z เพื่อย้อนกลับ)`,
          })
          fetchState()
        }
      } catch (err) {
        toast({
          title: "ปรับขนาดกรอบห้องไม่สำเร็จ",
          description: err.message,
          variant: "destructive",
        })
      }
    },
    [rooms, adminToken, pushUndoCommand, toast, fetchState]
  )

  // Delete a Room Zone with Undo support (Button or Delete/Backspace shortcut)
  const handleDeleteRoomZone = useCallback(
    async (roomId) => {
      const target = rooms.find((r) => r.id === roomId)
      if (!target) return
      const beforeRoom = JSON.parse(JSON.stringify(target))
      try {
        const res = await fetch(`/api/admin/rooms/${encodeURIComponent(roomId)}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${adminToken}`,
          },
        })
        if (res.ok) {
          pushUndoCommand({
            type: "DELETE_ROOM",
            room: beforeRoom,
          })
          if (activeAdminRoomId === roomId) {
            setActiveAdminRoomId(null)
          }
          if (selectedRoomId === roomId) {
            setRoomModalOpen(false)
          }
          toast({
            title: `ลบกรอบห้อง [${beforeRoom.roomNumber}] (${beforeRoom.name}) แล้ว`,
            description: "กด Ctrl+Z หรือปุ่ม Undo บน Toolbar เพื่อกู้คืนกรอบห้องนี้ได้ทันที",
          })
          fetchState()
        }
      } catch (err) {
        toast({
          title: "ลบกรอบห้องไม่สำเร็จ",
          description: err.message,
          variant: "destructive",
        })
      }
    },
    [rooms, adminToken, activeAdminRoomId, selectedRoomId, pushUndoCommand, toast, fetchState]
  )

  // Commit Move & Rotate transform for placed device / server rack
  const handleDeviceTransformCommit = useCallback(
    async ({ deviceId, position, rotationY }) => {
      const dev = devices.find((d) => d.id === deviceId)
      if (!dev) return

      try {
        const res = await fetch(`/api/admin/devices/${encodeURIComponent(deviceId)}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${adminToken}`,
          },
          body: JSON.stringify({
            ...dev,
            position,
            rotationY,
          }),
        })
        if (res.ok) {
          fetchState()
        }
      } catch (err) {
        console.error("Failed to update device transform:", err)
      }
    },
    [devices, adminToken, fetchState]
  )

  // Quick Rotate active device by +90° or -90°
  const handleQuickRotateActiveDevice = useCallback(
    async (deltaDeg = 90) => {
      if (!activeAdminDeviceId) return
      const dev = devices.find((d) => d.id === activeAdminDeviceId)
      if (!dev) return
      const currentAngle = Number(dev.rotationY ?? 0)
      const nextAngle = (currentAngle + deltaDeg + 360) % 360
      await handleDeviceTransformCommit({
        deviceId: activeAdminDeviceId,
        position: dev.position,
        rotationY: nextAngle,
      })
      toast({
        title: `หมุนตู้ ${dev.name || dev.ip}`,
        description: `ปรับทิศทางเป็น ${nextAngle}° เรียบร้อยแล้ว`,
      })
    },
    [activeAdminDeviceId, devices, handleDeviceTransformCommit, toast]
  )

  // Permanent Delete device from database
  const handleDeleteDevicePermanently = useCallback(
    async (deviceId) => {
      const dev = devices.find((d) => d.id === deviceId)
      if (!dev) return
      const confirmDel = window.confirm(
        `คุณแน่ใจหรือไม่ว่าต้องการลบ "${dev.name || dev.ip}" ออกจากระบบอย่างถาวร?`
      )
      if (!confirmDel) return

      try {
        const res = await fetch(`/api/admin/devices/${encodeURIComponent(deviceId)}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${adminToken}`,
          },
        })
        if (res.ok) {
          setActiveAdminDeviceId(null)
          if (deviceId === selectedDeviceId) {
            setSelectedDeviceId(null)
            setModalOpen(false)
          }
          if (deviceId === selectedRackId || dev.modelType === "server_rack") {
            notifyRackulaOfRemoval(deviceId)
            setSelectedRackId(null)
          }
          toast({
            title: "ลบอุปกรณ์ออกจากระบบสำเร็จ",
            description: `${dev.name || dev.ip} ถูกลบเรียบร้อยแล้ว`,
            variant: "destructive",
          })
          fetchState()
        }
      } catch (err) {
        toast({
          title: "ลบอุปกรณ์ไม่สำเร็จ",
          description: err.message,
          variant: "destructive",
        })
      }
    },
    [devices, adminToken, toast, fetchState, selectedDeviceId, selectedRackId, notifyRackulaOfRemoval]
  )

  // Unplace device (remove from 3D view back to Admin queue)
  const handleUnplaceDevice = useCallback(
    async (deviceId) => {
      try {
        const res = await fetch(
          `/api/admin/devices/${encodeURIComponent(deviceId)}/unplace`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${adminToken}`,
            },
          }
        )
        if (res.ok) {
          const dev = devices.find((d) => d.id === deviceId)
          if (deviceId === selectedRackId || dev?.modelType === "server_rack") {
            notifyRackulaOfRemoval(deviceId)
            setSelectedRackId(null)
          }
          toast({
            title: "ถอนหมุดอุปกรณ์กลับเข้าคิวแล้ว",
            description:
              "อุปกรณ์นี้จะไม่แสดงบนหน้า Public 3D Viewer จนกว่าจะจัดวางใหม่",
          })
          setModalOpen(false)
          setActiveAdminDeviceId(null)
          fetchState()
        }
      } catch (err) {
        toast({
          title: "ไม่สามารถถอนหมุดได้",
          description: err.message,
          variant: "destructive",
        })
      }
    },
    [devices, adminToken, toast, fetchState, selectedRackId, notifyRackulaOfRemoval]
  )

  // Save current layer & view settings as system-wide default for general users
  const handleSaveAsAdminDefaultView = useCallback(async () => {
    try {
      const res = await fetch("/api/admin/settings/default-view", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify(viewState),
      })
      const data = await res.json()
      if (res.ok && data.defaultViewState) {
        setAdminDefaultViewState(data.defaultViewState)
        toast({
          title: "บันทึกเป็นมุมมองเริ่มต้นสำเร็จ!",
          description: "การเปิด-ปิด Layer ปัจจุบันถูกบันทึกเป็นค่า Default กลางสำหรับ User ทั่วไปแล้ว",
          variant: "success",
        })
      } else {
        throw new Error(data.error || "Failed to save default view")
      }
    } catch (err) {
      toast({
        title: "บันทึกค่าเริ่มต้นไม่สำเร็จ",
        description: err.message,
        variant: "destructive",
      })
    }
  }, [adminToken, viewState, toast])

  // Reset current viewer layers back to Admin default
  const handleResetToAdminDefaultView = useCallback(() => {
    try {
      sessionStorage.removeItem("ludus_user_view_state")
    } catch (_) {}
    const base = adminDefaultViewState || DEFAULT_VIEW_STATE
    setViewState(base)
    toast({
      title: "คืนค่ามุมมองเริ่มต้นแล้ว",
      description: "รีเซ็ตเลเยอร์กลับสู่มุมมองมาตรฐานที่ Admin กำหนด",
    })
  }, [adminDefaultViewState, toast])

  // Execute Transactional Undo (Ctrl+Z)
  const handleUndo = useCallback(async () => {
    if (undoStack.length === 0) return
    const cmd = undoStack[undoStack.length - 1]
    setUndoStack((prev) => prev.slice(0, -1))

    try {
      if (cmd.type === "CREATE_ROOM") {
        await fetch(`/api/admin/rooms/${encodeURIComponent(cmd.room.id)}`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${adminToken}` },
        })
        setRedoStack((prev) => [...prev, cmd])
        if (activeAdminRoomId === cmd.room.id) setActiveAdminRoomId(null)
        toast({
          title: `Undo (Ctrl+Z): ยกเลิกการวาดกรอบห้อง [${cmd.room.roomNumber}]`,
          description: "กด Ctrl+Y เพื่อทำซ้ำ (Redo)",
        })
      } else if (cmd.type === "DELETE_ROOM") {
        await fetch("/api/admin/rooms", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${adminToken}`,
          },
          body: JSON.stringify(cmd.room),
        })
        setRedoStack((prev) => [...prev, cmd])
        setActiveAdminRoomId(cmd.room.id)
        toast({
          title: `Undo (Ctrl+Z): กู้คืนกรอบห้อง [${cmd.room.roomNumber}] สำเร็จ!`,
          description: `${cmd.room.name} (${cmd.room.zoneSize?.width ?? 12}m × ${cmd.room.zoneSize?.depth ?? 10}m)`,
          variant: "success",
        })
      } else if (cmd.type === "UPDATE_ROOM") {
        await fetch(`/api/admin/rooms/${encodeURIComponent(cmd.beforeRoom.id)}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${adminToken}`,
          },
          body: JSON.stringify(cmd.beforeRoom),
        })
        setRedoStack((prev) => [...prev, cmd])
        setActiveAdminRoomId(cmd.beforeRoom.id)
        toast({
          title: `Undo (Ctrl+Z): คืนค่าขนาด/ตำแหน่งห้อง [${cmd.beforeRoom.roomNumber}]`,
          description: `กลับสู่ขนาด ${cmd.beforeRoom.zoneSize?.width}m × ${cmd.beforeRoom.zoneSize?.depth}m`,
        })
      }
      fetchState()
    } catch (err) {
      toast({
        title: "Undo ไม่สำเร็จ",
        description: err.message,
        variant: "destructive",
      })
    }
  }, [undoStack, adminToken, activeAdminRoomId, toast, fetchState])

  // Execute Transactional Redo (Ctrl+Y / Ctrl+Shift+Z)
  const handleRedo = useCallback(async () => {
    if (redoStack.length === 0) return
    const cmd = redoStack[redoStack.length - 1]
    setRedoStack((prev) => prev.slice(0, -1))

    try {
      if (cmd.type === "CREATE_ROOM") {
        await fetch("/api/admin/rooms", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${adminToken}`,
          },
          body: JSON.stringify(cmd.room),
        })
        setUndoStack((prev) => [...prev, cmd])
        setActiveAdminRoomId(cmd.room.id)
        toast({
          title: `Redo (Ctrl+Y): สร้างกรอบห้อง [${cmd.room.roomNumber}] อีกครั้ง`,
          variant: "success",
        })
      } else if (cmd.type === "DELETE_ROOM") {
        await fetch(`/api/admin/rooms/${encodeURIComponent(cmd.room.id)}`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${adminToken}` },
        })
        setUndoStack((prev) => [...prev, cmd])
        if (activeAdminRoomId === cmd.room.id) setActiveAdminRoomId(null)
        toast({
          title: `Redo (Ctrl+Y): ลบกรอบห้อง [${cmd.room.roomNumber}]`,
        })
      } else if (cmd.type === "UPDATE_ROOM") {
        await fetch(`/api/admin/rooms/${encodeURIComponent(cmd.afterRoom.id)}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${adminToken}`,
          },
          body: JSON.stringify(cmd.afterRoom),
        })
        setUndoStack((prev) => [...prev, cmd])
        setActiveAdminRoomId(cmd.afterRoom.id)
        toast({
          title: `Redo (Ctrl+Y): ปรับขนาดกรอบห้อง [${cmd.afterRoom.roomNumber}]`,
        })
      }
      fetchState()
    } catch (err) {
      toast({
        title: "Redo ไม่สำเร็จ",
        description: err.message,
        variant: "destructive",
      })
    }
  }, [redoStack, adminToken, activeAdminRoomId, toast, fetchState])

  // Global Keyboard Shortcuts for Admin (Ctrl+Z Undo, Ctrl+Y / Ctrl+Shift+Z Redo, Enter Close Polygon, Delete/Backspace, Escape)
  useEffect(() => {
    if (!isAdminRoute || !adminAuthenticated) return

    const onKeyDown = (e) => {
      const tag = (e.target?.tagName || "").toUpperCase()
      const isTyping =
        tag === "INPUT" ||
        tag === "TEXTAREA" ||
        tag === "SELECT" ||
        e.target?.isContentEditable

      if (e.key === "Escape") {
        if (polygonDraftCount > 0 && viewportRef.current?.cancelPolygonDraft) {
          viewportRef.current.cancelPolygonDraft()
          return
        }
        setDrawRoomZoneMode(false)
        setPlacingRoom(null)
        setPlacingDevice(null)
        setActiveAdminRoomId(null)
        setActiveAdminDeviceId(null)
        return
      }

      if (isTyping) return

      // Hotkeys for Active 3D Device / Server Rack (Move, Rotate, Unplace)
      if (activeAdminDeviceId) {
        if (e.key.toLowerCase() === "t" || e.key.toLowerCase() === "m") {
          e.preventDefault()
          setDeviceTransformMode("translate")
          return
        }
        if (e.key.toLowerCase() === "r") {
          e.preventDefault()
          handleQuickRotateActiveDevice(90)
          return
        }
        if (e.key === "Delete" || e.key === "Backspace") {
          e.preventDefault()
          handleUnplaceDevice(activeAdminDeviceId)
          setActiveAdminDeviceId(null)
          return
        }
      }

      // Enter -> Finish / Close active Polygon draft if >= 3 vertices
      if (e.key === "Enter" && drawRoomZoneMode && drawShapeType === "polygon") {
        if (viewportRef.current?.finishPolygonDraft?.()) {
          e.preventDefault()
          return
        }
      }

      // Ctrl+Z or Cmd+Z -> If currently placing Polygon points, pop the last point first; otherwise Transactional Undo
      if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === "z") {
        e.preventDefault()
        if (
          drawRoomZoneMode &&
          drawShapeType === "polygon" &&
          viewportRef.current?.undoLastPolygonVertex?.()
        ) {
          return
        }
        handleUndo()
        return
      }

      // Ctrl+Y or Ctrl+Shift+Z -> Redo
      if (
        ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "y") ||
        ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "z")
      ) {
        e.preventDefault()
        handleRedo()
        return
      }

      // Backspace while drawing Polygon -> remove last vertex
      if (
        e.key === "Backspace" &&
        drawRoomZoneMode &&
        drawShapeType === "polygon" &&
        viewportRef.current?.undoLastPolygonVertex?.()
      ) {
        e.preventDefault()
        return
      }

      // Delete or Backspace -> Delete selected 3D Room Zone
      if ((e.key === "Delete" || e.key === "Backspace") && activeAdminRoomId) {
        e.preventDefault()
        handleDeleteRoomZone(activeAdminRoomId)
      }
    }

    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [
    isAdminRoute,
    adminAuthenticated,
    drawRoomZoneMode,
    drawShapeType,
    polygonDraftCount,
    activeAdminRoomId,
    activeAdminDeviceId,
    handleQuickRotateActiveDevice,
    handleUnplaceDevice,
    handleUndo,
    handleRedo,
    handleDeleteRoomZone,
  ])

  // Handle 3D raycast click to place EITHER a Room OR a Device
  const handleSurfacePick = async (hitInfo) => {
    const targetFloorIdx =
      hitInfo.floorIdx !== undefined ? hitInfo.floorIdx : placementFloorIdx

    // CASE A: Placing or Moving a Room on the 3D Building
    if (placingRoom) {
      const fl = FLOORS.find((f) => f.index === Number(targetFloorIdx)) || FLOORS[0]
      try {
        const endpoint = placingRoom.id
          ? `/api/admin/rooms/${encodeURIComponent(placingRoom.id)}`
          : "/api/admin/rooms"
        const method = placingRoom.id ? "PUT" : "POST"
        const res = await fetch(endpoint, {
          method,
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${adminToken}`,
          },
          body: JSON.stringify({
            id: placingRoom.id || undefined,
            roomNumber: placingRoom.roomNumber,
            name: placingRoom.name || `Room ${placingRoom.roomNumber}`,
            roomType: placingRoom.roomType || "Office",
            floorIdx: Number(targetFloorIdx),
            color: placingRoom.color || "#38bdf8",
            vlan: placingRoom.vlan || "",
            description: placingRoom.description || "",
            zoneSize: {
              width: Math.max(2, Number(placingRoom.width) || 12),
              depth: Math.max(2, Number(placingRoom.depth) || 10),
            },
            position: {
              x: hitInfo.x,
              y: Number((fl.elevation + 1.6).toFixed(2)),
              z: hitInfo.z,
            },
          }),
        })
        const data = await res.json()
        if (res.ok && data.room) {
          toast({
            title: `ปักหมุดห้อง [${data.room.roomNumber}] บนอาคาร 3D สำเร็จ!`,
            description: `${data.room.name} → ชั้น ${fl.shortLabel} พิกัด (${hitInfo.x}, ${hitInfo.z})`,
            variant: "success",
          })
          setPlacingRoom(null)
          fetchState()
        } else {
          throw new Error(data.error || "ไม่สามารถบันทึกตำแหน่งห้องได้")
        }
      } catch (err) {
        toast({
          title: "บันทึกตำแหน่งห้อง 3D ไม่สำเร็จ",
          description: err.message,
          variant: "destructive",
        })
      }
      return
    }

    // CASE B: Placing or Moving a Device on the 3D Building (with Smart Auto-Snap to Room Zone & Mandatory Boundary Clamp)
    if (!placingDevice) return

    let targetRoom = null

    // 1. Raycast direct hit on room zone
    if (hitInfo.roomId) {
      targetRoom = rooms.find((r) => r.id === hitInfo.roomId) || null
    }

    // 2. Point-in-polygon containment on clicked floor
    if (!targetRoom && autoSnapRoomEnabled) {
      targetRoom = findMatchingRoomForPoint(
        rooms,
        Number(targetFloorIdx),
        hitInfo.x,
        hitInfo.z,
        14
      )
    }

    // 3. Search across all floors if not found
    if (!targetRoom && rooms.length > 0) {
      for (const fl of [0, 1, 2, 3]) {
        const found = findMatchingRoomForPoint(rooms, fl, hitInfo.x, hitInfo.z, 14)
        if (found) {
          targetRoom = found
          break
        }
      }
    }

    // 4. Fallback to room selected in banner dropdown or active room
    if (!targetRoom) {
      if (placementRoom) {
        targetRoom =
          rooms.find((r) => r.roomNumber === placementRoom && Number(r.floorIdx) === Number(targetFloorIdx)) ||
          rooms.find((r) => r.roomNumber === placementRoom) ||
          rooms.find((r) => r.id === placementRoom) ||
          null
      }
      if (!targetRoom && activeAdminRoomId) {
        targetRoom = rooms.find((r) => r.id === activeAdminRoomId) || null
      }
      if (!targetRoom && rooms.length > 0) {
        targetRoom = rooms.find((r) => Number(r.floorIdx) === Number(targetFloorIdx)) || rooms[0]
      }
    }

    const resolvedFloorIdx = targetRoom ? Number(targetRoom.floorIdx ?? 0) : Number(targetFloorIdx)
    const finalRoomId = targetRoom ? targetRoom.id : ""
    const finalRoomNumber = targetRoom ? targetRoom.roomNumber : (placementRoom || "101")

    // MANDATORY ROOM BOUNDARY CLAMPING:
    // If a room is targeted/selected, ALWAYS force coordinates to be strictly inside this room's 3D boundary
    let finalX = hitInfo.x
    let finalZ = hitInfo.z
    if (targetRoom) {
      const clamped = clampPointToRoomBounds(targetRoom, hitInfo.x, hitInfo.z, 0.4)
      finalX = clamped.x
      finalZ = clamped.z
      setPlacementRoom(targetRoom.roomNumber)
    }

    const fl = FLOORS.find((f) => f.index === Number(resolvedFloorIdx)) || FLOORS[0]
    const finalY = Number((fl.elevation + (placingModelType === "server_rack" ? 0.05 : 1.2)).toFixed(2))

    try {
      const isNewDev = !placingDevice.id
      const url = isNewDev ? "/api/admin/devices" : `/api/admin/devices/${encodeURIComponent(placingDevice.id)}`
      const method = isNewDev ? "POST" : "PUT"

      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify({
          ...placingDevice,
          isPlaced: true,
          floorIdx: Number(resolvedFloorIdx),
          roomId: finalRoomId,
          roomNumber: finalRoomNumber,
          autoSnapRoom: autoSnapRoomEnabled,
          modelType: placingModelType || placingDevice.modelType || "pin",
          rotationY: Number(placingRotationY ?? placingDevice.rotationY ?? 0),
          position: {
            x: finalX,
            y: finalY,
            z: finalZ,
          },
        }),
      })
      const data = await res.json()
      if (res.ok && data.device) {
        const flLabel = fl.label || `Floor ${resolvedFloorIdx}`
        toast({
          title: targetRoom
            ? `จัดวางในกรอบห้อง [${finalRoomNumber}] (${targetRoom.name}) สำเร็จ!`
            : "จัดวางอุปกรณ์ลงอาคาร 3D สำเร็จ!",
          description: `${placingDevice.name || placingDevice.ip} → ${flLabel} ห้อง ${finalRoomNumber}`,
          variant: "success",
        })
        setPlacingDevice(null)
        fetchState()
      } else {
        throw new Error(data.error || "ไม่สามารถบันทึกตำแหน่งได้")
      }
    } catch (err) {
      toast({
        title: "เกิดข้อผิดพลาดในการบันทึกตำแหน่ง",
        description: err.message,
        variant: "destructive",
      })
    }
  }

  // Trigger Network Subnet Scan
  const handleTriggerScan = async () => {
    setScanStatus({ running: true, progress: 5, cidr: subnetInput })
    toast({
      title: "เริ่มสแกนเครือข่าย...",
      description: `กำลังค้นหาอุปกรณ์ในวง ${subnetInput} (อุปกรณ์ใหม่จะเข้าคิวรอจัดวาง)`,
    })
    try {
      const res = await fetch("/api/admin/scan/subnet", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify({ cidr: subnetInput }),
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.error || "Scan failed")
      }
    } catch (err) {
      setScanStatus({ running: false, progress: 0, cidr: "" })
      toast({
        title: "สแกนเครือข่ายล้มเหลว",
        description: err.message,
        variant: "destructive",
      })
    }
  }

  // Scan single target IP immediately
  const handleScanSingleIp = async (e) => {
    e?.preventDefault()
    if (!singleIpInput.trim()) return
    setScanningSingleIp(true)
    toast({
      title: `กำลังสแกน IP: ${singleIpInput.trim()}`,
      description: "กำลังตรวจสอบ Ping, ARP, OUI และพอร์ตเปิด...",
    })
    try {
      const res = await fetch("/api/admin/scan/ip", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify({ ip: singleIpInput.trim(), mode: "fast" }),
      })
      const data = await res.json()
      if (res.ok && data.device) {
        toast({
          title: "พบอุปกรณ์และนำเข้าคิวรอวางสำเร็จ!",
          description: `${data.device.name} (${data.device.ip})`,
          variant: "success",
        })
        setSingleIpInput("")
        await fetchState()
        setSelectedDeviceId(data.device.id)
        setModalOpen(true)
      } else {
        throw new Error(data.error || "ไม่พบการตอบสนองจาก IP นี้")
      }
    } catch (err) {
      toast({
        title: "สแกน IP เดี่ยวไม่สำเร็จ",
        description: err.message,
        variant: "destructive",
      })
    } finally {
      setScanningSingleIp(false)
    }
  }

  // Add manual device (starts unplaced in queue)
  const handleAddDevice = async (e) => {
    e.preventDefault()
    if (!newDevForm.name || !newDevForm.ip) return
    try {
      const res = await fetch("/api/admin/devices", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify({
          ...newDevForm,
          isPlaced: false,
          status: "Online",
        }),
      })
      const data = await res.json()
      if (res.ok && data.device) {
        toast({
          title: "เพิ่มอุปกรณ์เข้าคิวรอจัดวางแล้ว",
          description: `${newDevForm.name} (${newDevForm.ip})`,
          variant: "success",
        })
        setNewDevForm({
          name: "",
          ip: "",
          category: "Switch",
          networkType: "LAN",
          vendor: "Cisco",
          model: "Catalyst",
        })
        fetchState()
      }
    } catch (err) {
      toast({
        title: "เพิ่มอุปกรณ์ไม่สำเร็จ",
        description: err.message,
        variant: "destructive",
      })
    }
  }

  // Add room label & 3D floor zone
  const handleAddRoom = async (e) => {
    e?.preventDefault()
    if (!newRoomForm.roomNumber) return
    const fl = FLOORS.find((f) => f.index === Number(newRoomForm.floorIdx)) || FLOORS[0]
    const rMeta = ROOM_TYPES.find((r) => r.id === newRoomForm.roomType) || ROOM_TYPES[1]
    try {
      const res = await fetch("/api/admin/rooms", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify({
          roomNumber: newRoomForm.roomNumber.trim(),
          name: newRoomForm.name.trim() || `Room ${newRoomForm.roomNumber.trim()}`,
          roomType: newRoomForm.roomType || "Office",
          floorIdx: Number(newRoomForm.floorIdx),
          color: newRoomForm.color || rMeta.color || "#38bdf8",
          vlan: (newRoomForm.vlan || "").trim(),
          zoneSize: {
            width: Math.max(2, Number(newRoomForm.width) || 12),
            depth: Math.max(2, Number(newRoomForm.depth) || 10),
          },
          position: { x: 0, y: fl.elevation + 1.6, z: 0 },
        }),
      })
      if (res.ok) {
        toast({
          title: "เพิ่มป้ายหมายเลขห้องสำเร็จ",
          description: `ห้อง [${newRoomForm.roomNumber}] (${newRoomForm.name || "Room"}) ชั้น ${fl.shortLabel}`,
          variant: "success",
        })
        fetchState()
      }
    } catch (err) {
      toast({
        title: "เพิ่มห้องไม่สำเร็จ",
        description: err.message,
        variant: "destructive",
      })
    }
  }

  // Batch generate rooms by numbering pattern on a floor
  const handleBatchGenerateRooms = async (e) => {
    e?.preventDefault()
    try {
      const res = await fetch("/api/admin/rooms/batch", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify(batchRoomForm),
      })
      const data = await res.json()
      if (res.ok && data.rooms) {
        const fl =
          FLOORS.find((f) => f.index === Number(batchRoomForm.floorIdx)) || FLOORS[0]
        toast({
          title: `สร้างชุดเลขห้องอัตโนมัติ ${data.count} ห้องสำเร็จ!`,
          description: `ชั้น ${fl.shortLabel}: ${data.rooms.map((r) => r.roomNumber).join(", ")} (คลิกที่ห้องเพื่อย้ายจุด 3D หรือแก้ไขชื่อได้เลย)`,
          variant: "success",
        })
        updateView({ selectedFloor: String(batchRoomForm.floorIdx), showRooms: true })
        fetchState()
      } else {
        throw new Error(data.error || "Batch generation failed")
      }
    } catch (err) {
      toast({
        title: "สร้างชุดห้องอัตโนมัติไม่สำเร็จ",
        description: err.message,
        variant: "destructive",
      })
    }
  }

  const activeFloorLabel = useMemo(() => {
    if (viewState.selectedFloor === "all") return "ทุกชั้น (All Floors)"
    const fl = FLOORS.find((f) => f.index === Number(viewState.selectedFloor))
    return fl ? fl.label : `Floor ${viewState.selectedFloor}`
  }, [viewState.selectedFloor])

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-background text-foreground select-none">
      {/* 1. THREE.JS 3D BUILDING VIEWPORT */}
      <div className="w-full h-full">
        <ThreeViewport
          ref={viewportRef}
          theme={theme}
          viewState={viewState}
          rooms={rooms}
          placedDevices={placedDevices}
          placementMode={Boolean(placingDevice || placingRoom)}
          drawRoomZoneMode={Boolean(isAdminRoute && adminAuthenticated && drawRoomZoneMode)}
          drawShapeType={drawShapeType}
          drawFloorIdx={
            viewState.selectedFloor === "all"
              ? Number(newRoomForm.floorIdx ?? placementFloorIdx ?? 0)
              : Number(viewState.selectedFloor)
          }
          snapToGrid={snapToGrid}
          magneticWallSnap={magneticWallSnap}
          activeRoomId={isAdminRoute && adminAuthenticated ? activeAdminRoomId : null}
          roomTransformMode={
            isAdminRoute && adminAuthenticated && activeAdminRoomId
              ? roomTransformMode
              : null
          }
          activeAdminDeviceId={isAdminRoute && adminAuthenticated ? activeAdminDeviceId : null}
          deviceTransformMode={deviceTransformMode}
          onDeviceTransformCommit={handleDeviceTransformCommit}
          onSurfacePick={handleSurfacePick}
          onRoomZoneDrawn={handleRoomZoneDrawn}
          onPolygonDraftChange={setPolygonDraftCount}
          onRoomTransformCommit={handleRoomTransformCommit}
          onAdminSelectRoom={
            isAdminRoute && adminAuthenticated
              ? (roomId) => {
                  setActiveAdminRoomId(roomId)
                  const rm = rooms.find((r) => r.id === roomId)
                  const hasPoly = Array.isArray(rm?.polygon) && rm.polygon.length >= 3
                  setRoomTransformMode((prev) =>
                    prev || (hasPoly ? "vertices" : "scale")
                  )
                }
              : null
          }
          onSelectDevice={(devId) => {
            const target = devices.find((d) => d.id === devId)
            if (target?.modelType === "server_rack") {
              setSelectedRackId(devId)
              openRackHierarchy(devId)
              if (isAdminRoute && adminAuthenticated) {
                setActiveAdminDeviceId(devId)
                if (target.roomId) setActiveAdminRoomId(target.roomId)
              }
              return
            }
            if (target?.parentRackId) {
              setSelectedRackId(target.parentRackId)
              openRackHierarchy(target.parentRackId)
              return
            }
            if (isAdminRoute && adminAuthenticated) {
              setActiveAdminDeviceId(devId)
              if (target?.roomId) {
                setActiveAdminRoomId(target.roomId)
              }
            } else {
              setSelectedDeviceId(devId)
              setModalOpen(true)
            }
          }}
          onSelectRoom={(roomId) => {
            setSelectedRoomId(roomId)
            setRoomModalOpen(true)
          }}
          onModelLoaded={(info) => setModelStats({ loaded: true, ...info })}
        />
      </div>

      {/* Floating Material 3 Action Control (Quick Camera Reset & Orbit FAB) */}
      <div className="fixed bottom-6 right-6 z-20 pointer-events-auto flex flex-col items-end gap-2 animate-in fade-in duration-200">
        <M3Fab
          variant="surface"
          size="medium"
          label="รีเซ็ตมุมกล้อง 3D"
          icon={<RotateCcw className="h-4 w-4 text-primary" />}
          onClick={() => {
            updateView({ selectedFloor: "all" })
            viewportRef.current?.resetCamera()
          }}
          title="รีเซ็ตมุมกล้อง 3D (Reset Orbit Camera)"
        />
      </div>

      {/* 2. TOP FLOATING TELEMETRY BAR (Material 3 Elevated App Bar) */}
      <header className="fixed top-3 left-3 right-3 z-30 flex items-center justify-between gap-3 pointer-events-none">
        {/* Left: Hamburger Trigger + Brand Title */}
        <div className="flex items-center gap-2.5 rounded-full border border-border/80 bg-card/90 backdrop-blur-xl px-3.5 py-1.5 shadow-xl pointer-events-auto">
          <M3IconButton
            variant="standard"
            onClick={() => setMenuOpen(true)}
            ariaLabel="เปิดเมนูหลัก Navigation Drawer"
            className="text-primary"
          >
            <Menu className="h-4 w-4 text-primary" />
          </M3IconButton>

          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <Building2 className="h-4 w-4 text-primary" />
              <span className="text-xs sm:text-sm font-bold tracking-tight text-foreground">
                LUDUS DIGITAL TWIN
              </span>
              {isAdminRoute ? (
                <Badge variant="warning" className="text-[10px] rounded-full px-2 py-0">
                  ADMIN
                </Badge>
              ) : (
                <Badge variant="info" className="text-[10px] rounded-full px-2 py-0">
                  3D VIEWER
                </Badge>
              )}
            </div>
            <span className="text-[11px] text-muted-foreground hidden sm:inline">
              {activeFloorLabel} · {rooms.length} ห้อง ·{" "}
              {modelStats.loaded
                ? `${modelStats.meshCount} 3D Meshes`
                : "กำลังโหลดโมเดลอาคาร 3D..."}
            </span>
          </div>
        </div>

        {/* Right: Live Telemetry Counters (Placed Only) + Theme Toggle */}
        <div className="flex items-center gap-2 rounded-2xl border border-border bg-card/85 backdrop-blur-xl px-3 py-1.5 shadow-xl pointer-events-auto">
          <div className="hidden md:flex items-center gap-1.5 pr-2 border-r border-border">
            <M3ChipSet>
              <M3AssistChip
                label={`Placed: ${stats.total}`}
                icon={<MapPin className="h-3.5 w-3.5 text-primary" />}
              />
              <M3AssistChip
                label={`Online: ${stats.online}`}
                icon={<CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />}
              />
              <M3AssistChip
                label={`Warn: ${stats.warning}`}
                icon={<AlertTriangle className="h-3.5 w-3.5 text-amber-400" />}
              />
              <M3AssistChip
                label={`Offline: ${stats.offline}`}
                icon={<XCircle className="h-3.5 w-3.5 text-rose-400" />}
              />
            </M3ChipSet>
          </div>

          {(activeInterfaces[0]?.cidr || networks[0]?.cidr) && (
            <Badge variant="secondary" className="hidden lg:inline-flex font-mono text-[11px]">
              <Wifi className="h-3 w-3 mr-1 text-emerald-400" />
              {activeInterfaces[0]?.cidr || networks[0]?.cidr}
            </Badge>
          )}

          <M3IconButton
            variant="standard"
            ariaLabel="สลับโหมดมืด/สว่าง (Dark/Light Theme)"
            title="สลับโหมดมืด/สว่าง"
            onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
          >
            {theme === "dark" ? (
              <Sun className="h-4 w-4 text-amber-400" />
            ) : (
              <Moon className="h-4 w-4 text-muted-foreground" />
            )}
          </M3IconButton>
        </div>
      </header>

      {/* 3A. ACTIVE 3D DEVICE PLACEMENT INTERACTION BANNER (Admin Only) */}
      {isAdminRoute && placingDevice && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 z-30 w-[94%] max-w-3xl rounded-xl border-2 border-primary bg-card/95 backdrop-blur-xl p-3.5 shadow-2xl">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className="h-9 w-9 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
                <Crosshair className="h-5 w-5 animate-pulse" />
              </div>
              <div>
                <div className="text-xs font-bold uppercase tracking-wider text-primary">
                  โหมดคลิกจัดวางอุปกรณ์ลงบนโมเดล 3D (Auto-Snap Room Zone)
                </div>
                <div className="text-sm font-semibold">
                  กำลังวาง: <span className="text-primary">{placingDevice.name}</span>{" "}
                  <span className="font-mono text-xs text-muted-foreground">
                    ({placingDevice.ip || (placingDevice.modelType === "server_rack" ? "Rack เปล่า" : "-")})
                  </span>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <div className="flex items-center gap-1.5">
                <Label className="text-xs">ชั้น:</Label>
                <SelectNative
                  value={placementFloorIdx}
                  onChange={(e) => {
                    const idx = Number(e.target.value)
                    setPlacementFloorIdx(idx)
                    updateView({ selectedFloor: String(idx) })
                  }}
                  className="h-8 w-32 text-xs"
                >
                  {FLOORS.map((f) => (
                    <option key={f.index} value={f.index}>
                      {f.shortLabel} — {f.label}
                    </option>
                  ))}
                </SelectNative>
              </div>

              {rooms.length > 0 && (
                <div className="flex items-center gap-1.5">
                  <Label className="text-xs font-bold text-primary">บังคับในห้อง:</Label>
                  <SelectNative
                    value={placementRoom}
                    onChange={(e) => {
                      const selectedNum = e.target.value
                      setPlacementRoom(selectedNum)
                      const rm = rooms.find((r) => r.roomNumber === selectedNum)
                      if (rm && rm.floorIdx !== undefined) {
                        const fIdx = Number(rm.floorIdx)
                        setPlacementFloorIdx(fIdx)
                        updateView({ selectedFloor: String(fIdx) })
                      }
                    }}
                    className="h-8 w-44 text-xs font-mono font-semibold border-primary/50"
                  >
                    {rooms.map((rm) => (
                      <option key={rm.id} value={rm.roomNumber}>
                        [{FLOORS.find((f) => f.index === Number(rm.floorIdx))?.shortLabel || 'F'}] [{rm.roomNumber}] {rm.name}
                      </option>
                    ))}
                  </SelectNative>
                </div>
              )}

              {/* 3D Model Selector */}
              <div className="flex items-center gap-1.5">
                <Label className="text-xs">โมเดล:</Label>
                <SelectNative
                  value={placingModelType}
                  onChange={(e) => setPlacingModelType(e.target.value)}
                  className="h-8 text-xs font-semibold"
                >
                  <option value="pin">📍 หมุด 3D เรืองแสง</option>
                  <option value="server_rack">🖥️ Server Rack (3D)</option>
                </SelectNative>
              </div>

              {/* Rotation Y Control (Shown for Server Rack or 3D Models) */}
              {placingModelType === "server_rack" && (
                <div className="flex items-center gap-1 bg-secondary/50 px-2 py-1 rounded-lg border border-primary/30">
                  <Label className="text-[11px] text-primary font-bold">หมุนตู้:</Label>
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    className="h-6 px-1.5 text-xs font-mono cursor-pointer"
                    onClick={() => setPlacingRotationY((prev) => (prev - 90 + 360) % 360)}
                    title="หมุนทวนเข็ม 90 องศา"
                  >
                    ↺ -90°
                  </Button>
                  <Badge variant="info" className="h-5 px-1.5 text-[11px] font-mono font-bold">
                    {placingRotationY}°
                  </Badge>
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    className="h-6 px-1.5 text-xs font-mono cursor-pointer"
                    onClick={() => setPlacingRotationY((prev) => (prev + 90) % 360)}
                    title="หมุนตามเข็ม 90 องศา"
                  >
                    ↻ +90°
                  </Button>
                </div>
              )}

              {/* Lock within Room 3D Bounds Toggle */}
              <div className="flex items-center gap-1.5 px-2 py-1 rounded border border-border bg-secondary/30">
                <Switch
                  id="clamp-room-bounds"
                  checked={clampToRoomBoundsEnabled}
                  onCheckedChange={setClampToRoomBoundsEnabled}
                />
                <Label htmlFor="clamp-room-bounds" className="text-[11px] cursor-pointer">
                  ล็อกในกรอบ 3D
                </Label>
              </div>

              <div className="flex items-center gap-1.5 px-2 py-1 rounded border border-border bg-secondary/30">
                <Switch
                  id="auto-snap-room"
                  checked={autoSnapRoomEnabled}
                  onCheckedChange={setAutoSnapRoomEnabled}
                />
                <Label htmlFor="auto-snap-room" className="text-[11px] cursor-pointer">
                  Auto-Snap ห้อง
                </Label>
              </div>

              <Button
                size="sm"
                variant="destructive"
                onClick={() => setPlacingDevice(null)}
              >
                ยกเลิก
              </Button>
            </div>
          </div>
          <p className="text-[11px] text-muted-foreground mt-2">
            คำแนะนำ: คลิกซ้ายลงบนพื้นห้องในโมเดล 3D ได้เลย หากเปิด{" "}
            <strong>Auto-Snap ห้อง</strong> ระบบจะตรวจจับกรอบพื้นที่ห้องและผูกหมายเลขห้องให้อัตโนมัติทันที
          </p>
        </div>
      )}

      {/* 3B. ACTIVE 3D ROOM PLACEMENT / RELOCATION BANNER (Admin Only) */}
      {isAdminRoute && placingRoom && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 z-30 w-[94%] max-w-3xl rounded-xl border-2 border-emerald-400 bg-card/95 backdrop-blur-xl p-3.5 shadow-2xl">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className="h-9 w-9 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                <MapPin className="h-5 w-5 animate-bounce" />
              </div>
              <div>
                <div className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                  โหมดคลิกกำหนดตำแหน่งห้อง & กรอบโซน 3D บนอาคาร
                </div>
                <div className="text-sm font-semibold">
                  ห้อง: <span className="text-emerald-400 font-mono">[{placingRoom.roomNumber}]</span>{" "}
                  <span>{placingRoom.name}</span>{" "}
                  <span className="text-xs text-muted-foreground font-mono">
                    (โซน {placingRoom.width}m × {placingRoom.depth}m)
                  </span>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <div className="flex items-center gap-1.5">
                <Label className="text-xs">ชั้น:</Label>
                <SelectNative
                  value={placingRoom.floorIdx}
                  onChange={(e) => {
                    const idx = Number(e.target.value)
                    setPlacingRoom({ ...placingRoom, floorIdx: idx })
                    setPlacementFloorIdx(idx)
                    updateView({ selectedFloor: String(idx), showRooms: true })
                  }}
                  className="h-8 w-32 text-xs"
                >
                  {FLOORS.map((f) => (
                    <option key={f.index} value={f.index}>
                      {f.shortLabel} — {f.label}
                    </option>
                  ))}
                </SelectNative>
              </div>

              <div className="flex items-center gap-1.5">
                <Label className="text-xs">เลขห้อง:</Label>
                <Input
                  value={placingRoom.roomNumber}
                  onChange={(e) =>
                    setPlacingRoom({ ...placingRoom, roomNumber: e.target.value })
                  }
                  className="h-8 w-20 text-xs font-mono font-bold"
                />
              </div>

              <div className="flex items-center gap-1.5">
                <Label className="text-xs">ชื่อห้อง:</Label>
                <Input
                  value={placingRoom.name}
                  onChange={(e) =>
                    setPlacingRoom({ ...placingRoom, name: e.target.value })
                  }
                  className="h-8 w-36 text-xs"
                />
              </div>

              <Button
                size="sm"
                variant="destructive"
                onClick={() => setPlacingRoom(null)}
              >
                ยกเลิก
              </Button>
            </div>
          </div>
          <p className="text-[11px] text-muted-foreground mt-2">
            คำแนะนำ: <strong>คลิกซ้ายลงบนพื้นอาคาร 3D</strong> ในบริเวณกึ่งกลางห้องที่ต้องการกำหนดเลขห้อง{" "}
            <span className="font-mono text-emerald-400">[{placingRoom.roomNumber}]</span>
          </p>
        </div>
      )}

      {/* 3C. ACTIVE 3D DEVICE / SERVER RACK CAD GIZMO & MANIPULATION BANNER (Admin Only) */}
      {isAdminRoute &&
        adminAuthenticated &&
        activeAdminDevice &&
        !placingDevice &&
        !placingRoom && (
          <div className="fixed top-20 left-1/2 -translate-x-1/2 z-30 w-[96%] max-w-4xl rounded-xl border-2 border-primary/80 bg-card/95 backdrop-blur-xl p-3 shadow-2xl pointer-events-auto animate-in fade-in slide-in-from-top-2 duration-150">
            <div className="flex flex-wrap items-center justify-between gap-2.5">
              <div className="flex items-center gap-2.5">
                <div className="h-9 w-9 rounded-lg bg-primary/20 flex items-center justify-center text-primary font-bold text-base shrink-0">
                  {activeAdminDevice.modelType === "server_rack" ? "🖥️" : "📍"}
                </div>
                <div>
                  <div className="text-xs font-bold flex items-center gap-1.5">
                    <span className="text-primary font-mono font-bold">
                      [{activeAdminDevice.roomNumber || "No Room"}]
                    </span>
                    <span className="truncate max-w-[200px]">
                      {activeAdminDevice.name || activeAdminDevice.ip}
                    </span>
                    <Badge variant="outline" className="text-[10px] font-mono shrink-0">
                      {activeAdminDevice.modelType === "server_rack"
                        ? "Server Rack 3D"
                        : "Glowing Pin"}
                    </Badge>
                  </div>
                  <div className="text-[11px] text-muted-foreground font-mono">
                    พิกัด X:{activeAdminDevice.position?.x} Z:{activeAdminDevice.position?.z} · ทิศ {activeAdminDevice.rotationY || 0}°
                  </div>
                </div>
              </div>

              {/* Manipulation Controls */}
              <div className="flex flex-wrap items-center gap-1.5">
                {/* Mode toggle */}
                <div className="flex items-center rounded-lg border border-border bg-secondary/30 p-0.5">
                  <Button
                    type="button"
                    size="sm"
                    variant={deviceTransformMode === "translate" ? "default" : "ghost"}
                    className="h-7 px-2 text-xs gap-1"
                    onClick={() => setDeviceTransformMode("translate")}
                    title="โหมดเลื่อนตำแหน่งบนพื้นห้อง (ปุ่มลัด T หรือ M)"
                  >
                    <Move className="h-3 w-3" />
                    <span>เลื่อน (T)</span>
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant={deviceTransformMode === "rotate" ? "default" : "ghost"}
                    className="h-7 px-2 text-xs gap-1"
                    onClick={() => setDeviceTransformMode("rotate")}
                    title="โหมดหมุนตู้ด้วย Gizmo (ปุ่มลัด R)"
                  >
                    <Compass className="h-3 w-3" />
                    <span>หมุน (R)</span>
                  </Button>
                </div>

                {/* Quick 90 deg rotation */}
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  className="h-7 px-2 text-xs font-mono cursor-pointer"
                  onClick={() => handleQuickRotateActiveDevice(-90)}
                  title="หมุนทวนเข็ม 90°"
                >
                  ↺ -90°
                </Button>
                <Badge variant="info" className="h-7 px-2 text-xs font-mono font-bold">
                  {activeAdminDevice.rotationY || 0}°
                </Badge>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  className="h-7 px-2 text-xs font-mono cursor-pointer"
                  onClick={() => handleQuickRotateActiveDevice(90)}
                  title="หมุนตามเข็ม 90°"
                >
                  ↻ +90°
                </Button>

                <Separator orientation="vertical" className="h-6 mx-1 hidden sm:block" />

                {/* Open Rackula 19-Inch Elevation Designer (When active device is a 3D Server Rack) */}
                {activeAdminDevice.modelType === "server_rack" && (
                  <Button
                    type="button"
                    size="sm"
                    className="h-7 px-3 text-xs cursor-pointer font-bold bg-primary hover:bg-primary text-white"
                    onClick={() => {
                      setSelectedRackId(activeAdminDevice.id)
                      setRackModalOpen(true)
                    }}
                    title="เปิดจัดผังตู้แร็ค 19 นิ้ว (Rackula Elevation Designer)"
                  >
                    🗄️ จัดผังตู้แร็ค (Rackula)
                  </Button>
                )}

                {/* Open Specs Modal */}
                <Button
                  type="button"
                  size="sm"
                  variant="secondary"
                  className="h-7 px-2.5 text-xs cursor-pointer"
                  onClick={() => {
                    setSelectedDeviceId(activeAdminDevice.id)
                    setModalOpen(true)
                  }}
                  title="เปิดดูการ์ดข้อมูลและ Login อุปกรณ์"
                >
                  <Eye className="h-3 w-3 mr-1" />
                  ดูข้อมูล
                </Button>

                {/* เอาโมเดลออกจากพื้นที่ (Unplace) */}
                <Button
                  type="button"
                  size="sm"
                  variant="destructive"
                  className="h-7 px-3 text-xs cursor-pointer font-medium"
                  onClick={() => {
                    handleUnplaceDevice(activeAdminDevice.id)
                    setActiveAdminDeviceId(null)
                  }}
                  title="เอาโมเดลออกจากพื้นที่ 3D ส่งกลับเข้าคิวรอจัดวาง (ปลอดภัย ไม่ลบข้อมูลอุปกรณ์หรือ Network/IP)"
                >
                  <Undo2 className="h-3.5 w-3.5 mr-1.5" />
                  เอาโมเดลออกจากพื้นที่
                </Button>

                {/* Close / Deselect */}
                <Button
                  type="button"
                  size="sm"
                  variant="ghost"
                  className="h-7 px-2 text-xs cursor-pointer"
                  onClick={() => setActiveAdminDeviceId(null)}
                  title="เสร็จสิ้น / ปิด (Esc)"
                >
                  เสร็จสิ้น (Esc)
                </Button>
              </div>
            </div>
          </div>
        )}

      {/* 3C. ACTIVE 3D POLYGON (POINT-BY-POINT) / RECTANGLE ZONE DRAWING & CAD GIZMO BANNER (Admin Only) */}
      {isAdminRoute &&
        adminAuthenticated &&
        !placingDevice &&
        !placingRoom &&
        (drawRoomZoneMode || activeAdminRoom) && (
          <div className="fixed top-20 left-1/2 -translate-x-1/2 z-30 w-[96%] max-w-5xl rounded-xl border-2 border-emerald-400 bg-card/95 backdrop-blur-xl p-3 shadow-2xl pointer-events-auto">
            <div className="flex flex-wrap items-center justify-between gap-2.5">
              {/* Left Status & Active Room / Draw Mode Info */}
              <div className="flex items-center gap-2.5">
                <div className="h-9 w-9 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
                  <SquareDashed className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
                    <span>
                      {drawRoomZoneMode
                        ? drawShapeType === "polygon"
                          ? `โหมดคลิกปักหมุดวาดกรอบห้องทีละมุม (Polygon Vertices: ${polygonDraftCount} จุด)`
                          : "โหมดคลิกลากวาดกรอบสี่เหลี่ยมโซนห้อง 3D (Rectangle Marquee)"
                        : `กำลังแก้ไขกรอบโซนห้อง 3D: [${activeAdminRoom?.roomNumber}]`}
                    </span>
                    <Badge variant="outline" className="text-[10px] font-mono">
                      Ctrl+Z Undo ({undoStack.length})
                    </Badge>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {drawRoomZoneMode ? (
                      drawShapeType === "polygon" ? (
                        <>
                          คลิกซ้ายปักหมุดตามมุมห้อง{" "}
                          <strong className="text-emerald-400 font-mono">
                            [{newRoomForm.roomNumber || "101"}]
                          </strong>{" "}
                          ทีละจุด (กด <kbd className="px-1 rounded bg-secondary font-mono">Shift</kbd> ล็อกมุม 45°/90°) — คลิกซ้ำจุดแรก, Double-Click หรือกด{" "}
                          <kbd className="px-1 rounded bg-secondary font-mono">Enter</kbd> เพื่อปิดกรอบห้อง
                        </>
                      ) : (
                        <>
                          คลิกซ้ายค้างแล้วลากบนพื้นอาคารเพื่อวาดกรอบสี่เหลี่ยมห้อง{" "}
                          <strong className="text-emerald-400 font-mono">
                            [{newRoomForm.roomNumber || "101"}]
                          </strong>
                        </>
                      )
                    ) : (
                      <>
                        {Array.isArray(activeAdminRoom?.polygon) &&
                        activeAdminRoom.polygon.length >= 3 ? (
                          <>
                            รูปทรง Polygon{" "}
                            <strong className="text-foreground font-mono">
                              {activeAdminRoom.polygon.length} มุม · พื้นที่{" "}
                              {computePolygonArea(activeAdminRoom.polygon).toFixed(1)} ตร.ม.
                            </strong>{" "}
                            — คลิกเลือกหมุดลูกบอลที่มุมห้องเพื่อดัดมุม หรือสลับโหมดย้าย/หมุนทั้งห้อง
                          </>
                        ) : (
                          <>
                            ขนาดปัจจุบัน:{" "}
                            <strong className="text-foreground font-mono">
                              {activeAdminRoom?.zoneSize?.width ?? 12}m ×{" "}
                              {activeAdminRoom?.zoneSize?.depth ?? 10}m
                            </strong>{" "}
                            — ลากแกนลูกศร 3D เพื่อดึงขนาดหรือย้ายตำแหน่ง
                          </>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Right Quick Controls */}
              <div className="flex flex-wrap items-center gap-1.5">
                {drawRoomZoneMode && (
                  <>
                    {/* Toggle Polygon (Point-by-Point) vs Rectangle Marquee */}
                    <div className="flex items-center rounded-lg border border-border bg-secondary/30 p-0.5 gap-0.5">
                      <Button
                        size="sm"
                        variant={drawShapeType === "polygon" ? "default" : "ghost"}
                        className="h-7 px-2 text-xs"
                        onClick={() => setDrawShapeType("polygon")}
                        title="ปักหมุดทีละมุมตามแนวกำแพงจริง (รองรับห้องเฉียง/หลายเหลี่ยม)"
                      >
                        📍 ปักหมุดทีละมุม (Polygon)
                      </Button>
                      <Button
                        size="sm"
                        variant={drawShapeType === "rectangle" ? "default" : "ghost"}
                        className="h-7 px-2 text-xs"
                        onClick={() => {
                          viewportRef.current?.cancelPolygonDraft?.()
                          setDrawShapeType("rectangle")
                        }}
                        title="คลิกลากกรอบสี่เหลี่ยมมุมฉากแบบรวดเร็ว"
                      >
                        📐 ลากกรอบสี่เหลี่ยม
                      </Button>
                    </div>

                    {drawShapeType === "polygon" && polygonDraftCount >= 3 && (
                      <Button
                        size="sm"
                        variant="default"
                        className="h-8 px-2.5 text-xs bg-emerald-600 hover:bg-emerald-500 text-white"
                        onClick={() => viewportRef.current?.finishPolygonDraft?.()}
                        title="ปิดกรอบห้องหลายเหลี่ยมและบันทึกทันที (ปุ่มลัด Enter)"
                      >
                        ✅ ปิดกรอบห้อง ({polygonDraftCount} มุม)
                      </Button>
                    )}

                    {drawShapeType === "polygon" && polygonDraftCount > 0 && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="h-8 px-2 text-xs"
                        onClick={() => viewportRef.current?.undoLastPolygonVertex?.()}
                        title="ลบหมุดมุมล่าสุดที่เพิ่งคลิก (Backspace / Ctrl+Z)"
                      >
                        ลบจุดล่าสุด
                      </Button>
                    )}

                    <SelectNative
                      value={
                        viewState.selectedFloor === "all"
                          ? newRoomForm.floorIdx
                          : Number(viewState.selectedFloor)
                      }
                      onChange={(e) => {
                        const idx = Number(e.target.value)
                        setPlacementFloorIdx(idx)
                        setNewRoomForm({ ...newRoomForm, floorIdx: idx })
                        updateView({ selectedFloor: String(idx), showRooms: true })
                      }}
                      className="h-8 w-24 text-xs"
                    >
                      {FLOORS.map((f) => (
                        <option key={f.index} value={f.index}>
                          ชั้น {f.shortLabel}
                        </option>
                      ))}
                    </SelectNative>

                    <Input
                      value={newRoomForm.roomNumber}
                      onChange={(e) =>
                        setNewRoomForm({ ...newRoomForm, roomNumber: e.target.value })
                      }
                      placeholder="เลขห้องถัดไป"
                      className="h-8 w-20 text-xs font-mono font-bold"
                      title="หมายเลขห้องที่จะใช้เมื่อปิดกรอบเสร็จ"
                    />
                  </>
                )}

                {activeAdminRoom && (
                  <div className="flex items-center rounded-lg border border-border bg-secondary/30 p-0.5 gap-0.5">
                    {Array.isArray(activeAdminRoom.polygon) &&
                      activeAdminRoom.polygon.length >= 3 && (
                        <Button
                          size="sm"
                          variant={roomTransformMode === "vertices" ? "default" : "ghost"}
                          className="h-7 px-2 text-xs"
                          onClick={() => setRoomTransformMode("vertices")}
                          title="คลิกเลือกหมุดลูกบอลที่แต่ละมุมห้องแล้วลากดัดมุมอิสระ"
                        >
                          📍 ดัดมุมทีละจุด
                        </Button>
                      )}
                    <Button
                      size="sm"
                      variant={roomTransformMode === "translate" ? "default" : "ghost"}
                      className="h-7 px-2 text-xs"
                      onClick={() => setRoomTransformMode("translate")}
                      title="เลื่อนย้ายตำแหน่งกรอบห้องบนระนาบพื้น (Translate Gizmo)"
                    >
                      <Move className="h-3.5 w-3.5 mr-1" />
                      ย้ายห้อง
                    </Button>
                    <Button
                      size="sm"
                      variant={roomTransformMode === "rotate" ? "default" : "ghost"}
                      className="h-7 px-2 text-xs"
                      onClick={() => setRoomTransformMode("rotate")}
                      title="หมุนทิศทางกรอบห้องตามแนวกำแพงเฉียง (Rotate Gizmo)"
                    >
                      <RotateCcw className="h-3.5 w-3.5 mr-1" />
                      หมุนทิศ
                    </Button>
                    <Button
                      size="sm"
                      variant={roomTransformMode === "scale" ? "default" : "ghost"}
                      className="h-7 px-2 text-xs"
                      onClick={() => setRoomTransformMode("scale")}
                      title="ดึงขยายขนาดกรอบห้อง (Scale Gizmo)"
                    >
                      <Maximize2 className="h-3.5 w-3.5 mr-1" />
                      ขยายกรอบ
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-7 px-2 text-xs"
                      onClick={() => {
                        setSelectedRoomId(activeAdminRoom.id)
                        setRoomModalOpen(true)
                      }}
                    >
                      แก้ไขเลขห้อง
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      className="h-7 px-2 text-xs"
                      onClick={() => handleDeleteRoomZone(activeAdminRoom.id)}
                      title="ลบกรอบโซนห้องนี้ (Delete / Backspace)"
                    >
                      <Trash2 className="h-3.5 w-3.5 mr-1" />
                      ลบกรอบ
                    </Button>
                  </div>
                )}

                <Button
                  size="sm"
                  variant={magneticWallSnap ? "secondary" : "outline"}
                  className="h-8 px-2 text-xs"
                  onClick={() => setMagneticWallSnap((s) => !s)}
                  title="เปิด/ปิดแม่เหล็กดูดเข้ามุมเสาและผนังอาคาร 3D อัตโนมัติ (Magnetic Corner Snap)"
                >
                  🧲 Snap มุมตึก: {magneticWallSnap ? "ON" : "OFF"}
                </Button>

                <Button
                  size="sm"
                  variant={snapToGrid ? "secondary" : "outline"}
                  className="h-8 px-2 text-xs"
                  onClick={() => setSnapToGrid((s) => !s)}
                  title="เปิด/ปิด Snap to Grid 0.5 เมตร"
                >
                  <Grid className="h-3.5 w-3.5 mr-1 text-emerald-400" />
                  Grid 0.5m: {snapToGrid ? "ON" : "OFF"}
                </Button>

                <Button
                  size="sm"
                  variant="outline"
                  className="h-8 px-2 text-xs"
                  onClick={() => {
                    const fIdx =
                      viewState.selectedFloor === "all"
                        ? Number(
                            activeAdminRoom?.floorIdx ??
                              newRoomForm.floorIdx ??
                              placementFloorIdx ??
                              1
                          )
                        : Number(viewState.selectedFloor)
                    updateView({
                      selectedFloor: String(fIdx),
                      showRooms: true,
                      showPlans: true,
                    })
                    viewportRef.current?.flyToTopDown(fIdx)
                  }}
                  title="สลับเป็นมุมมอง Top-Down 90° ดิ่งจากด้านบนเหมือนพิมพ์เขียว CAD"
                >
                  <Compass className="h-3.5 w-3.5 mr-1 text-primary" />
                  มุมมอง 90°
                </Button>

                <Button
                  size="sm"
                  variant="outline"
                  disabled={undoStack.length === 0 && polygonDraftCount === 0}
                  className="h-8 px-2 text-xs"
                  onClick={() => {
                    if (
                      drawRoomZoneMode &&
                      drawShapeType === "polygon" &&
                      viewportRef.current?.undoLastPolygonVertex?.()
                    ) {
                      return
                    }
                    handleUndo()
                  }}
                  title="ย้อนกลับ (Ctrl+Z)"
                >
                  <Undo2 className="h-3.5 w-3.5 mr-1 text-amber-400" />
                  Undo
                </Button>

                <Button
                  size="sm"
                  variant="outline"
                  disabled={redoStack.length === 0}
                  className="h-8 px-2 text-xs"
                  onClick={handleRedo}
                  title="ทำซ้ำ (Ctrl+Y)"
                >
                  <Redo2 className="h-3.5 w-3.5" />
                </Button>

                <Button
                  size="sm"
                  variant="ghost"
                  className="h-8 px-2 text-xs"
                  onClick={() => {
                    viewportRef.current?.cancelPolygonDraft?.()
                    setDrawRoomZoneMode(false)
                    setActiveAdminRoomId(null)
                  }}
                >
                  ปิดโหมด (Esc)
                </Button>
              </div>
            </div>
          </div>
        )}

      {/* QUICK CONTROLS: floor switcher + reset view (viewer shortcuts; full controls remain in the menu) */}
      <nav
        aria-label="Quick floor controls"
        className={`fixed bottom-4 z-20 flex items-center gap-1.5 rounded-full border border-border/80 bg-card/90 backdrop-blur-xl px-2 py-1 shadow-lg transition-[left] ${
          menuPinned && menuOpen ? "left-[376px] sm:left-[416px]" : "left-4"
        } ${isAdminRoute ? "hidden md:flex" : ""}`}
      >
        <M3SegmentedButtonSet>
          {[{ key: "all", label: "All" }, ...FLOORS.map((fl) => ({ key: String(fl.index), label: fl.shortLabel }))].map((f) => (
            <M3SegmentedButton
              key={f.key}
              label={f.label}
              selected={String(viewState.selectedFloor) === f.key}
              ariaLabel={`เลือกชั้น ${f.label}`}
              onClick={() => updateView({ selectedFloor: f.key })}
            />
          ))}
        </M3SegmentedButtonSet>
        <span className="mx-0.5 h-5 w-px bg-border" aria-hidden="true" />
        <M3IconButton
          variant="standard"
          ariaLabel="รีเซ็ตมุมกล้อง 3D (Reset Orbit)"
          title="รีเซ็ตมุมกล้อง 3D"
          onClick={() => {
            updateView({ selectedFloor: "all" })
            viewportRef.current?.resetCamera()
          }}
        >
          <RotateCcw className="h-4 w-4 text-primary" />
        </M3IconButton>
      </nav>

      <RackNameDialog
        open={rackNameDialogOpen}
        defaultName={rackSuggestedName}
        existingNames={devices.filter((d) => d.modelType === 'server_rack').map((d) => d.name)}
        onCancel={() => setRackNameDialogOpen(false)}
        onConfirm={handleConfirmRackName}
      />

      {/* 4. VIEWER MENU (extracted to src/components/ViewerMenu.jsx) */}
      <ViewerMenu
        adminAuthenticated={adminAuthenticated}
        devices={devices}
        directorySearch={directorySearch}
        expandedDirectoryRoomId={expandedDirectoryRoomId}
        filteredDirectoryRooms={filteredDirectoryRooms}
        filteredPlacedDevices={filteredPlacedDevices}
        handleResetToAdminDefaultView={handleResetToAdminDefaultView}
        handleSaveAsAdminDefaultView={handleSaveAsAdminDefaultView}
        isAdminRoute={isAdminRoute}
        menuOpen={menuOpen}
        menuPinned={menuPinned}
        networks={networks}
        onOpenRackula={openRackHierarchy}
        placedDevices={placedDevices}
        roomDirectorySearch={roomDirectorySearch}
        rooms={rooms}
        setDirectorySearch={setDirectorySearch}
        setExpandedDirectoryRoomId={setExpandedDirectoryRoomId}
        setMainViewMode={openRackHierarchy}
        setMenuOpen={setMenuOpen}
        setModalOpen={setModalOpen}
        setRoomDirectorySearch={setRoomDirectorySearch}
        setRoomModalOpen={setRoomModalOpen}
        setSelectedDeviceId={setSelectedDeviceId}
        setSelectedRackId={setSelectedRackId}
        setSelectedRoomId={setSelectedRoomId}
        toggleAllCategories={toggleAllCategories}
        toggleCategoryFilter={toggleCategoryFilter}
        toggleMenuPinned={toggleMenuPinned}
        updateView={updateView}
        viewState={viewState}
        viewportRef={viewportRef}
      />

      {/* 5. ADMIN BACKOFFICE COMMAND TOOLBAR & CONTEXTUAL TOOL DRAWER (Strictly on /admin route only) */}
      {isAdminRoute && adminAuthenticated && (
        <AdminToolbar
          unplacedDevices={unplacedDevices}
          filteredUnplacedDevices={filteredUnplacedDevices}
          placedDevices={placedDevices}
          rooms={rooms}
          filteredAdminRooms={filteredAdminRooms}
          networks={networks}
          viewState={viewState}
          updateView={updateView}
          placingDevice={placingDevice}
          placingRoom={placingRoom}
          drawRoomZoneMode={drawRoomZoneMode}
          toggleDrawRoomZoneMode={toggleDrawRoomZoneMode}
          drawShapeType={drawShapeType}
          setDrawShapeType={setDrawShapeType}
          snapToGrid={snapToGrid}
          setSnapToGrid={setSnapToGrid}
          magneticWallSnap={magneticWallSnap}
          setMagneticWallSnap={setMagneticWallSnap}
          autoSnapRoomEnabled={autoSnapRoomEnabled}
          setAutoSnapRoomEnabled={setAutoSnapRoomEnabled}
          cancelActiveMode={() => {
            setPlacingDevice(null)
            setPlacingRoom(null)
            if (drawRoomZoneMode) toggleDrawRoomZoneMode()
          }}
          activeAdminRoomId={activeAdminRoomId}
          setActiveAdminRoomId={setActiveAdminRoomId}
          roomTransformMode={roomTransformMode}
          setRoomTransformMode={setRoomTransformMode}
          undoCount={undoStack.length}
          redoCount={redoStack.length}
          handleUndo={handleUndo}
          handleRedo={handleRedo}
          handleDeleteRoomZone={handleDeleteRoomZone}
          onFlyToTopDown={() => {
            const fIdx =
              viewState.selectedFloor === "all"
                ? Number(newRoomForm.floorIdx ?? placementFloorIdx ?? 1)
                : Number(viewState.selectedFloor)
            updateView({
              selectedFloor: String(fIdx),
              showRooms: true,
              showPlans: true,
            })
            viewportRef.current?.flyToTopDown(fIdx)
          }}
          startPlacingDevice={startPlacingDevice}
          onQuickPlaceServerRack={handleQuickPlaceServerRack}
          startPlacingRoom={startPlacingRoom}
          onSaveAsDefaultView={handleSaveAsAdminDefaultView}
          handleUnplaceDevice={handleUnplaceDevice}
          onSelectDevice={(devId) => {
            const target = devices.find((d) => d.id === devId)
            if (target?.modelType === "server_rack") {
              setSelectedRackId(devId)
              openRackHierarchy(devId)
              return
            }
            if (target?.parentRackId) {
              setSelectedRackId(target.parentRackId)
              openRackHierarchy(target.parentRackId)
              return
            }
            setSelectedDeviceId(devId)
            setModalOpen(true)
          }}
          onSelectRoom={(rmId) => {
            setSelectedRoomId(rmId)
            setRoomModalOpen(true)
          }}
          onFlyTo={(pos, fIdx) => viewportRef.current?.flyTo(pos, fIdx)}
          adminSearch={adminSearch}
          setAdminSearch={setAdminSearch}
          adminRoomSearch={adminRoomSearch}
          setAdminRoomSearch={setAdminRoomSearch}
          subnetInput={subnetInput}
          setSubnetInput={setSubnetInput}
          scanStatus={scanStatus}
          handleTriggerScan={handleTriggerScan}
          singleIpInput={singleIpInput}
          setSingleIpInput={setSingleIpInput}
          scanningSingleIp={scanningSingleIp}
          handleScanSingleIp={handleScanSingleIp}
          newDevForm={newDevForm}
          setNewDevForm={setNewDevForm}
          handleAddDevice={handleAddDevice}
          newRoomForm={newRoomForm}
          setNewRoomForm={setNewRoomForm}
          handleAddRoom={handleAddRoom}
          batchRoomForm={batchRoomForm}
          setBatchRoomForm={setBatchRoomForm}
          handleBatchGenerateRooms={handleBatchGenerateRooms}
          onOpenRackula={openRackHierarchy}
        />
      )}

      {/* 6. ADMIN AUTHENTICATION DIALOG (/admin only) */}
      <Dialog open={isAdminRoute && loginDialogOpen} onOpenChange={setLoginDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Lock className="h-5 w-5 text-primary" />
              ยืนยันตัวตนผู้ดูแลระบบ (Admin Backoffice)
            </DialogTitle>
            <DialogDescription>
              ส่วนจัดการตำแหน่งอุปกรณ์ 3D การระบุหมายเลขห้อง และระบบสแกนเครือข่าย
              สงวนสิทธิ์เฉพาะผู้ดูแลระบบเท่านั้น
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleAdminLogin} className="space-y-3 py-2">
            <div className="space-y-1.5">
              <Label htmlFor="admin-pw">Admin Password</Label>
              <Input
                id="admin-pw"
                type="password"
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                placeholder="กรอกรหัสผ่านผู้ดูแลระบบ (ค่าเริ่มต้น: admin123)"
                autoFocus
              />
              {loginError && <p className="text-xs text-destructive">{loginError}</p>}
            </div>
            <DialogFooter>
              <Button type="submit" className="w-full">
                เข้าสู่ระบบจัดการหลังบ้าน (/admin)
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* 7. SHADCN/UI DEVICE INSPECTION & WEB LOGIN MODAL */}
      <DeviceModal
        device={selectedDevice}
        allDevices={devices}
        open={modalOpen}
        onOpenChange={setModalOpen}
        isAdmin={isAdminRoute && adminAuthenticated}
        onDeviceUpdated={(updatedDev) => {
          setDevices((prev) =>
            prev.map((d) => (d.id === updatedDev.id ? updatedDev : d))
          )
        }}
        onUnplaceDevice={handleUnplaceDevice}
        onOpenRackula={(rackId) => {
          setSelectedRackId(rackId)
          openRackHierarchy(rackId)
          setModalOpen(false)
        }}
      />

      {/* 8. SHADCN/UI INTERACTIVE ROOM INSPECTION & RENUMBERING MODAL */}
      <RoomModal
        room={selectedRoom}
        placedDevices={placedDevices}
        open={roomModalOpen}
        onOpenChange={setRoomModalOpen}
        isAdmin={isAdminRoute && adminAuthenticated}
        adminToken={adminToken}
        onFlyToRoom={(rm) => {
          updateView({ selectedFloor: String(rm.floorIdx ?? 0), showRooms: true })
          viewportRef.current?.flyTo(rm.position, Number(rm.floorIdx ?? 0))
        }}
        onSelectDevice={(devId) => {
          const target = devices.find((d) => d.id === devId)
          if (target?.modelType === "server_rack") {
            setSelectedRackId(devId)
            openRackHierarchy(devId)
            return
          }
          if (target?.parentRackId) {
            setSelectedRackId(target.parentRackId)
            openRackHierarchy(target.parentRackId)
            return
          }
          setSelectedDeviceId(devId)
          setModalOpen(true)
        }}
        onStartMovingRoom={(rm) => startPlacingRoom(rm)}
        onRoomUpdated={() => fetchState()}
        onRoomDeleted={() => fetchState()}
      />

      {/* 9. RACK HIERARCHY & ELEVATION INSPECTOR MODAL (In-place modal, root tree & mini units) */}
      <RackHierarchyModal
        open={rackHierarchyModalOpen}
        onOpenChange={setRackHierarchyModalOpen}
        rack={selectedRack}
        allDevices={devices}
        rooms={rooms}
        isAdmin={isAdminRoute && adminAuthenticated}
        adminToken={adminToken}
        onOpenDeviceModal={(devId) => {
          setSelectedDeviceId(devId)
          setModalOpen(true)
        }}
        onOpenRackulaDesigner={(rackId) => {
          openRackulaWindow(rackId)
        }}
        onFlyToRack={(pos, fIdx) => viewportRef.current?.flyTo(pos, fIdx)}
      />

      {/* 10. RACKULA 19-INCH RACK ELEVATION DESIGNER & HARDWARE MANAGER MODAL */}
      <RackulaModal
        open={rackModalOpen}
        rack={selectedRack}
        allDevices={devices}
        rooms={rooms}
        isAdmin={isAdminRoute && adminAuthenticated}
        adminToken={adminToken}
        onClose={() => setRackModalOpen(false)}
        onRefreshState={() => fetchState()}
        onInspectMountedDevice={(mountedDev) => {
          setSelectedDeviceId(mountedDev.id)
          setModalOpen(true)
        }}
        onStartMove3DRack={(rk) => {
          setActiveAdminDeviceId(rk.id)
          setDeviceTransformMode("translate")
        }}
        onUnplace3DRack={(rk) => {
          handleUnplaceDevice(rk.id)
        }}
        toast={toast}
      />
    </div>
  )
}

---
name: building-digital-twin
description: Complete architectural modeling guide, CAD vector extraction pipeline, 3D GLB conversion, and Full-Stack Web Application standards (React + Vite + Tailwind CSS v4 + Material 3 tokens + Radix UI + Three.js + Rackula + Multi-Network Scanner + JSON Schema v2.0.0) for the LUDUS 4-Story Building Digital Twin on port 8085.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# LUDUS Building Digital Twin — Complete Architecture, 3D Modeling & Full-Stack Engineering Skill Guide

> **⚠️ กฎเหล็กสำหรับ AI Agent ทุกเซสชัน (Mandatory First Step)**:
> ก่อนแก้ไขโค้ดใดๆ ในโปรเจคต์นี้ คุณ **ต้อง** อ่านไฟล์นี้ควบคู่กับ [`docs/FEATURES_REQUIREMENTS.md`](file:///c:/Coding%20Projects/Digital%20Twin/docs/FEATURES_REQUIREMENTS.md) และ [`docs/API_AND_SCHEMA_DOCS.md`](file:///c:/Coding%20Projects/Digital%20Twin/docs/API_AND_SCHEMA_DOCS.md) เสมอ และ **ห้ามลบหรือตัดทอนฟีเจอร์เดิมโดยไม่ได้รับอนุญาตจากผู้ใช้เด็ดขาด** หลังแก้ไขโค้ดทุกครั้ง ต้องรัน `npm run build; npm test` ให้ผ่าน 100%

---

## 1. ภาพรวมโปรเจคต์และโครงสร้างไฟล์สำคัญ (Project Overview & Repository Map)

โปรเจคต์ **LUDUS Building Digital Twin** (`c:\Coding Projects\Digital Twin`) คือระบบจำลองอาคาร 3 มิติ (4 ชั้น + ดาดฟ้าและสนามบาสเกตบอล) ร่วมกับระบบสำรวจเครือข่ายอัตโนมัติ (Multi-Network LAN/WAN/Router/Switch/AP Discovery & Port Inspector) ที่ทำงานบนพอร์ตมาตรฐาน **`8085`** (รองรับทั้ง Local Dev และ Docker Container)

### แผนผังไฟล์หลักในระบบ (Core File Map)
| หมวดหมู่ | ไฟล์สำคัญ | หน้าที่รับผิดชอบ |
| :--- | :--- | :--- |
| **3D Source & GLB Pipeline** | `LUDUS_Building_No_Glass.igz` | ไฟล์โมเดล 3D ต้นฉบับจาก IngeTrazo (ประกอบด้วย 4 ชั้น + สนามบาสเกตบอลดาดฟ้า + โครงถักหลังคา + เลเยอร์กระจก/ผนัง/ลูกศร) |
| | `scripts/build_glb_from_igz.py` | สคริปต์แปลงไฟล์ `.igz` เป็น `public/models/building.glb` โดยแยกชื่อโหนดตามชั้น (`F0_`, `F1_`, `F2_`, `F3_`) และหมวดหมู่ (`Slab`, `Column`, `Wall`, `Glass`, `Roof`, `Basketball`, `Arrow`, `Stair`, `Parapet`) |
| | `public/models/building.glb` | โมเดล 3D GLTF Binary ที่โหลดเข้าสู่ Three.js บนหน้าเว็บ |
| | `public/plans/floor_00..03.png` | ภาพแปลนสถาปัตยกรรม 2D CAD สำหรับฉายซ้อนทับบนแผ่นพื้นแต่ละชั้น |
| **Frontend (Material 3 + shadcn/ui + Three.js)** | `index.html`, `src/main.jsx`, `src/style.css` | จุดเริ่มต้นของแอป React 19 + Tailwind CSS v4 + Design Tokens ของ `shadcn/ui` (รองรับ Dark Slate & Light Clean Mode) |
| | `src/App.jsx` | คอมโพเนนต์หลัก ควบคุมการแยก Route (`/` vs `/admin`), แถบสถานะด้านบน, Hamburger Menu (`<Sheet>` + `<Accordion>`), โหมดปักหมุด 3D และแผงควบคุม Admin Backoffice |
| | `src/components/ThreeViewport.jsx` | เอนจินแสดงผล 3D Three.js WebGL, ระบบแยกชั้นแนวตั้ง (`exploded`), การเปิด/ปิดเลเยอร์โครงสร้าง 8 เลเยอร์, หมุดอุปกรณ์ 3D (`3D Pin`), ป้ายหมายเลขห้อง และระบบ Raycast คลิกวางตำแหน่งอุปกรณ์ |
| | `src/components/DeviceModal.jsx` | หน้าต่าง `<Dialog>` แสดงข้อมูลอุปกรณ์ละเอียด 4 แท็บ, ปุ่มเข้าเว็บพอร์ต `80`/`443`/Custom Ports, หน้าต่าง Reverse Proxy (`/api/proxy`), แผงพอร์ต Switch/SNMP (`switchInterfaces`), เส้นทางสายสัญญาณ Hierarchy และตัวช่วยคัดลอกรหัสผ่าน Login |
| | `src/components/RoomModal.jsx` | หน้าต่าง `<Dialog>` แสดงข้อมูลห้อง, สถานะเครือข่ายรวมของห้อง, รายการอุปกรณ์ที่ติดตั้งในห้อง (`isPlaced === true` เท่านั้น), ระบบแก้ไขหมายเลขห้องแบบ Smart Cascade (อัพเดทอุปกรณ์ในห้องตามอัตโนมัติ), ปรับขนาดกรอบพื้นที่ห้อง 3D (`zoneSize: width × depth`) และปุ่มคลิกย้ายตำแหน่งห้องบนโมเดล 3D |
| | `src/components/m3/*`, `src/theme/m3-tokens.css` | Material 3 wrappers (M3Button, M3Chip, M3Dialog, M3Tabs, ...) และ design tokens `--md-sys-*` (neutral zinc + accent น้ำเงิน) |
| | `src/components/RackulaModal.jsx`, `rackula/` | มุมมอง Rack Elevation 19 นิ้ว (Sub-App) |
| **Docs & Rules** | `docs/CODING_GUIDELINES.md`, `.agents/rules/coding-guidelines.md` | Coding & UX/UI guideline สำหรับคนและ Agent |
| | `src/components/ViewerMenu.jsx` | เมนู Hamburger ฝั่ง Viewer (5 Accordion + 8 layer switches) แยกออกจาก `App.jsx` — เทสต์ตรวจ `App.jsx` + `ViewerMenu.jsx` รวมกัน |
| | `src/components/ui/*` | คอมโพเนนต์มาตรฐาน `shadcn/ui` (`button`, `badge`, `card`, `input`, `label`, `switch`, `tabs`, `dialog`, `sheet`, `accordion`, `table`, `progress`, `scroll-area`, `separator`, `toaster`) |
| | `src/data/twinData.js` | ข้อมูลคงที่ของชั้นอาคาร (`FLOORS` index `0..3`), ขอบเขตแปลน (`OVERLAY_BOUNDS`), หมวดหมู่อุปกรณ์ 14 ประเภท (`DEVICE_CATEGORIES`), ประเภทห้อง (`ROOM_TYPES`) และฟังก์ชันตรวจจับห้องอัตโนมัติ (`findMatchingRoomForPoint`) |
| **Backend & Network Scanner** | `server/index.js`, `vite.config.js` | เซิร์ฟเวอร์ Express + WebSocket (`/ws`) บนพอร์ต `8085` (ตั้งค่า `watch.ignored: ['**/data/**']` ใน Vite เพื่อป้องกันหน้าเว็บรีโหลดเองเมื่อไฟล์ JSON อัปเดต) |
| | `server/api.js` | REST API Endpoints ทั้งหมด (Public Query, Admin CRUD, Subnet/IP Scanner, Port Scanner, Ping, Reverse Proxy `/api/proxy`, OpenAPI 3.0 `/api/openapi.json` และหน้าเอกสาร `/api/docs`) |
| | `server/scanner.js` | เอนจินสแกนเครือข่ายจริง (ICMP Ping, ARP Table MAC Extraction, Fast 48-Port & Full `1–65535` TCP Port Scanner, HTTP/HTTPS Banner Grabber, SNMPv2c `sysDescr` Probe) |
| | `server/oui.js` | ฐานข้อมูล MAC OUI Vendor Lookup และตัวจำแนกประเภทอุปกรณ์อัตโนมัติ (`Router`, `Switch`, `Access Point`, `Server`, `CCTV`, `Printer`, `Sensor`, `Network`) พร้อมคำนวณ Hierarchy Tier (`0..3`) |
| | `server/store.js` | ตัวจัดการฐานข้อมูล `data/digital_twin_db.json` ตามมาตรฐาน **JSON Schema v2.0.0**, คำนวณโครงสร้างต้นไม้ `networkTopologyTree` และ `spatialBuildingTree` |
| **CLI, Tests & Docs** | `scripts/scan_and_build_hierarchy.mjs` | สคริปต์ CLI (`npm run scan`) สแกนทุกวงเครือข่ายในเครื่องและสร้างฐานข้อมูลอุปกรณ์เริ่มต้นโดยตั้งค่า `isPlaced: false` |
| | `tests/api_and_schema.test.mjs` | ชุดทดสอบอัตโนมัติ 4 ส่วน (`npm test`) ตรวจสอบ Schema v2.0.0, OUI/Hierarchy, REST API Unplaced Rules และ Regression Guard ป้องกันฟีเจอร์ UI หาย |
| | `docs/FEATURES_REQUIREMENTS.md` | เอกสารข้อกำหนดฟีเจอร์บังคับ (FRS v2.0.0) |
| | `docs/API_AND_SCHEMA_DOCS.md` | เอกสารอ้างอิงโครงสร้าง JSON Schema v2.0.0 และ REST/WebSocket API |

---

## 2. สถาปัตยกรรม 3 ส่วนหลัก และกฎเหล็กที่ห้ามละเมิด (Core System Rules)

### 2.1 การแบ่งแยก 3 ส่วนของระบบอย่างเด็ดขาด (3-Part Architecture)
1. **ส่วนที่ 1 — หน้าแสดงผลหลักสำหรับผู้ใช้งาน (`/` — Public / Operator 3D Viewer)**:
   - แสดงเฉพาะโครงสร้างอาคาร 3 มิติ ตำแหน่งอุปกรณ์ที่จัดวางแล้ว และสถานะแบบเรียลไทม์ (Read-Only)
   - ❌ **ห้ามมีปุ่ม ลิงก์ หรือทางเข้าสู่หน้า `/admin` ปรากฏบนหน้า `/` เด็ดขาด**
   - ปุ่มควบคุมการแสดงผลทั้งหมดต้องจัดระเบียบอยู่ใน **Hamburger Menu (`☰`)** (`<Sheet>` ด้านซ้าย) แบ่งเป็น 4 หมวดหมู่ (`Accordion`):
     1. **เลือกชั้นอาคาร & มุมกล้อง (`Floors & View`)**: ปุ่ม `All Floors`, `G (00_Ground_Floor)`, `1F (01_First_Floor)`, `2F (02_Second_Floor)`, `RF (03_Rooftop)` และปุ่ม `Reset 3D Orbit`
     2. **เลเยอร์โครงสร้างอาคาร 3D (`Display Layers`)** — **ต้องมีครบทั้ง 8 สวิตช์บังคับ**:
        - `exploded`: แยกชั้นอาคารแนวตั้ง (`Explode Floors`)
        - `showGlass`: แสดงกระจกหน้าต่างอาคาร (`Window Glass Layer`)
        - `showWalls`: แสดงผนังอาคาร (`Architectural Walls`)
        - `showRoof`: แสดงหลังคาดาดฟ้า (`Rooftop Canopies`)
        - `showBasketball`: แสดงสนามบาสเกตบอลดาดฟ้า (`Basketball Court`)
        - `showArrows`: แสดงลูกศรทิศทางจราจร (`Traffic Flow Arrows`)
        - `showPlans`: แสดงแปลนพื้นสถาปัตย์ 2D (`CAD Blueprints`)
        - `showRooms`: แสดงป้ายหมายเลขห้อง (`Room Number Tags`)
     3. **กรองวงเครือข่าย หมวดหมู่ & สถานะ (`Filters`)**:
        - กรองตามสถานะ (`ALL`, `Online`, `Warning`, `Offline`)
        - กรองตามวงเครือข่าย (`Subnet CIDR`)
        - กรองตามหมวดหมู่อุปกรณ์ (`DEVICE_CATEGORIES` ชิปปุ่มกดทั้ง 14 หมวดหมู่ พร้อมปุ่ม `เลือกทั้งหมด / ซ่อนทั้งหมด`)
     4. **รายการอุปกรณ์ที่จัดวางแล้ว (`Placed Device Directory`)**:
        - ค้นหาและคลิกเพื่อซูมกล้อง 3D (`flyTo`) ไปยังหมุดอุปกรณ์พร้อมเปิด `DeviceModal`
     5. **สารบัญห้องแยกตามชั้น (`Spatial Rooms Directory`)**:
        - ค้นหาห้องตามเลขห้อง/ชื่อห้อง แสดงไฟสถานะเครือข่ายรวมของห้อง จำนวนอุปกรณ์ในห้อง และคลิกเพื่อซูมกล้องเข้าห้อง (`Fly-to-Room`) พร้อมเปิด `RoomModal`

2. **ส่วนที่ 2 — ระบบจัดการหลังบ้านสำหรับผู้ดูแลระบบ (`/admin` — Admin Backoffice & Studio Command Toolbar)**:
   - เข้าถึงได้เฉพาะเมื่อพิมพ์ URL `/admin` เท่านั้น และต้องล็อกอินด้วยรหัสผ่านผ่าน `<Dialog>` (`ADMIN_PASSWORD`, ค่าเริ่มต้น `admin123`)
   - มี **Floating Admin Command Toolbar (`src/components/AdminToolbar.jsx`)** ลอยอยู่ด้านล่างกึ่งกลางจอ พร้อมแผงเครื่องมือด้านขวาที่พับเก็บได้:
     - **เครื่องมือคิวรอวาง (`Unplaced Queue`)**: แสดงอุปกรณ์ที่สแกนพบแต่ยังไม่ได้จัดวาง (`isPlaced: false`) พร้อมปุ่ม **"วางบนตึก 3D"** เพื่อเข้าสู่โหมด Raycast คลิกเลือกจุดติดตั้งบนพื้นผิวอาคาร 3 มิติ พร้อมระบบ **Auto-Snap Room** ที่ตรวจจับกรอบพื้นที่ห้อง (`zoneSize`) และผูกหมายเลขห้องให้อัตโนมัติทันที
     - **เครื่องมือวางแล้ว (`Placed Devices`)**: แสดงอุปกรณ์ที่จัดวางบนตึกแล้ว สามารถกด **"ย้ายจุด"** หรือ **"ถอนหมุดกลับเข้าคิว"** (`POST /api/admin/devices/:id/unplace`)
     - **เครื่องมือจัดการห้องและวาดกรอบโซน 3D (`Rooms Manager & 3D Rectangle Zone Drawer`)**:
       - **3D Click & Drag Rectangle Marquee (`drawRoomZoneMode`)**: คลิกซ้ายค้างและลากบนพื้นอาคาร 3D เพื่อวาดกรอบสี่เหลี่ยมกำหนดความกว้าง×ลึกของห้อง (`zoneSize: width × depth`) พร้อมป้ายวัดขนาดสด (`W × D = ตร.ม.`) และรันเลขห้องถัดไปอัตโนมัติ
       - **Three.js `TransformControls` CAD Gizmo**: คลิกเลือกกรอบห้องบน 3D เพื่อดึงขยายขนาด (`scale`) หรือเลื่อนตำแหน่ง (`translate`) พร้อม **Snap to Grid (`0.5m`)** และมุมมอง **Top-Down 90° (`flyToTopDown`)**
       - **Room Zone Deletion & Transactional Undo/Redo (`Ctrl+Z` / `Ctrl+Y` / `Delete`)**: ลบกรอบสี่เหลี่ยมโซนห้องได้ด้วยปุ่มหรือคีย์ลัด `Delete`/`Backspace` และรองรับ `Ctrl+Z` (`Undo`) / `Ctrl+Y` (`Redo`) ที่ซิงค์กับฐานข้อมูลหลังบ้าน
       - **Pattern Generator & Smart Cascade**: สร้างชุดเลขห้องอัตโนมัติตาม Pattern (`POST /api/admin/rooms/batch` เช่น `101–104`) และแก้ไขเลขห้องแบบ **Smart Cascade** (`PUT /api/admin/rooms/:id`)
     - **เครื่องมือสแกนเนอร์ (`Scanner`)**: สแกนทั้งวงเครือข่าย (`Subnet CIDR`), สแกนเจาะจง IP เดี่ยว (`Single IP Scan`), เพิ่มอุปกรณ์ใหม่เข้าคิว และ Export JSON Bundle (`/api/export`)

3. **ส่วนที่ 3 — เอนจินสแกนเครือข่าย ตรวจสอบพอร์ต และหน้าต่างข้อมูลอุปกรณ์ (`Core Scanner & DeviceModal`)**:
   - เมื่อคลิกที่อุปกรณ์ (ทั้งในหน้า `/` และ `/admin`) จะเปิด [`DeviceModal`](file:///c:/Coding%20Projects/Digital%20Twin/src/components/DeviceModal.jsx) ซึ่งต้องมี:
     - **แถบปุ่มด่วนเข้าหน้าเว็บอุปกรณ์**: ปุ่ม `HTTP :80`, `HTTPS :443`, ปุ่มพอร์ตเว็บอื่นๆ ที่เปิดอยู่ (`8080`, `8443`, `8008`, `3000`, `5000`, `8006`, `9000`, ฯลฯ), ปุ่ม **"เปิดผ่าน Reverse Proxy (ในหน้านี้)"** (`/api/proxy?url=...`) และปุ่ม **"Ping เช็คสถานะสด"**
     - **4 แท็บข้อมูลละเอียด**:
       1. `ข้อมูลอุปกรณ์`: IP, MAC (พร้อมปุ่ม Copy), Vendor, Model, OS/Firmware, Serial/Asset Tag, Subnet, Gateway, VLAN, Latency, Role/Tier, พิกัด 3D `(X, Y, Z)`
       2. `พอร์ต TCP`: ตารางแสดงทุกพอร์ตที่เปิด + Banner + ปุ่มสแกนพอร์ต **Fast Scan (48 พอร์ต)** และ **Full Scan (1–65535)**
       3. `แผงพอร์ต Switch/SNMP`: แสดงผังพอร์ตกายภาพของ Switch/Router (`#1`..`#24` สถานะ `🟢 UP / ⚪ DN`, ความเร็ว, VLAN และข้อมูล SNMP MIB-II)
       4. `Hierarchy & Login`: แผนผังเส้นทางสายสัญญาณ (`WAN-ROOT -> Gateway -> Switch -> AP -> Endpoint`) และตัวช่วยคัดลอก `Username` / `Password` พร้อมแจ้งเตือน Toast

---

### 2.2 กฎเหล็กการซ่อนอุปกรณ์ที่ยังไม่จัดวาง (Strict Unplaced Device Visibility Rule)
- **อุปกรณ์ใดที่มี `isPlaced: false` (หรือยังไม่มีพิกัด `position` / `floorIdx`) ห้ามนำมาแสดงผลในหน้าแสดงผลหลักและส่วนสาธารณะทุกจุด**:
  1. ห้ามสร้างหมุด 3D (`3D Pin`) หรือป้ายชื่อลอยบนโมเดลอาคารใน `ThreeViewport.jsx`
  2. ห้ามนำมานับรวมในตัวเลขสถิติด้านบน (`Placed`, `Online`, `Warn`, `Offline`)
  3. ห้ามแสดงในรายการ Directory ของ Hamburger Menu
  4. ห้ามส่งออกใน `GET /api/public/state` และ `networkTopologyTree` สาธารณะ
- อุปกรณ์ที่สแกนพบใหม่ทั้งหมด (ทั้งจาก `npm run scan`, `/api/admin/scan/subnet`, `/api/admin/scan/ip`) ต้องเริ่มต้นด้วย `isPlaced: false`, `floorIdx: null`, `roomNumber: ""`, `position: null` เสมอ จนกว่า Admin จะจัดวางลงบนโมเดล 3D

---

## 3. UX/UI Design System (Redesign v3 — Neutral Clean)

รายละเอียดเต็มอยู่ที่ [`docs/CODING_GUIDELINES.md`](file:///c:/Coding%20Projects/Digital%20Twin/docs/CODING_GUIDELINES.md) §5 และกฎ Agent ที่ `.agents/rules/coding-guidelines.md`

- **ทิศทาง**: Light clean (SaaS dashboard) + Dark mode; Material 3 roles บน neutral zinc + accent น้ำเงิน (`#2563eb`). Tokens อยู่ที่ `src/style.css` (`--primary`, `--background`, …) และ `src/theme/m3-tokens.css` (`--md-sys-*`) — ❌ ห้าม hard-code สี
- **Viewer `/`**: Top bar · Hamburger Sheet ซ้าย (ปุ่ม **Pin** ค้างเมนูไว้บน desktop, จำค่าใน `localStorage` `ludus.menuPinned`) · **Quick Floor Controls** ลอยล่างซ้าย (All/G/1F/2F/RF + Reset camera) — ยังคง 5 หมวดใน Accordion และ 8 layer switches
- **Admin `/admin`**: Right dock แบบ tabs (คิวรอวาง / วางแล้ว / ห้อง / สแกน / +อุปกรณ์ / มุมมอง) + toolbar ล่างเหลือเครื่องมือหลัก (เปิด Dock, วาดโซน/ปักเลขห้อง, Undo/Redo/Delete, Top-down 90°); โหมดวางหมุด/วาดโซนต้องมีแถบสถานะโหมดและ `Esc` ยกเลิก
- **A11y/Responsive**: `aria-label` ปุ่มไอคอน, `aria-pressed` toggle, focus ring, `prefers-reduced-motion`, ใช้งานบน tablet/มือถือได้
- **สีสถานะ**: Online `#22c55e` · Warning `#f59e0b` · Offline `#ef4444` · Idle `#64748b` (ต้องมีไอคอน/ข้อความกำกับ)

---

## 4. มาตรฐานโมเดล 3D และ CAD (อ่านเมื่อจำเป็น)

เนื้อหากฎการปั้นโมเดล เสา/ผนัง/พื้น และการแปลง `.igz` → `.glb` อยู่ที่ [`references/3d-pipeline.md`](file:///c:/Coding%20Projects/Digital%20Twin/.agents/skills/building-digital-twin/references/3d-pipeline.md) — รัน `python scripts/build_glb_from_igz.py` เมื่อแก้ `.igz`

---

## 5. Mandatory Agent Checklist

1. ตรวจ [`docs/FEATURES_REQUIREMENTS.md`](file:///c:/Coding%20Projects/Digital%20Twin/docs/FEATURES_REQUIREMENTS.md) ว่าไม่มี `FR-SYS/VIEW/VIS/ADM/NET` สูญหาย
2. โค้ดใหม่แยกเป็นคอมโพเนนต์/hook (อย่าขยาย `App.jsx` เพิ่ม); ถ้าย้ายโค้ดที่เทสต์ตรวจสตริง ต้องอัปเดตเทสต์ในงานเดียวกันโดยไม่ลดความเข้มงวด
3. รัน `npm run build; npm test` — ต้องผ่านทั้งหมด (ปัจจุบัน **11/11**; ชุดทดสอบครอบคลุม Schema v2.0.0, OUI/Hierarchy, REST Unplaced rules, FRS Regression Guard, Room/Auto-Snap/Cascade, Model Catalog/Rack, Move/Rotate/Delete, Label layer & Default View, PostgreSQL/Prisma, Rackula Elevation, Rackula REST/YAML)
4. คำสั่งมาตรฐาน: `npm run dev` (8085) · `npm run build` · `npm start` · `npm run scan` · `npm test`
5. ตรวจ UI ด้วยตา Light/Dark และกว้าง 375/768/1440 ก่อนส่งมอบ

# LUDUS Building 3D Digital Twin — Features Requirement Specification (FRS v2.0.0)

เอกสารฉบับนี้กำหนดรายการฟีเจอร์บังคับ (Mandatory Features Requirement) ของระบบ **LUDUS Building 3D Network & Infrastructure Digital Twin** เพื่อใช้เป็นมาตรฐานอ้างอิงและป้องกันไม่ให้ฟีเจอร์ใดตกหล่นหรือสูญหายเมื่อมีการอัปเดตโค้ดในอนาคต

---

## 1. สถาปัตยกรรมระบบและพอร์ตมาตรฐาน (System & Port Configuration)
- **FR-SYS-01**: เว็บแอปพลิเคชันและ API Server ต้องทำงานที่พอร์ต **`8085`** เป็นค่าเริ่มต้น (ทั้งโหมด Development `vite --port 8085`, Production `node server/index.js`, และ Docker `8085:8085`)
- **FR-SYS-02**: ใช้โมเดลอาคาร 3 มิติจากไฟล์ต้นฉบับ [`LUDUS_Building_No_Glass.igz`](file:///c:/Coding%20Projects/Digital%20Twin/LUDUS_Building_No_Glass.igz) แปลงเป็น [`public/models/building.glb`](file:///c:/Coding%20Projects/Digital%20Twin/public/models/building.glb) (ประกอบด้วย 4 ชั้น: `00_Ground_Floor`, `01_First_Floor`, `02_Second_Floor`, `03_Rooftop` พร้อมสนามบาสเกตบอลดาดฟ้าและหลังคาโครงถัก)
- **FR-SYS-03**: ใช้ UI Framework **`shadcn/ui`** (React + Vite + Tailwind CSS v4 + Radix UI Primitives + Lucide Icons) ทั้งโปรเจคต์ พร้อมปุ่มสลับธีม **Dark Slate / Light Clean Mode**

---

## 2. ส่วนที่ 1: หน้าแสดงผลหลัก (Public / Operator 3D Viewer — `/`)
- **FR-VIEW-01 (Strict Route Isolation)**: หน้าแสดงผลหลัก (`/`) มีหน้าที่แสดงผลโครงสร้างอาคาร 3D ตำแหน่งอุปกรณ์ และสถานะแบบ Read-Only เท่านั้น **ห้ามมีปุ่ม ลิงก์ หรือทางเข้าสู่หน้า `/admin` ปรากฏในหน้า `/` เด็ดขาด**
- **FR-VIEW-02 (Hamburger Menu Organization)**: ปุ่มควบคุมการแสดงผลทั้งหมดต้องถูกจัดระเบียบไว้ภายใน **Hamburger Menu (`☰`)** (`<Sheet>` + `<Accordion>`) แบ่งออกเป็น 4 หมวดหมู่อย่างชัดเจน:
  1. **หมวดที่ 1 — เลือกชั้นอาคาร & มุมกล้อง (`Floors & View`)**:
     - ปุ่มเลือกดูทุกชั้น (`All Floors`) หรือแยกดูเฉพาะชั้น: `G (00_Ground_Floor)`, `1F (01_First_Floor)`, `2F (02_Second_Floor)`, `RF (03_Rooftop)`
     - ปุ่มรีเซ็ตมุมกล้อง 3 มิติ (`Reset 3D Orbit`)
  2. **หมวดที่ 2 — เลเยอร์โครงสร้างอาคาร 3D (`Display Layers`)** — ต้องมีสวิตช์เปิด/ปิดครบทั้ง **8 เลเยอร์บังคับ**:
     - `exploded`: แยกชั้นอาคารแนวตั้ง (`Explode Floors`)
     - `showGlass`: แสดง/ซ่อนกระจกหน้าต่างอาคาร (`Window Glass Layer`)
     - `showWalls`: แสดง/ซ่อนผนังอาคาร (`Architectural Walls`)
     - `showRoof`: แสดง/ซ่อนหลังคาดาดฟ้า (`Rooftop Canopies`)
     - `showBasketball`: แสดง/ซ่อนสนามบาสเกตบอลดาดฟ้า (`Basketball Court`)
     - `showArrows`: แสดง/ซ่อนลูกศรทิศทางจราจร (`Traffic Flow Arrows`)
     - `showPlans`: แสดง/ซ่อนแปลนพื้นสถาปัตย์ 2D (`CAD Blueprints`)
     - `showRooms`: แสดง/ซ่อนป้ายหมายเลขห้อง (`Room Number Tags`)
  3. **หมวดที่ 3 — กรองวงเครือข่าย หมวดหมู่ และสถานะ (`Filters`)**:
     - กรองตามสถานะอุปกรณ์ (`ALL`, `Online`, `Warning`, `Offline`)
     - กรองตามวงเครือข่าย (`Subnet CIDR` เช่น `192.168.110.0/24`, `192.168.111.0/24`)
     - กรองตามหมวดหมู่อุปกรณ์ (`DEVICE_CATEGORIES` ทั้ง 14 หมวดหมู่ พร้อมปุ่ม `เลือกทั้งหมด / ซ่อนทั้งหมด`)
  4. **หมวดที่ 4 — รายการอุปกรณ์ที่จัดวางแล้ว (`Placed Device Directory`)**:
     - ช่องค้นหา (`Search`) ตามชื่อ, IP, หมายเลขห้อง, ยี่ห้อ หรือหมวดหมู่
     - รายการอุปกรณ์ที่จัดวางแล้ว เมื่อคลิกจะซูมกล้อง 3D (`flyTo`) ไปยังตำแหน่งอุปกรณ์และเปิดหน้าต่างข้อมูลอุปกรณ์ (`DeviceModal`)
  5. **หมวดที่ 5 — สารบัญห้องแยกตามชั้น (`Spatial Rooms Directory`)**:
     - ค้นหาและเลือกดูห้องตามชั้นอาคาร (`[roomNumber]`, ชื่อห้อง, ประเภทห้อง, ขนาดโซน `W×D`, จำนวนอุปกรณ์ในห้อง และไฟสถานะสุขภาพเครือข่ายรวมของห้อง) พร้อมปุ่มคลิกซูมกล้องเข้าห้อง (`Fly-to-Room`) และเปิดหน้าต่าง `RoomModal`

---

## 3. กฎเหล็กการซ่อนอุปกรณ์ที่ยังไม่จัดวาง (Unplaced Device Visibility Rule)
- **FR-VIS-01**: อุปกรณ์ใดที่เพิ่งสแกนพบหรือเพิ่มเข้ามาใหม่ และ**ยังไม่ถูกจัดวางตำแหน่งลงบนโมเดล 3D โดย Admin (`isPlaced: false`) จะต้องไม่ถูกนำมาแสดงผลในทุกจุดของหน้าแสดงผล** ได้แก่:
  - ห้ามแสดงหมุด 3D (`3D Pin`) และป้ายชื่อบนตัวอาคาร
  - ห้ามนำมานับรวมในแถบสถิติด้านบน (`Placed / Online / Warn / Offline`)
  - ห้ามแสดงในรายการ Directory ของ Hamburger Menu หรือในรายการอุปกรณ์ของ `RoomModal`
  - ห้ามส่งออกใน Public API (`GET /api/public/state`)
- **FR-VIS-02**: อุปกรณ์ที่มี `isPlaced: false` จะแสดงอยู่ในแท็บ **"คิวรอวาง (`Unplaced Queue`)"** ในหน้า `/admin` เท่านั้น จนกว่า Admin จะกดเลือกวางลงบนพิกัดอาคาร 3D

---

## 4. ส่วนที่ 2: ระบบจัดการหลังบ้านและระบบบริหารจัดการหมายเลขห้อง 3D (Admin Backoffice & Spatial Room Numbering — `/admin`)
- **FR-ADM-01 (Authentication)**: เข้าถึงได้เฉพาะผ่าน URL `/admin` เท่านั้น และต้องยืนยันตัวตนด้วยรหัสผ่านผู้ดูแลระบบ (`ADMIN_PASSWORD`, ค่าเริ่มต้น `admin123`) ผ่าน `<Dialog>`
- **FR-ADM-02 (Unplaced Queue & 3D Raycast Placement with Auto-Snap Room)**:
  - แสดงรายการอุปกรณ์ที่สแกนพบแต่ยังไม่ได้จัดวาง (`isPlaced: false`) พร้อมช่องค้นหา
  - ปุ่ม **"วางบนตึก 3D"** เพื่อเข้าสู่โหมด Raycast Placement: เมื่อคลิกซ้ายลงบนพื้นห้องในโมเดล 3D ระบบ **Auto-Snap Room** จะตรวจจับกรอบพื้นที่ห้อง (`zoneSize: width × depth`) และผูกหมายเลขห้อง (`roomNumber` & `roomId`) ให้อัตโนมัติทันที
- **FR-ADM-03 (Placed Device Management)**:
  - แสดงรายการอุปกรณ์ที่จัดวางแล้ว (`isPlaced: true`)
  - สามารถกด **"ย้ายจุด"** เพื่อเปลี่ยนตำแหน่งบนโมเดล 3D หรือกด **"ถอนหมุดกลับเข้าคิว"** (`POST /api/admin/devices/:id/unplace`) เพื่อซ่อนอุปกรณ์ออกจากหน้าแสดงผลกลับเข้าสู่คิวรอวาง
- **FR-ADM-04 (Interactive 3D Room Numbering & Spatial Zone Management — `RoomModal.jsx`)**:
  - **FR-ROOM-01 (3D Click-to-Place Room & Floor Zone Highlight)**: Admin สามารถคลิกเลือกตำแหน่งห้องบนพื้นโมเดล 3D โดยตรง (`placingRoom`) พร้อมไฮไลต์กรอบพื้นที่ห้อง (`3D Floor Zone Highlight` ขนาด `width × depth` เมตร) และแยกสีตามประเภทห้อง (`ROOM_TYPES`: `NOC`, `Office`, `Classroom`, `Lobby`, `ME`, `Sport`, `Security`, `Custom`)
  - **FR-ROOM-02 (Interactive 3D Room Tag & Live Room Health)**: ป้ายหมายเลขห้องบนโมเดล 3D (`.room-label-3d`) ต้องแสดงไฟสถานะเครือข่ายรวมของห้อง (`Online`/`Warning`/`Offline`/`Idle`), ไอคอนประเภทห้อง, `[roomNumber]`, ชื่อห้อง และจำนวนอุปกรณ์ในห้อง เมื่อคลิกที่ป้ายห้องหรือกรอบพื้นห้องจะเปิด `RoomModal`
  - **FR-ROOM-03 (Smart Room Renumbering Cascade)**: เมื่อ Admin แก้ไขหมายเลขห้อง (`PUT /api/admin/rooms/:id`) ระบบต้องอัพเดท `roomNumber` ของอุปกรณ์ทุกตัวที่ติดตั้งอยู่ในห้องนั้นให้อัตโนมัติทันที
  - **FR-ROOM-04 (Batch Room Pattern Generator)**: รองรับการสร้างชุดหมายเลขห้องอัตโนมัติตาม Pattern (`POST /api/admin/rooms/batch` เช่น `101–104`, `201–204`, `G01–G04`) บนชั้นที่เลือก พร้อมคลิกย้ายตำแหน่งบน 3D ได้ทุกห้อง
  - **FR-ROOM-05 (Interactive 3D Polygon Point-by-Point & Rectangle Zone Drawing, Per-Vertex Handles, Magnetic Snap, Deletion & Undo/Redo `Ctrl+Z`)**:
    - **3D Point-by-Point Polygon Zone Drawing (`drawShapeType: 'polygon'`)**: Admin สามารถคลิกซ้ายปักหมุดกำหนดมุมกรอบห้องทีละจุดตามแนวกำแพงจริง (`polygon: [{x, z}, ...]`, รองรับห้องเฉียง/รูปตัว L/หลายเหลี่ยม) มีเส้น Rubber-band ลากตามเมาส์ คำนวณความยาวแต่ละด้านและพื้นที่รวม (`Shoelace Formula`) แบบสดๆ พร้อมคลิกจุดแรก, Double-Click หรือกด `Enter` เพื่อปิดกรอบห้อง (และสลับเป็นโหมดลากกรอบสี่เหลี่ยมเร็ว `rectangle` ได้)
    - **Magnetic Wall/Column Corner Snap & Angle Constraint (`Shift`)**: รองรับแม่เหล็กดูดเข้ามุมเสาและผนังอาคาร 3D อัตโนมัติ (`magneticWallSnap`) พร้อมกด `Shift` ค้างเพื่อล็อกมุม `45°/90°`
    - **Per-Vertex Polygon Editing & `TransformControls` CAD Gizmo**: เมื่อคลิกเลือกกรอบห้องบน 3D จะแสดงหมุดลูกบอลที่แต่ละมุม (`vertices` mode) ให้ลากดัดมุมห้องได้อิสระ รวมถึงสลับโหมดเลื่อนทั้งห้อง (`translate`), หมุนทิศทางห้อง (`rotate`) หรือดึงขยายกรอบ (`scale`) พร้อมระบบ **Point-in-Polygon Ray-Casting Auto-Snap** สำหรับตรวจจับอุปกรณ์ที่วางในห้องหลายเหลี่ยม
    - **Room Zone Deletion & Transactional Undo/Redo (`Ctrl+Z` / `Ctrl+Y` / `Delete`)**: รองรับการลบจุดหมุดล่าสุดระหว่างวาด (`Ctrl+Z` / `Backspace`), ลบกรอบโซนห้อง (`Delete` / `Backspace`), และ **`Ctrl+Z` (`Undo`)** / **`Ctrl+Y` (`Redo`)** ที่ซิงค์กับฐานข้อมูลหลังบ้านครบทุกการกระทำ
- **FR-ADM-05 (Floating Admin Command Toolbar — `AdminToolbar.jsx`)**:
  - แถบเครื่องมือลอยด้านล่างกึ่งกลางจอ (`role="toolbar"`) สำหรับหน้า `/admin` รวมคำสั่งสำคัญครบในที่เดียว: คิวรอวาง, อุปกรณ์ที่วางแล้ว, วาดกรอบห้อง 3D (`Draw Zone`), ปักเลขห้อง, จัดการห้อง, ปุ่ม `Undo (Ctrl+Z)` / `Redo (Ctrl+Y)` / `ลบกรอบ (Del)`, สแกนเครือข่าย, สลับชั้น `ALL/G/1F/2F/RF`, มุมมอง `90°`, และ `Export JSON`

---

## 5. ส่วนที่ 3: ระบบสแกนเครือข่าย ตรวจสอบพอร์ต และหน้าต่างข้อมูลอุปกรณ์ (Core Scanner & Device Inspection Modal)
- **FR-NET-01 (Multi-Network LAN/WAN/Router/Switch Discovery)**:
  - รองรับการสแกนทั้งวงเครือข่าย (`POST /api/admin/scan/subnet`) และการสแกนเจาะจง IP เดี่ยว (`POST /api/admin/scan/ip`) รวมถึง CLI Script (`npm run scan`)
  - ตรวจสอบสถานะ Online/Offline, Latency, ARP MAC Address, OUI Vendor Lookup, HTTP/HTTPS Title & Server Header, SNMPv2c `sysDescr` และจัดลำดับชั้นเครือข่าย (`Hierarchy Tier 0..3`: `WAN -> Core Router -> Distribution/Access Switch -> Wireless AP -> Endpoint`)
- **FR-NET-02 (Device Inspection & Direct Login Modal — `DeviceModal.jsx`)**:
  - เมื่อคลิกที่หมุดอุปกรณ์ 3D หรือรายการอุปกรณ์ ต้องเปิด `<Dialog>` แสดงข้อมูลละเอียด 4 แท็บ:
    1. **ข้อมูลอุปกรณ์ (`Overview`)**: IPv4, MAC (พร้อมปุ่ม Copy), Vendor, Model, OS/Firmware, Serial Number, Subnet, Gateway, VLAN, Latency, Hierarchy Role & Tier, พิกัด 3D `(X, Y, Z)` และเวลา Last Seen
    2. **พอร์ต TCP ทั้งหมด (`Ports`)**: แสดงทุกพอร์ตที่เปิด พร้อมโปรโตคอล, Banner, ปุ่มสแกนพอร์ต **Fast Scan (48 พอร์ต)** และ **Full Scan (1–65535)**
    3. **แผงพอร์ต Switch/SNMP (`Switch Matrix`)**: แสดงผังพอร์ตกายภาพของ Switch/Router (`#1`..`#24` สถานะ `UP/DOWN`, ความเร็ว, VLAN และข้อมูล SNMP MIB-II)
    4. **Hierarchy & Login (`Hierarchy & Credentials`)**: แสดงแผนผังเส้นทางสายสัญญาณตั้งแต่ต้นทางถึงปลายทาง และ **Login Credential Helper** (ปุ่มคัดลอก Username / Password พร้อมแจ้งเตือน Toast)
- **FR-NET-03 (Quick Web Access 80 / 443 / Custom Ports & Reverse Proxy)**:
  - มีปุ่มกดเข้าหน้าเว็บจัดการอุปกรณ์ได้ทันทีสำหรับพอร์ต **`HTTP :80`**, **`HTTPS :443`**, และพอร์ตเว็บอื่นๆ ที่ตรวจพบ (`8080`, `8443`, `8008`, `3000`, `5000`, `8006`, `9000`, ฯลฯ)
  - มีปุ่ม **"เปิดผ่าน Reverse Proxy (ในหน้านี้)"** (`/api/proxy?url=...`) เพื่อเปิดหน้า Login ของอุปกรณ์ภายใน Modal ได้ทันทีโดยไม่ติดปัญหา `X-Frame-Options`
  - มีปุ่ม **"Ping เช็คสถานะสด"** (`POST /api/devices/:id/ping`) เพื่อตรวจสอบสถานะและ Latency แบบเรียลไทม์

---

## 6. การตรวจสอบป้องกันฟีเจอร์หายอัตโนมัติ (Automated Regression Guard)
ชุดทดสอบ [`tests/api_and_schema.test.mjs`](file:///c:/Coding%20Projects/Digital%20Twin/tests/api_and_schema.test.mjs) (`npm test`) จะตรวจสอบทั้ง:
1. ความถูกต้องของโครงสร้าง JSON Schema v2.0.0 และกฎ `isPlaced: false` สำหรับอุปกรณ์ที่เพิ่งสแกน
2. ความถูกต้องของระบบจำแนกหมวดหมู่อุปกรณ์และลำดับชั้นเครือข่าย (OUI & Topology Hierarchy)
3. การทำงานของ REST API ทั้งฝั่ง Public (`/api/public/state`) และ Admin (`Place / Unplace Lifecycle`)
4. **Feature Requirement Regression Check**: ตรวจสอบซอร์สโค้ดของ [`src/App.jsx`](file:///c:/Coding%20Projects/Digital%20Twin/src/App.jsx), [`src/components/ThreeViewport.jsx`](file:///c:/Coding%20Projects/Digital%20Twin/src/components/ThreeViewport.jsx), และ [`src/components/DeviceModal.jsx`](file:///c:/Coding%20Projects/Digital%20Twin/src/components/DeviceModal.jsx) ว่ายังมีสวิตช์เลเยอร์ทั้ง 8 ตัว (`exploded`, `showGlass`, `showWalls`, `showRoof`, `showBasketball`, `showArrows`, `showPlans`, `showRooms`) ปุ่มเข้าพอร์ต `80`/`443`/`/api/proxy` และฟีเจอร์บังคับครบถ้วน 100%
5. **Spatial Room Numbering, 3D Zone Highlight & Smart Room Cascade**: ตรวจสอบการผูกหมายเลขห้องและอัพเดทเลเยอร์ห้อง
6. **3D Model Catalog Registry, Room Boundary Clamping & Server Rack Placement with Rotation**: ตรวจสอบการวางโมเดล 3D ตู้ Server Rack
7. **Active Device Move, Rotate, Unplace & Permanent Delete Lifecycle**: ตรวจสอบการย้าย หมุนตำแหน่ง และลบอุปกรณ์
8. **Device Badge/Label Layer Toggle, Global Admin Default View Persistence & Public Synchronization**: ตรวจสอบการเปิด-ปิดเลเยอร์ป้ายชื่ออุปกรณ์และบันทึกค่าเริ่มต้นจาก Admin
9. **PostgreSQL 16 & Prisma ORM Hybrid Relational + JSONB Persistence**: ตรวจสอบการเชื่อมต่อฐานข้อมูล PostgreSQL ผ่าน Prisma ORM, ระบบ Auto-Seed จาก JSON เดิม และการบันทึกข้อมูลแบบเรียลไทม์

---

## 7. ส่วนที่ 4: สถาปัตยกรรมฐานข้อมูลระดับ Enterprise (PostgreSQL 16 & Prisma ORM)
- **Database Engine**: PostgreSQL 16 Alpine รันบน Docker Compose (`ludus_digital_twin_postgres`) พอร์ต `5432` พร้อม Healthcheck และ Persistent Volume (`postgres_data`)
- **Data Access & Schema**: Prisma ORM (`@prisma/client@6.19.3`) โครงสร้างแบบ Hybrid Relational + JSONB:
  - ตาราง Relational: `Network`, `Room`, `Device`, `ScanHistory`, `SystemSetting`
  - คอลัมน์ Spatial และ Filtering ดัชนีความเร็วสูง: `floorIdx`, `posX`, `posY`, `posZ`, `rotationY`, `modelType`, `width`, `depth`
  - คอลัมน์ JSONB สำหรับโครงสร้างยืดหยุ่น: `polygon`, `openPorts`, `snmpInfo`, `switchInterfaces`, `credentials`, `hierarchy`
- **Zero-Data-Loss Auto-Seed**: ระบบจะตรวจสอบตารางใน PostgreSQL อัตโนมัติเมื่อเริ่มทำงาน หากยังว่างอยู่จะโหลดข้อมูลจาก `data/digital_twin_db.json` เข้าสู่ PostgreSQL ทันที พร้อมเขียนไฟล์สำรองต่อเนื่อง และมี Endpoints `/api/export` / `/api/import` เพื่อความปลอดภัยสูงสุด



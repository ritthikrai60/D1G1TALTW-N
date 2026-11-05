# LUDUS Building Digital Twin — API, Network Hierarchy & JSON Schema Documentation (v2.0.0)

เอกสารฉบับนี้อธิบายสถาปัตยกรรมระบบ **3D Building Digital Twin & Multi-Network Discovery Engine**, โครงสร้างข้อมูล **JSON Schema v2.0.0**, ผังลำดับชั้นเครือข่ายและอาคาร (**Network & Spatial Hierarchy**) และรายละเอียด **REST API / WebSocket** ทั้งหมดของโปรเจคต์

---

## 1. ภาพรวมสถาปัตยกรรมระบบ (System Architecture)

โปรเจคต์แบ่งออกเป็น 3 ส่วนหลักที่ทำงานร่วมกันบนพอร์ต `8085`:

| ส่วนระบบ | เส้นทาง (URL) | หน้าที่หลัก |
| :--- | :--- | :--- |
| **1. Public 3D Viewer** | `http://localhost:8085/` | แสดงโมเดลอาคาร 3 มิติ (`LUDUS_Building_No_Glass.igz`), สถานะเครือข่าย, หมุดอุปกรณ์ตามห้อง/ชั้น และจัดระเบียบปุ่มควบคุมทั้งหมดไว้ใน **Hamburger Menu (`☰`)** (โหมดอ่านอย่างเดียว ไม่มีลิงก์ไปหน้า Admin) |
| **2. Admin Backoffice** | `http://localhost:8085/admin` | ระบบจัดการหลังบ้าน (ป้องกันด้วยรหัสผ่าน `ADMIN_PASSWORD` ค่าเริ่มต้น `admin123`) สำหรับสั่งสแกนเครือข่าย, จัดวางหมุดอุปกรณ์ลงพิกัด 3D, กำหนดหมายเลขห้อง และแก้ไขทะเบียนครุภัณฑ์ |
| **3. Core Scanner & REST/WS API** | `http://localhost:8085/api/*` และ `/ws` | เซอร์วิสสแกนเครือข่ายหลายวง (LAN/WAN/Router/Switch/AP), ตรวจสอบพอร์ต (`1–65535`), ดึง MAC OUI Vendor, HTTP/HTTPS Banner, SNMP, คำนวณผัง Hierarchy อัตโนมัติ และให้บริการ Reverse Proxy (`/api/proxy`) |

---

## 2. โครงสร้างลำดับชั้น (Dual Hierarchy Architecture)

ระบบจัดทำ Hierarchy อัตโนมัติเป็น 2 แกนควบคู่กันใน `hierarchy`:

### 2.1 ผังลำดับชั้นเครือข่าย (`hierarchy.networkTopologyTree`)
จัดลำดับอุปกรณ์ตามโครงสร้างเครือข่ายจริง (`Tier 0` ถึง `Tier 4`):
- **Tier 0 (`WAN-ROOT`)**: เกตเวย์อินเทอร์เน็ตภายนอก (`1.1.1.1`)
- **Tier 1 (`Core Gateway / Router`)**: เราเตอร์หลักประจำวงแลน เช่น `192.168.110.50` (`Core-GW-Router-110-50`, พอร์ต `80, 443, 1883, 8883`) และ `172.17.0.1` (`HyperV-vSwitch-Gateway`)
- **Tier 2 (`Distribution / PoE Switch`)**: สวิตช์กระจายสัญญาณประจำชั้น เช่น `192.168.110.52`, `.53`, `.54`, `.58`, `.69`, `.134`, `192.168.111.93`, `.100`, `.104`, `.105`, `.106`, `.197`
- **Tier 3 (`Wireless Access Point / Infrastructure Server`)**: จุดกระจายสัญญาณไร้สาย (`192.168.110.51`, `.70`, `.71`, `.79`, `.93`, `.98`, `.124`, `.128`, `.129`, `.130`, `.132`, `.235`) และเซิร์ฟเวอร์ (`192.168.111.2`, `172.17.6.21`)
- **Tier 4 (`Endpoint / Printer / Sensor / IoT`)**: เครื่องพิมพ์เครือข่าย (`192.168.110.141`, `.155`, `.199` พอร์ต `80, 161, 443, 515, 631, 9100`), เซ็นเซอร์ และเครื่องลูกข่ายทั้งหมด

### 2.2 ผังลำดับชั้นพื้นที่อาคาร (`hierarchy.spatialBuildingTree`)
จัดลำดับตามกายภาพของโมเดล 3 มิติ (`Building -> Floor -> Room -> Device`):
- `LUDUS_BUILDING` (`LUDUS_Building_No_Glass.igz`)
  - **Floor 0 (`00_Ground_Floor`)**: ห้อง `G-101` (Main MDF & Core Gateway), `G-102` (West Lobby), `G-103` (East Wing)
  - **Floor 1 (`01_First_Floor`)**: ห้อง `1F-201` (1F IDF Switch Closet), `1F-202` (North Operations), `1F-203` (South Office)
  - **Floor 2 (`02_Second_Floor`)**: ห้อง `2F-301` (2F NOC & Server Center), `2F-302` (East R&D Lab), `2F-303` (West Studio)
  - **Floor 3 (`03_Rooftop`)**: โซน `RF-401` (East Pergola Lounge), `RF-402` (Rooftop Basketball Court)

---

## 3. โครงสร้าง JSON Schema v2.0.0 (`data/digital_twin_db.json`)

```json
{
  "schemaVersion": "2.0.0",
  "metadata": {
    "projectName": "LUDUS Building Digital Twin & Network Command",
    "buildingModel": "LUDUS_Building_No_Glass.igz",
    "schemaVersion": "2.0.0",
    "totalNetworks": 4,
    "totalRooms": 11,
    "totalDevices": 44,
    "placedDevices": 44,
    "onlineDevices": 44,
    "updatedAt": "2026-11-04T11:05:50.000Z"
  },
  "networks": [
    {
      "id": "NET-INFRA-110",
      "name": "LAN Infrastructure Segment (192.168.110.0/24)",
      "cidr": "192.168.110.0/24",
      "gateway": "192.168.110.50",
      "dnsServers": ["192.168.110.50", "1.1.1.1"],
      "dhcpServer": "192.168.110.50",
      "interfaceName": "Wi-Fi (802.11ax)",
      "localIp": "192.168.111.2",
      "vlanId": "VLAN 110 (Infra)",
      "isAutoDetected": true,
      "isConnectedNow": true
    }
  ],
  "rooms": [
    {
      "id": "ROOM-G-101",
      "roomNumber": "G-101",
      "name": "Main MDF & Core Gateway Room",
      "floorIdx": 0,
      "floorLabel": "00_Ground_Floor",
      "color": "#f97316",
      "position": { "x": -12.0, "y": 1.6, "z": -8.0 }
    }
  ],
  "devices": [
    {
      "id": "DEV-192-168-110-50",
      "name": "Core-GW-Router-110-50 (Main Gateway & MQTT)",
      "category": "Router",
      "status": "Online",
      "ip": "192.168.110.50",
      "subnet": "192.168.110.0/24",
      "mac": "C4:B2:5B:F3:C4:9C",
      "vendor": "Huawei / Ruijie Enterprise Gateway",
      "isPlaced": true,
      "floorIdx": 0,
      "roomId": "ROOM-G-101",
      "roomNumber": "G-101",
      "position": { "x": -12.5, "y": 1.5, "z": -8.5 },
      "hierarchy": {
        "tier": 1,
        "role": "Core Gateway / Router",
        "parentDeviceId": "WAN-ROOT",
        "parentDeviceName": "WAN Internet Upstream (1.1.1.1)",
        "uplinkPort": "WAN1 (1000Base-T)",
        "childrenIds": ["DEV-192-168-110-52", "DEV-192-168-110-53"],
        "path": ["WAN-ROOT", "DEV-192-168-110-50"]
      },
      "networkInfo": {
        "ip": "192.168.110.50",
        "subnet": "192.168.110.0/24",
        "mac": "C4:B2:5B:F3:C4:9C",
        "vendor": "Huawei / Ruijie Enterprise Gateway",
        "hostname": "host-192-168-110-50.ludus.lan",
        "vlan": "VLAN 110 (Infra)",
        "connectedSwitch": "WAN Internet Upstream (1.1.1.1)",
        "switchPort": "WAN1 (1000Base-T)"
      },
      "hardwareInfo": {
        "vendor": "Huawei / Ruijie Enterprise Gateway",
        "osFirmware": "Enterprise Gateway OS / HTTPS + MQTT Broker (1883/8883)",
        "serialNumber": "SN-LUDUS-F3C49C",
        "assetTag": "AST-2026-110-50"
      },
      "spatialInfo": {
        "isPlaced": true,
        "building": "LUDUS_Building_No_Glass",
        "floorIdx": 0,
        "floorLabel": "00_Ground_Floor",
        "roomId": "ROOM-G-101",
        "roomNumber": "G-101",
        "position": { "x": -12.5, "y": 1.5, "z": -8.5 }
      },
      "openPorts": [
        { "port": 80, "protocol": "tcp", "service": "HTTP", "state": "open", "isWeb": true, "scheme": "http" },
        { "port": 443, "protocol": "tcp", "service": "HTTPS", "state": "open", "isWeb": true, "scheme": "https" },
        { "port": 1883, "protocol": "tcp", "service": "MQTT Broker (IoT)", "state": "open", "isWeb": false },
        { "port": 8883, "protocol": "tcp", "service": "MQTTS (Secure IoT)", "state": "open", "isWeb": false }
      ],
      "credentials": {
        "username": "admin",
        "password": "admin123",
        "loginUrl": "https://192.168.110.50:443",
        "defaultPort": "443"
      },
      "telemetry": {
        "status": "Online",
        "latencyMs": 6,
        "lastSeen": "2026-11-04T11:05:50.000Z"
      }
    }
  ],
  "hierarchy": {
    "networkTopologyTree": { "id": "WAN-ROOT", "children": [] },
    "spatialBuildingTree": { "id": "LUDUS_BUILDING", "floors": [] }
  }
}
```

---

## 4. รายละเอียด REST API Reference

สามารถเปิดดูหน้า Interactive API Docs ได้ที่ `http://localhost:8085/api/docs` หรือดึงไฟล์ OpenAPI 3.0 JSON ได้ที่ `http://localhost:8085/api/openapi.json`

### 4.1 Public & Query Endpoints (ไม่ต้องใช้ Token)

| Method | Endpoint | คำอธิบาย |
| :--- | :--- | :--- |
| `GET` | `/api/health` | ตรวจสอบสถานะเซิร์ฟเวอร์, Uptime และรุ่น Schema (`2.0.0`) |
| `GET` | `/api/public/state` | ดึงสถานะสำหรับหน้า Viewer (**คืนค่าเฉพาะอุปกรณ์ที่ถูกจัดวางโดย Admin แล้ว `isPlaced: true` เท่านั้น** อุปกรณ์ที่ยังไม่ถูกจัดวางจะถูกซ่อนทั้งหมด) |
| `GET` | `/api/hierarchy` | ดึง `networkTopologyTree` (เฉพาะอุปกรณ์ที่จัดวางแล้ว), `discoveredTopologyTree` และ `spatialBuildingTree` |
| `GET` | `/api/networks` | ดึงรายการวงเครือข่าย (LAN/WAN/VLAN) ทั้งหมด |
| `GET` | `/api/rooms` | ดึงรายการห้องทั้งหมด (กรองตามชั้นได้ด้วย `?floorIdx=0..3`) |
| `GET` | `/api/devices` | ดึงรายการอุปกรณ์ รองรับ Query Parameters: `?floorIdx=`, `?category=`, `?status=`, `?subnet=`, `?tier=1..4`, `?placed=true` |
| `GET` | `/api/devices/:id` | ดึงข้อมูลเชิงลึกและ Hierarchy ของอุปกรณ์รายตัวตาม `id` |
| `POST` | `/api/devices/:id/ping` | สั่งทดสอบ Ping เช็กสถานะและ Latency ของอุปกรณ์ทันที |
| `POST` | `/api/devices/:id/scan-ports` | สั่งสแกนพอร์ตอุปกรณ์ (`{"mode": "fast"}` 48 พอร์ต หรือ `{"mode": "full", "startPort": 1, "endPort": 65535}`) |
| `GET` | `/api/export` | ดาวน์โหลดข้อมูลทั้งหมดในรูปแบบ JSON Schema v2.0.0 |
| `GET` | `/api/proxy?url=...` | Reverse Proxy สำหรับเปิดหน้าเว็บของอุปกรณ์ (`80, 443, 8080, 8443`) ภายใน Modal |

### 4.2 Admin Protected Endpoints (ต้องแนบ Header `Authorization: Bearer <token>`)

| Method | Endpoint | คำอธิบาย |
| :--- | :--- | :--- |
| `POST` | `/api/admin/login` | ส่ง `{"password": "admin123"}` เพื่อรับ `{ "token": "...", "ok": true }` |
| `GET` | `/api/admin/verify` | ตรวจสอบความถูกต้องของ Admin Token |
| `GET` | `/api/admin/state` | ดึงข้อมูลทั้งหมดสำหรับหน้าจัดการหลังบ้าน `/admin` |
| `POST` | `/api/admin/devices` | เพิ่มหรืออัปเดตข้อมูลอุปกรณ์ + คำนวณผัง Hierarchy ใหม่อัตโนมัติ |
| `PUT` | `/api/admin/devices/:id` | แก้ไขข้อมูลอุปกรณ์ตาม `id` |
| `POST` | `/api/admin/devices/:id/unplace` | ถอนอุปกรณ์ออกจากโมเดล 3D (`isPlaced: false`) เพื่อส่งกลับไปยังคิวรอจัดวางในแท็บสแกนเครือข่าย |
| `DELETE` | `/api/admin/devices/:id` | ลบอุปกรณ์ออกจากระบบถาวร |
| `POST` | `/api/admin/rooms` | เพิ่มหรือแก้ไขหมายเลขห้อง (`roomNumber`, `name`, `floorIdx`, `position`) |
| `DELETE` | `/api/admin/rooms/:id` | ลบห้องออกจากระบบ |
| `POST` | `/api/admin/networks` | เพิ่มหรือแก้ไขวงเครือข่าย CIDR / VLAN |
| `POST` | `/api/admin/scan/subnet` | สั่งสแกนทั้งวงแลนแบบ Asynchronous (`{"cidr": "192.168.110.0/24"}`) พร้อมส่งผล Real-time ผ่าน WebSocket |
| `POST` | `/api/admin/scan/ip` | สแกนเจาะจง IP เดียวทันที (`{"ip": "192.168.110.50", "mode": "fast"}`) |
| `POST` | `/api/admin/import` | ตรวจสอบ Schema และนำเข้าไฟล์ JSON Bundle เข้าสู่ระบบ |

---

## 5. คำสั่งสแกนเครือข่ายและรันการทดสอบ (CLI Commands)

```bash
# 1. สแกนเครือข่ายจริงทั้งหมด สร้างผัง Hierarchy และนำเข้าสู่เว็บอัตโนมัติ
npm run scan

# 2. รันชุดทดสอบอัตโนมัติ (JSON Schema v2.0.0 + Hierarchy + OUI + REST API)
npm test

# 3. รันเซิร์ฟเวอร์พัฒนาบนพอร์ต 8085
npm run dev

# 4. Build และรัน Production Server (หรือผ่าน Docker)
npm run build
npm start
```


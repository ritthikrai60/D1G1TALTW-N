# Building Zones & Smart IoT Topology

## 1. Physical-to-Digital Hierarchy
The Digital Twin follows the graph hierarchy:
`Site` → `Building (Main Complex)` → `Floor (F0..F3)` → `Zone (Functional Space)` → `Device (IoT Sensor/Actuator)`

## 2. Semantic Zones by Floor

### Floor 00 — Ground Floor (`Z = 0.0m`)
| Zone ID | Name (TH / EN) | Category | Approx. Area | Description |
| :--- | :--- | :--- | :--- | :--- |
| `Zone_F0_Parking` | ลานจอดรถใต้ถุนและกลางแจ้ง (Under-croft Parking) | Parking | 1,150 m² | ช่องจอดรถหมายเลข 1–30 พร้อมทางวิ่งรถ |
| `Zone_F0_CoreService` | โถงบริการและห้องน้ำชั้นล่าง (Ground Service & WC) | Service / WC | 185 m² | ห้องน้ำส่วนกลาง ห้องเครื่อง และบันไดเชื่อมชั้น 1 |
| `Zone_F0_MainStairs` | บันไดทางขึ้นหลักหน้าอาคาร (Grand Entrance Stairs) | Circulation | 95 m² | บันไดหลักเชื่อมลานด้านหน้าขึ้นสู่มุขชั้น 1 |

### Floor 01 — First Floor (`Z = 3.5m`)
| Zone ID | Name (TH / EN) | Category | Approx. Area | Description |
| :--- | :--- | :--- | :--- | :--- |
| `Zone_F1_CircleLounge` | โถงกิจกรรมวงกลมและห้องรับรอง (Circular Lounge & Suites) | Lounge | 340 m² | โถงวงกลมปีกซ้ายหน้า พร้อมห้องย่อย 4 ห้องและระเบียงลูกกรง |
| `Zone_F1_LockerClub` | โซนล็อกเกอร์และคลับเฮาส์ (Locker & Club Facilities) | Facility | 480 m² | ห้องล็อกเกอร์ ห้องอาบน้ำ และโซนพักผ่อนนักกีฬา |
| `Zone_F1_MainLobby` | โถงต้อนรับหลักและบันไดวน (Grand Lobby & Spiral Stair) | Lobby | 360 m² | มุขทางเข้าหลัก เคาน์เตอร์ต้อนรับ โถงบันไดวน และห้องน้ำกลาง |
| `Zone_F1_EastGallery` | โถงปีกขวาและระเบียงโค้ง (East Curved Wing & Arcade) | Commercial | 720 m² | ห้องโถงตามแนวโค้งปีกขวา (13 ช่วงเสา) และทางเดินระเบียงหน้าอาคาร |
| `Zone_F1_EastCore` | โถงลิฟต์และบันไดปีกขวา (East Elevator & Stair Core) | Circulation | 140 m² | โถงลิฟต์โดยสารและบันไดหนีไฟฝั่งขวาสุด |
| `Zone_F1_SteelBase` | โครงสร้างโถงหลังฝั่งซ้าย (Rear-Left Steel Frame Base) | Structure | 1,280 m² | พื้นที่ฐานโครงเหล็กด้านหลังฝั่งซ้าย |

### Floor 02 — Second Floor (`Z = 7.5m`)
| Zone ID | Name (TH / EN) | Category | Approx. Area | Description |
| :--- | :--- | :--- | :--- | :--- |
| `Zone_F2_WestDining` | ห้องอาหารและคลับเลานจ์ปีกซ้าย (West Dining & Lounge) | Dining / Lounge | 820 m² | โถงรับประทานอาหารและเลานจ์พร้อมหน้าต่างซุ้มโค้ง 8 ช่อง |
| `Zone_F2_CentralAtrium` | โถงกลางและระเบียงซุ้มโค้งใหญ่ (Central Arch Atrium & WC) | Lobby / WC | 350 m² | โถงบันไดวนชั้น 2 ซุ้มระเบียงโค้งใหญ่ด้านหน้า และห้องน้ำกลาง |
| `Zone_F2_EastBanquet` | โถงจัดเลี้ยงและสัมมนาปีกขวา (East Curved Banquet Hall) | Banquet / Hall | 740 m² | โถงเปิดโล่งขนาดใหญ่ตามแนวโค้งปีกขวา หน้าต่างซุ้มโค้ง 13 ช่อง |
| `Zone_F2_EastCore` | โถงลิฟต์และบันไดชั้น 2 (East Core L2) | Circulation | 140 m² | โถงลิฟต์และบันไดฝั่งขวาสุด ชั้น 2 |

### Floor 03 — Roof Floor (`Z = 11.5m`)
| Zone ID | Name (TH / EN) | Category | Approx. Area | Description |
| :--- | :--- | :--- | :--- | :--- |
| `Zone_F3_SkyTerrace` | ลานดาดฟ้าและโครงหลังคาคลุม (Rooftop Sky Bar & Canopy) | Rooftop | 710 m² | ดาดฟ้าเปิดโล่งเหนือปีกขวาพร้อมโครงหลังคาเหล็กคลุม |
| `Zone_F3_CentralRoof` | โถงสกายไลท์และห้องน้ำดาดฟ้า (Skylight & Roof WC Core) | Service / WC | 240 m² | หลังคาสกายไลท์เหนือบันไดวนและห้องน้ำชั้นดาดฟ้า |
| `Zone_F3_EastPenthouse` | อาคารโถงลิฟต์ดาดฟ้า (East Rooftop Penthouse) | Circulation | 145 m² | โถงลิฟต์และบันไดขึ้นดาดฟ้าฝั่งขวาสุด |
| `Zone_F3_SteelCage` | โครงเหล็กสูงฝั่งซ้าย (Rear-Left Steel Arch Cage) | Structure | 980 m² | โครงเหล็กซุ้มโค้งสูงเหนืออาคารฝั่งซ้าย |

## 3. Smart Building IoT Sensor Categories
1. **Audio / PA Zones (`audio`)**: Zone speaker clusters reporting playback status (BGM / Paging / Standby), volume (dB), and active channel.
2. **HVAC & Air Quality (`hvac`)**: Zone temperature (°C), relative humidity (%), CO₂ (ppm), and AQI status.
3. **CCTV & Security (`cctv`)**: Camera nodes at entrances, parking bays, lobby, and rooftop with live status.
4. **Smart Parking (`parking`)**: Real-time occupancy counters for Stalls `#1–#30` (Floor 00) and VIP Front Stalls `#31–#37` (Floor 01).


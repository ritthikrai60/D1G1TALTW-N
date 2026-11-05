# LUDUS Digital Twin — Coding & UX/UI Guidelines

เอกสารสั้นสำหรับคนและ AI Agent (กฎแบบกระชับสำหรับ Agent อยู่ที่ `.agents/rules/`)

## 1. Golden Rules
1. **ห้ามลบ/ตัดทอนฟีเจอร์เดิม** โดยไม่ได้รับอนุญาต — ตรวจกับ [FEATURES_REQUIREMENTS.md](FEATURES_REQUIREMENTS.md) ก่อนแก้ทุกครั้ง
2. หน้า `/` (Viewer) **ห้ามมีลิงก์/ปุ่มไป `/admin`**
3. อุปกรณ์ `isPlaced: false` **ห้ามแสดงในส่วนสาธารณะ** (3D pin, สถิติ, directory, `/api/public/state`)
4. หลังแก้โค้ดทุกครั้ง: `npm run build; npm test` ต้องผ่านทั้งหมด (ปัจจุบัน 11/11)
5. แก้ทีละน้อย, commit/ตรวจสอบเป็นขั้น ๆ; ไม่ refactor + เปลี่ยนพฤติกรรมในขั้นเดียวกัน

## 2. Tech Stack & โครงสร้างไฟล์
| ส่วน | เทคโนโลยี |
| :-- | :-- |
| Frontend | React 19, Vite 6, Tailwind CSS v4, Radix UI (shadcn-style `src/components/ui/*`), Material 3 wrappers (`src/components/m3/*`), Three.js |
| Backend | Express 5 + WebSocket, `data/digital_twin_db.json` + Prisma/PostgreSQL |
| Sub-app | `rackula/` (Rack elevation) |

- Component ใหม่: `src/components/<Name>.jsx` (PascalCase); hooks `src/hooks/use<Name>.js`; ข้อมูลคงที่ `src/data/`.
- `App.jsx` ใหญ่เกินไป — **โค้ดใหม่ให้แยกเป็นคอมโพเนนต์/hook** แทนการเพิ่มใน `App.jsx`; ย้ายออกแบบค่อยเป็นค่อยไป (ทำแล้ว: `ViewerMenu.jsx`; ถัดไป: top bar, modal state, hooks ข้อมูล). เมื่อแยกไฟล์ ให้เพิ่มพาธใหม่ในเทสต์ที่ grep ซอร์ส.
- ⚠️ `tests/api_and_schema.test.mjs` ตรวจ **สตริงในซอร์ส** (`App.jsx`, `AdminToolbar.jsx`, `ThreeViewport.jsx`, …). ถ้าย้ายโค้ด ต้องย้าย/อัปเดตเทสต์ให้ครอบคลุมไฟล์ใหม่ในคอมมิตเดียวกัน และห้ามลดความเข้มงวดของเทสต์.

## 3. JavaScript / React
- ใช้ function components + hooks; ไม่มี class components.
- ชื่อ: component `PascalCase`, hook `useXxx`, ตัวแปร/ฟังก์ชัน `camelCase`, ค่าคงที่ `UPPER_SNAKE_CASE`, handler `handleXxx`, boolean `isXxx/showXxx/hasXxx`.
- State ที่เกี่ยวกับมุมมอง 3D ให้ผ่าน `viewState`/`updateView()` เท่านั้น.
- `useEffect` ต้อง cleanup (listener, timer, WebSocket, Three.js dispose geometry/material/renderer).
- ห้าม `fetch` กระจายใน JSX — ใช้ helper เดียว, จัดการ error และแจ้ง `useToast()`.
- Persist ค่า UI ด้วย `localStorage` คีย์ขึ้นต้น `ludus.` และครอบ `try/catch`.
- ห้ามคอมเมนต์/Docstring เดิมที่ไม่เกี่ยวข้องถูกลบ; คอมเมนต์อธิบาย "ทำไม" ไม่ใช่ "ทำอะไร".

## 4. Three.js
- ทุก geometry/material/texture ที่สร้างเองต้อง `dispose()` ตอน unmount/rebuild.
- ห้ามสร้าง object ใน render loop (`animate`) — reuse `Vector3`/`Matrix4`.
- ชื่อโหนดโมเดล: `F{0-3}_<Category>_…` (Slab, Column, Wall, Glass, Roof, Basketball, Arrow, Stair, Parapet).
- หน่วยเป็นเมตร; Snap to Grid 0.5 m.

## 5. Design System (UX/UI)
**ทิศทาง:** Light clean (SaaS dashboard) เป็นค่าเริ่มต้น + Dark mode; Material 3 roles บน neutral zinc + accent สีน้ำเงิน.
- **Tokens เท่านั้น**: ใช้ `bg-background/card/muted`, `text-foreground/muted-foreground`, `border-border`, `text-primary` และ `--md-sys-*` — ❌ ห้าม hard-code hex/`slate-*`/`purple-*` ใน JSX (ยกเว้นสีสถานะและ overlay 3D ใน `style.css`).
- **สีสถานะ (คงที่ทั้งแอป):** Online `#22c55e`, Warning `#f59e0b`, Offline `#ef4444`, Idle `#64748b` — สถานะต้องมี **ไอคอนหรือข้อความ** กำกับ ไม่พึ่งสีอย่างเดียว.
- **Radius:** ปุ่ม/ชิป `rounded-full`, การ์ด/แผง `rounded-xl` (12px), dialog `rounded-2xl`. **Elevation:** ใช้ `shadow-sm/md/lg` เท่านั้น.
- **Typography:** Roboto + Noto Sans Thai; IP/MAC/พอร์ต ใช้ `font-mono`; ขนาดต่ำสุด 11px; หัวข้อ section ใช้ `text-xs font-semibold` ไม่ใช้ uppercase+tracking-wider ซ้ำทุกที่.
- **Spacing:** สเกล 4px (`gap-1/2/3/4`); padding แผง `p-4`, ระยะระหว่าง section `space-y-3`.
- **ภาษา:** UI หลักภาษาไทย + คำศัพท์เทคนิคภาษาอังกฤษในวงเล็บเมื่อจำเป็น; ปุ่มใช้คำกริยาสั้น ๆ.
- **Layout:**
  - Viewer `/`: Top bar (แบรนด์ + สถิติ) · Hamburger Sheet ซ้าย (pin ได้บน desktop) · Quick floor controls ลอยล่างซ้าย.
  - Admin `/admin`: Right dock แบบ tabs (Queue / Placed / Rooms / Scanner) · Toolbar ล่างเหลือเครื่องมือหลัก (Undo/Redo/Top-down).
  - โหมดที่ต้องการโฟกัส (วางหมุด, วาดโซน) ต้องมี **แถบสถานะโหมดชัดเจน + ปุ่ม Esc ยกเลิก**.
- **Accessibility:** ทุกปุ่มไอคอนมี `aria-label`; toggle ใช้ `aria-pressed`; focus ring มองเห็นเสมอ; contrast ≥ 4.5:1; เคารพ `prefers-reduced-motion`; เป้าสัมผัส ≥ 32px (tablet ≥ 40px).
- **Responsive:** Desktop เป็นหลัก, ใช้งานบน tablet/มือถือได้ (Sheet เต็มจอ ≤ 640px, ซ่อน pin, toolbar เลื่อนแนวนอน).
- **Feedback:** การกระทำที่เปลี่ยนข้อมูลต้องมี toast; การลบ/ถอนหมุดต้องยืนยันหรือ Undo ได้; มี loading/empty/error state ทุกรายการ.

## 6. Backend / API / Schema
- Schema **v2.0.0** — เปลี่ยน schema ต้องอัปเดต [API_AND_SCHEMA_DOCS.md](API_AND_SCHEMA_DOCS.md) + เทสต์.
- Route แอดมินอยู่ใต้ `/api/admin/*` และต้องตรวจรหัสผ่านเสมอ; ห้าม log รหัสผ่านหรือ `.env`.
- อุปกรณ์ที่สแกนพบใหม่: `isPlaced:false, floorIdx:null, roomNumber:"", position:null`.
- Validate input ทุก endpoint (CIDR, IP, port 1–65535); error คืน `{ error: string }` พร้อม HTTP status ที่ถูกต้อง.

## 7. Testing & Definition of Done
- [ ] `npm run build` ผ่าน · [ ] `npm test` ผ่านทั้งหมด
- [ ] เพิ่ม/ปรับเทสต์เมื่อเพิ่มฟีเจอร์หรือย้ายโค้ดที่เทสต์ตรวจสตริง
- [ ] ตรวจ Viewer และ Admin ด้วยตา ทั้ง Light/Dark และความกว้าง 375 / 768 / 1440
- [ ] อัปเดต FRS / SKILL.md หากพฤติกรรมหรือโครงสร้างเปลี่ยน

## 8. Git
- Commit แบบ Conventional Commits: `feat(viewer): …`, `fix(admin): …`, `refactor:`, `docs:`, `test:`.
- 1 commit = 1 เรื่อง; ห้าม commit `.env`, `dist/`, `node_modules/`.


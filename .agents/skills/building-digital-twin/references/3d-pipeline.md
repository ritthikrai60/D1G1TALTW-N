# 3D Modeling & CAD Pipeline Reference

> ย้ายมาจาก SKILL.md (progressive disclosure) — อ่านเมื่องานเกี่ยวกับโมเดล 3D / `.igz` / `.glb` เท่านั้น


## Source Assets
- `LUDUS_Building_No_Glass.igz` — โมเดล 3D ต้นฉบับที่รวมโครงสร้างทั้ง 4 ชั้นและดาดฟ้าสนามบาสเกตบอล
- `00-Ground_Floor-Clean.pdf` — ชั้น G ($Z = 0.00 \to 3.50\text{ m}$; เสา 77 ต้น, ที่จอดรถ, บันได ST-1/ST-2/ST-3)
- `01-First_Floor-Clean.pdf` — ชั้น 1F ($Z = 3.50 \to 7.50\text{ m}$; ซุ้มทางเข้าหลัก Portico, โถงบันไดวน, ปีกตะวันตก 8 bays, ปีกโค้งตะวันออก 13 bays)
- `02-Second_Floor-Clean.pdf` — ชั้น 2F ($Z = 7.50 \to 11.50\text{ m}$; ห้องจัดเลี้ยง, หน้าต่างโค้ง, หน้าจั่วกลาง)
- `03-Roof_Floor-Clean.pdf` — ชั้นดาดฟ้า RF ($Z = 11.50 \to 15.50\text{ m}$; ลานดาดฟ้า, สนามบาสเกตบอลฝั่งตะวันตก, ซุ้มระแนงเหล็ก, ห้องเครื่องลิฟต์, โครงถักหลังคาโค้ง)

## กฎเหล็กการปั้นโมเดล 3D (Core 3D Modeling Rules & Anti-Patterns)
1. **เสาโครงสร้าง (Pure Structural Columns)**:
   - เสาทุกต้นต้องเป็นแท่งเสาอิสระ (`Column`) ❌ ห้ามทำ 2D Boolean Union รวมผนังเข้ากับเสาจนเกิดรอยหยักขั้นบันไดรอบเสา
2. **ผนังและช่องเปิดประตู (Walls & Open Portals)**:
   - ❌ ห้ามสร้างบานประตูหรือกล่องทึบบล็อกทางเข้า ช่องเปิดประตูทั้งหมดต้องเป็น **Open Portal (เปิดโล่งทะลุผ่านได้จริง)**
3. **แผ่นพื้นอาคาร (Architectural Floor Slabs)**:
   - ❌ ห้ามทำขอบพื้นหยักบากฟันปลาเข้ามุมเสา (Zigzag Cut-Ins) ขอบแผ่นพื้นต้องเรียบตรงหรือโค้งต่อเนื่อง และครอบคลุมเสาทุกต้น 100% (`shapely.geometry.Polygon(slab_poly).is_valid == True`)
4. **การอัปเดตโมเดล `.igz` สู่เว็บ (`.igz` → `.glb` Conversion)**:
   - เมื่อผู้ใช้แก้ไขไฟล์ `LUDUS_Building_No_Glass.igz` ให้รันสคริปต์:
     ```powershell
     python scripts/build_glb_from_igz.py
     ```
   - สคริปต์จะอ่านฐานข้อมูล SQLite ภายใน `.igz` และสร้างไฟล์ `public/models/building.glb` ใหม่โดยอัตโนมัติ

---


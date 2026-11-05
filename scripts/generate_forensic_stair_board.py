import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from PIL import Image, ImageDraw, ImageFont

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
stair = layers['A-stair']

# High-resolution analysis board (2400 x 1400)
board = Image.new('RGB', (2400, 1400), (248, 250, 252))
draw = ImageDraw.Draw(board)
font_title = ImageFont.truetype('arial.ttf', 36)
font_header = ImageFont.truetype('arial.ttf', 24)
font_body = ImageFont.truetype('arial.ttf', 18)
font_code = ImageFont.truetype('arial.ttf', 15)

# Header
draw.rectangle([0, 0, 2400, 90], fill=(30, 41, 59))
draw.text((40, 25), "FORENSIC SURVEY: UPDATED STAIR ARCHITECTURE & CAD VECTORS", font=font_title, fill=(255, 255, 255))

# Panel 1: Core Stair (Left half: 40, 120, 1180, 1340)
draw.rectangle([40, 120, 1180, 1340], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
draw.rectangle([40, 120, 1180, 180], fill=(15, 118, 110))
draw.text((60, 135), "1. INTERNAL CORE STAIRCASE (ปล่องคอร์บันไดหลัก)", font=font_header, fill=(255, 255, 255))

# Paste core stair detailed map
core_map = Image.open('C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/core_stair_detailed_map.png')
core_map_resized = core_map.resize((650, 800), Image.Resampling.LANCZOS)
board.paste(core_map_resized, (60, 200))

# Notes on Core Stair
ny = 200
core_notes = [
    "• โครงสร้างบันได: U-Shape Dogleg Stair 2-3 ช่วง",
    "• Flight 1 (ทางเข้าล่าง): 4 ขั้น ก้าวไปทิศตะวันออก",
    "  - Child 43, 39, 37, 35 (X: 8.08 -> 8.93m)",
    "  - ชานพักล่างเชื่อมต่อ (Lower Landing)",
    "• Flight 2 (ขาขึ้นฝั่งขวา): 10 ขั้น ไต่ขึ้นทิศเหนือ",
    "  - Child 12, 66, 68, 70, 72, 74, 76, 78, 80, 82",
    "  - Y: -11.24m -> -9.02m (ระยะก้าว 0.25m)",
    "• Upper Half-Landing: ชานพักบนทิศเหนือ",
    "  - กว้าง 1.80m x ลึก 1.50m (Y: -8.9m -> -6.5m)",
    "• Flight 3 (ขากลับฝั่งซ้าย): 10 ขั้น ไต่ลงทิศใต้",
    "  - Child 84, 83, 81, 79, 77, 75, 73, 71, 69, 67",
    "  - ในแบบเดิมมองเห็นแค่ 4 ขั้นเพราะเส้น Zigzag Breakline",
    "  - ในเลเยอร์ CAD มีเส้นขั้นครบ 10 ขั้นทั้งสองฝั่ง!",
    "• สรุป: เป็นบันไดสมมาตร 10 + 10 ขั้น (Riser 17.5cm)",
    "  ความสูงรวม 20 x 0.175m = 3.50m พอดี Floor-to-Floor!"
]
for line in core_notes:
    col = (20, 80, 70) if "สรุป" in line or "10 +" in line else (51, 65, 85)
    f = font_header if "สรุป" in line else font_body
    draw.text((730, ny), line, font=f, fill=col)
    ny += 34

# Panel 2: South Outdoor Stair (Right half: 1220, 120, 2360, 1340)
draw.rectangle([1220, 120, 2360, 1340], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
draw.rectangle([1220, 120, 2360, 180], fill=(2, 132, 199))
draw.text((1240, 135), "2. SOUTH OUTDOOR STAIRCASE (บันไดลาดทิศใต้)", font=font_header, fill=(255, 255, 255))

south_map = Image.open('C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/south_stair_detailed_map.png')
south_map_resized = south_map.resize((1080, 540), Image.Resampling.LANCZOS)
board.paste(south_map_resized, (1250, 200))

# Notes on South Stair
sy = 760
south_notes = [
    "• จำนวนขั้น: 16 ขั้นเต็ม (Child 85 ถึง Child 100)",
    "• ทิศทางการวางตัว: วางตัวเฉียง ~7.2 องศา ตามแนวเส้นระดับภูมิประเทศ",
    "• ขอบเขตบันได:",
    "  - ขอบล่าง (West Landing): Child 101 ที่ X=3.83m, Y=-18.72m (ติดพื้น Basement)",
    "  - ขอบบน (East Landing): Child 100 ที่ X=8.89m, Y=-20.63m (เชื่อมแนวเนินเขา)",
    "  - ขอบข้างเหนือ-ใต้: Polyline Child 0 (26 จุด) และ Child 102",
    "• ตรรกะระดับความสูงสำหรับ Basement:",
    "  - เริ่มจากระดับพื้น Basement Z = 0.00m (ไม่มีขั้นใดอยู่ต่ำกว่านี้)",
    "  - ไต่ระดับขึ้น (Ascending) ไปทางทิศตะวันออก ขั้นละ +0.15m",
    "  - ขั้นที่ 16 (Child 100) ขึ้นสู่ชานพักบนที่ระดับ Z = +2.40m"
]
for line in south_notes:
    col = (3, 105, 161) if "ตรรกะ" in line else (51, 65, 85)
    f = font_header if "ตรรกะ" in line else font_body
    draw.text((1250, sy), line, font=f, fill=col)
    sy += 36

out_board_path = 'C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/stair_survey_forensic_board.png'
board.save(out_board_path, quality=95)
print(f"Saved forensic board to {out_board_path}")


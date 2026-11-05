import sys
import os
import math
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m, X0, Y0, SCALE

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Image size: 3370 x 2384
W, H = 3370, 2384
base_img = Image.new('RGB', (W, H), (250, 252, 255))
draw_base = ImageDraw.Draw(base_img)

# Style mapping for clean architectural base
style_map = [
    ('GRID', (200, 210, 225), 1, None),
    ('เส้นบาง', (215, 220, 230), 1, None),
    ('SANITARY', (180, 210, 230), 1, None),
    ('WC-OUTL', (140, 180, 210), 1, None),
    ('P-2 (0.15)', (160, 100, 180), 2, None),
    ('P-4 (0.10)', (180, 140, 60), 2, None),
    ('P-1 (0.50)', (190, 40, 40), 4, None),
    ('A-wall', (50, 55, 65), 2, None),
    ('AR_HATCH', (70, 75, 85), 2, (225, 230, 235)),
    ('A-stair', (30, 140, 60), 2, None),
    ('A-col', (230, 90, 20), 2, (255, 210, 120)),
    ('P-1', (200, 60, 60), 2, None),
]

for lname, stroke, width, fill in style_map:
    l = layers.get(lname)
    if not l: continue
    all_sp = []
    for c in l.get('kind', {}).get('children', []):
        all_sp.extend(extract_subpaths(c))
    for sp in all_sp:
        anchors = sp['anchors']
        if len(anchors) < 2: continue
        pts = [(p[0], p[1]) for p in anchors]
        is_closed = sp['closed'] or (len(pts) > 2 and pts[0] == pts[-1])
        if is_closed and fill:
            draw_base.polygon(pts, fill=fill, outline=stroke, width=width)
        else:
            draw_base.line(pts, fill=stroke, width=width)

# Now create an overlay layer for translucent zones and architectural markups
overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
draw_ov = ImageDraw.Draw(overlay)

# Fonts
font_title = ImageFont.truetype('arial.ttf', 38)
font_head = ImageFont.truetype('arial.ttf', 26)
font_body = ImageFont.truetype('arial.ttf', 20)
font_badge = ImageFont.truetype('arial.ttf', 18)
font_small = ImageFont.truetype('arial.ttf', 15)

# 1. Color zones (Semi-transparent fills)
# North Wing Zone
draw_ov.rectangle([500, 350, 2700, 880], fill=(70, 130, 180, 25), outline=(70, 130, 180, 120), width=2)
# Central Undercroft Parking Zone
draw_ov.rectangle([350, 880, 2200, 1750], fill=(240, 180, 60, 20), outline=(240, 180, 60, 100), width=2)
# South Core & Service Zone
draw_ov.rectangle([1150, 1750, 2200, 2250], fill=(220, 60, 60, 25), outline=(220, 60, 60, 120), width=2)
# South Outdoor Entrance Plaza
draw_ov.rectangle([700, 1750, 1150, 2250], fill=(46, 139, 87, 25), outline=(46, 139, 87, 120), width=2)
# East Hillside Slope & Retaining Zone
draw_ov.rectangle([2200, 880, 3100, 2250], fill=(139, 69, 19, 20), outline=(139, 69, 19, 100), width=2)

def draw_callout(draw, target_pt, box_rect, tag, title, desc_lines, color=(40, 80, 180)):
    # Draw leader line
    bx0, by0, bx1, by1 = box_rect
    # determine closest point on box to target_pt
    cx = bx0 if target_pt[0] < bx0 else (bx1 if target_pt[0] > bx1 else target_pt[0])
    cy = by0 if target_pt[1] < by0 else (by1 if target_pt[1] > by1 else target_pt[1])
    
    draw.line([target_pt, (cx, cy)], fill=color + (200,), width=2)
    # Circle at target
    r = 6
    draw.ellipse([target_pt[0]-r, target_pt[1]-r, target_pt[0]+r, target_pt[1]+r], fill=color + (230,), outline=(255, 255, 255, 255), width=2)
    
    # Draw box
    draw.rectangle(box_rect, fill=(255, 255, 255, 240), outline=color + (220,), width=2)
    # Header strip
    draw.rectangle([bx0, by0, bx1, by0 + 32], fill=color + (230,))
    # Tag & Title
    draw.text((bx0 + 10, by0 + 6), f"[{tag}] {title}", font=font_head, fill=(255, 255, 255, 255))
    
    # Content lines
    y = by0 + 40
    for line in desc_lines:
        draw.text((bx0 + 12, y), line, font=font_body, fill=(30, 35, 45, 255))
        y += 24

def draw_level_tag(draw, pt, level_str, label):
    # Architectural datum marker (Circle divided into 4 with crosshair)
    x, y = pt
    r = 18
    draw.ellipse([x-r, y-r, x+r, y+r], outline=(30, 30, 30, 220), width=2)
    # quadrants
    draw.pieslice([x-r, y-r, x+r, y+r], 0, 90, fill=(30, 30, 30, 220))
    draw.pieslice([x-r, y-r, x+r, y+r], 180, 270, fill=(30, 30, 30, 220))
    # text
    draw.text((x + r + 6, y - 18), level_str, font=font_head, fill=(200, 20, 20, 255))
    draw.text((x + r + 6, y + 4), label, font=font_small, fill=(60, 60, 70, 255))

# Elevation Level Tags
draw_level_tag(draw_ov, (1100, 1300), "+-0.00", "Undercroft Parking FFL")
draw_level_tag(draw_ov, (1500, 600), "+0.10", "North Wing Raised FFL")
draw_level_tag(draw_ov, (1450, 1900), "+0.10", "South Core Interior FFL")
draw_level_tag(draw_ov, (850, 1900), "-0.15", "Outdoor Walkway Level")
draw_level_tag(draw_ov, (2500, 2050), "-2.55", "Lower Ground Level")
draw_level_tag(draw_ov, (1320, 1600), "+3.50", "Upper Floor 1 Landing")

# Callouts
# 1. Structural Columns
draw_callout(draw_ov, (1265, 1260), [380, 930, 880, 1100], "STRUCT-01", "77 Structural Columns (RC)", [
    "• CAD Layer: A-col (57) + P-1 (20)",
    "• Grid: 8.00m x 8.00m Structural Bays",
    "• Section: 0.40m x 0.40m Reinforced Concrete",
    "• BIM Action: Extrude Z = 0.00 to +3.50m",
    "• Function: Primary gravity & seismic load path"
], color=(220, 90, 20))

# 2. Retaining Wall
draw_callout(draw_ov, (1870, 1500), [2350, 1350, 2880, 1530], "STRUCT-02", "RC Retaining Wall (0.50m)", [
    "• CAD Layer: P-1 (0.50)",
    "• Alignment: North-South Hillside retention",
    "• Thickness: 0.50m Structural RC wall",
    "• BIM Action: Extrude Z = -0.20 to +3.50m",
    "• Function: Retains earth slope on East side"
], color=(190, 30, 30))

# 3. Core Dogleg Staircase
draw_callout(draw_ov, (1270, 1680), [1350, 1420, 1900, 1620], "CIRC-01", "3-Flight Core Dogleg Stair", [
    "• CAD Layer: A-stair (Shaft interior)",
    "• Flight 1: 4 risers East -> Lower Landing (+0.86)",
    "• Flight 2: 10 risers North -> Upper Landing (+2.76)",
    "• Flight 3: 4 risers South -> Floor 1 (+3.50)",
    "• Divider: 0.90m central handrail wall",
    "• BIM Action: Riser 0.19m, Thread 0.28m, 18 Steps"
], color=(30, 140, 60))

# 4. South Cascading Outdoor Stair
draw_callout(draw_ov, (1080, 1960), [380, 2000, 920, 2180], "CIRC-02", "16-Step Cascading Terrace Stair", [
    "• CAD Layer: A-stair (South entrance)",
    "• Orientation: Angled ~7 deg with natural topography",
    "• Geometry: 16 individual 4-corner step polygons",
    "• Elevation: Descends -0.30m down to -2.55m",
    "• BIM Action: Extrude true 4-corner CAD polygons"
], color=(30, 130, 140))

# 5. North Wing Architecture
draw_callout(draw_ov, (1400, 750), [450, 420, 1000, 600], "ARCH-01", "North Wing Multi-Room Facility", [
    "• CAD Layer: AR_HATCH + A-wall (41 wall loops)",
    "• Slabs: Raised FFL +0.10m (Water barrier)",
    "• Partitions: P-2 (0.15m) & P-4 (0.10m) for WCs",
    "• Openings: Service doors & windows",
    "• BIM Action: Extrude walls Z = +0.10 to +3.50m"
], color=(70, 120, 180))

# 6. North Parking Bays
draw_callout(draw_ov, (1850, 460), [2050, 420, 2600, 580], "SITE-01", "Outdoor Parking Stall Markings", [
    "• CAD Layer: A-stair (Upper drawing zone)",
    "• Dimensions: 5.00m x 2.50m standard parking bays",
    "• Clarification: Striping lines, NOT stairs",
    "• BIM Action: Surface striping / texture at Z=0.00m"
], color=(100, 110, 130))

# Legend and Title Box at Top Left
draw_ov.rectangle([100, 80, 1200, 320], fill=(255, 255, 255, 245), outline=(40, 50, 70, 230), width=3)
draw_ov.rectangle([100, 80, 1200, 145], fill=(35, 45, 65, 255))
draw_ov.text((125, 95), "ARCHITECTURAL FLOOR PLAN & BIM TRANSLATION MATRIX", font=font_title, fill=(255, 255, 255, 255))

legend_items = [
    ("STRUCTURAL COLUMNS (77 Units)", (230, 90, 20), "A-col / P-1 | Extrude Z: 0.00 -> +3.50m"),
    ("RETAINING WALL (0.50m RC)", (190, 30, 30), "P-1 (0.50) | Extrude Z: -0.20 -> +3.50m"),
    ("CORE WALLS & SHAFTS", (70, 75, 85), "AR_HATCH | Extrude Z: +0.10 -> +3.50m"),
    ("STAIRS & CIRCULATION", (30, 140, 60), "A-stair | 3D Riser/Tread Volumetric Solid"),
    ("SLAB LEVEL CHANGES", (200, 20, 20), "FFL Datums: +-0.00 / +0.10 / -0.15 / -2.55 / +3.50"),
]

lx, ly = 125, 160
for label, color, note in legend_items:
    draw_ov.rectangle([lx, ly, lx + 24, ly + 20], fill=color + (230,), outline=(40, 40, 40, 255), width=1)
    draw_ov.text((lx + 35, ly - 2), label, font=font_head, fill=(30, 35, 45, 255))
    draw_ov.text((lx + 550, ly + 1), note, font=font_body, fill=(90, 95, 105, 255))
    ly += 28

# Combine base and overlay
final_img = Image.alpha_composite(base_img.convert('RGBA'), overlay)
out_path = 'C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/floor_plan_architectural_markup.png'
final_img.convert('RGB').save(out_path, quality=95)
print(f"Generated comprehensive architectural markup plan: {out_path}")


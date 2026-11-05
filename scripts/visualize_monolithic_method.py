import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from shapely.geometry import Polygon
import shapely.ops
from PIL import Image, ImageDraw, ImageFont
import os

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Collect columns and walls near the core shaft (where ST-1 and service core meet columns)
cols = []
for lname in ['A-col', 'P-1']:
    l = layers.get(lname)
    if not l: continue
    for i, c in enumerate(l['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4:
                try:
                    p = Polygon(pts)
                    if p.is_valid and 0.04 <= p.area <= 4.0:
                        b = p.bounds
                        # Focus on core: X in [4.0, 11.0], Y in [0.0, 10.0]
                        if 4.0 <= b[0] <= 11.0 and 0.0 <= b[1] <= 10.0:
                            cols.append((f"{lname}_{i}", p))
                except: pass

walls = []
l_wall = layers.get('A-wall')
for i, c in enumerate(l_wall['kind']['children']):
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        if len(pts) >= 4:
            try:
                p = Polygon(pts)
                if p.is_valid and p.area > 0.005:
                    b = p.bounds
                    if 4.0 <= b[0] <= 11.0 and 0.0 <= b[1] <= 10.0:
                        walls.append((f"wall_{i}", p))
            except: pass

print(f"Core area: {len(cols)} columns, {len(walls)} wall sections")

# Create a 2D rendering comparison:
# Left: Disconnected / Overlapping (Columns vs Walls separate)
# Right: Monolithic Unified (2D Boolean Union)

img_w, img_h = 1000, 800
pad = 40

# World bounds
all_shapes = [p for _, p in cols] + [p for _, p in walls]
total_bounds = shapely.ops.unary_union(all_shapes).bounds
min_x, min_y, max_x, max_y = total_bounds

scale_render = 90.0 # pixels per meter

def world_to_pix(x, y, offset_x):
    px = int(offset_x + (x - min_x) * scale_render + pad)
    py = int(img_h - ((y - min_y) * scale_render + pad))
    return (px, py)

board = Image.new('RGB', (img_w * 2 + 60, img_h + 120), (255, 255, 255))
draw = ImageDraw.Draw(board)

# Header
draw.rectangle([(0, 0), (board.width, 70)], fill=(15, 23, 42))
draw.text((30, 22), "METHODOLOGY: HOW TO INTEGRATE WALLS & COLUMNS MONOLITHICALLY", fill=(255, 255, 255))

# Subheaders
draw.rectangle([(20, 80), (img_w + 20, 115)], fill=(239, 68, 68))
draw.text((30, 88), "BEFORE: SEPARATE & OVERLAPPING (Internal Seams & Z-Fighting)", fill=(255, 255, 255))

draw.rectangle([(img_w + 40, 80), (board.width - 20, 115)], fill=(16, 185, 129))
draw.text((img_w + 50, 88), "AFTER: MONOLITHIC 2D BOOLEAN UNION (Seamless Watertight Infill)", fill=(255, 255, 255))

# Left Panel: Separate
offset_left = 20
for _, cp in cols:
    pts = [world_to_pix(x, y, offset_left) for x, y in cp.exterior.coords]
    draw.polygon(pts, fill=(219, 234, 254), outline=(37, 99, 235), width=3)

for _, wp in walls:
    pts = [world_to_pix(x, y, offset_left) for x, y in wp.exterior.coords]
    draw.polygon(pts, fill=(254, 243, 199, 128), outline=(217, 119, 6), width=2)

# Right Panel: Unified Monolithic
offset_right = img_w + 40
unified_core = shapely.ops.unary_union([p for _, p in cols] + [p for _, p in walls])

if unified_core.geom_type == 'Polygon':
    geoms = [unified_core]
else:
    geoms = unified_core.geoms

for g in geoms:
    pts = [world_to_pix(x, y, offset_right) for x, y in g.exterior.coords]
    # Solid concrete color
    draw.polygon(pts, fill=(209, 250, 229), outline=(5, 150, 105), width=3)
    # Holes
    for hole in g.interiors:
        h_pts = [world_to_pix(x, y, offset_right) for x, y in hole.coords]
        draw.polygon(h_pts, fill=(255, 255, 255), outline=(5, 150, 105), width=2)

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
out_path = os.path.join(out_dir, 'monolithic_wall_column_methodology.png')
board.save(out_path)
print(f"Saved methodology comparison image: {out_path}")


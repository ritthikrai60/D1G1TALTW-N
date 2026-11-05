import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import json

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

def poly_area(pts):
    return 0.5 * sum(pts[i][0]*pts[(i+1)%len(pts)][1] - pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))

def ensure_ccw(pts):
    if poly_area(pts) < 0:
        return pts[::-1]
    return pts

# 1. Structural Columns
acol = layers['A-col']
columns = []
for c in acol.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if len(pts) >= 4:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
            w, h = (max(xs) - min(xs))/SCALE, (max(ys) - min(ys))/SCALE
            if cy >= 900 and cx < 1650 and w < 1.5 and h < 1.5:
                pts_m = [to_m(p) for p in pts]
                if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
                pts_m = ensure_ccw(pts_m)
                columns.append({'poly': pts_m, 'center': to_m((cx, cy))})

# 2. Retaining wall P-1 (0.50)
p1_050 = layers['P-1 (0.50)']
retaining_wall = []
for c in p1_050.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if len(pts) >= 8:
            pts_m = [to_m(p) for p in pts]
            if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
            retaining_wall = ensure_ccw(pts_m)

# 3. Core Walls (AR_HATCH)
ar_hatch = layers['AR_HATCH']
core_walls = []
for c in ar_hatch.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if min(p[1] for p in pts) >= 900:
            pts_m = [to_m(p) for p in pts]
            if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
            if len(pts_m) >= 3 and abs(poly_area(pts_m)) > 0.005:
                pts_m = ensure_ccw(pts_m)
                core_walls.append(pts_m)

# 4. Restroom Partitions from P-2 and P-4 (0.10)
partitions = []
for lname in ['P-2 (0.15)', 'P-4 (0.10)']:
    l = layers.get(lname)
    if not l: continue
    for c in l.get('kind', {}).get('children', []):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if min(p[1] for p in pts) >= 900:
                pts_m = [to_m(p) for p in pts]
                if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
                if len(pts_m) >= 3 and abs(poly_area(pts_m)) > 0.01:
                    pts_m = ensure_ccw(pts_m)
                    partitions.append(pts_m)

# 5. Grand Entrance Stairs
stair = layers['A-stair']
entrance_steps = []
for idx in range(89, 105):
    c = stair['kind']['children'][idx]
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        if len(pts) == 2:
            entrance_steps.append(pts)

# 6. Slabs
south_curb = stair['kind']['children'][6]
curb_pts = [to_m(p) for p in extract_subpaths(south_curb)[0]['anchors']]
curb_reversed = curb_pts[::-1]

# Core Slab Polygon
core_slab_poly = [
    (-11.5, 1.2),
    (-11.5, 6.5),
    (-1.0, 6.5),
    (-1.0, 9.5),
    (10.7, 9.5),
    (14.3, -12.8),
    (9.5, -14.0),
    (-0.5, -14.0),
    (-0.5, 1.2),
]
core_slab_poly = ensure_ccw(core_slab_poly)

# Parking & Driveway Slab Polygon
parking_poly = [
    (-24.0, 21.0),
    (-1.0, 21.0),
    (-1.0, 9.5),
    (-1.0, 6.5),
    (-11.5, 6.5),
    (-11.5, 1.2),
    (-0.5, 1.2),
    (-0.5, -14.0),
    (3.71, -14.0),
] + curb_reversed + [
    (-24.0, -0.35),
]
parking_poly = ensure_ccw(parking_poly)

# Generate Python code string for IngeTrazo
lines = [
    "# === Pure Direct CAD Ground Floor Generation ===",
    "# Clear existing groups except Engineer",
    "for g in [x for x in list(groups) if x.name != 'Engineer']:",
    "    groups.remove(g)",
    "",
    "# Ensure layers exist",
    "layer_names = [l.name for l in layers]",
    "for lname in ['Slabs', 'Columns', 'Retaining_Wall', 'Core_Walls', 'Partitions', 'Stairs']:",
    "    if lname not in layer_names:",
    "        layers.append(Layer(lname))",
    "",
    "# 1. SLABS",
    f"parking_poly = {parking_poly}",
    "g_park_slab = extrude(parking_poly, -0.15, 0.0, name='Slab_Open_Parking', color=(0.58, 0.60, 0.63, 1.0))",
    "g_park_slab.layer = 'Slabs'",
    "",
    f"core_slab_poly = {core_slab_poly}",
    "g_core_slab = extrude(core_slab_poly, 0.0, 0.10, name='Slab_Service_Core', color=(0.88, 0.88, 0.88, 1.0))",
    "g_core_slab.layer = 'Slabs'",
    "",
    "# Entrance Landing Slab (+0.05m)",
    "g_landing = box((3.50, -18.60, -0.05), (5.50, 4.60, 0.10), name='Slab_Entrance_Landing', color=(0.82, 0.82, 0.84, 1.0))",
    "g_landing.layer = 'Slabs'",
    "",
    "# 2. RETAINING WALL P-1 (0.50m)",
    f"ret_poly = {retaining_wall}",
    "g_ret = extrude(ret_poly, 0.0, 3.50, name='RetainingWall_P1_050', color=(0.68, 0.70, 0.72, 1.0))",
    "g_ret.layer = 'Retaining_Wall'",
    "",
    "# 3. STRUCTURAL COLUMNS (41 columns)",
]

for i, col in enumerate(columns):
    poly = col['poly']
    lines.append(f"g_col_{i} = extrude({poly}, 0.0, 3.50, name='Col_{i:02d}', color=(0.88, 0.88, 0.86, 1.0))")
    lines.append(f"g_col_{i}.layer = 'Columns'")

lines.append("\n# 4. CORE WALLS (AR_HATCH)")
for i, wall in enumerate(core_walls):
    lines.append(f"g_wall_{i} = extrude({wall}, 0.10, 3.10, name='Wall_Core_{i:02d}', color=(0.92, 0.90, 0.87, 1.0))")
    lines.append(f"g_wall_{i}.layer = 'Core_Walls'")

lines.append("\n# 5. RESTROOM PARTITIONS (P-2, P-4)")
for i, part in enumerate(partitions):
    lines.append(f"g_part_{i} = extrude({part}, 0.10, 2.20, name='Partition_{i:02d}', color=(0.78, 0.82, 0.86, 1.0))")
    lines.append(f"g_part_{i}.layer = 'Partitions'")

lines.append("\n# 6. GRAND ENTRANCE STAIRS (16 steps)")
for i, step in enumerate(entrance_steps):
    p0, p1 = step[0], step[1]
    z_step = -0.05 - (0.12 * (15 - i))
    lines.append(f"box(({min(p0[0], p1[0]) - 0.15:.3f}, {min(p0[1], p1[1]) - 0.15:.3f}, {z_step:.3f}), ({abs(p1[0] - p0[0]) + 0.30:.3f}, {abs(p1[1] - p0[1]) + 0.30:.3f}, 0.15), name='Stair_Entrance_{i:02d}', color=(0.75, 0.75, 0.78, 1.0))")

lines.append("\n# 7. INTERNAL CORE STAIRS (Dogleg)")
lines.extend([
    "# Flight 1: up from 0.10m to landing 1.75m",
    "for st in range(10):",
    "    box((8.80, -11.80 + st * 0.26, 0.10 + st * 0.165), (1.10, 0.28, 0.17), name=f'Stair_Core_F1_{st}', color=(0.75, 0.75, 0.78, 1.0))",
    "# Intermediate landing",
    "box((8.80, -9.20, 1.75), (2.40, 1.20, 0.18), name='Stair_Core_Landing', color=(0.75, 0.75, 0.78, 1.0))",
    "# Flight 2: up from 1.75m to 3.50m",
    "for st in range(10):",
    "    box((10.10, -9.20 - st * 0.26, 1.75 + st * 0.165), (1.10, 0.28, 0.17), name=f'Stair_Core_F2_{st}', color=(0.75, 0.75, 0.78, 1.0))",
])

lines.extend([
    "",
    "# 8. VIEWPORT CAMERA SETUP (South-West view)",
    "viewport.camera.target = QVector3D(-5.0, 0.0, 1.5)",
    "viewport.camera.distance = 62.0",
    "viewport.camera.yaw = -0.85",
    "viewport.camera.pitch = 0.58",
    "viewport.update()",
    "print('Ground Floor built successfully! Total groups:', len(groups))",
])

full_script = "\n".join(lines)
with open('scripts/generated_ingetrazo_payload.py', 'w', encoding='utf-8') as f:
    f.write(full_script)

print("Generated full payload script:", len(lines), "lines,", len(full_script), "bytes")

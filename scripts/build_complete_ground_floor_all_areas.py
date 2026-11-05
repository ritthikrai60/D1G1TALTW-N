import sys
sys.path.insert(0, '.')
from scripts.verify_all_77_cols import unique_cols, to_m, ensure_ccw, poly_area, load_pdf_doc, extract_subpaths
from scripts.verify_extraction import curb_pts

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
stair = layers['A-stair']

# 1. Retaining wall P-1 (0.50)
p1_050 = layers['P-1 (0.50)']
retaining_wall = []
for c in p1_050.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if len(pts) >= 8:
            pts_m = [to_m(p) for p in pts]
            if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
            retaining_wall = ensure_ccw(pts_m)

# 2. South Core walls (72 loops)
core_walls_south = []
for c in layers['AR_HATCH'].get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if min(p[1] for p in pts) >= 900:
            pts_m = [to_m(p) for p in pts]
            if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
            if len(pts_m) >= 3 and abs(poly_area(pts_m)) > 0.005:
                core_walls_south.append(ensure_ccw(pts_m))

# 3. North Wing walls (41 loops)
north_walls = []
for lname in ['AR_HATCH', 'A-wall']:
    l = layers.get(lname)
    if not l: continue
    for c in l.get('kind', {}).get('children', []):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if max(p[1] for p in pts) < 900:
                pts_m = [to_m(p) for p in pts]
                if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
                if len(pts_m) >= 3 and abs(poly_area(pts_m)) > 0.01:
                    north_walls.append(ensure_ccw(pts_m))

# 4. Restroom partitions (8 loops)
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
                    partitions.append(ensure_ccw(pts_m))

# 5. Slabs
curb_reversed = curb_pts[::-1]
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

north_wing_slab = ensure_ccw([(-16.0, 21.0), (0.5, 21.0), (0.5, 43.5), (-16.0, 43.5)])
north_parking_slab = ensure_ccw([(-25.0, 21.0), (-16.0, 21.0), (-16.0, 43.5), (-25.0, 43.5)])
north_terrace_slab = ensure_ccw([(0.5, 19.5), (32.0, 19.5), (32.0, 43.5), (0.5, 43.5)])
east_slope_slab = ensure_ccw([(14.0, -10.0), (66.0, 6.0), (66.0, 22.0), (32.0, 22.0), (14.0, 9.5)])

# 6. Stairs Extraction (Forensic True CAD)
# Internal Core Stair Flight 1 (4 steps Eastward)
f1_indices = [43, 39, 37, 35]
f1_steps = []
for idx in f1_indices:
    c = stair['kind']['children'][idx]
    pts = [to_m(p) for p in extract_subpaths(c)[0]['anchors']]
    f1_steps.append(pts)

# Internal Core Stair Flight 2 (10 steps Northward along retaining wall)
f2_indices = [11, 14, 15, 16, 17, 18, 19, 20, 21, 22]
f2_steps = []
for idx in f2_indices:
    c = stair['kind']['children'][idx]
    pts = [to_m(p) for p in extract_subpaths(c)[0]['anchors']]
    f2_steps.append(pts)

# South Outdoor Cascading Staircase (16 steps Eastward down to terrain)
outdoor_steps = []
for idx in range(89, 105):
    c = stair['kind']['children'][idx]
    pts = [to_m(p) for p in extract_subpaths(c)[0]['anchors']]
    outdoor_steps.append(pts)

# Outdoor Landing Polygon (Item 105 & 106)
outdoor_landing_poly = ensure_ccw([(2.044, -16.41), (3.536, -16.242), (4.13, -21.204), (2.642, -21.384)])

# Assemble IngeTrazo script lines
lines = [
    "# === COMPLETE GROUND FLOOR & ACCURATE STAIRS GENERATION ===",
    "# Clear existing groups except Engineer",
    "for g in [x for x in list(groups) if x.name != 'Engineer']:",
    "    groups.remove(g)",
    "",
    "# Ensure layers exist",
    "layer_names = [l.name for l in layers]",
    "for lname in ['Slabs', 'Columns', 'Retaining_Wall', 'Core_Walls', 'North_Walls', 'Partitions', 'Stairs', 'Landscape']:",
    "    if lname not in layer_names:",
    "        layers.append(Layer(lname))",
    "",
    "# 1. SLABS (COMPLETE SITE AREAS)",
    f"g_park_slab = extrude({parking_poly}, -0.15, 0.0, name='Slab_Open_Parking', color=(0.58, 0.60, 0.63, 1.0))",
    "g_park_slab.layer = 'Slabs'",
    "",
    f"g_core_slab = extrude({core_slab_poly}, 0.0, 0.10, name='Slab_Service_Core', color=(0.88, 0.88, 0.88, 1.0))",
    "g_core_slab.layer = 'Slabs'",
    "",
    f"g_north_wing = extrude({north_wing_slab}, 0.0, 0.10, name='Slab_North_Wing', color=(0.85, 0.87, 0.88, 1.0))",
    "g_north_wing.layer = 'Slabs'",
    "",
    f"g_north_park = extrude({north_parking_slab}, -0.15, 0.0, name='Slab_North_Parking', color=(0.55, 0.57, 0.60, 1.0))",
    "g_north_park.layer = 'Slabs'",
    "",
    f"g_north_terrace = extrude({north_terrace_slab}, -0.15, 0.0, name='Slab_North_Terrace', color=(0.68, 0.70, 0.72, 1.0))",
    "g_north_terrace.layer = 'Slabs'",
    "",
    f"g_east_slope = extrude({east_slope_slab}, -0.20, 0.0, name='Slab_East_Slope', color=(0.62, 0.68, 0.60, 1.0))",
    "g_east_slope.layer = 'Slabs'",
    "",
    "# West Landscape Islands",
    "g_isl_s = box((-26.3, -16.5, 0.0), (2.8, 16.2, 0.15), name='Island_West_South', color=(0.45, 0.65, 0.40, 1.0))",
    "g_isl_s.layer = 'Landscape'",
    "g_isl_n = box((-22.8, 4.6, 0.0), (1.5, 5.5, 0.15), name='Island_West_North', color=(0.45, 0.65, 0.40, 1.0))",
    "g_isl_n.layer = 'Landscape'",
    "",
    "# 2. RETAINING WALL P-1 (0.50m)",
    f"ret_poly = {retaining_wall}",
    "g_ret = extrude(ret_poly, 0.0, 3.50, name='RetainingWall_P1_050', color=(0.68, 0.70, 0.72, 1.0))",
    "g_ret.layer = 'Retaining_Wall'",
    "",
    "# 3. ALL STRUCTURAL COLUMNS (77 columns verified)",
]

for i, col in enumerate(unique_cols):
    poly = col['poly']
    src = col['src']
    lines.append(f"g_col_{i} = extrude({poly}, 0.0, 3.50, name='Col_{i:02d}_{src}', color=(0.88, 0.88, 0.86, 1.0))")
    lines.append(f"g_col_{i}.layer = 'Columns'")

lines.append("\n# 4. SOUTH SERVICE CORE WALLS (72 loops)")
for i, wall in enumerate(core_walls_south):
    lines.append(f"g_wall_s_{i} = extrude({wall}, 0.10, 3.10, name='Wall_Core_{i:02d}', color=(0.92, 0.90, 0.87, 1.0))")
    lines.append(f"g_wall_s_{i}.layer = 'Core_Walls'")

lines.append("\n# 5. NORTH WING WALLS (41 loops)")
for i, wall in enumerate(north_walls):
    lines.append(f"g_wall_n_{i} = extrude({wall}, 0.10, 3.10, name='Wall_North_{i:02d}', color=(0.90, 0.90, 0.88, 1.0))")
    lines.append(f"g_wall_n_{i}.layer = 'North_Walls'")

lines.append("\n# 6. RESTROOM PARTITIONS (8 loops)")
for i, part in enumerate(partitions):
    lines.append(f"g_part_{i} = extrude({part}, 0.10, 2.20, name='Partition_{i:02d}', color=(0.78, 0.82, 0.86, 1.0))")
    lines.append(f"g_part_{i}.layer = 'Partitions'")

lines.append("\n# 7. INTERNAL CORE L-STAIR (True CAD Layout)")
# Flight 1: 4 steps going East from entrance column (8.08, -12.42)
lines.append("# Flight 1 (4 steps Eastward)")
for st, pts in enumerate(f1_steps):
    p0, p1 = pts[0], pts[1]
    z_step = 0.10 + ((st + 1) * 0.18)
    cx = (p0[0] + p1[0])/2.0
    cy = (p0[1] + p1[1])/2.0
    lines.append(f"box(({cx - 0.14:.3f}, {min(p0[1], p1[1]):.3f}, 0.10), (0.28, {abs(p1[1] - p0[1]):.3f}, {z_step - 0.10:.3f}), name='Stair_Core_F1_{st:02d}', color=(0.78, 0.78, 0.82, 1.0))")

# Intermediate L-Landing at Z = 0.82m
lines.append("\n# Intermediate L-Landing")
lines.append("box((8.70, -13.10, 0.10), (1.95, 1.85, 0.72), name='Stair_Core_L_Landing', color=(0.78, 0.78, 0.82, 1.0))")

# Flight 2: 10 steps going North from Landing along East Retaining Wall
lines.append("\n# Flight 2 (10 steps Northward along Retaining Wall)")
for st, pts in enumerate(f2_steps):
    p0, p1 = pts[0], pts[1]
    z_step = 0.82 + ((st + 1) * 0.18)
    cx = (p0[0] + p1[0])/2.0
    cy = (p0[1] + p1[1])/2.0
    lines.append(f"box(({min(p0[0], p1[0]):.3f}, {cy - 0.14:.3f}, 0.10), ({abs(p1[0] - p0[0]):.3f}, 0.28, {z_step - 0.10:.3f}), name='Stair_Core_F2_{st:02d}', color=(0.78, 0.78, 0.82, 1.0))")

# Flight 2 Upper Landing to Upper Floor Level (Z = 2.62 to 3.50m)
lines.append("box((8.88, -8.95, 0.10), (1.40, 1.50, 2.70), name='Stair_Core_Upper_Landing', color=(0.78, 0.78, 0.82, 1.0))")

lines.append("\n# 8. SOUTH OUTDOOR CASCADING STAIRCASE (True CAD Layout)")
# Top Landing connected to Parking Walkway
lines.append(f"g_out_landing = extrude({outdoor_landing_poly}, -0.15, 0.0, name='Slab_Outdoor_Stair_Landing', color=(0.75, 0.75, 0.78, 1.0))")
lines.append("g_out_landing.layer = 'Stairs'")

# 16 cascading steps descending Eastward down the terrain
lines.append("\n# 16 Cascading Steps descending Eastward (-0.30m down to -2.55m)")
for i, step in enumerate(outdoor_steps):
    p0, p1 = step[0], step[1]
    z_top = -0.15 - ((i + 1) * 0.15)
    cx = (p0[0] + p1[0])/2.0
    cy = (p0[1] + p1[1])/2.0
    lines.append(f"box(({cx - 0.15:.3f}, {min(p0[1], p1[1]):.3f}, {z_top:.3f}), (0.30, {abs(p1[1] - p0[1]):.3f}, 0.15), name='Stair_Outdoor_Step_{i:02d}', color=(0.72, 0.72, 0.76, 1.0))")

lines.extend([
    "",
    "# 9. VIEWPORT CAMERA SETUP (Perspective of Core & Stairs)",
    "viewport.camera.target = QVector3D(8.0, -10.0, 1.5)",
    "viewport.camera.distance = 45.0",
    "viewport.camera.yaw = -0.85",
    "viewport.camera.pitch = 0.60",
    "viewport.update()",
    "print('Complete model with re-interpreted stairs built successfully! Total groups:', len(groups))",
])

full_script = "\n".join(lines)
payload_path = 'scripts/generated_complete_site_payload.py'
with open(payload_path, 'w', encoding='utf-8') as f:
    f.write(full_script)

print(f"Generated clean payload: {len(lines)} lines, {len(full_script)} bytes saved to {payload_path}")

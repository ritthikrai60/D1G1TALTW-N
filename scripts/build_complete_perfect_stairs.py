import sys
sys.path.insert(0, '.')
from scripts.verify_all_77_cols import unique_cols, to_m, ensure_ccw, poly_area, load_pdf_doc, extract_subpaths
from scripts.verify_extraction import curb_pts
from scripts.test_step_polygons import outdoor_step_polys
from scripts.test_core_stair_polygons import f1_polys, f2_polys, lower_landing_poly, upper_landing_poly

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

# Outdoor Top Landing Polygon
outdoor_landing_poly = ensure_ccw([(2.044, -16.41), (3.536, -16.242), (4.13, -21.204), (2.642, -21.384)])

# Flight 3 steps (Left return flight climbing South to Floor 1 at 3.50m)
f3_polys = []
for st in range(4):
    y_start = -9.025 - (st * 0.25)
    y_end = -9.025 - ((st + 1) * 0.25)
    poly = ensure_ccw([(8.877, y_start), (9.568, y_start), (9.568, y_end), (8.877, y_end)])
    f3_polys.append(poly)

# Assemble IngeTrazo script lines
lines = [
    "# === COMPLETE GROUND FLOOR & ARCHITECTURALLY TRUE STAIRS ===",
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

lines.append("\n# 7. INTERNAL CORE 3-FLIGHT DOGLEG STAIR (True 18-Riser System to +3.50m)")
# Flight 1: 4 steps going East from entrance column (8.08, -12.42)
for st, poly in enumerate(f1_polys):
    z_top = 0.10 + ((st + 1) * 0.19)
    lines.append(f"g_f1_{st} = extrude({poly}, 0.10, {z_top:.3f}, name='Stair_Core_F1_{st:02d}', color=(0.78, 0.78, 0.82, 1.0))")
    lines.append(f"g_f1_{st}.layer = 'Stairs'")

# Lower intermediate landing (Z = 0.86m)
lines.append(f"g_l_land = extrude({lower_landing_poly}, 0.10, 0.86, name='Stair_Core_Lower_Landing', color=(0.78, 0.78, 0.82, 1.0))")
lines.append("g_l_land.layer = 'Stairs'")

# Flight 2: 10 steps climbing North along retaining wall on East side (Z = 0.86m to 2.76m)
for st, poly in enumerate(f2_polys):
    z_top = 0.86 + ((st + 1) * 0.19)
    lines.append(f"g_f2_{st} = extrude({poly}, 0.10, {z_top:.3f}, name='Stair_Core_F2_{st:02d}', color=(0.78, 0.78, 0.82, 1.0))")
    lines.append(f"g_f2_{st}.layer = 'Stairs'")

# Upper half-landing at top of Flight 2 (Z = 2.76m)
lines.append(f"g_u_land = extrude({upper_landing_poly}, 0.10, 2.76, name='Stair_Core_Upper_Landing', color=(0.78, 0.78, 0.82, 1.0))")
lines.append("g_u_land.layer = 'Stairs'")

# Flight 3: 4 steps returning South on West side up to Floor 1 (+3.50m)
for st, poly in enumerate(f3_polys):
    z_top = 2.76 + ((st + 1) * 0.185)
    lines.append(f"g_f3_{st} = extrude({poly}, 0.10, {z_top:.3f}, name='Stair_Core_F3_{st:02d}', color=(0.78, 0.78, 0.82, 1.0))")
    lines.append(f"g_f3_{st}.layer = 'Stairs'")

# Center divider / handrail stringer
lines.append("g_rail = box((9.53, -11.45, 0.86), (0.08, 2.45, 1.00), name='Stair_Core_Center_Divider', color=(0.40, 0.42, 0.45, 1.0))")
lines.append("g_rail.layer = 'Stairs'")

lines.append("\n# 8. SOUTH OUTDOOR CASCADING STAIRCASE (16 Extruded Polygons)")
# Top Landing connected to Parking Walkway
lines.append(f"g_out_landing = extrude({outdoor_landing_poly}, -0.15, 0.0, name='Slab_Outdoor_Stair_Landing', color=(0.75, 0.75, 0.78, 1.0))")
lines.append("g_out_landing.layer = 'Stairs'")

# 16 cascading steps descending Eastward down the terrain
for i, poly in enumerate(outdoor_step_polys):
    z_top = -0.15 - ((i + 1) * 0.15)
    z_bot = z_top - 0.20 # solid step block
    lines.append(f"g_out_step_{i} = extrude({poly}, {z_bot:.3f}, {z_top:.3f}, name='Stair_Outdoor_Step_{i:02d}', color=(0.72, 0.72, 0.76, 1.0))")
    lines.append(f"g_out_step_{i}.layer = 'Stairs'")

lines.extend([
    "",
    "# 9. VIEWPORT CAMERA SETUP (Focus on Stairs & Core)",
    "viewport.camera.target = QVector3D(6.5, -14.0, 0.5)",
    "viewport.camera.distance = 28.0",
    "viewport.camera.yaw = -0.75",
    "viewport.camera.pitch = 0.55",
    "viewport.update()",
    "print('Complete model with architecturally true stairs built successfully! Total groups:', len(groups))",
])

full_script = "\n".join(lines)
payload_path = 'scripts/generated_complete_site_payload.py'
with open(payload_path, 'w', encoding='utf-8') as f:
    f.write(full_script)

print(f"Generated clean payload: {len(lines)} lines, {len(full_script)} bytes saved to {payload_path}")


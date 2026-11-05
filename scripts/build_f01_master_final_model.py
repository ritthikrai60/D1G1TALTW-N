import math
import json
import pypdf
from shapely.geometry import Polygon

# 1. LOAD F01 COLUMNS
reader = pypdf.PdfReader(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf')
data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
doc = json.loads(data.decode('utf-8'))['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

def get_subpaths(c):
    res = []
    if not isinstance(c, dict): return res
    kind = c.get('kind', {})
    if isinstance(kind, dict):
        if kind.get('type') == 'path' and 'path' in kind:
            res.extend(kind['path'].get('subpaths', []))
        if 'children' in kind:
            for ch in kind['children']: res.extend(get_subpaths(ch))
    if 'children' in c:
        for ch in c['children']: res.extend(get_subpaths(ch))
    return res

col_polys = []
for lname in ['A-col', '01-AE-Floor Post', 'P-1']:
    l = next((x for x in doc['layers'] if x['name'] == lname), None)
    if not l: continue
    for c in l['kind']['children']:
        for sp in get_subpaths(c):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) >= 4:
                try:
                    p = Polygon(pts)
                    if p.is_valid and 0.04 <= p.area <= 3.0:
                        xs = [pt[0] for pt in pts]
                        ys = [pt[1] for pt in pts]
                        dx, dy = max(xs) - min(xs), max(ys) - min(ys)
                        if 0.20 <= dx <= 2.2 and 0.20 <= dy <= 2.2:
                            col_polys.append(p)
                except: pass

unique_cols = []
seen = set()
for cp in col_polys:
    cx, cy = round(cp.centroid.x, 2), round(cp.centroid.y, 2)
    if (cx, cy) not in seen:
        seen.add((cx, cy))
        unique_cols.append(cp)

print(f"Loaded {len(unique_cols)} unique columns for Floor 01.")

# 2. LOAD F00 COLUMNS
with open('scripts/checkpoint_basement_v3_perfect_slab.py', 'r', encoding='utf-8') as f:
    f00_text = f.read()

import re
f00_col_matches = re.findall(r'extrude\(\[([^\]]+)\].*?name=\'(Structural_Column_\d+|Monolithic_Assembly_\d+)\'', f00_text)
f00_cols = []
for pts_str, cname in f00_col_matches:
    pts = eval(f"[{pts_str}]")
    f00_cols.append((cname, pts))

print(f"Loaded {len(f00_cols)} columns for Floor 00.")

# 3. F01 & F00 PERFECT CONTINUOUS SLAB (ZERO NOTCHES)
perfect_slab_pts = [
    (-26.5, 44.0),
    (-26.5, -17.5),
    (3.5, -17.5),
    (3.5, -22.5),
    (10.5, -22.5),
    (10.5, -18.0),
    (17.5, -18.0),
    (22.5, -14.5),
    (32.0, -10.0),
    (42.5, -6.0),
    (53.0, -1.5),
    (66.5, 5.0),
    (68.0, 8.0),
    (68.0, 23.0),
    (33.0, 23.0),
    (33.0, 44.0),
    (-26.5, 44.0)
]

payload = [
    "# === COMPLETE MASTER STRUCTURAL & ALL-STAIR MODEL (FLOOR 00 & FLOOR 01) ===",
    "# Strictly: NO WALLS, NO DOORS. Columns + Continuous Slabs + All 10 Authenticated Stairs.",
    "groups.clear()",
    "",
    "layer_names = [l.name for l in layers]",
    "for lname in ['F00_Structure', 'F01_Structure', 'Slabs', 'Stairs']:",
    "    if lname not in layer_names:",
    "        layers.append(Layer(lname))",
    "",
    "def make_box_prism(center_x, center_y, width, depth, z_bottom, z_top, angle_deg, name, color=(0.85, 0.82, 0.78, 1.0)):",
    "    rad = math.radians(angle_deg)",
    "    c, s = math.cos(rad), math.sin(rad)",
    "    hw, hd = width / 2.0, depth / 2.0",
    "    corners = [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)]",
    "    rot_pts = [(round(center_x + x * c - y * s, 3), round(center_y + x * s + y * c, 3)) for x, y in corners]",
    "    g = extrude(rot_pts, z_bottom, z_top, name=name, color=color)",
    "    g.layer = 'Stairs'",
    "    return g",
    "",
    "# -------------------------------------------------------------------------",
    "# FLOOR 00 (GROUND FLOOR: Z = 0.00m to 3.50m)",
    "# -------------------------------------------------------------------------",
    f"g_f00_slab = extrude({perfect_slab_pts}, -0.25, 0.00, name='F00_Ground_Slab', color=(0.70, 0.72, 0.75, 1.0))",
    "g_f00_slab.layer = 'Slabs'",
    ""
]

# F00 Columns
for i, (cname, pts) in enumerate(f00_cols):
    poly_pts = [(round(p[0], 3), round(p[1], 3)) for p in pts]
    payload.append(f"c0_{i} = extrude({poly_pts}, 0.00, 3.50, name='F00_{cname}', color=(0.82, 0.80, 0.78, 1.0))")
    payload.append(f"c0_{i}.layer = 'F00_Structure'")

# F01 Slab & Columns
payload.extend([
    "",
    "# -------------------------------------------------------------------------",
    "# FLOOR 01 (FIRST FLOOR: Z = 3.50m to 7.50m)",
    "# -------------------------------------------------------------------------",
    f"g_f01_slab = extrude({perfect_slab_pts}, 3.30, 3.50, name='F01_Floor_Slab', color=(0.78, 0.80, 0.82, 1.0))",
    "g_f01_slab.layer = 'Slabs'",
    ""
])

for i, cp in enumerate(unique_cols):
    pts = [(round(x, 3), round(y, 3)) for x, y in cp.exterior.coords[:-1]]
    payload.append(f"c1_{i} = extrude({pts}, 3.50, 7.50, name='F01_COL_{i+1:02d}', color=(0.90, 0.88, 0.86, 1.0))")
    payload.append(f"c1_{i}.layer = 'F01_Structure'")

# -------------------------------------------------------------------------
# ALL 10 STAIR SYSTEMS
# -------------------------------------------------------------------------
payload.extend([
    "",
    "# =========================================================================",
    "# 1. STAIR 3 (บันได 3: MAIN NORTH CORE CIRCULATION SHAFT)",
    "# Width = 3.25m, Flight width = 1.50m, North Mid-Landing, Tilted -4.5 deg",
    "# ========================================================================="
])

cos_st3 = math.cos(math.radians(-4.5))
sin_st3 = math.sin(math.radians(-4.5))

# F00 East Flight: South -> North UP (Z: 0.00 -> 1.75m)
for s in range(11):
    z_step = round((s + 1) * 0.160, 3)
    dist = s * 0.25
    cx = 8.65 - dist * sin_st3
    cy = 3.10 + dist * cos_st3
    payload.append(f"make_box_prism({cx:.3f}, {cy:.3f}, 1.50, 0.25, 0.00, {z_step:.3f}, -4.5, 'ST3_F00_East_Step_{s+1}')")

# North Mid-Landing (Z = 1.75m)
payload.append("make_box_prism(7.85, 7.50, 3.25, 1.60, 1.55, 1.75, -4.5, 'ST3_Mid_Landing_F00', color=(0.80, 0.78, 0.75, 1.0))")

# F00 West Flight: North -> South UP to F01 (Z: 1.75 -> 3.50m)
for s in range(11):
    z_step = round(1.75 + (s + 1) * 0.160, 3)
    dist = s * 0.25
    cx = 7.05 + dist * sin_st3
    cy = 5.85 - dist * cos_st3
    payload.append(f"make_box_prism({cx:.3f}, {cy:.3f}, 1.50, 0.25, 1.75, {z_step:.3f}, -4.5, 'ST3_F00_West_Step_{s+1}')")

# F01 South Landing (Z = 3.50m)
payload.append("make_box_prism(7.85, 2.80, 3.25, 1.50, 3.30, 3.50, -4.5, 'ST3_F01_South_Landing', color=(0.80, 0.78, 0.75, 1.0))")

# F01 Upper East Flight: South -> North UP to F02 (Z: 3.50 -> 5.25m)
for s in range(11):
    z_step = round(3.50 + (s + 1) * 0.160, 3)
    dist = s * 0.25
    cx = 8.65 - dist * sin_st3
    cy = 3.10 + dist * cos_st3
    payload.append(f"make_box_prism({cx:.3f}, {cy:.3f}, 1.50, 0.25, 3.50, {z_step:.3f}, -4.5, 'ST3_F01_East_Step_{s+1}')")

# F01 Upper Mid-Landing (Z = 5.25m)
payload.append("make_box_prism(7.85, 7.50, 3.25, 1.60, 5.05, 5.25, -4.5, 'ST3_Upper_Mid_Landing', color=(0.80, 0.78, 0.75, 1.0))")

# F01 Upper West Flight: North -> South UP to F02 (Z: 5.25 -> 7.00m)
for s in range(11):
    z_step = round(5.25 + (s + 1) * 0.160, 3)
    dist = s * 0.25
    cx = 7.05 + dist * sin_st3
    cy = 5.85 - dist * cos_st3
    payload.append(f"make_box_prism({cx:.3f}, {cy:.3f}, 1.50, 0.25, 5.25, {z_step:.3f}, -4.5, 'ST3_F02_West_Step_{s+1}')")

# -------------------------------------------------------------------------
# 2. STAIR 1 / ST-2 (บันไดโถงแกนใต้ข้าง LOCKER)
# SINGLE STRAIGHT FLIGHT ON FLOOR 01 (17 treads, South -> North UP to F01)
# -------------------------------------------------------------------------
payload.extend([
    "",
    "# =========================================================================",
    "# 2. STAIR 1 / ST-2 (SOUTH LOCKER STAIR: SINGLE STRAIGHT FLIGHT)",
    "# 17 Treads running South to North, Width = 1.52m, Tilted 9.3 degrees",
    "# ========================================================================="
])

cos_st1 = math.cos(math.radians(9.3))
sin_st1 = math.sin(math.radians(9.3))

for s in range(17):
    z_step = round((s + 1) * (3.50 / 17.0), 3)
    dist = s * 0.28
    cx = 9.83 - dist * sin_st1
    cy = -12.40 + dist * cos_st1
    payload.append(f"make_box_prism({cx:.3f}, {cy:.3f}, 1.52, 0.28, 0.00, {z_step:.3f}, 9.3, 'ST1_Straight_Step_{s+1:02d}')")

# ST-1 Upper Landing (Z = 3.50m)
cx_land = 9.83 - 17 * 0.28 * sin_st1
cy_land = -12.40 + 17 * 0.28 * cos_st1
payload.append(f"make_box_prism({cx_land:.3f}, {cy_land:.3f}, 1.52, 1.50, 3.30, 3.50, 9.3, 'ST1_Arrival_Landing', color=(0.80, 0.78, 0.75, 1.0))")

# -------------------------------------------------------------------------
# 3. SOUTH PORTICO ENTRANCE STEPS (ST-2)
# West-to-East 17 steps, 5.59m run + 3 facade porch steps
# -------------------------------------------------------------------------
payload.extend([
    "",
    "# =========================================================================",
    "# 3. SOUTH PORTICO MAIN ENTRANCE STEPS & FACADE PORCH STEPS",
    "# Dimension 5,590mm: Steps West-to-East UP along X (17 treads)",
    "# =========================================================================",
    "portico_treads = 17",
    "dx_step = 5.59 / portico_treads",
    "for s in range(portico_treads):",
    "    z_step = round((s + 1) * (3.50 / portico_treads), 3)",
    "    x_pos = 3.50 + s * dx_step",
    "    make_box_prism(x_pos, -20.00, dx_step, 4.20, 0.00, z_step, 0.0, f'Portico_Step_{s+1:02d}', color=(0.85, 0.82, 0.79, 1.0))",
    "",
    "# Facade Porch Continuous Steps along front columns (3 tiers)",
    "for s in range(3):",
    "    z_step = round(3.50 - (s + 1) * 0.15, 3)",
    "    y_pos = -17.50 - s * 0.35",
    "    make_box_prism(15.00, y_pos, 16.00, 0.35, z_step, 3.50, 5.0, f'Facade_Porch_Step_{s+1:02d}', color=(0.83, 0.80, 0.77, 1.0))"
])

# -------------------------------------------------------------------------
# 4. LOBBY GRAND CURVED STAIR (A6-01)
# Rin = 1.25m, Rout = 2.50m, 16 treads on bottom 200 deg arc
# -------------------------------------------------------------------------
payload.extend([
    "",
    "# =========================================================================",
    "# 4. LOBBY GRAND CURVED STAIR (A6-01: Rin = 1.25m, Rout = 2.50m)",
    "# Center: (22.80, -4.20), bottom 200 deg arc, counter-clockwise to mezzanine",
    "# =========================================================================",
    "cx_sp, cy_sp = 22.80, -4.20",
    "r_in, r_out = 1.25, 2.50",
    "num_spiral_steps = 16",
    "total_angle = 200.0",
    "start_angle = -15.0",
    "d_ang = total_angle / num_spiral_steps",
    "for s in range(num_spiral_steps):",
    "    a1 = math.radians(start_angle + s * d_ang)",
    "    a2 = math.radians(start_angle + (s + 1.08) * d_ang)",
    "    z_b = round(3.50 + s * 0.20, 3)",
    "    z_t = round(z_b + 0.12, 3)",
    "    p1 = (round(cx_sp + r_in * math.cos(a1), 3), round(cy_sp + r_in * math.sin(a1), 3))",
    "    p2 = (round(cx_sp + r_out * math.cos(a1), 3), round(cy_sp + r_out * math.sin(a1), 3))",
    "    p3 = (round(cx_sp + r_out * math.cos(a2), 3), round(cy_sp + r_out * math.sin(a2), 3))",
    "    p4 = (round(cx_sp + r_in * math.cos(a2), 3), round(cy_sp + r_in * math.sin(a2), 3))",
    "    tread = extrude([p1, p2, p3, p4], z_b, z_t, name=f'Lobby_Spiral_Tread_{s+1:02d}', color=(0.88, 0.84, 0.80, 1.0))",
    "    tread.layer = 'Stairs'",
    "ang_land = math.radians(start_angle + total_angle)",
    "px_land, py_land = cx_sp + r_out * math.cos(ang_land), cy_sp + r_out * math.sin(ang_land)",
    "make_box_prism(px_land - 0.5, py_land, 2.20, 2.20, 6.50, 6.70, 15.0, 'Lobby_Mezzanine_Landing', color=(0.82, 0.80, 0.78, 1.0))"
])

# -------------------------------------------------------------------------
# 5. FOYER GRAND FAN-SHAPED AMPHITHEATER STEPS (บันได 4)
# -------------------------------------------------------------------------
payload.extend([
    "",
    "# =========================================================================",
    "# 5. FOYER GRAND FAN-SHAPED AMPHITHEATER STEPS (บันได 4)",
    "# Center: (19.50, 1.50), Radiating outward from 2.40m to 4.80m, 10 fan steps",
    "# =========================================================================",
    "cx_fan, cy_fan = 19.50, 1.50",
    "fan_treads = 10",
    "fan_ang_span = 80.0",
    "fan_start_ang = 40.0",
    "for s in range(fan_treads):",
    "    r_t = 2.40 + s * 0.24",
    "    r_t_next = r_t + 0.25",
    "    z_step = round(3.50 + s * 0.10, 3)",
    "    arc_pts = []",
    "    for k in range(9):",
    "        ang = math.radians(fan_start_ang + k * (fan_ang_span / 8))",
    "        arc_pts.append((round(cx_fan + r_t_next * math.cos(ang), 3), round(cy_fan + r_t_next * math.sin(ang), 3)))",
    "    for k in range(8, -1, -1):",
    "        ang = math.radians(fan_start_ang + k * (fan_ang_span / 8))",
    "        arc_pts.append((round(cx_fan + r_t * math.cos(ang), 3), round(cy_fan + r_t * math.sin(ang), 3)))",
    "    g_fan = extrude(arc_pts, 3.50, z_step, name=f'Foyer_Fan_Step_{s+1:02d}', color=(0.84, 0.82, 0.79, 1.0))",
    "    g_fan.layer = 'Stairs'"
])

# -------------------------------------------------------------------------
# 6. EAST WING NORTH WALL STAIR (10 STEPS)
# -------------------------------------------------------------------------
payload.extend([
    "",
    "# =========================================================================",
    "# 6. EAST WING NORTH WALL STAIR (10 steps along wall tilted 33 deg)",
    "# Center: (53.49, 18.06), Width = 1.23m",
    "# ========================================================================="
])

for s in range(10):
    z_step = round(3.50 + (s + 1) * 0.175, 3)
    dist = s * 0.28
    cx_e = 52.0 + dist * math.cos(math.radians(33.0))
    cy_e = 16.0 + dist * math.sin(math.radians(33.0))
    payload.append(f"make_box_prism({cx_e:.3f}, {cy_e:.3f}, 1.23, 0.28, 3.50, {z_step:.3f}, 33.0, f'East_Wing_North_Step_{s+1:02d}', color=(0.85, 0.82, 0.78, 1.0))")

# -------------------------------------------------------------------------
# 7. EAST WING KITCHEN SERVICE STEPS & EXTERIOR TERRACE STEPS
# -------------------------------------------------------------------------
payload.extend([
    "",
    "# =========================================================================",
    "# 7. EAST WING KITCHEN SERVICE STEPS & EXTERIOR CURVED TERRACE STEPS",
    "# ========================================================================="
])

# Kitchen service steps (9 steps)
for s in range(9):
    z_step = round(3.85 - (s + 1) * 0.10, 3)
    dist = s * 0.28
    cx_k = 61.49 + dist * math.cos(math.radians(33.0 - 90.0))
    cy_k = 9.66 + dist * math.sin(math.radians(33.0 - 90.0))
    payload.append(f"make_box_prism({cx_k:.3f}, {cy_k:.3f}, 1.57, 0.28, {z_step:.3f}, 3.85, 33.0, f'Kitchen_Service_Step_{s+1:02d}', color=(0.82, 0.80, 0.77, 1.0))")

# Exterior Curved Terrace Steps (6 steps at southeast tip)
for s in range(6):
    z_step = round(3.50 - (s + 1) * 0.18, 3)
    dist = s * 0.35
    cx_t = 64.50 + dist * math.cos(math.radians(45.0))
    cy_t = 3.50 - dist * math.sin(math.radians(45.0))
    payload.append(f"make_box_prism({cx_t:.3f}, {cy_t:.3f}, 3.50, 0.35, {z_step:.3f}, 3.50, 45.0, f'East_Terrace_Ext_Step_{s+1:02d}', color=(0.80, 0.78, 0.75, 1.0))")

# -------------------------------------------------------------------------
# 8. WEST WING MMA / GYM GRAND STEPS (2 FLIGHTS, WIDTH 4.55M)
# -------------------------------------------------------------------------
payload.extend([
    "",
    "# =========================================================================",
    "# 8. WEST WING MMA / GYM GRAND ACCESS STEPS (2 flights, Width = 4.55m each)",
    "# Centers: (-14.41, 20.94) and (-4.45, 20.15)",
    "# ========================================================================="
])

for f_idx, cx_base in [(1, -14.41), (2, -4.45)]:
    for s in range(4):
        z_step = round(2.50 + (s + 1) * 0.25, 3)
        y_pos = 20.00 + s * 0.35
        payload.append(f"make_box_prism({cx_base}, {y_pos:.3f}, 4.55, 0.35, 2.50, {z_step:.3f}, -4.5, f'Gym_Grand_Flight{f_idx}_Step_{s+1:02d}', color=(0.86, 0.83, 0.80, 1.0))")

# -------------------------------------------------------------------------
# 9. GYM NORTH WALL MEZZANINE STAIR
# -------------------------------------------------------------------------
payload.extend([
    "",
    "# =========================================================================",
    "# 9. GYM NORTH WALL MEZZANINE STAIR",
    "# Straight flight climbing North UP to upper concourse",
    "# ========================================================================="
])

for s in range(12):
    z_step = round(2.00 + (s + 1) * 0.165, 3)
    y_pos = 23.00 + s * 0.28
    payload.append(f"make_box_prism(-0.35, {y_pos:.3f}, 1.20, 0.28, 2.00, {z_step:.3f}, 0.0, f'Gym_Mezzanine_Step_{s+1:02d}', color=(0.84, 0.81, 0.78, 1.0))")

# -------------------------------------------------------------------------
# 10. NORTH OUTDOOR RESTROOM ENTRANCE STEPS
# -------------------------------------------------------------------------
payload.extend([
    "",
    "# =========================================================================",
    "# 10. NORTH OUTDOOR RESTROOM ENTRANCE STEPS (3 steps, Width = 1.80m)",
    "# Center: (32.20, 32.75)",
    "# ========================================================================="
])

for s in range(3):
    z_step = round(3.50 + (s + 1) * 0.15, 3)
    y_pos = 32.30 + s * 0.30
    payload.append(f"make_box_prism(32.20, {y_pos:.3f}, 1.80, 0.30, 3.50, {z_step:.3f}, 0.0, f'North_Restroom_Step_{s+1:02d}', color=(0.83, 0.80, 0.77, 1.0))")

with open('scripts/f01_master_final_payload.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(payload))

print(f"Generated scripts/f01_master_final_payload.py successfully ({len(payload)} lines).")


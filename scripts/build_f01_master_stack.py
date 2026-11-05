import math
import json
import pypdf
from shapely.geometry import Polygon

# 1. LOAD F01 COLUMNS
reader = pypdf.PdfReader('01-First_Floor-Clean.pdf')
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

print(f"Extracted {len(unique_cols)} unique columns for Floor 01.")

# 2. LOAD F00 COLUMNS FOR STACKING
with open('scripts/checkpoint_basement_v3_perfect_slab.py', 'r', encoding='utf-8') as f:
    f00_text = f.read()

import re
f00_col_matches = re.findall(r'extrude\(\[([^\]]+)\].*?name=\'(Structural_Column_\d+|Monolithic_Assembly_\d+)\'', f00_text)
f00_cols = []
for pts_str, cname in f00_col_matches:
    pts = eval(f"[{pts_str}]")
    f00_cols.append((cname, pts))

print(f"Extracted {len(f00_cols)} columns for Floor 00.")

# 3. F01 PERFECT CONTINUOUS SLAB (ZERO NOTCHES)
f01_slab_pts = [
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

# Generate Python script for IngeTrazo
payload_lines = [
    "# === MASTER MULTI-FLOOR STACK (F00 & F01) WITH ACCURATE STAIRS & ZERO-NOTCH SLABS ===",
    "# Strictly: NO WALLS, NO DOORS. Standalone columns, continuous slabs, authentic stairs.",
    "groups.clear()",
    "",
    "layer_names = [l.name for l in layers]",
    "for lname in ['F00_Structure', 'F01_Structure', 'Slabs', 'Stairs']:",
    "    if lname not in layer_names:",
    "        layers.append(Layer(lname))",
    "",
    "# ==========================================================================",
    "# LEVEL 00 (GROUND FLOOR / BASEMENT: Z = 0.00m to 3.50m)",
    "# ==========================================================================",
    "# F00 Slab (Z: -0.25 to 0.00m)",
    f"g_f00_slab = extrude({f01_slab_pts}, -0.25, 0.00, name='F00_Ground_Slab', color=(0.70, 0.72, 0.75, 1.0))",
    "g_f00_slab.layer = 'Slabs'",
    ""
]

# Add F00 Columns (Z: 0.00 to 3.50m)
payload_lines.append("# F00 Structural Columns (Z: 0.00 -> 3.50m)")
for i, (cname, pts) in enumerate(f00_cols):
    poly_pts = [(round(p[0], 3), round(p[1], 3)) for p in pts]
    payload_lines.append(f"c0_{i} = extrude({poly_pts}, 0.00, 3.50, name='F00_{cname}', color=(0.82, 0.80, 0.78, 1.0))")
    payload_lines.append(f"c0_{i}.layer = 'F00_Structure'")

payload_lines.extend([
    "",
    "# ==========================================================================",
    "# LEVEL 01 (FIRST FLOOR: Z = 3.50m to 7.50m)",
    "# ==========================================================================",
    "# F01 Slab (Z: 3.30 to 3.50m) - Continuous flat slab, ZERO notches",
    f"g_f01_slab = extrude({f01_slab_pts}, 3.30, 3.50, name='F01_Floor_Slab', color=(0.78, 0.80, 0.82, 1.0))",
    "g_f01_slab.layer = 'Slabs'",
    "",
    "# F01 Structural Columns (Z: 3.50 -> 7.50m, Height = 4.00m)"
])

# Add F01 Columns (Z: 3.50 to 7.50m)
for i, cp in enumerate(unique_cols):
    pts = [(round(x, 3), round(y, 3)) for x, y in cp.exterior.coords[:-1]]
    payload_lines.append(f"c1_{i} = extrude({pts}, 3.50, 7.50, name='F01_COL_{i+1:02d}', color=(0.90, 0.88, 0.86, 1.0))")
    payload_lines.append(f"c1_{i}.layer = 'F01_Structure'")

# ==========================================================================
# STAIRS
# ==========================================================================
payload_lines.extend([
    "",
    "# ==========================================================================",
    "# ACCURATE STAIR SYSTEMS",
    "# ==========================================================================",
    "# 1. CORE FIRE STAIR ST-1 (Connecting F00 -> F01 and F01 -> F02)",
    "# Orientation tilted along structural grid (-9.17 degrees)",
    "# Lower Flight (F00 -> Mid-Landing, Z: 0.00 -> 1.75m)"
])

# Flight 1: F00 -> Landing (10 steps)
# Stairwell bounds approx: X in [8.0, 11.5], Y in [-13.5, -8.0]
cos_th = math.cos(math.radians(-9.17))
sin_th = math.sin(math.radians(-9.17))

# Step builder helper along grid
payload_lines.append("""
def make_box_prism(center_x, center_y, width, depth, z_bottom, z_top, angle_deg, name, color=(0.85, 0.82, 0.78, 1.0)):
    rad = math.radians(angle_deg)
    c, s = math.cos(rad), math.sin(rad)
    hw, hd = width / 2.0, depth / 2.0
    corners = [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)]
    rot_pts = [(round(center_x + x * c - y * s, 3), round(center_y + x * s + y * c, 3)) for x, y in corners]
    g = extrude(rot_pts, z_bottom, z_top, name=name, color=color)
    g.layer = 'Stairs'
    return g
""")

# ST-1 Lower Flight (F00 -> Mid-Landing, Z: 0.00 to 1.75m, 10 risers)
payload_lines.append("# ST-1 Lower Flight (F00 -> Mid-Landing)")
for s in range(10):
    z_bot = 0.00
    z_step = round((s + 1) * 0.175, 3)
    dist = s * 0.28
    cx = 8.80 - dist * sin_th
    cy = -12.50 + dist * cos_th
    payload_lines.append(f"make_box_prism({cx:.3f}, {cy:.3f}, 1.35, 0.28, 0.00, {z_step:.3f}, -9.17, 'ST1_F00_Step_{s+1}')")

# ST-1 Mid-Landing (Z = 1.75m)
payload_lines.append("make_box_prism(9.60, -9.60, 2.90, 1.40, 1.55, 1.75, -9.17, 'ST1_Mid_Landing', color=(0.80, 0.78, 0.75, 1.0))")

# ST-1 Upper Flight (Mid-Landing -> F01, Z: 1.75 to 3.50m, 10 risers)
payload_lines.append("# ST-1 Upper Flight (Mid-Landing -> F01 Arrival)")
for s in range(10):
    z_step = round(1.75 + (s + 1) * 0.175, 3)
    dist = s * 0.28
    cx = 10.35 + dist * sin_th
    cy = -9.90 - dist * cos_th
    payload_lines.append(f"make_box_prism({cx:.3f}, {cy:.3f}, 1.35, 0.28, 1.75, {z_step:.3f}, -9.17, 'ST1_F01_Step_{s+1}')")

# ST-1 F01 Arrival Landing (Z = 3.50m)
payload_lines.append("make_box_prism(9.60, -13.00, 2.90, 1.40, 3.30, 3.50, -9.17, 'ST1_F01_Arrival_Landing', color=(0.80, 0.78, 0.75, 1.0))")

# 2. LOBBY GRAND CURVED/SPIRAL STAIR (Ascends from F01 Z = 3.50m to Mezzanine Z = 6.70m)
payload_lines.extend([
    "",
    "# 2. LOBBY GRAND CURVED/SPIRAL STAIR (Z: 3.50m -> 6.70m)",
    "# Center: (22.80, -4.20), Rin = 0.85m, Rout = 2.45m, 16 cantilevered treads",
    "cx_sp, cy_sp = 22.80, -4.20",
    "r_in, r_out = 0.85, 2.45",
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
    "# Upper Mezzanine Landing Platform",
    "ang_land = math.radians(start_angle + total_angle)",
    "px_land, py_land = cx_sp + r_out * math.cos(ang_land), cy_sp + r_out * math.sin(ang_land)",
    "make_box_prism(px_land - 0.5, py_land, 2.20, 2.20, 6.50, 6.70, 15.0, 'Lobby_Mezzanine_Landing', color=(0.82, 0.80, 0.78, 1.0))"
])

# 3. FOYER GRAND FAN-SHAPED AMPHITHEATER STEPS (Z: 3.50m -> 4.50m)
payload_lines.extend([
    "",
    "# 3. FOYER GRAND FAN-SHAPED AMPHITHEATER STEPS (Z: 3.50m -> 4.50m)",
    "# Center: (19.50, 1.50), Radiating outward from 2.40m to 4.80m",
    "cx_fan, cy_fan = 19.50, 1.50",
    "fan_treads = 10",
    "fan_ang_span = 80.0",
    "fan_start_ang = 40.0",
    "for s in range(fan_treads):",
    "    r_t = 2.40 + s * 0.24",
    "    r_t_next = r_t + 0.25",
    "    z_step = round(3.50 + s * 0.10, 3)",
    "    # Generate arc polygon with 8 points",
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

# 4. SOUTH PORTICO ENTRANCE STEPS (ST-2) (Z: 0.00m to 3.50m entrance terrace)
payload_lines.extend([
    "",
    "# 4. SOUTH PORTICO ENTRANCE STEPS (ST-2: Z: 0.00m -> 3.50m terrace)",
    "# Center: (7.0, -20.0), Width 6.0m, 14 steps stepping South to North",
    "for s in range(14):",
    "    z_step = round((s + 1) * 0.25, 3)",
    "    y_pos = -22.50 + s * 0.35",
    "    make_box_prism(7.00, y_pos, 6.00, 0.35, 0.00, z_step, 0.0, f'South_Portico_Step_{s+1:02d}', color=(0.85, 0.82, 0.79, 1.0))"
])

# 5. EAST WING FIRE STAIR (Z: 3.50m -> 7.50m)
payload_lines.extend([
    "",
    "# 5. EAST WING FIRE STAIR (Z: 3.50m -> 7.50m, Tilted 33 degrees)",
    "# Center: (59.0, 13.0)",
    "for s in range(12):",
    "    z_step = round(3.50 + (s + 1) * 0.175, 3)",
    "    dist = s * 0.28",
    "    cx_e = 58.0 + dist * math.cos(math.radians(33.0))",
    "    cy_e = 12.0 + dist * math.sin(math.radians(33.0))",
    "    make_box_prism(cx_e, cy_e, 1.30, 0.28, 3.50, z_step, 33.0, f'East_Wing_Step_{s+1:02d}', color=(0.85, 0.82, 0.78, 1.0))"
])

with open('scripts/f01_master_stack_payload.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(payload_lines))

print(f"Generated scripts/f01_master_stack_payload.py successfully ({len(payload_lines)} lines).")


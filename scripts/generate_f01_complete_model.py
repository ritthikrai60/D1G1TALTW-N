import json
import math
import numpy as np

# Load 64 columns
with open('scripts/f01_columns.json', 'r') as f:
    cols_data = json.load(f)

# Load candidate clean slab
import zlib, re, sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round(float((pt[0] - X0) / SCALE), 3), round(float(-(pt[1] - Y0) / SCALE), 3))

l_p2_15 = next((x for x in doc['layers'] if x['name'] == 'P-2 (0.15)'), None)
c75_pts = [to_m(p) for p in extract_subpaths(l_p2_15['kind']['children'][75])[0]['anchors']]

south_west_curve = [p for p in c75_pts if p[1] < -15.5]
south_west_curve.sort(key=lambda p: -p[0])
clean_sw_curve = []
for p in south_west_curve:
    if not clean_sw_curve or math.hypot(p[0]-clean_sw_curve[-1][0], p[1]-clean_sw_curve[-1][1]) > 0.5:
        clean_sw_curve.append(p)

slab_poly = [
    (-26.5, 44.0),
    (-26.5, -18.0),
]
for p in clean_sw_curve[::-1]:
    slab_poly.append((round(float(p[0]), 3), round(float(p[1]) - 0.5, 3)))
slab_poly.extend([
    (3.71, -22.5),
    (10.0, -22.5),
    (68.0, 5.0),
    (68.0, 23.0),
    (33.0, 23.0),
    (33.0, 44.0),
    (-26.5, 44.0)
])

# Write standalone payload script
code = []
code.append("# === FLOOR 01 PURE MODEL (NO WALLS, NO DOORS) ===")
code.append("# Pure structural columns + clean continuous slab + stairs")
code.append("groups.clear()")
code.append("")
code.append("layer_names = [l.name for l in layers]")
code.append("for lname in ['Slabs', 'Columns', 'Stairs']:")
code.append("    if lname not in layer_names:")
code.append("        layers.append(Layer(lname))")
code.append("")

# 1. Slab
code.append("# 1. SINGLE CONTINUOUS FLAT SLAB (ZERO NOTCHES, 4,605.49 m^2)")
code.append(f"slab_poly = {slab_poly}")
code.append("g_slab = extrude(slab_poly, -0.20, 0.0, name='F01_Floor_Slab', color=(0.78, 0.80, 0.82, 1.0))")
code.append("g_slab.layer = 'Slabs'")
code.append("")

# 2. Columns
code.append(f"# 2. ALL {len(cols_data)} STANDALONE STRUCTURAL COLUMNS (EXTRUDE Z: 0.00 -> 4.00m)")
for idx, c in enumerate(cols_data, 1):
    pts = [(round(float(x), 3), round(float(y), 3)) for x, y in c['coords']]
    cid = c['id']
    code.append(f"g_col_{idx} = extrude({pts}, 0.0, 4.00, name='{cid}', color=(0.88, 0.86, 0.84, 1.0))")
    code.append(f"g_col_{idx}.layer = 'Columns'")
code.append("")

# 3. Stairs
code.append("# 3. STAIRS")
code.append("# 3A. ST-1 CORE FIRE STAIR (Flights 1 & 2 + Intermediate Landing)")
fl1_y = [float(y) for y in np.linspace(-11.3, -7.7, 12)]
for i in range(len(fl1_y)-1):
    y1, y2 = fl1_y[i], fl1_y[i+1]
    z1 = round(float(i * 0.175), 3)
    z2 = round(float((i+1) * 0.175), 3)
    step_poly = [(8.60, round(y1, 3)), (9.75, round(y1, 3)), (9.75, round(y2, 3)), (8.60, round(y2, 3))]
    code.append(f"s_st1_f1_{i} = extrude({step_poly}, 0.0, {z2}, name='ST1_F1_Step_{i+1}', color=(0.75, 0.77, 0.80, 1.0))")
    code.append(f"s_st1_f1_{i}.layer = 'Stairs'")

landing_poly = [(8.60, -7.70), (11.00, -7.70), (11.00, -6.60), (8.60, -6.60)]
code.append(f"s_st1_land = extrude({landing_poly}, 0.0, 1.925, name='ST1_Landing', color=(0.75, 0.77, 0.80, 1.0))")
code.append("s_st1_land.layer = 'Stairs'")

fl2_y = [float(y) for y in np.linspace(-7.7, -11.3, 12)]
for i in range(len(fl2_y)-1):
    y1, y2 = fl2_y[i], fl2_y[i+1]
    z1 = round(float(1.925 + i * 0.175), 3)
    z2 = round(float(1.925 + (i+1) * 0.175), 3)
    step_poly = [(9.85, round(y1, 3)), (11.00, round(y1, 3)), (11.00, round(y2, 3)), (9.85, round(y2, 3))]
    code.append(f"s_st1_f2_{i} = extrude({step_poly}, 1.925, {z2}, name='ST1_F2_Step_{i+1}', color=(0.75, 0.77, 0.80, 1.0))")
    code.append(f"s_st1_f2_{i}.layer = 'Stairs'")

code.append("")
code.append("# 3B. ST-2 SOUTH ENTRANCE STAIR (Ground up to slab level Z: -0.60 -> 0.00)")
st2_x = [float(x) for x in np.linspace(4.17, 8.94, 17)]
for i in range(len(st2_x)-1):
    x1, x2 = round(st2_x[i], 3), round(st2_x[i+1], 3)
    z_step = round(float(-0.60 + (i+1) * (0.60 / 16)), 3)
    st2_poly = [(x1, -21.20), (x2, -21.20), (x2, -18.40), (x1, -18.40)]
    code.append(f"s_st2_{i} = extrude({st2_poly}, -0.60, {z_step}, name='ST2_Step_{i+1}', color=(0.75, 0.77, 0.80, 1.0))")
    code.append(f"s_st2_{i}.layer = 'Stairs'")

code.append("")
code.append("# 3C. GRAND SPIRAL STAIRCASE IN LOBBY")
xc, yc = 22.586, -4.264
R_in = 0.25
R_out = 1.40
n_steps = 24
total_rot_deg = 360.0

# Central column hub
hub_pts = [(round(float(xc + R_in * math.cos(math.radians(a))), 3), round(float(yc + R_in * math.sin(math.radians(a))), 3)) for a in range(0, 360, 20)]
code.append(f"s_spiral_hub = extrude({hub_pts}, 0.0, 4.00, name='Spiral_Center_Hub', color=(0.30, 0.32, 0.35, 1.0))")
code.append("s_spiral_hub.layer = 'Stairs'")

step_deg = total_rot_deg / n_steps
overlap_deg = 2.0
step_dz = 4.00 / n_steps

for i in range(n_steps):
    a1 = float(i * step_deg)
    a2 = float(a1 + step_deg + overlap_deg)
    sector_pts = []
    for a in [float(x) for x in np.linspace(a1, a2, 4)]:
        sector_pts.append((round(float(xc + R_in * math.cos(math.radians(a))), 3), round(float(yc + R_in * math.sin(math.radians(a))), 3)))
    for a in [float(x) for x in np.linspace(a2, a1, 6)]:
        sector_pts.append((round(float(xc + R_out * math.cos(math.radians(a))), 3), round(float(yc + R_out * math.sin(math.radians(a))), 3)))
    
    z_bot = round(float(i * step_dz), 3)
    z_top = round(float(z_bot + 0.06), 3)
    code.append(f"s_tread_{i} = extrude({sector_pts}, {z_bot}, {z_top}, name='Spiral_Tread_{i+1:02d}', color=(0.90, 0.88, 0.84, 1.0))")
    code.append(f"s_tread_{i}.layer = 'Stairs'")

full_code = '\n'.join(code)

with open('scripts/f01_pure_columns_clean_slab.py', 'w', encoding='utf-8') as f:
    f.write(full_code)

print("Generated pure float scripts/f01_pure_columns_clean_slab.py successfully!")

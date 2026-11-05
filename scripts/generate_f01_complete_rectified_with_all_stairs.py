import json
import math
import numpy as np

# Load 64 columns
with open('scripts/f01_columns.json', 'r') as f:
    cols_data = json.load(f)

# Continuous flat slab polygon (4605.49 m2)
slab_poly = [
    (-26.5, 44.0),
    (-26.5, -18.0),
    (-25.73, -18.025),
    (-24.18, -17.925),
    (-22.63, -17.825),
    (-21.08, -17.725),
    (-19.53, -17.625),
    (-17.98, -17.525),
    (-16.43, -17.425),
    (-14.88, -17.325),
    (-13.33, -17.225),
    (-11.78, -17.125),
    (-10.23, -17.025),
    (-8.67, -16.925),
    (-7.12, -16.825),
    (-5.58, -16.725),
    (-4.03, -16.635),
    (-2.48, -16.525),
    (-0.93, -16.402),
    (0.62, -16.263),
    (2.16, -16.102),
    (3.73, -15.891),
    (3.71, -22.5),
    (10.0, -22.5),
    (68.0, 5.0),
    (68.0, 23.0),
    (33.0, 23.0),
    (33.0, 44.0),
    (-26.5, 44.0)
]

code = []
code.append("# === FLOOR 01 MASTER MODEL: ALL STAIRS & VERIFIED STACKING ===")
code.append("# 64 pure structural columns, continuous slab, 6 comprehensive stair systems")
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

# 2. Columns (64 pure structural columns, height 4.00m)
code.append(f"# 2. ALL {len(cols_data)} STRUCTURAL COLUMNS (EXTRUDE Z: 0.00 -> 4.00m)")
for idx, c in enumerate(cols_data, 1):
    pts = [(round(float(x), 3), round(float(y), 3)) for x, y in c['coords']]
    cid = c['id']
    code.append(f"g_col_{idx} = extrude({pts}, 0.0, 4.00, name='{cid}', color=(0.88, 0.86, 0.84, 1.0))")
    code.append(f"g_col_{idx}.layer = 'Columns'")
code.append("")

# 3. Stairs (All 6 Systems)
code.append("# 3. ALL STAIR SYSTEMS (FULLY RECTIFIED & RESTORED)")
code.append("")

# ==============================================================================
# 3A. GRAND FAN-SHAPED ROTUNDA STAIR (FOYER AMPHITHEATER STEPS) - WAS MISSING!
# ==============================================================================
code.append("# 3A. GRAND FAN-SHAPED ROTUNDA STAIR (Foyer Reception Amphitheater)")
# Center: (13.50, -0.50), Rin = 2.40m, Rout = 4.80m, Spanning 110° to -20° (130° arc)
xc_fan, yc_fan = 13.50, -0.50
R_in_fan = 2.40
R_out_fan = 4.80
n_fan_steps = 12
fan_start_deg = 110.0
fan_arc = 130.0
fan_step_deg = fan_arc / n_fan_steps
dz_fan = 0.15 # 15cm riser per step

for i in range(n_fan_steps):
    a1 = float(fan_start_deg - i * fan_step_deg)
    a2 = float(fan_start_deg - (i + 1) * fan_step_deg - 1.0)
    # Radiating wedge tread polygon
    pts = [
        (round(float(xc_fan + R_in_fan * math.cos(math.radians(a1))), 3), round(float(yc_fan + R_in_fan * math.sin(math.radians(a1))), 3)),
        (round(float(xc_fan + R_out_fan * math.cos(math.radians(a1))), 3), round(float(yc_fan + R_out_fan * math.sin(math.radians(a1))), 3)),
        (round(float(xc_fan + R_out_fan * math.cos(math.radians(a2))), 3), round(float(yc_fan + R_out_fan * math.sin(math.radians(a2))), 3)),
        (round(float(xc_fan + R_in_fan * math.cos(math.radians(a2))), 3), round(float(yc_fan + R_in_fan * math.sin(math.radians(a2))), 3)),
    ]
    z_bot = round(float(i * dz_fan), 3)
    z_top = round(float(z_bot + 0.08), 3)
    code.append(f"s_fan_{i} = extrude({pts}, {z_bot}, {z_top}, name='Foyer_Fan_Tread_{i+1:02d}', color=(0.91, 0.88, 0.83, 1.0))")
    code.append(f"s_fan_{i}.layer = 'Stairs'")

code.append("")

# ==============================================================================
# 3B. RECTIFIED CIRCULAR LOBBY STAIR (200° Arc, Counter-Clockwise, Open Core)
# ==============================================================================
code.append("# 3B. RECTIFIED CIRCULAR LOBBY STAIR (200° Arc, Rin=0.85m, Rout=1.45m)")
xc_lob, yc_lob = 22.586, -4.264
R_in_lob = 0.85
R_out_lob = 1.45
start_lob = 160.0
arc_lob = 200.0
n_lob_steps = 16
step_lob_deg = arc_lob / n_lob_steps
dz_lob = 2.80 / n_lob_steps

for i in range(n_lob_steps):
    a1 = float(start_lob - i * step_lob_deg)
    a2 = float(start_lob - (i + 1) * step_lob_deg - 1.5)
    pts = [
        (round(float(xc_lob + R_in_lob * math.cos(math.radians(a1))), 3), round(float(yc_lob + R_in_lob * math.sin(math.radians(a1))), 3)),
        (round(float(xc_lob + R_out_lob * math.cos(math.radians(a1))), 3), round(float(yc_lob + R_out_lob * math.sin(math.radians(a1))), 3)),
        (round(float(xc_lob + R_out_lob * math.cos(math.radians(a2))), 3), round(float(yc_lob + R_out_lob * math.sin(math.radians(a2))), 3)),
        (round(float(xc_lob + R_in_lob * math.cos(math.radians(a2))), 3), round(float(yc_lob + R_in_lob * math.sin(math.radians(a2))), 3)),
    ]
    z_bot = round(float(i * dz_lob), 3)
    z_top = round(float(z_bot + 0.06), 3)
    code.append(f"s_lob_{i} = extrude({pts}, {z_bot}, {z_top}, name='Lobby_Curved_Tread_{i+1:02d}', color=(0.92, 0.90, 0.85, 1.0))")
    code.append(f"s_lob_{i}.layer = 'Stairs'")

# Top Platform for Circular Stair (at Z = 2.80m)
plat_pts = []
for a in [float(x) for x in np.linspace(-40.0, 160.0, 12)]:
    plat_pts.append((round(float(xc_lob + R_out_lob * math.cos(math.radians(a))), 3), round(float(yc_lob + R_out_lob * math.sin(math.radians(a))), 3)))
for a in [float(x) for x in np.linspace(160.0, -40.0, 8)]:
    plat_pts.append((round(float(xc_lob + R_in_lob * math.cos(math.radians(a))), 3), round(float(yc_lob + R_in_lob * math.sin(math.radians(a))), 3)))

code.append(f"s_lob_plat = extrude({plat_pts}, 2.65, 2.80, name='Lobby_Upper_Platform', color=(0.88, 0.86, 0.82, 1.0))")
code.append("s_lob_plat.layer = 'Stairs'")
code.append("")

# ==============================================================================
# 3C. ST-1 CORE FIRE STAIR (Angle: -9.17°, South U-Turn Landing)
# ==============================================================================
code.append("# 3C. ST-1 CORE FIRE STAIR (Angle: -9.17°, South U-Turn Landing)")
theta_rad = math.radians(-9.17)
cos_t = math.cos(theta_rad)
sin_t = math.sin(theta_rad)
x0_st1, y0_st1 = 9.20, -7.50

def st1_to_world(u, v):
    wx = x0_st1 + u * cos_t - v * sin_t
    wy = y0_st1 + u * sin_t - v * cos_t
    return (round(float(wx), 3), round(float(wy), 3))

# South Landing at Z = 1.925m
land_pts = [st1_to_world(0.0, 3.80), st1_to_world(2.55, 3.80), st1_to_world(2.55, 5.30), st1_to_world(0.0, 5.30)]
code.append(f"s_st1_land = extrude({land_pts}, 0.0, 1.925, name='ST1_South_Landing', color=(0.75, 0.77, 0.80, 1.0))")
code.append("s_st1_land.layer = 'Stairs'")

# Flight 1 (West Flight: North Z=0.0 -> South Landing Z=1.925)
dv = 3.80 / 11.0
for i in range(11):
    v1, v2 = i * dv, (i + 1) * dv
    z_step = round(float((i + 1) * 0.175), 3)
    step_poly = [st1_to_world(0.0, v1), st1_to_world(1.20, v1), st1_to_world(1.20, v2), st1_to_world(0.0, v2)]
    code.append(f"s_st1_f1_{i} = extrude({step_poly}, 0.0, {z_step}, name='ST1_Flight1_Step_{i+1}', color=(0.75, 0.77, 0.80, 1.0))")
    code.append(f"s_st1_f1_{i}.layer = 'Stairs'")

# Flight 2 (East Flight: South Landing Z=1.925 -> North Z=3.85)
for i in range(11):
    v1, v2 = 3.80 - (i + 1) * dv, 3.80 - i * dv
    z_step = round(float(1.925 + (i + 1) * 0.175), 3)
    step_poly = [st1_to_world(1.35, v1), st1_to_world(2.55, v1), st1_to_world(2.55, v2), st1_to_world(1.35, v2)]
    code.append(f"s_st1_f2_{i} = extrude({step_poly}, 1.925, {z_step}, name='ST1_Flight2_Step_{i+1}', color=(0.75, 0.77, 0.80, 1.0))")
    code.append(f"s_st1_f2_{i}.layer = 'Stairs'")

code.append("")

# ==============================================================================
# 3D. EAST WING FIRE STAIR (Angle: 33°, Slanted with East Wing)
# ==============================================================================
code.append("# 3D. EAST WING FIRE STAIR (Angle: 33°, Slanted with East Wing)")
x0_east, y0_east = 58.5, 13.5
theta_east = math.radians(33.0)
cos_e = math.cos(theta_east)
sin_e = math.sin(theta_east)

def east_to_world(u, v):
    wx = x0_east - v * cos_e - u * sin_e
    wy = y0_east - v * sin_e + u * cos_e
    return (round(float(wx), 3), round(float(wy), 3))

east_land = [east_to_world(0.0, 3.2), east_to_world(2.2, 3.2), east_to_world(2.2, 4.4), east_to_world(0.0, 4.4)]
code.append(f"s_east_land = extrude({east_land}, 0.0, 1.75, name='ST_East_Landing', color=(0.75, 0.77, 0.80, 1.0))")
code.append("s_east_land.layer = 'Stairs'")

dv_e = 3.2 / 10.0
for i in range(10):
    v1, v2 = i * dv_e, (i + 1) * dv_e
    z_step = round(float((i + 1) * 0.175), 3)
    step_poly = [east_to_world(0.0, v1), east_to_world(1.05, v1), east_to_world(1.05, v2), east_to_world(0.0, v2)]
    code.append(f"s_east_f1_{i} = extrude({step_poly}, 0.0, {z_step}, name='ST_East_F1_Step_{i+1}', color=(0.75, 0.77, 0.80, 1.0))")
    code.append(f"s_east_f1_{i}.layer = 'Stairs'")

for i in range(10):
    v1, v2 = 3.2 - (i + 1) * dv_e, 3.2 - i * dv_e
    z_step = round(float(1.75 + (i + 1) * 0.175), 3)
    step_poly = [east_to_world(1.15, v1), east_to_world(2.20, v1), east_to_world(2.20, v2), east_to_world(1.15, v2)]
    code.append(f"s_east_f2_{i} = extrude({step_poly}, 1.75, {z_step}, name='ST_East_F2_Step_{i+1}', color=(0.75, 0.77, 0.80, 1.0))")
    code.append(f"s_east_f2_{i}.layer = 'Stairs'")

code.append("")

# ==============================================================================
# 3E. ST-2 SOUTH OUTDOOR ENTRANCE STAIR (Ground -0.60m -> Slab 0.00m)
# ==============================================================================
code.append("# 3E. ST-2 SOUTH OUTDOOR ENTRANCE STAIR (16 Steps, Ground -0.60m -> Slab 0.00m)")
st2_x = [float(x) for x in np.linspace(4.17, 8.94, 17)]
for i in range(len(st2_x)-1):
    x1, x2 = round(st2_x[i], 3), round(st2_x[i+1], 3)
    z_step = round(float(-0.60 + (i+1) * (0.60 / 16)), 3)
    st2_poly = [(x1, -21.20), (x2, -21.20), (x2, -18.40), (x1, -18.40)]
    code.append(f"s_st2_{i} = extrude({st2_poly}, -0.60, {z_step}, name='ST2_Step_{i+1}', color=(0.75, 0.77, 0.80, 1.0))")
    code.append(f"s_st2_{i}.layer = 'Stairs'")

code.append("")

# ==============================================================================
# 3F. NORTH TERRACE SPORTS STEPS (Connecting Gym Floor to Sports Platform)
# ==============================================================================
code.append("# 3F. NORTH TERRACE SPORTS STEPS (4 Steps from Floor 0.00m to Platform +0.60m)")
# Location: X in [-16.5, -14.5], Y in [21.5, 23.5]
for i in range(4):
    y1 = round(float(21.80 + i * 0.35), 3)
    y2 = round(float(21.80 + (i + 1) * 0.35), 3)
    z_s = round(float((i + 1) * 0.15), 3)
    step_box = [(-16.50, y1), (-14.50, y1), (-14.50, y2), (-16.50, y2)]
    code.append(f"s_sport_{i} = extrude({step_box}, 0.0, {z_s}, name='North_Sports_Step_{i+1}', color=(0.75, 0.77, 0.80, 1.0))")
    code.append(f"s_sport_{i}.layer = 'Stairs'")

full_code = '\n'.join(code)

with open('scripts/f01_master_accurate_model.py', 'w', encoding='utf-8') as f:
    f.write(full_code)

print("Generated scripts/f01_master_accurate_model.py successfully!")
print(f"Total lines of code: {len(code)}")


import json
import math
import numpy as np

# Load 64 columns
with open('scripts/f01_columns.json', 'r') as f:
    cols_data = json.load(f)

# Load clean slab points
# Using the proven notchless continuous slab polygon
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
code.append("# === FLOOR 01 ACCURATE MODEL (RECTIFIED STAIR DIRECTIONS) ===")
code.append("# Zero walls, zero doors, 64 pure columns, clean continuous slab")
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
code.append("# 3. RECTIFIED STAIRS BASED ON FORENSIC CAD ANALYSIS")
code.append("")

# ==============================================================================
# 3A. ST-1 CORE FIRE STAIR (Accurate -9.17° tilt, South Landing, North Entry)
# ==============================================================================
# Riser angle is -170.83° (tilt = -9.17° from horizontal)
# Flight direction vector along stairs (perpendicular to riser):
# Angle = -80.83° -> cos(-80.83°) = 0.1593, sin(-80.83°) = -0.9872
# Width across flight (along riser):
# cos(-170.83°) = -0.9872, sin(-170.83°) = -0.1593
code.append("# 3A. ST-1 CORE FIRE STAIR (Angle: -9.17°, South U-Turn Landing)")
theta_rad = math.radians(-9.17)
cos_t = math.cos(theta_rad)
sin_t = math.sin(theta_rad)

# Helper function to project local stair coords (u = across width, v = along flight) to world (X, Y)
# Origin at stair north-west corner: (x0, y0) = (9.20, -7.50)
x0_st1, y0_st1 = 9.20, -7.50
def st1_to_world(u, v):
    # u is across width (positive towards East/right)
    # v is along flight (positive towards South/downwards)
    # local X along riser: dx = u * cos_t, dy = u * sin_t
    # local Y along flight: dx = -v * sin_t, dy = -v * cos_t
    wx = x0_st1 + u * cos_t - v * sin_t
    wy = y0_st1 + u * sin_t - v * cos_t
    return (round(float(wx), 3), round(float(wy), 3))

# Flight width = 1.20m per flight, separator = 0.15m, total width = 2.55m
# Flight length = 3.80m (12 risers * 0.28m + margin), South Landing depth = 1.50m
# Total length = 5.30m
# 1. South Landing: u from 0.0 to 2.55, v from 3.80 to 5.30 at Z = 1.925m
land_pts = [st1_to_world(0.0, 3.80), st1_to_world(2.55, 3.80), st1_to_world(2.55, 5.30), st1_to_world(0.0, 5.30)]
code.append(f"s_st1_land = extrude({land_pts}, 0.0, 1.925, name='ST1_South_Landing', color=(0.75, 0.77, 0.80, 1.0))")
code.append("s_st1_land.layer = 'Stairs'")

# Flight 1 (West Flight: u in [0.0, 1.20]):
# Descends from North (Z = 0.00 at v = 0) down to South Landing (Z = 1.925 at v = 3.80)
# (11 steps, dz = 1.925 / 11 = 0.175m)
dv = 3.80 / 11.0
for i in range(11):
    v1 = i * dv
    v2 = (i + 1) * dv
    z_step = round(float((i + 1) * 0.175), 3)
    step_poly = [st1_to_world(0.0, v1), st1_to_world(1.20, v1), st1_to_world(1.20, v2), st1_to_world(0.0, v2)]
    code.append(f"s_st1_f1_{i} = extrude({step_poly}, 0.0, {z_step}, name='ST1_Flight1_Step_{i+1}', color=(0.75, 0.77, 0.80, 1.0))")
    code.append(f"s_st1_f1_{i}.layer = 'Stairs'")

# Flight 2 (East Flight: u in [1.35, 2.55]):
# Continues from South Landing (Z = 1.925 at v = 3.80) up to North (Z = 3.85 at v = 0)
for i in range(11):
    v1 = 3.80 - (i + 1) * dv
    v2 = 3.80 - i * dv
    z_step = round(float(1.925 + (i + 1) * 0.175), 3)
    step_poly = [st1_to_world(1.35, v1), st1_to_world(2.55, v1), st1_to_world(2.55, v2), st1_to_world(1.35, v2)]
    code.append(f"s_st1_f2_{i} = extrude({step_poly}, 1.925, {z_step}, name='ST1_Flight2_Step_{i+1}', color=(0.75, 0.77, 0.80, 1.0))")
    code.append(f"s_st1_f2_{i}.layer = 'Stairs'")

code.append("")

# ==============================================================================
# 3B. GRAND CIRCULAR LOBBY STAIR (True CAD geometry: 200° bottom arc, Rin=0.85m, Rout=1.45m)
# ==============================================================================
code.append("# 3B. GRAND CIRCULAR LOBBY STAIR (Rectified: 200° Arc, Counter-Clockwise Walk)")
xc, yc = 22.586, -4.264
R_in = 0.85   # Wide open central rotunda
R_out = 1.45  # Outer balustrade
# Treads run from 160° (NW) counter-clockwise down to -40° (SE) -> 200° arc
start_deg = 160.0
total_arc = 200.0
n_lobby_steps = 16
step_arc = total_arc / n_lobby_steps  # 12.5° per step
step_h = 2.80 / n_lobby_steps         # 0.175m riser

for i in range(n_lobby_steps):
    # moving counter-clockwise: angles increase negatively (160 -> 147.5 -> ... -> -40)
    a1 = float(start_deg - i * step_arc)
    a2 = float(start_deg - (i + 1) * step_arc - 1.5) # 1.5 deg overlap
    # build 4-point sector polygon
    sector_pts = [
        (round(float(xc + R_in * math.cos(math.radians(a1))), 3), round(float(yc + R_in * math.sin(math.radians(a1))), 3)),
        (round(float(xc + R_out * math.cos(math.radians(a1))), 3), round(float(yc + R_out * math.sin(math.radians(a1))), 3)),
        (round(float(xc + R_out * math.cos(math.radians(a2))), 3), round(float(yc + R_out * math.sin(math.radians(a2))), 3)),
        (round(float(xc + R_in * math.cos(math.radians(a2))), 3), round(float(yc + R_in * math.sin(math.radians(a2))), 3)),
    ]
    z_bot = round(float(i * step_h), 3)
    z_top = round(float(z_bot + 0.06), 3) # 6cm marble tread
    code.append(f"s_spiral_tread_{i} = extrude({sector_pts}, {z_bot}, {z_top}, name='Lobby_Curved_Tread_{i+1:02d}', color=(0.92, 0.90, 0.85, 1.0))")
    code.append(f"s_spiral_tread_{i}.layer = 'Stairs'")

# Top Landing Platform (Upper semicircle arc from -40° to 160° at Z = 2.80m)
platform_pts = []
for a in [float(x) for x in np.linspace(-40.0, 160.0, 12)]:
    platform_pts.append((round(float(xc + R_out * math.cos(math.radians(a))), 3), round(float(yc + R_out * math.sin(math.radians(a))), 3)))
for a in [float(x) for x in np.linspace(160.0, -40.0, 8)]:
    platform_pts.append((round(float(xc + R_in * math.cos(math.radians(a))), 3), round(float(yc + R_in * math.sin(math.radians(a))), 3)))

code.append(f"s_lobby_platform = extrude({platform_pts}, 2.65, 2.80, name='Lobby_Upper_Landing_Platform', color=(0.88, 0.86, 0.82, 1.0))")
code.append("s_lobby_platform.layer = 'Stairs'")
code.append("")

# ==============================================================================
# 3C. EAST WING FIRE STAIR (Slanted 33° along East Curved Wing Axis)
# ==============================================================================
code.append("# 3C. EAST WING FIRE STAIR (Angle: 33°, Slanted with East Wing)")
# Center at X=57.5, Y=12.0, slanted at 33 degrees
x0_east, y0_east = 58.5, 13.5
theta_east = math.radians(33.0)
cos_e = math.cos(theta_east)
sin_e = math.sin(theta_east)

def east_to_world(u, v):
    # u is across width (towards interior)
    # v is along flight (descending towards south-west)
    wx = x0_east - v * cos_e - u * sin_e
    wy = y0_east - v * sin_e + u * cos_e
    return (round(float(wx), 3), round(float(wy), 3))

# East Landing at v in [3.2, 4.4], u in [0, 2.2]
east_land = [east_to_world(0.0, 3.2), east_to_world(2.2, 3.2), east_to_world(2.2, 4.4), east_to_world(0.0, 4.4)]
code.append(f"s_east_land = extrude({east_land}, 0.0, 1.75, name='ST_East_Landing', color=(0.75, 0.77, 0.80, 1.0))")
code.append("s_east_land.layer = 'Stairs'")

# East Flight 1 (u in [0, 1.05], v in [0, 3.2]): 10 steps
dv_e = 3.2 / 10.0
for i in range(10):
    v1 = i * dv_e
    v2 = (i + 1) * dv_e
    z_step = round(float((i + 1) * 0.175), 3)
    step_poly = [east_to_world(0.0, v1), east_to_world(1.05, v1), east_to_world(1.05, v2), east_to_world(0.0, v2)]
    code.append(f"s_east_f1_{i} = extrude({step_poly}, 0.0, {z_step}, name='ST_East_F1_Step_{i+1}', color=(0.75, 0.77, 0.80, 1.0))")
    code.append(f"s_east_f1_{i}.layer = 'Stairs'")

# East Flight 2 (u in [1.15, 2.20], v in [3.2, 0]): 10 steps
for i in range(10):
    v1 = 3.2 - (i + 1) * dv_e
    v2 = 3.2 - i * dv_e
    z_step = round(float(1.75 + (i + 1) * 0.175), 3)
    step_poly = [east_to_world(1.15, v1), east_to_world(2.20, v1), east_to_world(2.20, v2), east_to_world(1.15, v2)]
    code.append(f"s_east_f2_{i} = extrude({step_poly}, 1.75, {z_step}, name='ST_East_F2_Step_{i+1}', color=(0.75, 0.77, 0.80, 1.0))")
    code.append(f"s_east_f2_{i}.layer = 'Stairs'")

code.append("")

# ==============================================================================
# 3D. ST-2 SOUTH OUTDOOR ENTRANCE STAIR (16 steps from ground -0.60m to 0.00m)
# ==============================================================================
code.append("# 3D. ST-2 SOUTH OUTDOOR ENTRANCE STAIR (Ground -0.60m -> Slab 0.00m)")
st2_x = [float(x) for x in np.linspace(4.17, 8.94, 17)]
for i in range(len(st2_x)-1):
    x1, x2 = round(st2_x[i], 3), round(st2_x[i+1], 3)
    z_step = round(float(-0.60 + (i+1) * (0.60 / 16)), 3)
    st2_poly = [(x1, -21.20), (x2, -21.20), (x2, -18.40), (x1, -18.40)]
    code.append(f"s_st2_{i} = extrude({st2_poly}, -0.60, {z_step}, name='ST2_Step_{i+1}', color=(0.75, 0.77, 0.80, 1.0))")
    code.append(f"s_st2_{i}.layer = 'Stairs'")

full_code = '\n'.join(code)

with open('scripts/f01_accurate_stairs_payload.py', 'w', encoding='utf-8') as f:
    f.write(full_code)

print("Generated scripts/f01_accurate_stairs_payload.py successfully!")
print(f"Total lines: {len(code)}")


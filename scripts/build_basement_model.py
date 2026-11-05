import sys
import os

sys.path.insert(0, '.')
from scripts.verify_all_77_cols import unique_cols, ensure_ccw, poly_area
from scripts.verify_extraction import curb_pts
from scripts.test_step_polygons import outdoor_step_polys
from scripts.test_core_stair_polygons import f1_polys, f2_polys, lower_landing_poly, upper_landing_poly

# 1. Single Unified Basement Slab Polygon
curb_rev = curb_pts[::-1]

unified_basement_poly = [
    (-26.0, 44.0),
    (32.0, 44.0),
    (32.0, 22.0),
    (66.0, 22.0),
    (66.0, 6.0),
    (14.0, -10.0),
    (10.0, -14.0),
    (10.0, -22.0),
    (2.0, -22.0),
    (2.0, -14.0),
    (3.71, -14.0),
] + curb_rev + [
    (-26.0, -0.35),
    (-26.0, 44.0)
]
unified_basement_poly = ensure_ccw(unified_basement_poly[:-1])

# 2. Flight 3 steps (Left return flight climbing South to Floor 1 at 3.50m)
f3_polys = []
for st in range(4):
    y_start = -9.025 - (st * 0.25)
    y_end = -9.025 - ((st + 1) * 0.25)
    poly = ensure_ccw([(8.877, y_start), (9.568, y_start), (9.568, y_end), (8.877, y_end)])
    f3_polys.append(poly)

# Handrail divider
rail_poly = ensure_ccw([(9.568, -12.45), (9.60, -12.45), (9.60, -6.50), (9.568, -6.50)])

# Assemble IngeTrazo python script
payload_lines = [
    "# === BASEMENT FLOOR MODEL: COLUMNS, STAIRS & UNIFIED FLAT SLAB ===",
    "# Clear scene",
    "scene.clear()",
    "",
    "# Ensure layers exist",
    "layer_names = [l.name for l in layers]",
    "for lname in ['Slabs', 'Columns', 'Stairs']:",
    "    if lname not in layer_names:",
    "        layers.append(Layer(lname))",
    "",
    "# 1. SINGLE UNIFIED CONTINUOUS BASEMENT SLAB (NO ELEVATION DIFFERENCE)",
    f"g_slab = extrude({unified_basement_poly}, -0.20, 0.0, name='Basement_Floor_Slab', color=(0.78, 0.80, 0.82, 1.0))",
    "g_slab.layer = 'Slabs'",
    "",
    "# 2. ALL 77 STRUCTURAL COLUMNS (EXTRUDE Z: 0.00 -> +3.50m)",
]

for i, col in enumerate(unique_cols):
    poly = col['poly']
    src = col['src']
    cx, cy = col['center']
    payload_lines.append(f"g_col_{i} = extrude({poly}, 0.0, 3.50, name='Col_{i:02d}_{src}', color=(0.88, 0.86, 0.84, 1.0))")
    payload_lines.append(f"g_col_{i}.layer = 'Columns'")

payload_lines.extend([
    "",
    "# 3. INTERNAL CORE STAIRCASE (3-FLIGHT DOGLEG STAIR, ASCENDING 0.00 -> +3.50m)",
    "# Flight 1: 4 steps stepping East (0.00 -> +0.76m)",
])

for i, poly in enumerate(f1_polys):
    z_step = round(0.19 * (i + 1), 3)
    payload_lines.append(f"g_f1_{i} = extrude({poly}, 0.0, {z_step}, name='Core_Stair_F1_Step_{i+1}', color=(0.82, 0.83, 0.85, 1.0))")
    payload_lines.append(f"g_f1_{i}.layer = 'Stairs'")

payload_lines.extend([
    "",
    "# Lower Intermediate Landing (+0.76m)",
    f"g_l_land = extrude({lower_landing_poly}, 0.0, 0.76, name='Core_Stair_Lower_Landing', color=(0.80, 0.81, 0.83, 1.0))",
    "g_l_land.layer = 'Stairs'",
    "",
    "# Flight 2: 10 steps stepping North along East wall (+0.76m -> +2.66m)",
])

for i, poly in enumerate(f2_polys):
    z_step = round(0.76 + 0.19 * (i + 1), 3)
    payload_lines.append(f"g_f2_{i} = extrude({poly}, 0.0, {z_step}, name='Core_Stair_F2_Step_{i+1}', color=(0.82, 0.83, 0.85, 1.0))")
    payload_lines.append(f"g_f2_{i}.layer = 'Stairs'")

payload_lines.extend([
    "",
    "# Upper Half-Landing (+2.66m)",
    f"g_u_land = extrude({upper_landing_poly}, 0.0, 2.66, name='Core_Stair_Upper_Landing', color=(0.80, 0.81, 0.83, 1.0))",
    "g_u_land.layer = 'Stairs'",
    "",
    "# Flight 3: 4 steps returning South (+2.66m -> +3.42m)",
])

for i, poly in enumerate(f3_polys):
    z_step = round(2.66 + 0.19 * (i + 1), 3)
    payload_lines.append(f"g_f3_{i} = extrude({poly}, 0.0, {z_step}, name='Core_Stair_F3_Step_{i+1}', color=(0.82, 0.83, 0.85, 1.0))")
    payload_lines.append(f"g_f3_{i}.layer = 'Stairs'")

payload_lines.extend([
    "",
    "# Center divider rail",
    f"g_rail = extrude({rail_poly}, 0.76, 3.50, name='Core_Stair_Center_Rail', color=(0.60, 0.65, 0.70, 1.0))",
    "g_rail.layer = 'Stairs'",
    "",
    "# 4. SOUTH STAIRCASE (16 STEPS, ASCENDING FROM BASEMENT 0.00 -> +2.40m)",
    "# No stair goes lower than basement! Starts at Z=0.00 and ascends Eastward up to ground level",
])

for i, poly in enumerate(outdoor_step_polys):
    z_top = round(0.15 * (i + 1), 3)
    payload_lines.append(f"g_out_step_{i} = extrude({poly}, 0.0, {z_top}, name='South_Stair_Step_{i+1:02d}', color=(0.75, 0.77, 0.80, 1.0))")
    payload_lines.append(f"g_out_step_{i}.layer = 'Stairs'")

# Top landing east of step 15
# Step 15 top edge: (8.585, -18.078) to (8.894, -20.626)
top_landing_poly = ensure_ccw([(8.585, -18.078), (10.0, -17.90), (10.3, -20.45), (8.894, -20.626)])
payload_lines.extend([
    "",
    "# South Stair Upper Landing (+2.40m)",
    f"g_out_top_land = extrude({top_landing_poly}, 0.0, 2.40, name='South_Stair_Top_Landing', color=(0.73, 0.75, 0.78, 1.0))",
    "g_out_top_land.layer = 'Stairs'",
    "",
    "print('Basement Model Generation Complete!')",
    "print(f'Total groups created: {len(scene.groups)}')",
])

out_script_path = 'scripts/generated_basement_payload.py'
with open(out_script_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(payload_lines))

print(f"Generated {len(payload_lines)} lines to {out_script_path}")


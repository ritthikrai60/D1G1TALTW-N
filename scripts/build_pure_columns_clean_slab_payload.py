import re

# 1. Clean slab polygon (Zero notches, zero zigzag, 100% enclosure)
curb_pts = [
    (-18.849, -15.533), (-18.913, -17.107), (-18.132, -17.136), (-17.351, -17.162),
    (-16.57, -17.183), (-15.789, -17.2), (-15.007, -17.211), (-14.226, -17.22),
    (-13.444, -17.224), (-12.663, -17.223), (-11.881, -17.219), (-11.1, -17.209),
    (-10.319, -17.195), (-9.537, -17.179), (-8.756, -17.156), (-7.975, -17.13),
    (-7.193, -17.099), (-6.413, -17.064), (-5.632, -17.025), (-4.852, -16.982),
    (-4.072, -16.933), (-3.292, -16.881), (-2.512, -16.825), (-1.734, -16.764),
    (-0.955, -16.699), (-0.177, -16.629), (0.602, -16.556), (1.379, -16.478),
    (2.157, -16.396), (2.934, -16.31), (3.709, -16.219)
]

clean_slab_poly = [
    (-26.5, 44.0),
    (-26.5, -18.0),     # Smooth SW boundary enclosing Col 02 & curb
] + curb_pts + [
    (3.71, -22.5),      # Enclose ST-3 base cleanly
    (10.0, -22.5),
    (68.0, 5.0),        # ONE SINGLE CLEAN STRAIGHT LINE for entire Southeast wing! ZERO NOTCHES!
    (68.0, 23.0),
    (33.0, 23.0),
    (33.0, 44.0),
    (-26.5, 44.0)
]

# 2. Load columns and stairs from checkpoint v1
with open('scripts/checkpoint_basement_v1_base.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract columns lines (lines 15 to 171)
lines = text.splitlines()
col_and_stair_lines = []
in_content = False
for l in lines:
    if '# 2. ALL 77 STRUCTURAL COLUMNS' in l:
        in_content = True
    if in_content:
        col_and_stair_lines.append(l)

payload_lines = [
    "# === PURE COLUMNS & CLEAN SLAB BASEMENT MODEL (NO WALLS, NO DOORS) ===",
    "# Clear scene",
    "groups.clear()",
    "",
    "# Ensure layers exist",
    "layer_names = [l.name for l in layers]",
    "for lname in ['Slabs', 'Columns', 'Stairs']:",
    "    if lname not in layer_names:",
    "        layers.append(Layer(lname))",
    "",
    "# 1. SINGLE UNIFIED FLAT BASEMENT SLAB (CLEAN, NO NOTCHES, 4583.05 m^2)",
    f"slab_poly = {clean_slab_poly}",
    "g_slab = extrude(slab_poly, -0.20, 0.0, name='Basement_Floor_Slab', color=(0.78, 0.80, 0.82, 1.0))",
    "g_slab.layer = 'Slabs'",
    ""
]

payload_lines.extend(col_and_stair_lines)

out_file = 'scripts/basement_pure_columns_clean_slab.py'
with open(out_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(payload_lines))

print(f"Generated {out_file}: {len(payload_lines)} lines.")


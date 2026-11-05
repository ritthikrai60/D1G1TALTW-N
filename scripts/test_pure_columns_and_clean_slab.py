import re
import shapely
from shapely.geometry import Polygon, Point

# 1. Clean, smooth slab polygon without ANY jagged notches
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
    (-26.5, -18.0),     # SW straight boundary
] + curb_pts + [
    (3.71, -22.5),      # Enclose ST-3 base
    (10.0, -22.5),
    (68.0, 5.0),        # ONE SINGLE CLEAN STRAIGHT LINE for entire Southeast wing!
    (68.0, 23.0),
    (33.0, 23.0),
    (33.0, 44.0),
    (-26.5, 44.0)
]

p_slab = Polygon(clean_slab_poly)
print(f"Clean slab valid: {p_slab.is_valid}, Area: {p_slab.area:.2f} m^2, Vertices: {len(clean_slab_poly)}")

# 2. Load 77 columns from checkpoint v1
with open('scripts/checkpoint_basement_v1_base.py', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = re.compile(r"g_col_(\d+)\s*=\s*extrude\((\[.*?\]),", re.DOTALL)
matches = pattern.findall(text)
print(f"Found {len(matches)} pure standalone columns in checkpoint v1")

outside_cols = []
for idx_str, poly_str in matches:
    pts = eval(poly_str)
    p_col = Polygon(pts)
    if not p_slab.contains(p_col):
        diff = p_col.difference(p_slab)
        outside_cols.append((idx_str, diff.area))

print(f"Columns outside clean slab: {len(outside_cols)} (MUST BE 0)")


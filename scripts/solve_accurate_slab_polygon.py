import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import shapely
from shapely.geometry import Polygon, MultiPolygon, Point, box, LineString
import shapely.ops
import re

# 1. Load payload elements
with open('scripts/flawless_basement_final_payload.py', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = re.compile(r"g_(\d+)\s*=\s*(?:extrude|prism)\((\[.*?\]),.*?name='(.*?)'", re.DOTALL)
matches = pattern.findall(text)

all_elems = []
for idx_str, poly_str, name in matches:
    coords = eval(poly_str)
    pts_2d = [(p[0], p[1]) for p in coords]
    if len(pts_2d) >= 3:
        p = Polygon(pts_2d)
        if not p.is_valid: p = p.buffer(0)
        all_elems.append(p)

union_structure = shapely.ops.unary_union(all_elems)
print(f"Union structure bounds: {union_structure.bounds}")

# Load ST-3 bounding box:
# ST-3: X in [4.15, 8.95], Y in [-21.2, -18.0]
st3_box = box(3.8, -22.5, 9.5, -17.5)

# 2. Construct clean, authentic slab boundary:
# A. West boundary: must enclose Col 02 (X = -24.23, Y = -15.24) and the curb island
# Start at NW: (-26.5, 44.0) -> (-26.5, -17.5) -> (-23.0, -17.5) -> (-18.849, -17.22)
# B. South curb curve: from (-18.849, -17.22) along curb points to (3.709, -16.219)
# C. ST-3 extension: smoothly enclose ST-3: (3.71, -16.22) -> (3.71, -22.5) -> (9.5, -22.5) -> (14.5, -15.0) -> (21.5, -13.0)
# D. South-East diagonal column row: smoothly enclose Cols 56, 57, 58, 61 with margin:
# Col 56 is at (20.3, -11.5) -> edge at (21.5, -13.0)
# Col 57 is at (30.8, -8.6)  -> edge at (32.0, -10.0)
# Col 58 is at (41.5, -4.6)  -> edge at (42.5, -6.0)
# Col 61 is at (51.6, 0.1)   -> edge at (53.0, -1.5)
# Eastmost corner: (66.5, 5.0) -> (66.5, 23.0) -> (32.5, 23.0) -> (32.5, 44.0) -> (-26.5, 44.0)

# South curb points from payload
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

corrected_slab_poly = [
    (-26.5, 44.0),
    (-26.5, -17.5),     # Covers SW island and Col 02
    (-23.0, -17.5),
] + curb_pts + [
    (3.71, -22.5),      # Encloses ST-3 cleanly without crossing back
    (9.5, -22.5),
    (15.0, -15.0),      # Encloses retaining wall corner at (14.29, -12.83)
    (21.5, -13.0),      # Encloses Col 56
    (32.0, -10.0),      # Encloses Col 57
    (42.5, -6.0),       # Encloses Col 58
    (53.0, -1.5),       # Encloses Col 61
    (66.5, 5.0),        # East boundary
    (66.5, 23.0),
    (32.5, 23.0),
    (32.5, 44.0),
    (-26.5, 44.0)
]

p_corr = Polygon(corrected_slab_poly)
print(f"Corrected slab valid: {p_corr.is_valid}, Area: {p_corr.area:.2f} m^2")

# Check if ALL elements are now completely inside:
outside_count = 0
for idx_str, poly_str, name in matches:
    coords = eval(poly_str)
    pts_2d = [(p[0], p[1]) for p in coords]
    p_elem = Polygon(pts_2d)
    if not p_elem.is_valid: p_elem = p_elem.buffer(0)
    if not p_corr.contains(p_elem):
        diff = p_elem.difference(p_corr)
        if diff.area > 1e-4:
            print(f"STILL OUTSIDE: {name}, area={diff.area:.4f}")
            outside_count += 1

print(f"Total elements outside corrected slab: {outside_count} (should be 0!)")


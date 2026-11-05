import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import shapely
from shapely.geometry import Polygon, MultiPolygon, LineString, box
import shapely.ops
import math

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# 1. SLAB
with open('scripts/checkpoint_basement_v1_base.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
slab_match = re.search(r'g_slab\s*=\s*extrude\((\[.*?\]),', text, re.DOTALL)
slab_poly = eval(slab_match.group(1))

# 2. COLUMNS (77 unique columns)
cols = []
for lname in ['A-col', 'P-1']:
    l = layers.get(lname)
    if not l: continue
    for i, c in enumerate(l['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4:
                try:
                    p = Polygon(pts)
                    if p.is_valid and 0.04 <= p.area <= 3.0:
                        xs = [pt[0] for pt in pts]
                        ys = [pt[1] for pt in pts]
                        dx = max(xs) - min(xs)
                        dy = max(ys) - min(ys)
                        if 0.20 <= dx <= 2.0 and 0.20 <= dy <= 2.0:
                            cols.append(p)
                except: pass

unique_cols = []
seen = set()
for cp in cols:
    center = (round(cp.centroid.x, 2), round(cp.centroid.y, 2))
    if center not in seen:
        seen.add(center)
        unique_cols.append(cp)

print(f"Total unique columns: {len(unique_cols)}")

# 3. WALLS
all_wall_polys = []

# A. Layer A-wall (closed polygons, open doorways)
l_wall = layers.get('A-wall')
if l_wall:
    for i, c in enumerate(l_wall['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4:
                try:
                    p = Polygon(pts)
                    if p.is_valid and p.area > 0.005:
                        all_wall_polys.append(p)
                except: pass

# B. Layer P-1 (0.50) item 2 (East retaining wall)
p1_50 = layers.get('P-1 (0.50)')
if p1_50:
    for i, c in enumerate(p1_50['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4:
                try:
                    p = Polygon(pts)
                    if p.is_valid and p.area > 5.0:
                        all_wall_polys.append(p)
                except: pass

# C. South Retaining Wall line at Y = -14.0m
south_ret_pts = [(3.969, -14.6), (9.071, -13.878), (9.039, -13.681), (3.941, -14.403)]
south_ret_poly = Polygon(south_ret_pts)
if south_ret_poly.is_valid:
    all_wall_polys.append(south_ret_poly)

# D. West Utility Room South Wall
west_util_pts = [(-18.299, 27.60), (-9.798, 27.60), (-9.798, 27.75), (-18.299, 27.75)]
west_util_poly = Polygon(west_util_pts)
if west_util_poly.is_valid:
    all_wall_polys.append(west_util_poly)

# E. Ramp Retaining Wall (WALL item 0)
ramp_wall = LineString([(9.781, 7.535), (10.697, 19.099)]).buffer(0.125, cap_style=2)
if ramp_wall.is_valid:
    all_wall_polys.append(ramp_wall)

# F. West Exterior Boundary Wall (WALL item 1)
west_ext_wall = LineString([(-19.701, 20.954), (-20.453, 16.468)]).buffer(0.125, cap_style=2)
if west_ext_wall.is_valid:
    all_wall_polys.append(west_ext_wall)

# G. NORTH PARKING ROOM COMPLEX (Behind Stalls 9-12)
p_north = Polygon([(0.077, 42.857), (10.727, 42.857), (10.727, 43.107), (0.077, 43.107)])
p_center_div = Polygon([(4.577, 27.607), (4.827, 27.607), (4.827, 42.857), (4.577, 42.857)])
p_mid_ew = Polygon([(0.402, 27.607), (10.402, 27.607), (10.402, 27.857), (0.402, 27.857)])
p_east_retaining = Polygon([(10.402, 18.851), (10.652, 18.851), (10.652, 43.107), (10.402, 43.107)])
p_west_north = Polygon([(0.152, 27.532), (0.402, 27.532), (0.402, 43.107), (0.152, 43.107)])
p_room1_2_div = Polygon([(0.152, 23.382), (10.402, 23.382), (10.402, 23.632), (0.152, 23.632)])
p_south_curb = Polygon([
    (0.152, 19.683), (10.652, 18.851),
    (10.652, 19.125), (0.152, 19.918)
])
p_west_room1 = Polygon([(0.152, 19.683), (0.402, 19.683), (0.402, 23.382), (0.152, 23.382)])
# Open doorway for Room 2 (Y in [24.819, 26.42] is left OPEN)
p_west_room2_south = Polygon([(0.152, 23.632), (0.402, 23.632), (0.402, 24.819), (0.152, 24.819)])
p_west_room2_north = Polygon([(0.152, 26.42), (0.402, 26.42), (0.402, 27.532), (0.152, 27.532)])

all_wall_polys.extend([
    p_north, p_center_div, p_mid_ew, p_east_retaining,
    p_west_north, p_room1_2_div, p_south_curb, p_west_room1,
    p_west_room2_south, p_west_room2_north
])

print(f"Total wall polygons before union: {len(all_wall_polys)}")

# 4. BOOLEAN UNION FOR MONOLITHIC INTEGRATION
combined = unique_cols + all_wall_polys
monolithic_union = shapely.ops.unary_union(combined)

if monolithic_union.geom_type == 'MultiPolygon':
    assemblies = list(monolithic_union.geoms)
elif monolithic_union.geom_type == 'Polygon':
    assemblies = [monolithic_union]

print(f"Total monolithic assemblies: {len(assemblies)}")
total_area = sum(a.area for a in assemblies)
print(f"Total monolithic structural area: {total_area:.2f} m^2")

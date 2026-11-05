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

# 1. LOAD SLAB POLYGON
with open('scripts/generated_basement_updated_payload.py', 'r', encoding='utf-8') as f:
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

print(f"Unique columns: {len(unique_cols)}")

# 3. WALLS - Comprehensive Collection from ALL Layers!
all_wall_polys = []

# Layer A-wall (closed polygons)
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

print(f"A-wall polygons: {len(all_wall_polys)}")

# Layer P-1 (0.50) item 2 (East retaining wall)
p1_50 = layers.get('P-1 (0.50)')
if p1_50:
    for i, c in enumerate(p1_50['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4:
                try:
                    p = Polygon(pts)
                    # Filter: keep the true retaining wall along the east boundary (area > 5m^2)
                    if p.is_valid and p.area > 5.0:
                        all_wall_polys.append(p)
                except: pass

# Layer P-1 (0.50) items 0 and 1: South Retaining Wall!
# In CAD: item 0: (3.969, -14.6) -> (9.071, -13.878), item 1: (3.941, -14.403) -> (9.039, -13.681)
# Create a 4-point closed polygon between these two parallel lines:
south_ret_pts = [(3.969, -14.6), (9.071, -13.878), (9.039, -13.681), (3.941, -14.403)]
south_ret_poly = Polygon(south_ret_pts)
if south_ret_poly.is_valid:
    all_wall_polys.append(south_ret_poly)
    print("Added South Retaining Wall (P-1 0.50) polygon!")

# Layer P-3 items 0 and 1: West Utility Room South Wall!
# item 0: (-18.299, 27.657) -> (-9.798, 27.657), item 1: (-18.299, 27.706) -> (-9.798, 27.706)
# Thickness is 0.15m:
west_util_pts = [(-18.299, 27.60), (-9.798, 27.60), (-9.798, 27.75), (-18.299, 27.75)]
west_util_poly = Polygon(west_util_pts)
if west_util_poly.is_valid:
    all_wall_polys.append(west_util_poly)
    print("Added West Utility Room Wall (P-3) polygon!")

# Layer WALL item 3: North boundary wall (-19.657, 21.503) -> (10.689, 18.998)
# Buffer line by 0.10m to create 0.20m thick wall:
line_wall = LineString([(-19.657, 21.503), (-1.0, 20.0), (10.689, 18.998)])
poly_north_wall = line_wall.buffer(0.10, cap_style=2) # cap_style=2 is flat
if poly_north_wall.is_valid:
    all_wall_polys.append(poly_north_wall)
    print("Added North Boundary Wall (WALL) polygon!")

print(f"Total full-height wall polygons to union: {len(all_wall_polys)}")

# 4. PERFORM MONOLITHIC BOOLEAN UNION WITH COLUMNS!
combined = unique_cols + all_wall_polys
monolithic_union = shapely.ops.unary_union(combined)

if monolithic_union.geom_type == 'MultiPolygon':
    assemblies = list(monolithic_union.geoms)
elif monolithic_union.geom_type == 'Polygon':
    assemblies = [monolithic_union]

print(f"Total Monolithic Assemblies generated: {len(assemblies)}")



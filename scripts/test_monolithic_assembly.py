import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import shapely
from shapely.geometry import Polygon, MultiPolygon, LineString, Point
import shapely.ops
import json
import math

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# 1. LOAD SLAB POLYGON
with open('scripts/generated_basement_updated_payload.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
slab_match = re.search(r'g_slab\s*=\s*extrude\((\[.*?\]),', text, re.DOTALL)
slab_poly = eval(slab_match.group(1))
print(f"Loaded slab polygon: {len(slab_poly)} points")

# 2. LOAD ALL 77 STRUCTURAL COLUMNS
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
                    # Filter for real columns: area between 0.04 and 3.0 m^2
                    if p.is_valid and 0.04 <= p.area <= 3.0:
                        xs = [pt[0] for pt in pts]
                        ys = [pt[1] for pt in pts]
                        dx = max(xs) - min(xs)
                        dy = max(ys) - min(ys)
                        if 0.20 <= dx <= 2.0 and 0.20 <= dy <= 2.0:
                            cols.append((f"{lname}_{i}", p))
                except: pass

print(f"Extracted valid columns: {len(cols)}")

# Deduplicate columns if any share the same centroid
unique_cols = []
seen_centers = set()
for name, cp in cols:
    cx, cy = round(cp.centroid.x, 2), round(cp.centroid.y, 2)
    if (cx, cy) not in seen_centers:
        seen_centers.add((cx, cy))
        unique_cols.append((name, cp))

print(f"Unique structural columns: {len(unique_cols)}")

# 3. LOAD FULL-HEIGHT WALLS (A-wall, P-1 (0.50))
wall_polys = []
l_wall = layers.get('A-wall')
for i, c in enumerate(l_wall['kind']['children']):
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        if len(pts) >= 4:
            try:
                p = Polygon(pts)
                if p.is_valid and p.area > 0.005:
                    wall_polys.append((f"A_wall_{i}", p))
            except: pass

print(f"Valid A-wall polygons: {len(wall_polys)}")

# Retaining wall P-1 (0.50) item 2
p1_50 = layers.get('P-1 (0.50)')
if p1_50:
    for i, c in enumerate(p1_50['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4:
                try:
                    p = Polygon(pts)
                    if p.is_valid and p.area > 0.5:
                        wall_polys.append((f"RetainingWall_{i}", p))
                except: pass

print(f"Total full-height wall polygons: {len(wall_polys)}")

# 4. PERFORM 2D MONOLITHIC BOOLEAN UNION
# Union columns and walls together!
all_column_geoms = [p for _, p in unique_cols]
all_wall_geoms = [p for _, p in wall_polys]

# Combine all shapes
combined_shapes = all_column_geoms + all_wall_geoms
monolithic_union = shapely.ops.unary_union(combined_shapes)

print(f"\nMonolithic Union result type: {monolithic_union.geom_type}")

monolithic_assemblies = []
if monolithic_union.geom_type == 'MultiPolygon':
    for idx, poly in enumerate(monolithic_union.geoms):
        monolithic_assemblies.append(poly)
elif monolithic_union.geom_type == 'Polygon':
    monolithic_assemblies.append(monolithic_union)

print(f"Total Monolithic 3D Prisms to generate: {len(monolithic_assemblies)}")

# 5. RESTROOM PARTITIONS (P-4 (0.10) - height 2.20m)
partitions = []
l_part = layers.get('P-4 (0.10)')
if l_part:
    for i, c in enumerate(l_part['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) == 2:
                p0, p1 = pts[0], pts[1]
                length = math.hypot(p1[0]-p0[0], p1[1]-p0[1])
                # Filter for restroom partition lines (0.4m to 3.0m)
                if 0.40 <= length <= 3.5:
                    partitions.append((p0, p1, length))

print(f"Restroom partitions extracted: {len(partitions)}")


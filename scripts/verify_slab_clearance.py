from shapely.geometry import Polygon, Point
import json

# Define master smooth slab polygon (no jagged notches)
slab_pts = [
    (-26.5, 44.0),
    (-26.5, -17.5),
    (2.5, -17.5),
    (2.5, -23.0),
    (10.5, -23.0),
    (10.5, -18.0),
    (17.5, -18.0),
    (22.5, -14.5),
    (32.0, -10.0),
    (42.5, -6.0),
    (53.0, -1.5),
    (66.5, 3.5),
    (68.5, 7.5),
    (68.5, 23.5),
    (33.0, 23.5),
    (33.0, 44.0),
    (-26.5, 44.0)
]

slab_poly = Polygon(slab_pts)

# Load F00 & F01 columns
from scripts.extract_f00_columns import pure_cols as f00_cols
from scripts.extract_pure_columns import pure_cols as f01_cols

print(f"Slab Area: {slab_poly.area:.2f} m2")

# Check F00 columns
f00_outside = []
f00_min_dist = 999.0
for pts, cx, cy, dx, dy, area in f00_cols:
    pt = Point(cx, cy)
    if not slab_poly.contains(pt):
        f00_outside.append((cx, cy))
    dist = slab_poly.exterior.distance(pt)
    if dist < f00_min_dist:
        f00_min_dist = dist

# Check F01 columns
f01_outside = []
f01_min_dist = 999.0
for pts, cx, cy, dx, dy, area in f01_cols:
    pt = Point(cx, cy)
    if not slab_poly.contains(pt):
        f01_outside.append((cx, cy))
    dist = slab_poly.exterior.distance(pt)
    if dist < f01_min_dist:
        f01_min_dist = dist

print(f"F00 cols outside slab: {len(f00_outside)}, Min margin: {f00_min_dist:.2f} m")
print(f"F01 cols outside slab: {len(f01_outside)}, Min margin: {f01_min_dist:.2f} m")


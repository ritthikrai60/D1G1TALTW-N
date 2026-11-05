import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
import shapely.ops
from PIL import Image, ImageDraw
import os

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

print("=== COMPLETE AUDIT OF ALL ROOMS AND WALLS ===")

# Check layer A-wall polygons by region:
l_wall = layers.get('A-wall')
wall_polys = []
for i, c in enumerate(l_wall['kind']['children']):
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        if len(pts) >= 4:
            try:
                p = Polygon(pts)
                if p.is_valid and p.area > 0.005:
                    wall_polys.append((i, p))
            except: pass

print(f"Total A-wall valid polygons: {len(wall_polys)}")

# Group walls by zone:
zones = {
    'Core (Restrooms, ST-1, Locker)': box(3.0, -15.0, 15.0, 10.0),
    'West Utility Rooms': box(-22.0, 20.0, 3.0, 38.0),
    'North MEP / Storage': box(-15.0, 38.0, 20.0, 60.0),
    'South Zone': box(-5.0, -25.0, 15.0, -14.0)
}

for zname, zbox in zones.items():
    z_walls = [p for i, p in wall_polys if p.intersects(zbox)]
    print(f"Zone '{zname}': {len(z_walls)} A-wall polygons")

# Check layer 'WALL'
l_w = layers.get('WALL')
if l_w:
    print(f"\nLayer 'WALL' ({len(l_w['kind']['children'])} items):")
    for i, c in enumerate(l_w['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            print(f"  item {i}: {len(pts)} pts, p0={pts[0]}, p1={pts[-1]}")

# Check layer 'P-1 (0.50)'
l_p1_50 = layers.get('P-1 (0.50)')
if l_p1_50:
    print(f"\nLayer 'P-1 (0.50)' ({len(l_p1_50['kind']['children'])} items):")
    for i, c in enumerate(l_p1_50['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            print(f"  item {i}: {len(pts)} pts, p0={pts[0]}, p1={pts[-1]}")



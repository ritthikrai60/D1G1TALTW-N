import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import shapely
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Inspect A-wall closed polygons
a_wall = layers['A-wall']
closed_polys = []
for i, c in enumerate(a_wall['kind']['children']):
    sps = extract_subpaths(c)
    for sp in sps:
        pts = [to_m(p) for p in sp['anchors']]
        if len(pts) >= 4 and sp['closed']:
            poly = Polygon(pts)
            if poly.is_valid and poly.area > 0.01:
                bounds = poly.bounds
                closed_polys.append((i, poly, bounds))

print(f"Valid closed polygons in A-wall: {len(closed_polys)}")
for i, poly, b in closed_polys[:15]:
    print(f"  Wall {i:2d}: Area={poly.area:.2f} m^2, Bounds: X=[{b[0]:.2f}, {b[2]:.2f}], Y=[{b[1]:.2f}, {b[3]:.2f}]")

# Inspect P-1 (0.50)
p1_50 = layers.get('P-1 (0.50)')
if p1_50:
    print("\n=== P-1 (0.50) Retaining Wall ===")
    for i, c in enumerate(p1_50['kind']['children']):
        sps = extract_subpaths(c)
        for sp in sps:
            pts = [to_m(p) for p in sp['anchors']]
            print(f"  P-1 (0.50) item {i}: {len(pts)} pts, p0={pts[0]}, p1={pts[-1]}")



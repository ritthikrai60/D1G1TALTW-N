import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from shapely.geometry import Polygon, LineString
import math

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

print("=== WALL STRUCTURE ANALYSIS ===")

for lname in ['A-wall', 'WALL', 'P-1 (0.50)', 'P-4 (0.10)', 'P-2 (0.15)', 'P-3 (0.25)']:
    l = layers.get(lname)
    if not l: continue
    
    closed_boxes = []
    lines = []
    
    for i, c in enumerate(l['kind']['children']):
        sps = extract_subpaths(c)
        for sp in sps:
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4 and (pts[0] == pts[-1] or sp['closed']):
                try:
                    poly = Polygon(pts)
                    if poly.is_valid and poly.area > 0.001:
                        closed_boxes.append((i, poly))
                except: pass
            elif len(pts) >= 2:
                # polyline
                lines.append((i, pts))
    
    print(f"\nLayer '{lname}': {len(closed_boxes)} closed polygons, {len(lines)} open lines/polylines")
    if closed_boxes:
        print("  Sample closed boxes (thickness / area):")
        for i, p in closed_boxes[:5]:
            minx, miny, maxx, maxy = p.bounds
            print(f"    item {i:2d}: size=({maxx-minx:.2f} x {maxy-miny:.2f} m), area={p.area:.3f} m^2, bounds: X=[{minx:.2f}, {maxx:.2f}], Y=[{miny:.2f}, {maxy:.2f}]")
    if lines:
        print("  Sample lines (endpoints / length):")
        for i, pts in lines[:5]:
            p0, p1 = pts[0], pts[-1]
            length = math.hypot(p1[0]-p0[0], p1[1]-p0[1])
            print(f"    item {i:2d}: pts={len(pts)}, len={length:.2f} m, {p0} -> {p1}")



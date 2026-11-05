import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from shapely.geometry import Polygon, MultiPolygon, LineString

doc = load_pdf_doc()['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Let's inspect long lines (length > 10m) across the entire CAD file
long_lines = []
for l in doc['layers']:
    lname = l['name']
    for i, c in enumerate(l['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 2:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                dx = max(xs) - min(xs)
                dy = max(ys) - min(ys)
                import math
                p0, p1 = pts[0], pts[-1]
                dist = math.hypot(p1[0]-p0[0], p1[1]-p0[1])
                if dx > 15.0 or dy > 15.0 or dist > 15.0:
                    long_lines.append((lname, i, len(pts), min(xs), max(xs), min(ys), max(ys), pts))

print(f"Total long lines (> 15m): {len(long_lines)}")
for ll in long_lines:
    print(f"Layer {ll[0]:15s} child {ll[1]:2d}: pts={ll[2]}, X=[{ll[3]:6.2f}, {ll[4]:6.2f}], Y=[{ll[5]:6.2f}, {ll[6]:6.2f}]")


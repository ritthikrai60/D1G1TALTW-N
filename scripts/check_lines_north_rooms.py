import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import math

doc = load_pdf_doc()['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

print("=== CHECKING ALL 2-POINT LINES IN ZONE X in [0, 12], Y in [20, 38] ===")

for l in doc['layers']:
    lname = l['name']
    found = []
    for i, c in enumerate(l['kind'].get('children', [])):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) == 2:
                p0, p1 = pts[0], pts[1]
                xs = [p0[0], p1[0]]
                ys = [p0[1], p1[1]]
                if min(xs) >= -1.0 and max(xs) <= 12.0 and min(ys) >= 20.0 and max(ys) <= 38.0:
                    dist = math.hypot(p1[0]-p0[0], p1[1]-p0[1])
                    if dist > 0.5:
                        found.append((i, dist, p0, p1))
    if found:
        print(f"\nLayer '{lname}' has {len(found)} wall lines:")
        for i, dist, p0, p1 in found:
            print(f"  item {i:3d}: len={dist:5.2f}m, {p0} -> {p1}")



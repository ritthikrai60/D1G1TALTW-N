import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import math

doc = load_pdf_doc()['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

print("=== ALL ELEMENTS IN ZONE X in [0, 11], Y in [21, 37] ===")

for l in doc['layers']:
    lname = l['name']
    found = []
    for i, c in enumerate(l['kind'].get('children', [])):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if min(xs) >= -1.0 and max(xs) <= 12.0 and min(ys) >= 20.0 and max(ys) <= 38.0:
                p0, p1 = pts[0], pts[-1]
                length = math.hypot(p1[0]-p0[0], p1[1]-p0[1])
                found.append((i, len(pts), length, p0, p1, sp['closed']))
    if found:
        print(f"\nLayer '{lname}': {len(found)} items")
        for i, npts, length, p0, p1, closed in found[:15]:
            print(f"  item {i:3d}: pts={npts}, len={length:5.2f}m, closed={closed}, {p0} -> {p1}")



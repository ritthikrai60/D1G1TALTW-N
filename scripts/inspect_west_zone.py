import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import math

doc = load_pdf_doc()['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

print("=== WEST UTILITY ZONE DETAILS ===")
for lname in ['WALL', 'P-4', 'P-3', 'A-wall']:
    l = [x for x in doc['layers'] if x['name'] == lname][0]
    for i, c in enumerate(l['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if min(xs) < 2.0 and max(xs) > -15.0 and min(ys) < 36.0 and max(ys) > 18.0:
                p0, p1 = pts[0], pts[-1]
                length = math.hypot(p1[0]-p0[0], p1[1]-p0[1])
                print(f"Layer {lname:8s} item {i:2d}: pts={len(pts)}, len={length:.2f} m, {p0} -> {p1}")


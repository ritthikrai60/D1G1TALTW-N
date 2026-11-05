import sys, math
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import numpy as np

doc = load_pdf_doc('00-Ground_Floor-Clean.pdf')['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

l_stair = next(x for x in doc['layers'] if x['name'] == 'A-stair')
east_pts = []
for idx, c in enumerate(l_stair['kind']['children']):
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        if any(50.0 <= p[0] <= 65.0 and 5.0 <= p[1] <= 18.0 for p in pts):
            east_pts.extend(pts)

print(f"East stair points in F00: {len(east_pts)}")
if east_pts:
    xs = [p[0] for p in east_pts]
    ys = [p[1] for p in east_pts]
    print(f"East stair bounds: X=[{min(xs)}, {max(xs)}], Y=[{min(ys)}, {max(ys)}]")


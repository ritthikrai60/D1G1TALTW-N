import sys, math
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import numpy as np

doc = load_pdf_doc('00-Ground_Floor-Clean.pdf')['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

l_stair = next(x for x in doc['layers'] if x['name'] == 'A-stair')
st1_pts = []
for idx, c in enumerate(l_stair['kind']['children']):
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        if any(8.0 <= p[0] <= 11.5 and -14.0 <= p[1] <= -6.5 for p in pts):
            st1_pts.extend(pts)

xs = [p[0] for p in st1_pts]
ys = [p[1] for p in st1_pts]
print(f"ST-1 points: {len(st1_pts)}, X=[{min(xs)}, {max(xs)}], Y=[{min(ys)}, {max(ys)}]")

# Calculate angle of riser lines
risers = []
for idx, c in enumerate(l_stair['kind']['children']):
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        if len(pts) == 2 and any(8.0 <= p[0] <= 11.5 and -14.0 <= p[1] <= -6.5 for p in pts):
            dx = pts[1][0] - pts[0][0]
            dy = pts[1][1] - pts[0][1]
            length = math.hypot(dx, dy)
            if 0.8 <= length <= 1.4:
                angle = math.degrees(math.atan2(dy, dx))
                risers.append((pts[0], pts[1], angle, length))

print(f"Found {len(risers)} riser segments in ST-1")
angles = [r[2] for r in risers]
print(f"Riser angles: min={min(angles):.2f}°, max={max(angles):.2f}°, mean={np.mean(angles):.2f}°")
for r in risers[:6]:
    print(f"  {r[0]} -> {r[1]}, angle={r[2]:.2f}°, len={r[3]:.2f}m")

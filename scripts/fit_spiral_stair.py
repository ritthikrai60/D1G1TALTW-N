import zlib, re, json
import numpy as np

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Collect points from P-5 child 240-270 (the outer circle of spiral stair)
import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths

l_p5 = next((x for x in doc['layers'] if x['name'] == 'P-5'), None)
circle_pts = []
for idx in range(240, 280):
    if idx < len(l_p5['kind']['children']):
        c = l_p5['kind']['children'][idx]
        for sp in extract_subpaths(c):
            for p in sp['anchors']:
                pt = to_m(p)
                if 21 <= pt[0] <= 25 and -5 <= pt[1] <= -2:
                    circle_pts.append(pt)

pts = np.array(circle_pts)
print(f"Collected {len(pts)} points for spiral stair outer ring")
# Fit circle: (x - xc)^2 + (y - yc)^2 = R^2
# x^2 - 2*x*xc + xc^2 + y^2 - 2*y*yc + yc^2 = R^2
# 2*x*xc + 2*y*yc + c = x^2 + y^2
A = np.column_stack([2*pts[:, 0], 2*pts[:, 1], np.ones(len(pts))])
b = pts[:, 0]**2 + pts[:, 1]**2
res, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
xc, yc = res[0], res[1]
R = np.sqrt(res[2] + xc**2 + yc**2)
print(f"Spiral Stair Outer Ring: Center = ({xc:.3f}, {yc:.3f}), Radius = {R:.3f} m (Diameter = {2*R:.3f} m)")

# Let's inspect the treads (step lines) of this spiral stair
l_wall = next((x for x in doc['layers'] if x['name'] == 'WALL'), None)
treads = []
for idx in range(300, 350):
    if idx < len(l_wall['kind']['children']):
        c = l_wall['kind']['children'][idx]
        for sp in extract_subpaths(c):
            p_m = [to_m(p) for p in sp['anchors']]
            if len(p_m) == 2 and any(21 <= pt[0] <= 25 and -5 <= pt[1] <= -2 for pt in p_m):
                treads.append((p_m[0], p_m[1], idx))

print(f"Found {len(treads)} tread lines in WALL layer")
for t in treads[:10]:
    print(f"  tread: {t[0]} -> {t[1]} (child {t[2]})")


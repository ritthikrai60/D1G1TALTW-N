import zlib, re, json
import numpy as np
import math

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

xc, yc = 22.586, -4.264
R_out = 1.400

import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths

l_wall = next((x for x in doc['layers'] if x['name'] == 'WALL'), None)
treads = []
for idx in range(300, 360):
    if idx < len(l_wall['kind']['children']):
        c = l_wall['kind']['children'][idx]
        for sp in extract_subpaths(c):
            p_m = [to_m(p) for p in sp['anchors']]
            if len(p_m) == 2:
                p1, p2 = p_m[0], p_m[1]
                d1 = math.hypot(p1[0]-xc, p1[1]-yc)
                d2 = math.hypot(p2[0]-xc, p2[1]-yc)
                if abs(d1 - R_out) < 0.25 or abs(d2 - R_out) < 0.25:
                    r_inner = min(d1, d2)
                    r_outer = max(d1, d2)
                    angle = math.degrees(math.atan2(p2[1]-yc, p2[0]-xc))
                    treads.append((p1, p2, r_inner, r_outer, angle, idx))

print(f"Found {len(treads)} spiral tread lines matching outer radius {R_out:.2f} m")
inner_radii = [t[2] for t in treads]
print(f"Inner radius range: {min(inner_radii):.3f} to {max(inner_radii):.3f} m (avg: {np.mean(inner_radii):.3f} m)")

# Let's inspect unique tread angles
angles = sorted([math.degrees(math.atan2(t[1][1]-yc, t[1][0]-xc)) % 360 for t in treads])
print(f"Sample angles: {[round(a, 1) for a in angles[:12]]}")


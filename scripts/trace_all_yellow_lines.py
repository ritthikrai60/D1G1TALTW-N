import zlib, re
from PIL import Image, ImageDraw
import os

with open(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf', 'rb') as f:
    data = f.read()

streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s0 = zlib.decompress(streams[0]).decode('latin1', errors='ignore')

# The transformation matrix in Stream 0:
# '1 0 0 -1 0 2384 cm'
# In PDF: y_pdf = 2384 - y_vc
# VectorCraft: pt = (x_vc, y_vc)
# Then to_m: xm = (x_vc - 1000)/28.346, ym = -(y_vc - 1500)/28.346

blocks = s0.split('1 1 0 RG')
yellow_lines = []

for b in blocks[1:]:
    # Get stroke path
    ops = re.findall(r'([-\d\.]+\s+[-\d\.]+\s+[ml])', b.split('S')[0].split('s')[0])
    pts = []
    for op in ops:
        p = op.split()
        x_pt, y_pdf = float(p[0]), float(p[1])
        y_vc = 2384.0 - y_pdf
        xm = (x_pt - 1000.0) / 28.3464567
        ym = -(y_vc - 1500.0) / 28.3464567
        pts.append((round(xm, 3), round(ym, 3)))
    if len(pts) >= 2:
        yellow_lines.append(pts)

print(f"Total yellow lines: {len(yellow_lines)}")
for idx, l in enumerate(yellow_lines):
    p0, p1 = l[0], l[-1]
    import math
    dist = math.hypot(p1[0]-p0[0], p1[1]-p0[1])
    print(f"L{idx:2d}: pts={len(l)}, len={dist:.2f}m, ({p0[0]:.2f}, {p0[1]:.2f}) -> ({p1[0]:.2f}, {p1[1]:.2f})")



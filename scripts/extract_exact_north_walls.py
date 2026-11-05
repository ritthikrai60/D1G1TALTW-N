import zlib, re

with open(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf', 'rb') as f:
    data = f.read()

streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s0 = zlib.decompress(streams[0]).decode('latin1', errors='ignore')

blocks = s0.split('1 1 0 RG')
yellow_lines = []

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567

for b in blocks[1:]:
    ops = re.findall(r'([-\d\.]+\s+[-\d\.]+\s+[ml])', b.split('S')[0].split('s')[0])
    pts = []
    for op in ops:
        p = op.split()
        x_pt, y_pdf = float(p[0]), float(p[1])
        # In PDF: y_pdf = 0 at bottom, 2384 at top.
        # VectorCraft y_vc = 2384 - y_pdf
        # Then ym = -(y_vc - 1500)/SCALE = (y_pdf - 2384 + 1500)/SCALE = (y_pdf - 884)/SCALE ???
        # Wait! Let's check a column whose coordinates we KNOW:
        # Col 0 was at x=6.111, ym=+7.425!
        # In PDF stream 0, where is Col 0?
        # Let's find out!
        pass

# Let's search for (6.111, 7.425) in Stream 0:
# x_pt = 1000 + 6.111 * 28.346 = 1173.2 pt
# ym = +7.425 -> y_vc = 1500 - 7.425 * 28.346 = 1289.5 pt
# y_pdf = 2384 - 1289.5 = 1094.5 pt!
# So: ym = (y_pdf - 884) / 28.346 ???
# Let's check: (1094.5 - 884) / 28.346 = 210.5 / 28.346 = 7.425!
# YES! ym = (y_pdf - 884.0) / 28.3464567!
# And xm = (x_pt - 1000.0) / 28.3464567!

for b in blocks[1:]:
    ops = re.findall(r'([-\d\.]+\s+[-\d\.]+\s+[ml])', b.split('S')[0].split('s')[0])
    pts = []
    for op in ops:
        p = op.split()
        x_pt, y_pdf = float(p[0]), float(p[1])
        xm = (x_pt - 1000.0) / SCALE
        ym = (y_pdf - 884.0) / SCALE
        pts.append((round(xm, 3), round(ym, 3)))
    if len(pts) >= 2:
        yellow_lines.append(pts)

print(f"Total yellow lines: {len(yellow_lines)}")
# Filter for lines with length > 0.5m
import math
real_walls = []
for idx, l in enumerate(yellow_lines):
    dist = math.hypot(l[-1][0]-l[0][0], l[-1][1]-l[0][1])
    if dist > 0.5:
        real_walls.append((dist, l[0], l[-1]))
        print(f"Wall {len(real_walls)}: len={dist:5.2f}m, {l[0]} -> {l[-1]}")



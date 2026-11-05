import zlib, re

with open(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf', 'rb') as f:
    data = f.read()

streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s0 = zlib.decompress(streams[0]).decode('latin1', errors='ignore')

# Split by graphic state or find blocks where '1 1 0 RG' is active
# In PDF: '1 1 0 RG' sets stroke color to yellow. Then follows path construction: m (moveto), l (lineto), c (curveto), S (stroke) or s (close and stroke).
blocks = s0.split('1 1 0 RG')
print(f"Blocks after '1 1 0 RG': {len(blocks)-1}")

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

yellow_paths = []
for b in blocks[1:]:
    # Find up to the next color operator or 'Q' (restore state)
    # Extract coordinates: numbers followed by m, l, c, S, s
    # e.g. 1234.56 789.01 m 1234.56 800.00 l S
    ops = re.findall(r'([-\d\.]+\s+[-\d\.]+\s+[ml])', b[:500])
    pts = []
    for op in ops:
        parts = op.split()
        x, y = float(parts[0]), float(parts[1])
        # In PDF spec: y is from bottom (y_pdf = 2384 - y_vc)
        # So y_vc = 2384 - y_pdf
        # Then xm = (x - X0)/SCALE, ym = -(y_vc - Y0)/SCALE
        y_vc = 2384.0 - y
        pts.append((round((x - X0)/SCALE, 3), round(-(y_vc - Y0)/SCALE, 3)))
    if len(pts) >= 2:
        yellow_paths.append(pts)

print(f"Extracted {len(yellow_paths)} yellow paths!")
for idx, p in enumerate(yellow_paths[:20]):
    print(f"Yellow path {idx}: pts={len(p)}, p0={p[0]}, p1={p[-1]}")


import zlib, re, json
import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths
import math

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Let's inspect all 2-point lines in the central zone: X in [15, 45], Y in [-5, 20]
# across ALL layers!
lines_by_layer = {}
for l in doc['layers']:
    lname = l['name']
    lines = []
    for idx, c in enumerate(l['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) == 2:
                p1, p2 = pts[0], pts[1]
                if 15 <= p1[0] <= 45 and -5 <= p1[1] <= 20 and 15 <= p2[0] <= 45 and -5 <= p2[1] <= 20:
                    length = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
                    if 0.5 <= length <= 6.0:
                        angle = math.degrees(math.atan2(p2[1]-p1[1], p2[0]-p1[0])) % 180
                        lines.append((p1, p2, length, angle, idx))
    if lines:
        lines_by_layer[lname] = lines

print("=== 2-point lines in central lobby area ===")
for lname, lns in lines_by_layer.items():
    # check diversity of angles (spiral stairs have steps at many different angles!)
    angles = [round(ln[3], 1) for ln in lns]
    unique_angles = len(set([round(a/5)*5 for a in angles])) # rounded to 5 deg
    print(f"Layer '{lname:25s}': {len(lns):3d} lines, {unique_angles:2d} distinct angle bins")
    if unique_angles > 5 and len(lns) > 8:
        print(f"   --> High angle diversity! Potential spiral stair or curved feature!")
        # print first few
        for ln in lns[:5]:
            print(f"       p1={ln[0]}, p2={ln[1]}, len={ln[2]:.2f}, angle={ln[3]:.1f}° (child {ln[4]})")


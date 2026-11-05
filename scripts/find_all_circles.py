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

# Let's search all circles or arcs in the drawing!
# In PDF/SVG paths, circles are often drawn as 4 cubic beziers or closed paths with ~4 to 12 anchors
circles = []
for l in doc['layers']:
    for idx, c in enumerate(l['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4 and sp['closed']:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                dx = max(xs) - min(xs)
                dy = max(ys) - min(ys)
                # check if approximately circular (aspect ratio ~ 1.0)
                if 0.5 <= dx <= 10.0 and 0.5 <= dy <= 10.0 and abs(dx - dy) < 0.2:
                    cx = (min(xs) + max(xs)) / 2
                    cy = (min(ys) + max(ys)) / 2
                    circles.append((l['name'], idx, round(cx, 2), round(cy, 2), round(dx, 2), round(dy, 2), len(pts)))

print(f"Total circle candidates: {len(circles)}")
# group circles by center
from collections import defaultdict
grouped = defaultdict(list)
for c in circles:
    key = (round(c[2], 1), round(c[3], 1))
    grouped[key].append(c)

for key, clist in sorted(grouped.items()):
    if len(clist) >= 2:
        print(f"Concentric Circle cluster at Center {key}: {len(clist)} circles")
        for item in clist[:5]:
            print(f"   Layer: {item[0]}, child {item[1]}, D=({item[4]}, {item[5]}), pts={item[6]}")


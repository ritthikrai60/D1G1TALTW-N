import zlib, re, json
import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths
from shapely.geometry import Point, LineString, Polygon

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

print("=== Elements in Spiral Stair Region: X in [20, 26], Y in [-5, 0] ===")
elements_in_box = []
for l in doc['layers']:
    lname = l['name']
    for idx, c in enumerate(l['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if any(20 <= x <= 26 and -5 <= y <= 0 for x, y in zip(xs, ys)):
                elements_in_box.append((lname, idx, sp['closed'], pts))

print(f"Total paths in region: {len(elements_in_box)}")
# Group by layer
by_layer = {}
for lname, idx, closed, pts in elements_in_box:
    by_layer.setdefault(lname, []).append((idx, closed, pts))

for lname, items in by_layer.items():
    print(f"Layer '{lname}': {len(items)} paths")
    for idx, closed, pts in items[:8]:
        print(f"   child {idx}, closed={closed}, len={len(pts)}, pts={pts[:3]}...")


import zlib, re, json
import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
from shapely.ops import unary_union

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Inspect P-2 (0.15) which usually contains slab perimeters
l_p2_15 = next((x for x in doc['layers'] if x['name'] == 'P-2 (0.15)'), None)
print("=== P-2 (0.15) Children ===")
for idx, c in enumerate(l_p2_15['kind']['children']):
    for sp_idx, sp in enumerate(extract_subpaths(c)):
        pts = [to_m(p) for p in sp['anchors']]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        dx = max(xs) - min(xs)
        dy = max(ys) - min(ys)
        if dx > 10 or dy > 10:
            print(f"Child {idx:2d} (sp {sp_idx}): closed={sp['closed']}, len={len(pts)}, dx={dx:.2f}, dy={dy:.2f}, X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}]")

# Also check P-1 (0.50)
l_p1_50 = next((x for x in doc['layers'] if x['name'] == 'P-1 (0.50)'), None)
if l_p1_50:
    print("\n=== P-1 (0.50) Children ===")
    for idx, c in enumerate(l_p1_50['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            dx = max(xs) - min(xs)
            dy = max(ys) - min(ys)
            if dx > 10 or dy > 10:
                print(f"Child {idx:2d}: closed={sp['closed']}, len={len(pts)}, dx={dx:.2f}, dy={dy:.2f}, X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}]")


import sys, zlib, re, json
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths
from shapely.geometry import Polygon

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)

doc = meta['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

print('Large paths in F01:')
for l in doc['layers']:
    lname = l['name']
    for i, c in enumerate(l['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 10:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                dx = max(xs) - min(xs)
                dy = max(ys) - min(ys)
                if dx > 30 or dy > 30:
                    print(f'{lname} child {i}: pts={len(pts)}, dx={dx:.1f}, dy={dy:.1f}, X=[{min(xs):.1f}, {max(xs):.1f}], Y=[{min(ys):.1f}, {max(ys):.1f}]')


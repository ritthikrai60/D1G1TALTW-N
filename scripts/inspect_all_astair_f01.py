import zlib, re, json
import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths
from shapely.geometry import Polygon, LineString

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

l_stair = next((x for x in doc['layers'] if x['name'] == 'A-stair'), None)
print(f"Total children in A-stair: {len(l_stair['kind']['children'])}")

for idx, c in enumerate(l_stair['kind']['children']):
    sps = extract_subpaths(c)
    for sp_idx, sp in enumerate(sps):
        pts = [to_m(p) for p in sp['anchors']]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        closed = sp.get('closed', False)
        print(f"Child {idx:2d} (sp {sp_idx}): closed={closed}, len={len(pts):2d}, X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}]")


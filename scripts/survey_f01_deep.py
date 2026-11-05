import zlib, re, json
import sys
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

print("=== Layers in F01 and children count ===")
for l in doc['layers']:
    if l['kind']['children']:
        print(f"  {l['name']:25s}: {len(l['kind']['children'])} elements")

# Survey columns in F01:
cols = []
for lname in ['A-col', 'P-1', '01-AE-Floor Post']:
    l = next((x for x in doc['layers'] if x['name'] == lname), None)
    if not l: continue
    for i, c in enumerate(l['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4:
                try:
                    p = Polygon(pts)
                    if p.is_valid and 0.04 <= p.area <= 3.0:
                        xs = [pt[0] for pt in pts]
                        ys = [pt[1] for pt in pts]
                        dx = max(xs) - min(xs)
                        dy = max(ys) - min(ys)
                        if 0.20 <= dx <= 2.0 and 0.20 <= dy <= 2.0:
                            cols.append(p)
                except: pass

unique_cols = []
seen = set()
for cp in cols:
    center = (round(cp.centroid.x, 2), round(cp.centroid.y, 2))
    if center not in seen:
        seen.add(center)
        unique_cols.append(cp)

print(f"\nTotal unique columns found in F01: {len(unique_cols)}")

# Survey stairs in F01:
stair_elements = []
l_stair = next((x for x in doc['layers'] if x['name'] == 'A-stair'), None)
if l_stair:
    print(f"Total elements in A-stair: {len(l_stair['kind']['children'])}")

# Check for curved spiral stair in lobby (radius around center)
l_sym = next((x for x in doc['layers'] if x['name'] == 'SYMBOL' or x['name'] == 'A-stair'), None)


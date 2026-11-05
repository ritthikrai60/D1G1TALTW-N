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

with open('scripts/f01_columns.json', 'r') as f:
    cols_data = json.load(f)

cols = [Polygon(c['coords']) for c in cols_data]
col_union = unary_union(cols)

# Let's inspect P-2 (0.15) child 74
l_p2_15 = next((x for x in doc['layers'] if x['name'] == 'P-2 (0.15)'), None)
c74_pts = [to_m(p) for p in extract_subpaths(l_p2_15['kind']['children'][74])[0]['anchors']]

print("=== Child 74 points sample ===")
for p in c74_pts[::4]:
    print(f"  {p}")

# Let's check south boundary lines in P-4 or P-2
# Let's see what lines form the south façade:
south_pts = []
for l in doc['layers']:
    if l['name'] in ['P-2 (0.15)', 'P-2', 'P-1', 'WALL', 'A-wall']:
        for idx, c in enumerate(l['kind']['children']):
            for sp in extract_subpaths(c):
                pts = [to_m(p) for p in sp['anchors']]
                if len(pts) > 10:
                    xs = [p[0] for p in pts]
                    ys = [p[1] for p in pts]
                    if min(ys) < -10 and max(xs) > 20:
                        print(f"Layer '{l['name']}' child {idx}: len={len(pts)}, X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}]")


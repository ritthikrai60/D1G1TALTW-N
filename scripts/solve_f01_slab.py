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
print(f"Loaded {len(cols)} columns, bounds: {col_union.bounds}")

# Let's inspect the perimeter chains from P-2 (0.15), WALL, A-wall
l_p2_15 = next((x for x in doc['layers'] if x['name'] == 'P-2 (0.15)'), None)
c74_pts = [to_m(p) for p in extract_subpaths(l_p2_15['kind']['children'][74])[0]['anchors']]
c75_pts = [to_m(p) for p in extract_subpaths(l_p2_15['kind']['children'][75])[0]['anchors']]

print(f"Child 74 (North arc): {len(c74_pts)} pts, start={c74_pts[0]}, end={c74_pts[-1]}")
print(f"Child 75 (West south edge): {len(c75_pts)} pts, start={c75_pts[0]}, end={c75_pts[-1]}")

# Let's see the coordinates along the perimeter of Floor 01:
# West wing boundary:
# X min column is at -23.93 -> west wall is at X approx -25.8
# Y max column is at 21.16 -> north wall of west wing is at Y approx 22.0
# Y min column in west wing is at -15.0 -> south wall is at Y approx -17.5
# Main curved wing:
# North arc goes from X=9.52, Y=3.66 up to X=55.99, Y=22.09
# East end wall: goes from (56.0, 22.1) down to (65.5, 7.5) and (60.0, 4.0)
# South colonnade: goes from east wing back to central lobby X=20, Y=-13


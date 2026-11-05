import json
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, Point, box
from shapely.ops import unary_union
# No matplotlib needed

with open('scripts/f01_columns.json', 'r') as f:
    cols_data = json.load(f)

cols = [Polygon(c['coords']) for c in cols_data]
col_union = unary_union(cols)

# Load Child 74 (North arc) points
import zlib, re, sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths
with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))
l_p2_15 = next((x for x in doc['layers'] if x['name'] == 'P-2 (0.15)'), None)
c74_pts = [to_m(p) for p in extract_subpaths(l_p2_15['kind']['children'][74])[0]['anchors']]
c75_pts = [to_m(p) for p in extract_subpaths(l_p2_15['kind']['children'][75])[0]['anchors']]

# Let's inspect the south curb curve of west wing from c75
# c75 goes from 3.7 to -25.8 along south
# Let's filter c75 points along the south curve (from X=3.7 down to X=-25.8)
south_west_curve = []
for p in c75_pts:
    if p[1] < -15.5:
        south_west_curve.append(p)
# sort by X descending (from 3.7 to -25.8)
south_west_curve.sort(key=lambda p: -p[0])
# remove duplicates
clean_sw_curve = []
for p in south_west_curve:
    if not clean_sw_curve or np.hypot(p[0]-clean_sw_curve[-1][0], p[1]-clean_sw_curve[-1][1]) > 0.5:
        clean_sw_curve.append(p)

print(f"Clean SW curve points: {len(clean_sw_curve)}, X=[{clean_sw_curve[-1][0]} -> {clean_sw_curve[0][0]}]")

# Let's trace candidate continuous slab:
# 1. Start at top-left: (-26.5, 44.0) [or (-26.5, 23.0) if only building core]
# Let's include the full sports terrace (-26.5, 44.0) to (33.0, 44.0) exactly matching Floor 00,
# BUT for the building wing, let's see how it connects to the curved wing:
# In Floor 00: (-26.5, 44.0) -> (-26.5, -18.0) -> clean_sw_curve -> (3.71, -22.5) -> (10.0, -22.5) -> (68.0, 5.0) -> (68.0, 23.0) -> (33.0, 23.0) -> (33.0, 44.0) -> (-26.5, 44.0)

# Let's test this candidate polygon against Floor 01 columns:
cand_pts = [
    (-26.5, 44.0),
    (-26.5, -18.0),
]
for p in clean_sw_curve[::-1]: # from west to east: -25.8 to 3.7
    cand_pts.append((p[0], p[1] - 0.5)) # 0.5m margin outside curb
cand_pts.extend([
    (3.71, -22.5),
    (10.0, -22.5),
    (68.0, 5.0),
    (68.0, 23.0),
    (33.0, 23.0),
    (33.0, 44.0),
    (-26.5, 44.0)
])

p_cand = Polygon(cand_pts)
print(f"Candidate Slab: is_valid={p_cand.is_valid}, area={p_cand.area:.2f} m2")

# Check coverage of all 64 columns
all_inside = True
min_margin = 999.0
cut_columns = []
for i, col in enumerate(cols):
    if not p_cand.contains(col):
        all_inside = False
        cut_columns.append(i)
    else:
        dist = col.exterior.distance(p_cand.exterior)
        if dist < min_margin: min_margin = dist

print(f"All columns inside: {all_inside}")
print(f"Minimum margin: {min_margin:.3f} m")
if cut_columns:
    print(f"Columns outside or cut: {cut_columns}")

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

# 1. Survey Columns
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

print(f"=== Columns: {len(unique_cols)} unique ===")
all_col_union = unary_union(unique_cols)
minx, miny, maxx, maxy = all_col_union.bounds
print(f"Column bounds: X=[{minx:.2f}, {maxx:.2f}], Y=[{miny:.2f}, {maxy:.2f}]")

# 2. Survey Stairs
l_stair = next((x for x in doc['layers'] if x['name'] == 'A-stair'), None)
print(f"\n=== A-stair Analysis: {len(l_stair['kind']['children'])} children ===")
stair_lines = []
stair_polys = []
for idx, c in enumerate(l_stair['kind']['children']):
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        if len(pts) == 2:
            stair_lines.append((idx, LineString(pts)))
        elif len(pts) > 2:
            try:
                poly = Polygon(pts)
                if poly.is_valid and poly.area > 0.01:
                    stair_polys.append((idx, poly))
                else:
                    stair_lines.append((idx, LineString(pts)))
            except:
                stair_lines.append((idx, LineString(pts)))

print(f"Stair lines/curves: {len(stair_lines)}, Stair closed polys: {len(stair_polys)}")

# Group stair elements by location
from collections import defaultdict
clusters = []
for idx, geom in stair_lines + stair_polys:
    c = geom.centroid
    clusters.append((c.x, c.y, idx, geom))

print("\nStair elements locations sample:")
# Let's cluster them roughly by X, Y ranges
stair_groups = defaultdict(list)
for x, y, idx, geom in clusters:
    # identify general zone
    if x < 25:
        zone = "West Wing"
    elif 25 <= x <= 45:
        zone = "Center / Lobby"
    else:
        zone = "East Wing"
    stair_groups[zone].append((x, y, idx, geom))

for zone, items in stair_groups.items():
    xs = [it[0] for it in items]
    ys = [it[1] for it in items]
    print(f"  Zone {zone}: {len(items)} elements, X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}]")


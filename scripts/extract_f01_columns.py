import zlib, re, json
import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

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

print(f"Total unique columns found in F01: {len(unique_cols)}")

# Sort columns systematically: by Y descending, then X ascending
unique_cols.sort(key=lambda p: (-round(p.centroid.y, 1), round(p.centroid.x, 1)))

# Print table of columns
print("\n=== Floor 01 Columns Inventory ===")
print(f"{'ID':>4} | {'Center X':>8} | {'Center Y':>8} | {'Width (dx)':>10} | {'Depth (dy)':>10} | {'Area':>6} | {'Shape'}")
print("-" * 65)

column_data = []
for idx, c in enumerate(unique_cols, 1):
    minx, miny, maxx, maxy = c.bounds
    dx = maxx - minx
    dy = maxy - miny
    cx = c.centroid.x
    cy = c.centroid.y
    # check if rotated
    # simplified bounding box or polygon coords
    coords = list(c.exterior.coords)[:-1]
    shape = f"{len(coords)}-pt"
    column_data.append({
        'id': f"COL_F01_{idx:02d}",
        'center': (round(cx, 3), round(cy, 3)),
        'dx': round(dx, 3),
        'dy': round(dy, 3),
        'bounds': (round(minx, 3), round(miny, 3), round(maxx, 3), round(maxy, 3)),
        'coords': [(round(x, 3), round(y, 3)) for x, y in coords]
    })
    print(f"{idx:4d} | {cx:8.2f} | {cy:8.2f} | {dx:10.2f} | {dy:10.2f} | {c.area:6.2f} | {shape}")

with open('scripts/f01_columns.json', 'w') as f:
    json.dump(column_data, f, indent=2)

print("\nSaved scripts/f01_columns.json")


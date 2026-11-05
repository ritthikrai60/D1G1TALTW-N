import pypdf
import json
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union

# Load F01 columns
reader = pypdf.PdfReader('01-First_Floor-Clean.pdf')
data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
doc = json.loads(data.decode('utf-8'))['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

def get_subpaths(c):
    res = []
    if not isinstance(c, dict): return res
    kind = c.get('kind', {})
    if isinstance(kind, dict):
        if kind.get('type') == 'path' and 'path' in kind:
            res.extend(kind['path'].get('subpaths', []))
        if 'children' in kind:
            for ch in kind['children']: res.extend(get_subpaths(ch))
    if 'children' in c:
        for ch in c['children']: res.extend(get_subpaths(ch))
    return res

col_polys = []
for lname in ['A-col', '01-AE-Floor Post', 'P-1']:
    l = next((x for x in doc['layers'] if x['name'] == lname), None)
    if not l: continue
    for c in l['kind']['children']:
        for sp in get_subpaths(c):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) >= 4:
                try:
                    p = Polygon(pts)
                    if p.is_valid and 0.04 <= p.area <= 3.0:
                        xs = [pt[0] for pt in pts]
                        ys = [pt[1] for pt in pts]
                        dx, dy = max(xs) - min(xs), max(ys) - min(ys)
                        if 0.20 <= dx <= 2.2 and 0.20 <= dy <= 2.2:
                            col_polys.append(p)
                except: pass

unique_cols = []
seen = set()
for cp in col_polys:
    cx, cy = round(cp.centroid.x, 2), round(cp.centroid.y, 2)
    if (cx, cy) not in seen:
        seen.add((cx, cy))
        unique_cols.append(cp)

print(f"Total unique columns: {len(unique_cols)}")

# To prevent ANY notch or indentation cutting into column corners:
# A clean architectural perimeter polygon for the entire building:
# West wing: X in [-26.5, 33.0], Y in [-18.0, 44.0]
# South entry portico: X in [3.0, 11.0], Y extends down to -22.5
# East curved wing: extends along the arc X in [33.0, 68.0], Y in [-12.0, 23.0]
# North grandstand/terrace: extends up to Y = 44.0

# Let's define the outer perimeter with smooth continuous edges:
# Notice in Image 2, the bottom edge had a notch jumping from Y=-17.5 to Y=-15.533 at X=-18.85.
# If we keep the bottom line continuous along Y = -17.50, the column at (-18.55, -14.92) is 100% inside!
# And on the South-East diagonal, follow the true building exterior:
# From South portico (10.5, -22.5) -> (11.0, -17.0) -> (21.5, -13.0) -> (32.0, -10.0) -> (42.5, -6.0) -> (53.0, -1.5) -> (66.5, 5.0) -> (68.0, 8.0) -> (68.0, 23.0) -> (33.0, 23.0) -> (33.0, 44.0) -> (-26.5, 44.0) -> (-26.5, -17.5) -> (-18.0, -17.5) -> (3.7, -17.5) -> (3.7, -22.5) -> (10.5, -22.5)

perfect_slab_pts = [
    # North-West corner
    (-26.5, 44.0),
    # West edge going South
    (-26.5, -17.5),
    # South-West edge going East smoothly (NO NOTCH at -18.85!)
    (3.5, -17.5),
    # South Portico drop-down
    (3.5, -22.5),
    (10.5, -22.5),
    (10.5, -17.5),
    # South-East curved wing exterior perimeter
    (15.0, -15.0),
    (21.5, -13.0),
    (32.0, -10.0),
    (42.5, -6.0),
    (53.0, -1.5),
    (66.5, 5.0),
    (68.0, 8.0),
    # East tip
    (68.0, 23.0),
    # North edge of curved wing meeting sports center
    (33.0, 23.0),
    # North terrace / grandstand
    (33.0, 44.0),
    # Close back to North-West corner
    (-26.5, 44.0)
]

slab_poly = Polygon(perfect_slab_pts)
print(f"Slab is valid: {slab_poly.is_valid}")
print(f"Slab Area: {slab_poly.area:.2f} m^2")

# Verify every single column:
all_covered = True
min_margin = 999.0
for i, cp in enumerate(unique_cols):
    if not slab_poly.contains(cp):
        diff = cp.difference(slab_poly)
        if diff.area > 0.0001:
            print(f"Column {i} (centroid={cp.centroid.x:.2f}, {cp.centroid.y:.2f}) NOT fully inside! Diff area: {diff.area:.4f}")
            all_covered = False
    else:
        dist = slab_poly.exterior.distance(cp)
        min_margin = min(min_margin, dist)

print(f"All {len(unique_cols)} columns fully covered: {all_covered}")
print(f"Minimum margin from any column to slab edge: {min_margin:.3f} m")

with open('scripts/f01_perfect_slab_pts.json', 'w') as f:
    json.dump(perfect_slab_pts, f, indent=2)


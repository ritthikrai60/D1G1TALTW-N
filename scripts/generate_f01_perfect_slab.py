import pypdf
import json
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, box
from shapely.ops import unary_union

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

# Extract all wall segments and columns
wall_lines = []
for lname in ['A-wall', 'WALL', 'P-1 (0.50)', 'P-1']:
    layer = next((l for l in doc['layers'] if l['name'] == lname), None)
    if not layer: continue
    for elem in layer['kind']['children']:
        for sp in get_subpaths(elem):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) >= 2:
                try:
                    ls = LineString(pts)
                    if ls.is_valid and ls.length > 0.05:
                        wall_lines.append(ls)
                except: pass

col_polys = []
col_layer = next((l for l in doc['layers'] if l['name'] == 'A-col'), None)
if col_layer:
    for elem in col_layer['kind']['children']:
        for sp in get_subpaths(elem):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) >= 4:
                try:
                    poly = Polygon(pts)
                    if poly.is_valid and 0.05 <= poly.area <= 3.0:
                        col_polys.append(poly)
                except: pass

print(f"Walls: {len(wall_lines)}, Columns: {len(col_polys)}")

# Let's create an accurate building footprint:
# Buffer all wall lines by 0.6m (exterior wall thickness is ~0.3-0.4m, buffer fills gaps)
buffered_walls = unary_union([w.buffer(0.5, resolution=4) for w in wall_lines])
buffered_cols = unary_union([c.buffer(0.3, resolution=4) for c in col_polys])
building_footprint = unary_union([buffered_walls, buffered_cols])

# Close interior holes or keep outer shell
# We want the exterior boundary of the building
if building_footprint.geom_type == 'MultiPolygon':
    # Find main building polygon (largest)
    main_poly = max(building_footprint.geoms, key=lambda p: p.area)
else:
    main_poly = building_footprint

# Fill holes inside the main building shell so it's a solid continuous slab!
slab_solid = Polygon(main_poly.exterior)

# Simplify slightly (0.05m tolerance) to avoid tiny CAD segmentations
slab_simplified = slab_solid.simplify(0.05, preserve_topology=True)

print(f"Generated solid continuous slab area: {slab_simplified.area:.2f} m^2")
print(f"Slab exterior vertices count: {len(slab_simplified.exterior.coords)}")

# Verify: does the slab fully cover ALL columns with positive margin?
all_covered = True
min_margin = 999.0
for i, cp in enumerate(col_polys):
    if not slab_simplified.contains(cp):
        diff = cp.difference(slab_simplified)
        if diff.area > 0.001:
            print(f"Column {i} NOT fully covered! Diff area: {diff.area:.4f} m^2, Centroid: {cp.centroid.x:.2f}, {cp.centroid.y:.2f}")
            all_covered = False
    else:
        margin = slab_simplified.exterior.distance(cp)
        min_margin = min(min_margin, margin)

print(f"All columns fully inside slab: {all_covered}")
print(f"Minimum column-to-slab-edge margin: {min_margin:.3f} m")

# Save slab coordinates
coords = list(slab_simplified.exterior.coords)
with open('scripts/f01_perfect_slab_coords.json', 'w') as f:
    json.dump([(round(x, 3), round(y, 3)) for x, y in coords], f, indent=2)

print("Saved scripts/f01_perfect_slab_coords.json!")

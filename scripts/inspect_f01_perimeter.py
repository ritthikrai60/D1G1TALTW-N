import pypdf
import json
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from shapely.ops import unary_union, polygonize, linemerge

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

# Check all layers that have perimeter lines: 'A-wall', 'WALL', '0', 'P-1', 'P-1 (0.50)'
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
                    if ls.is_valid and ls.length > 0.1:
                        wall_lines.append(ls)
                except: pass

print(f"Total wall/perimeter line segments: {len(wall_lines)}")

# Also extract columns
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

print(f"Total column polygons in A-col: {len(col_polys)}")

# Compute bounds of columns
all_cols_union = unary_union(col_polys)
print(f"Columns bounding box: {all_cols_union.bounds}")


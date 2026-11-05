import pypdf
import json
from shapely.geometry import Point, LineString, Polygon, box
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

# Search regions where we know stairs are:
regions = {
    'spiral_lobby': (20.0, -8.0, 26.0, -1.0),
    'fan_rotunda': (15.0, -2.0, 25.0, 8.0),
    'st1_core': (7.0, -15.0, 13.0, -5.0),
    'st2_south_portico': (0.0, -23.0, 10.0, -15.0),
    'east_curved_wing': (50.0, 6.0, 65.0, 20.0),
    'north_terrace': (-30.0, 25.0, 30.0, 55.0)
}

for rname, (x1, y1, x2, y2) in regions.items():
    rbox = box(x1, y1, x2, y2)
    print(f"\n=== REGION: {rname} ===")
    layer_counts = {}
    for l in doc['layers']:
        lname = l['name']
        count = 0
        for elem in l['kind']['children']:
            for sp in get_subpaths(elem):
                pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
                if len(pts) >= 2:
                    try:
                        ls = LineString(pts)
                        if rbox.intersects(ls):
                            count += 1
                    except: pass
        if count > 0:
            layer_counts[lname] = count
    for ln, cnt in sorted(layer_counts.items(), key=lambda x: -x[1]):
        print(f"  Layer '{ln}': {cnt} segments")


import pypdf
import json
from shapely.geometry import Polygon

reader = pypdf.PdfReader('00-Ground_Floor-Clean.pdf')
data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
doc = json.loads(data.decode('utf-8'))['document']
layers = doc.get('layers', [])

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

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

pure_cols = []
seen = set()

for lname in ['A-col', '01-AE-Floor Post', 'P-1', 'COL', 'COLUMN']:
    l = next((x for x in layers if x['name'] == lname), None)
    if not l: continue
    for c in l.get('kind', {}).get('children', []):
        for sp in get_subpaths(c):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) >= 4:
                try:
                    p = Polygon(pts)
                    if p.is_valid and 0.08 <= p.area <= 2.0:
                        xs = [pt[0] for pt in pts]
                        ys = [pt[1] for pt in pts]
                        dx, dy = max(xs) - min(xs), max(ys) - min(ys)
                        if 0.25 <= dx <= 1.50 and 0.25 <= dy <= 1.50 and max(dx, dy)/min(dx, dy) <= 3.5:
                            cx, cy = round(p.centroid.x, 2), round(p.centroid.y, 2)
                            if (cx, cy) not in seen:
                                seen.add((cx, cy))
                                pure_cols.append((pts, cx, cy, dx, dy, p.area))
                except:
                    pass

print(f"Floor 00: Total pure structural columns extracted: {len(pure_cols)}")


import pypdf
import json
from shapely.geometry import Polygon

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

for fname in ['02-Second_Floor-Clean.pdf', '03-Roof_Floor-Clean.pdf']:
    reader = pypdf.PdfReader(fname)
    att = reader.attachments
    data = att['vectorcraft-editing.vectorcraft'][0]
    doc = json.loads(data.decode('utf-8'))['document']
    layers = doc.get('layers', [])
    print(f"\n=== {fname} ===")
    for l in layers:
        children = l.get('kind', {}).get('children', [])
        if any(k in l.get('name', '').lower() for k in ['col', 'post', 'wall', 'stair', 'beam']):
            print(f"  Layer: '{l.get('name')}' -> {len(children)} children")


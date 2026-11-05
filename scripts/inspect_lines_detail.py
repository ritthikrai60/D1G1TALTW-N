import pypdf
import json
import numpy as np

reader = pypdf.PdfReader('01-First_Floor-Clean.pdf')
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

for lname in ['P-4 (0.10)', 'P-2', 'A-wall', 'WALL', '0']:
    l = next((x for x in layers if x['name'] == lname), None)
    if not l: continue
    children = l.get('kind', {}).get('children', [])
    lines = []
    for c in children:
        for sp in get_subpaths(c):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) == 2:
                length = np.hypot(pts[1][0]-pts[0][0], pts[1][1]-pts[0][1])
                if 0.5 <= length <= 6.0:
                    lines.append((pts, length))
            elif len(pts) > 2:
                # check if poly is small
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                dx, dy = max(xs)-min(xs), max(ys)-min(ys)
                if (0.2 <= dx <= 4.0 and 0.2 <= dy <= 4.0):
                    pass
    print(f"\n--- Layer '{lname}': {len(lines)} lines ---")
    for pts, length in lines[:20]:
        cx = round((pts[0][0]+pts[1][0])/2, 2)
        cy = round((pts[0][1]+pts[1][1])/2, 2)
        print(f"  len={length:5.2f}m center=({cx:6.2f}, {cy:6.2f}) : {pts[0]} -> {pts[1]}")


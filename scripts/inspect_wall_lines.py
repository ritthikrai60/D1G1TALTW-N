import pypdf
import json
import numpy as np

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

reader = pypdf.PdfReader('01-First_Floor-Clean.pdf')
data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
doc = json.loads(data.decode('utf-8'))['document']
layers = doc.get('layers', [])

l_wall = next(l for l in layers if l['name'] == 'WALL')
children = l_wall.get('kind', {}).get('children', [])

lines = []
for c in children:
    for sp in get_subpaths(c):
        pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
        if not sp.get('closed', False) and len(pts) >= 2:
            lines.append(pts)

print(f"Total open wall lines in F01 'WALL': {len(lines)}")
for idx, pts in enumerate(lines[:25]):
    if len(pts) == 2:
        length = np.hypot(pts[1][0]-pts[0][0], pts[1][1]-pts[0][1])
        print(f"Line {idx:2d}: len={length:5.2f}m | {pts[0]} -> {pts[1]}")
    else:
        print(f"Polyline {idx:2d}: {len(pts)} pts | {pts[0]} -> ... -> {pts[-1]}")


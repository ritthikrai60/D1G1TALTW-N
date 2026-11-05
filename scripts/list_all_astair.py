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

l_stair = next(l for l in layers if l['name'] == 'A-stair')
children = l_stair.get('kind', {}).get('children', [])

all_items = []
for i, c in enumerate(children):
    sps = get_subpaths(c)
    for sp in sps:
        pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
        all_items.append((pts, sp.get('closed', False)))

print(f"Total items in A-stair: {len(all_items)}")
for i, (pts, closed) in enumerate(all_items):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx = round(sum(xs)/len(xs), 2)
    cy = round(sum(ys)/len(ys), 2)
    if len(pts) == 2:
        length = round(np.hypot(pts[1][0]-pts[0][0], pts[1][1]-pts[0][1]), 3)
        print(f"[{i:2d}] LINE: center=({cx:6.2f}, {cy:6.2f}) len={length:5.3f} | {pts[0]} -> {pts[1]}")
    else:
        print(f"[{i:2d}] POLY ({len(pts)} pts, closed={closed}): center=({cx:6.2f}, {cy:6.2f}) X=[{min(xs):6.2f}, {max(xs):6.2f}], Y=[{min(ys):6.2f}, {max(ys):6.2f}]")


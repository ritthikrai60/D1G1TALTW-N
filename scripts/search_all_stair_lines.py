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

# Search for lines of length between 0.8m and 5.0m across various layers
target_layers = ['เส้นบาง', 'P-4 (0.10)', 'P-2', '0', 'SN-RL', 'P-5', 'P-1']

for lname in target_layers:
    l = next((x for x in layers if x['name'] == lname), None)
    if not l: continue
    children = l.get('kind', {}).get('children', [])
    line_count = 0
    stair_like_lines = []
    for c in children:
        for sp in get_subpaths(c):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) == 2:
                length = np.hypot(pts[1][0]-pts[0][0], pts[1][1]-pts[0][1])
                if 0.8 <= length <= 6.0:
                    stair_like_lines.append((pts, length))
    print(f"Layer '{lname}': {len(stair_like_lines)} stair-like lines (0.8m - 6.0m)")


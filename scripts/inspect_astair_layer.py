import pypdf
import json

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

print("=== INSPECTING A-stair LAYER ===")
l_stair = next(l for l in layers if l['name'] == 'A-stair')
children = l_stair.get('kind', {}).get('children', [])
print(f"Total children in A-stair: {len(children)}")

stair_paths = []
for i, c in enumerate(children):
    sps = get_subpaths(c)
    for sp in sps:
        pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
        stair_paths.append((pts, sp.get('closed', False)))

print(f"Total subpaths in A-stair: {len(stair_paths)}")

# Check bounds of each subpath to cluster into stairs
import numpy as np

# Print summary of lines/shapes in A-stair
for idx, (pts, closed) in enumerate(stair_paths[:30]):
    if len(pts) == 2:
        print(f"Line {idx}: {pts[0]} -> {pts[1]} (length: {np.hypot(pts[1][0]-pts[0][0], pts[1][1]-pts[0][1]):.3f}m)")
    else:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        print(f"Poly {idx} ({len(pts)} pts, closed={closed}): X=[{min(xs)}, {max(xs)}], Y=[{min(ys)}, {max(ys)}]")


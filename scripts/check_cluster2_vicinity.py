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

# Check all elements near (7.6, 5.0) within radius 8m
print("=== ELEMENTS NEAR X=7.6, Y=5.0 ===")
for l in layers:
    lname = l.get('name')
    if lname in ['H-1', 'H-3', 'Potplant', 'AR_HATCH']: continue
    children = l.get('kind', {}).get('children', [])
    for c in children:
        for sp in get_subpaths(c):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if not pts: continue
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
            if abs(cx - 7.6) < 6.0 and abs(cy - 5.0) < 6.0:
                print(f"Layer '{lname}': {len(pts)} pts, closed={sp.get('closed')}, center=({cx:.2f}, {cy:.2f})")


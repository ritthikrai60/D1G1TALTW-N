import pypdf
import json
import math

reader = pypdf.PdfReader(r'C:\Users\ritth\Downloads\Telegram Desktop\NEW_NOTEXT\01-First_Floor-Clean.pdf')
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

# Search for all elements in STAIR 3 region: X in [6, 12], Y in [2, 11]
print("=== VECTORS IN STAIR 3 REGION (X: 6 to 12, Y: 2 to 11) ===")
st3_lines = []
for l in doc['layers']:
    for elem in l['kind']['children']:
        for sp in get_subpaths(elem):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) >= 2:
                if any(6.0 <= p[0] <= 12.0 and 2.0 <= p[1] <= 11.0 for p in pts):
                    st3_lines.append((l['name'], pts))

print(f"Total lines in STAIR 3 region: {len(st3_lines)}")

# Group by layer
by_layer = {}
for lname, pts in st3_lines:
    by_layer[lname] = by_layer.get(lname, 0) + 1

for ln, cnt in sorted(by_layer.items(), key=lambda x: -x[1]):
    print(f"  Layer '{ln}': {cnt} segments")

# Let's inspect tread lines in STAIR 3
treads = []
for lname, pts in st3_lines:
    if len(pts) == 2:
        dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
        length = math.hypot(dx, dy)
        if 1.0 <= length <= 1.8: # flight width ~ 1.50m
            treads.append((lname, pts, length))

print(f"Identified {len(treads)} tread segments in STAIR 3:")
for ln, pts, length in treads[:15]:
    print(f"  [{ln}] L={length:.2f}m : {pts[0]} -> {pts[1]}")

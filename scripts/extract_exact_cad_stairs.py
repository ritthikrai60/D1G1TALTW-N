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

# 1. FAN STAIR (X in [14, 23], Y in [-2, 6])
print("=== FAN STAIR VECTORS ===")
fan_lines = []
for l in doc['layers']:
    for elem in l['kind']['children']:
        for sp in get_subpaths(elem):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) >= 2:
                if any(14.0 <= p[0] <= 23.0 and -2.0 <= p[1] <= 6.0 for p in pts):
                    fan_lines.append((l['name'], pts))

print(f"Total lines in Fan Stair region: {len(fan_lines)}")
# Find radiating lines (treads)
fan_treads = []
for lname, pts in fan_lines:
    if len(pts) == 2:
        l = math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1])
        if 1.0 <= l <= 3.0: # radial length ~ 1.5 - 2.5m
            fan_treads.append((pts, l))

print(f"Identified {len(fan_treads)} radial fan tread lines:")
for pts, l in fan_treads[:20]:
    print(f"  L={l:.2f}m : {pts[0]} -> {pts[1]}")

# 2. LOBBY SPIRAL STAIR (X in [20, 26], Y in [-7, 0])
print("\n=== LOBBY SPIRAL STAIR VECTORS ===")
spiral_lines = []
for l in doc['layers']:
    for elem in l['kind']['children']:
        for sp in get_subpaths(elem):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) >= 2:
                if any(20.0 <= p[0] <= 26.0 and -7.0 <= p[1] <= 0.0 for p in pts):
                    spiral_lines.append((l['name'], pts))

spiral_treads = []
for lname, pts in spiral_lines:
    if len(pts) == 2:
        l = math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1])
        if 0.8 <= l <= 1.8: # spiral tread width ~ 1.0 - 1.5m
            spiral_treads.append((pts, l))

print(f"Identified {len(spiral_treads)} spiral tread lines:")
for pts, l in spiral_treads[:20]:
    print(f"  L={l:.2f}m : {pts[0]} -> {pts[1]}")


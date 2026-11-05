import json
import zlib
import re
import math

PT_PER_METER = 28.3464567
ORIGIN_X_PT = 1570.0
ORIGIN_Y_PT = 1180.0

def pdf_to_3d(x_pt, y_pt):
    return (
        round((x_pt - ORIGIN_X_PT) / PT_PER_METER, 2),
        round(-(y_pt - ORIGIN_Y_PT) / PT_PER_METER, 2),
    )

pdf_path = r"c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf"
with open(pdf_path, "rb") as f:
    raw = f.read()

streams = re.findall(rb'stream\r?\n(.*?)\r?\nendstream', raw, re.S)
layers = []
for s in streams:
    try:
        dec = zlib.decompress(s)
        if dec.startswith(b'{"format"'):
            layers = json.loads(dec.decode('utf-8'))['document'].get('layers', [])
            break
    except Exception:
        pass

def collect_paths(items):
    paths = []
    for item in items:
        kind = item.get('kind', {})
        ktype = kind.get('type')
        if ktype == 'path':
            for sp in kind.get('path', {}).get('subpaths', []):
                anchors = sp.get('anchors', [])
                pts = [tuple(a['p']) for a in anchors if 'p' in a]
                if len(pts) >= 2:
                    paths.append((pts, sp.get('closed', False)))
        elif ktype == 'group':
            paths.extend(collect_paths(kind.get('children', [])))
    return paths

# Find all paths in Layer 'A-stair' and any other stair references
stair_paths = []
for lyr in layers:
    lname = lyr.get('name')
    if 'stair' in lname.lower() or 'step' in lname.lower():
        stair_paths.extend(collect_paths(lyr.get('kind', {}).get('children', [])))

print(f"Total paths in A-stair: {len(stair_paths)}")

# Cluster stair paths by location to identify distinct staircases
stair_clusters = []
for pts, closed in stair_paths:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    matched = False
    for cl in stair_clusters:
        if math.hypot(cx - cl['cx'], cy - cl['cy']) < 120.0: # ~4.2m radius
            cl['xs'].extend(xs)
            cl['ys'].extend(ys)
            cl['cx'] = (min(cl['xs']) + max(cl['xs'])) / 2
            cl['cy'] = (min(cl['ys']) + max(cl['ys'])) / 2
            cl['items'].append(pts)
            matched = True
            break
    if not matched:
        stair_clusters.append({
            'cx': cx, 'cy': cy,
            'xs': list(xs), 'ys': list(ys),
            'items': [pts]
        })

print(f"\nFound {len(stair_clusters)} distinct stair/ramp clusters on Floor 00:")
for idx, cl in enumerate(stair_clusters):
    min_x, max_x = min(cl['xs']), max(cl['xs'])
    min_y, max_y = min(cl['ys']), max(cl['ys'])
    p1 = pdf_to_3d(min_x, min_y)
    p2 = pdf_to_3d(max_x, max_y)
    cx, cy = (min_x + max_x) / 2, (min_y + max_y) / 2
    cmid = pdf_to_3d(cx, cy)
    w_m = (max_x - min_x) / PT_PER_METER
    h_m = (max_y - min_y) / PT_PER_METER
    print(f"\nCluster #{idx+1}: center=({cmid[0]}, {cmid[1]}), size=({w_m:.2f}m x {h_m:.2f}m), lines={len(cl['items'])}")
    print(f"   Bounds 3D: X=[{min(p1[0], p2[0])}, {max(p1[0], p2[0])}], Y=[{min(p1[1], p2[1])}, {max(p1[1], p2[1])}]")


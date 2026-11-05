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

# Let's inspect all items in D&W
dw_paths = []
for lyr in layers:
    if lyr.get('name') == 'D&W':
        dw_paths = collect_paths(lyr.get('kind', {}).get('children', []))

print(f"Total D&W paths: {len(dw_paths)}")

# Group nearby paths to find door assemblies
door_groups = []
for pts, closed in dw_paths:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    w_pt, h_pt = max(xs) - min(xs), max(ys) - min(ys)
    # Check if this could be part of a door (arc or door leaf or swing)
    found = False
    for grp in door_groups:
        gcx, gcy = grp['center']
        if math.hypot(cx - gcx, cy - gcy) < 40.0: # ~1.4 meters
            grp['items'].append((cx, cy, w_pt, h_pt, pts))
            grp['xs'].extend(xs)
            grp['ys'].extend(ys)
            grp['center'] = ((min(grp['xs']) + max(grp['xs'])) / 2, (min(grp['ys']) + max(grp['ys'])) / 2)
            found = True
            break
    if not found:
        door_groups.append({
            'center': (cx, cy),
            'xs': list(xs),
            'ys': list(ys),
            'items': [(cx, cy, w_pt, h_pt, pts)]
        })

print(f"Grouped into {len(door_groups)} door/window assemblies:")
for i, grp in enumerate(door_groups):
    min_x, max_x = min(grp['xs']), max(grp['xs'])
    min_y, max_y = min(grp['ys']), max(grp['ys'])
    cx, cy = (min_x + max_x) / 2, (min_y + max_y) / 2
    w_m = (max_x - min_x) / PT_PER_METER
    h_m = (max_y - min_y) / PT_PER_METER
    p3d = pdf_to_3d(cx, cy)
    print(f"Door/Win #{i+1}: 3D pos=({p3d[0]}, {p3d[1]}), size=({w_m:.2f}m x {h_m:.2f}m), items={len(grp['items'])}")


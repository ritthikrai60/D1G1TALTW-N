import os
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

print(f"Total layers: {len(layers)}")
for i, lyr in enumerate(layers):
    lname = lyr.get('name', '')
    children = lyr.get('kind', {}).get('children', [])
    print(f"Layer {i}: '{lname}' -> {len(children)} items")

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

# Let's inspect D&W layer and door symbols
for lyr in layers:
    lname = lyr.get('name', '')
    if 'D&W' in lname or 'DOOR' in lname.upper() or 'WIN' in lname.upper():
        children = lyr.get('kind', {}).get('children', [])
        paths = collect_paths(children)
        print(f"\n--- Layer '{lname}' ({len(paths)} paths) ---")
        for idx, (pts, closed) in enumerate(paths[:25]):
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            w_pt = max(xs) - min(xs)
            h_pt = max(ys) - min(ys)
            cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
            x3d, y3d = pdf_to_3d(cx, cy)
            print(f"  Item {idx}: pts={len(pts)}, closed={closed}, bbox_pt=({w_pt:.1f}, {h_pt:.1f}), 3D=({x3d}, {y3d})")

# Let's inspect A-col layer
for lyr in layers:
    lname = lyr.get('name', '')
    if lname == 'A-col':
        children = lyr.get('kind', {}).get('children', [])
        paths = collect_paths(children)
        print(f"\n--- Layer 'A-col' ({len(paths)} paths) ---")
        for idx, (pts, closed) in enumerate(paths):
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            w_pt = max(xs) - min(xs)
            h_pt = max(ys) - min(ys)
            cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
            x3d, y3d = pdf_to_3d(cx, cy)
            print(f"  Col {idx}: pts={len(pts)}, closed={closed}, bbox_pt=({w_pt:.1f}, {h_pt:.1f}), 3D=({x3d}, {y3d})")


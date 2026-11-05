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

# Let's inspect EVERY layer in 00-Ground_Floor-Clean.pdf that contains lines
print(f"Inspecting all layers in {pdf_path}:")
for i, lyr in enumerate(layers):
    lname = lyr.get('name')
    children = lyr.get('kind', {}).get('children', [])
    if not children:
        continue
    paths = collect_paths(children)
    if not paths:
        continue
    
    # Analyze path lengths and bounding boxes
    total_len_m = 0
    seg_count = 0
    all_xs, all_ys = [], []
    for pts, closed in paths:
        for j in range(len(pts) - 1):
            l = math.hypot(pts[j+1][0] - pts[j][0], pts[j+1][1] - pts[j][1]) / PT_PER_METER
            total_len_m += l
            seg_count += 1
        all_xs.extend([p[0] for p in pts])
        all_ys.extend([p[1] for p in pts])
    
    min_3d = pdf_to_3d(min(all_xs), min(all_ys))
    max_3d = pdf_to_3d(max(all_xs), max(all_ys))
    print(f"Layer #{i:02d} '{lname}': {len(paths)} paths, {seg_count} segs, total_len={total_len_m:.1f}m, bbox_3d=({min_3d[0]}, {max_3d[1]}) to ({max_3d[0]}, {min_3d[1]})")


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

# Let's check all columns in A-col
acol_paths = []
for lyr in layers:
    if lyr.get('name') == 'A-col':
        acol_paths = collect_paths(lyr.get('kind', {}).get('children', []))

print(f"Total paths in A-col: {len(acol_paths)}")

real_cols = []
for idx, (pts, closed) in enumerate(acol_paths):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    w_pt = max(xs) - min(xs)
    h_pt = max(ys) - min(ys)
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    x3d, y3d = pdf_to_3d(cx, cy)
    w_m = w_pt / PT_PER_METER
    h_m = h_pt / PT_PER_METER
    if w_m < 1.2 and h_m < 1.2 and w_m > 0.15 and h_m > 0.15:
        real_cols.append((x3d, y3d, round(w_m, 2), round(h_m, 2), idx))
    else:
        print(f"Skipped in A-col (not a single column): idx={idx}, size=({w_m:.2f}m x {h_m:.2f}m), pos=({x3d}, {y3d})")

print(f"\nReal columns in A-col: {len(real_cols)}")
for c in sorted(real_cols, key=lambda x: (x[1], x[0])):
    print(f"  Col #{c[4]}: 3D=({c[0]:6.2f}, {c[1]:6.2f}), size=({c[2]:.2f}m x {c[3]:.2f}m)")


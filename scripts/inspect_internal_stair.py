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

# Inspect Cluster #8 (Internal stair): X in [-13, -9], Y in [-25, -19]
stair_paths = []
for lyr in layers:
    if lyr.get('name') == 'A-stair':
        for pts, closed in collect_paths(lyr.get('kind', {}).get('children', [])):
            pts_3d = [pdf_to_3d(p[0], p[1]) for p in pts]
            xs = [p[0] for p in pts_3d]
            ys = [p[1] for p in pts_3d]
            if min(xs) >= -13.0 and max(xs) <= -9.0 and min(ys) >= -25.5 and max(ys) <= -19.5:
                stair_paths.append(pts_3d)

print(f"Internal Stair (Cluster #8) lines: {len(stair_paths)}")
# Print unique Y levels (step treads)
y_levels = sorted(list(set(round(p[1], 2) for pts in stair_paths for p in pts)))
print(f"Tread Y levels ({len(y_levels)} levels): {y_levels}")


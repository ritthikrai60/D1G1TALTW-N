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

# Let's inspect what lines exist where X > -5.0 in 00-Ground_Floor-Clean.pdf
print("Lines on the East side (X > -5.0m) in 00-Ground_Floor-Clean.pdf:")
east_items = []
for lyr in layers:
    lname = lyr.get('name')
    if lname in ('GRID', 'DIMENSION', 'H-1'):
        continue
    paths = collect_paths(lyr.get('kind', {}).get('children', []))
    for idx, (pts, closed) in enumerate(paths):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        p_mid = pdf_to_3d((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
        if p_mid[0] > -7.0:
            pts_3d = [pdf_to_3d(p[0], p[1]) for p in pts]
            l = sum(math.hypot(pts[j+1][0] - pts[j][0], pts[j+1][1] - pts[j][1]) for j in range(len(pts) - 1)) / PT_PER_METER
            if l > 1.0:
                east_items.append((lname, l, p_mid, pts_3d))

print(f"Total significant lines on East side: {len(east_items)}")
for lname, l, pmid, pts_3d in sorted(east_items, key=lambda x: -x[1])[:30]:
    print(f"  Layer '{lname}' len={l:.2f}m mid=({pmid[0]}, {pmid[1]}): {pts_3d[:4]}")


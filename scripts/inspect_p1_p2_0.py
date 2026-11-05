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

target_layers = ['P-1 (0.50)', 'P-2', '0']
for lyr in layers:
    lname = lyr.get('name')
    if lname in target_layers:
        paths = collect_paths(lyr.get('kind', {}).get('children', []))
        print(f"\n==========================================")
        print(f"Layer '{lname}' ({len(paths)} paths)")
        print(f"==========================================")
        for idx, (pts, closed) in enumerate(paths):
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            w_m = (max(xs) - min(xs)) / PT_PER_METER
            h_m = (max(ys) - min(ys)) / PT_PER_METER
            seg_lengths = []
            for j in range(len(pts) - 1):
                seg_lengths.append(math.hypot(pts[j+1][0] - pts[j][0], pts[j+1][1] - pts[j][1]) / PT_PER_METER)
            total_l = sum(seg_lengths)
            pts_3d = [pdf_to_3d(p[0], p[1]) for p in pts]
            if total_l > 1.5:
                print(f"  Path {idx:02d}: pts={len(pts)}, len={total_l:.2f}m, bbox=({w_m:.2f}m x {h_m:.2f}m)")
                print(f"     coords: {pts_3d}")


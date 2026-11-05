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

def d3_to_pdf(x_3d, y_3d):
    return (
        x_3d * PT_PER_METER + ORIGIN_X_PT,
        -y_3d * PT_PER_METER + ORIGIN_Y_PT,
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

# Let's check every layer for small closed rectangles (columns!) across the whole drawing!
print("Searching for ALL square/rectangular column symbols across ALL layers in Floor 00:")
found_columns = []
for lyr in layers:
    lname = lyr.get('name')
    paths = collect_paths(lyr.get('kind', {}).get('children', []))
    for idx, (pts, closed) in enumerate(paths):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        w_pt = max(xs) - min(xs)
        h_pt = max(ys) - min(ys)
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        w_m = w_pt / PT_PER_METER
        h_m = h_pt / PT_PER_METER
        # Column criteria: 4 to 6 vertices, closed or almost closed, size 0.35m to 1.3m, aspect ratio between 0.3 and 3.0
        if 0.35 <= w_m <= 1.35 and 0.35 <= h_m <= 1.35 and len(pts) in (4, 5, 6):
            p3d = pdf_to_3d(cx, cy)
            found_columns.append((p3d[0], p3d[1], round(w_m, 2), round(h_m, 2), lname, idx))

print(f"Total column-like shapes found: {len(found_columns)}")

# Group by layer
by_lyr = {}
for c in found_columns:
    by_lyr[c[4]] = by_lyr.get(c[4], 0) + 1
print("By layer:", by_lyr)

# Let's inspect found columns
print("\nUnique column locations (deduplicated within 0.8m):")
unique_cols = []
for c in found_columns:
    if not any(math.hypot(c[0] - u[0], c[1] - u[1]) < 0.8 for u in unique_cols):
        unique_cols.append(c)

print(f"Total unique columns: {len(unique_cols)}")
for i, c in enumerate(sorted(unique_cols, key=lambda x: (round(x[1], 1), round(x[0], 1)))):
    print(f"#{i+1:02d}: 3D=({c[0]:6.2f}, {c[1]:6.2f}), size=({c[2]:.2f}m x {c[3]:.2f}m), layer='{c[4]}'")


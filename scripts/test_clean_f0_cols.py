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

# Extract all structural columns from layers: 'A-col', 'H-1', 'H-2'
# Notice: 'A-col' contains the boundary outlines, 'H-1' is the column hatch pattern, 'H-2' has north grid column boxes
raw_columns = []

for lyr in layers:
    lname = lyr.get('name')
    if lname not in ('A-col', 'H-2', 'H-1'):
        continue
    paths = collect_paths(lyr.get('kind', {}).get('children', []))
    for idx, (pts, closed) in enumerate(paths):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        w_pt = max(xs) - min(xs)
        h_pt = max(ys) - min(ys)
        w_m = w_pt / PT_PER_METER
        h_m = h_pt / PT_PER_METER
        # Column dimensions in CAD:
        # width/depth between 0.35m and 1.35m, vertex count between 4 and 6
        if 0.35 <= w_m <= 1.35 and 0.35 <= h_m <= 1.35 and len(pts) in (4, 5, 6):
            cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
            x3d, y3d = pdf_to_3d(cx, cy)
            # Skip sanitary fixtures or dimension ticks
            raw_columns.append({
                "x": x3d,
                "y": y3d,
                "w": round(w_m, 2),
                "d": round(h_m, 2),
                "layer": lname
            })

print(f"Total raw column shapes in A-col, H-1, H-2: {len(raw_columns)}")

# Deduplicate columns (within 0.6m radius)
clean_columns = []
for c in raw_columns:
    # Prefer A-col or H-2 outline over H-1 hatch
    existing = None
    for u in clean_columns:
        if math.hypot(c['x'] - u['x'], c['y'] - u['y']) < 0.6:
            existing = u
            break
    if existing is None:
        clean_columns.append(c)
    else:
        # Update with better size if from A-col
        if c['layer'] == 'A-col':
            existing['w'] = c['w']
            existing['d'] = c['d']
            existing['layer'] = c['layer']

print(f"\nDeduplicated exact structural columns: {len(clean_columns)}")
# Sort and print
clean_columns.sort(key=lambda c: (round(c['y'], 1), round(c['x'], 1)))
for i, c in enumerate(clean_columns):
    print(f"#{i+1:02d}: 3D=({c['x']:6.2f}, {c['y']:6.2f}), size=({c['w']:.2f}m x {c['d']:.2f}m), layer='{c['layer']}'")


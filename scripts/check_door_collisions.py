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

with open(r"c:\Coding Projects\Digital Twin\scripts\extracted_geometry.json", "r", encoding="utf-8") as f:
    cad_data = json.load(f)

f0_walls = cad_data["floors"]["00"]["wall_segments"]
print(f"Total extracted wall segments on Floor 00: {len(f0_walls)}")

# Let's inspect inspect_f0_doors results
with open(r"c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf", "rb") as f:
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

dw_paths = []
for lyr in layers:
    if lyr.get('name') == 'D&W':
        dw_paths = collect_paths(lyr.get('kind', {}).get('children', []))

# Find door positions
doors = []
for pts, closed in dw_paths:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    found = False
    for d in doors:
        if math.hypot(cx - d['cx'], cy - d['cy']) < 40.0:
            d['xs'].extend(xs)
            d['ys'].extend(ys)
            d['cx'] = (min(d['xs']) + max(d['xs'])) / 2
            d['cy'] = (min(d['ys']) + max(d['ys'])) / 2
            d['count'] += 1
            found = True
            break
    if not found:
        doors.append({'cx': cx, 'cy': cy, 'xs': list(xs), 'ys': list(ys), 'count': 1})

# Filter actual doors (count >= 5)
real_doors = []
for d in doors:
    if d['count'] >= 5:
        w_m = (max(d['xs']) - min(d['xs'])) / PT_PER_METER
        h_m = (max(d['ys']) - min(d['ys'])) / PT_PER_METER
        p3d = pdf_to_3d(d['cx'], d['cy'])
        real_doors.append({
            'pos': p3d,
            'size': (round(w_m, 2), round(h_m, 2)),
            'count': d['count']
        })

print(f"\nReal doors found: {len(real_doors)}")
for i, d in enumerate(real_doors):
    print(f"Door {i+1}: 3D=({d['pos'][0]:6.2f}, {d['pos'][1]:6.2f}), size={d['size']}")

# Check which walls pass near or through doors
print("\n--- Checking Walls intersecting or near doors ---")
for d in real_doors:
    dx, dy = d['pos']
    colliding_walls = []
    for w in f0_walls:
        p1 = w['p1']
        p2 = w['p2']
        # Distance from point to segment
        vx = p2[0] - p1[0]
        vy = p2[1] - p1[1]
        seg_len = math.hypot(vx, vy)
        if seg_len > 0:
            t = max(0, min(1, ((dx - p1[0]) * vx + (dy - p1[1]) * vy) / (seg_len * seg_len)))
            proj_x = p1[0] + t * vx
            proj_y = p1[1] + t * vy
            dist = math.hypot(dx - proj_x, dy - proj_y)
            if dist < 0.6: # Wall closer than 0.6m to door center!
                colliding_walls.append((dist, w, t))
    if colliding_walls:
        print(f"Door at ({dx:6.2f}, {dy:6.2f}) has {len(colliding_walls)} colliding/blocking walls:")
        for dist, w, t in colliding_walls:
            print(f"   dist={dist:.2f}m, t={t:.2f}, layer={w['layer']}, p1={w['p1']}, p2={w['p2']}")


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

dw_paths = []
for lyr in layers:
    if lyr.get('name') == 'D&W':
        dw_paths = collect_paths(lyr.get('kind', {}).get('children', []))

# Group paths by proximity into doors
door_clusters = []
for pts, closed in dw_paths:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    matched = False
    for cl in door_clusters:
        if math.hypot(cx - cl['cx'], cy - cl['cy']) < 45.0: # ~1.5m
            cl['xs'].extend(xs)
            cl['ys'].extend(ys)
            cl['cx'] = (min(cl['xs']) + max(cl['xs'])) / 2
            cl['cy'] = (min(cl['ys']) + max(cl['ys'])) / 2
            cl['paths'].append((pts, closed))
            matched = True
            break
    if not matched:
        door_clusters.append({
            'cx': cx, 'cy': cy,
            'xs': list(xs), 'ys': list(ys),
            'paths': [(pts, closed)]
        })

print(f"Total door clusters: {len(door_clusters)}")
door_list = []
for idx, cl in enumerate(door_clusters):
    if len(cl['paths']) < 4:
        continue
    min_x, max_x = min(cl['xs']), max(cl['xs'])
    min_y, max_y = min(cl['ys']), max(cl['ys'])
    cx, cy = (min_x + max_x) / 2, (min_y + max_y) / 2
    w_m = (max_x - min_x) / PT_PER_METER
    h_m = (max_y - min_y) / PT_PER_METER
    p3d = pdf_to_3d(cx, cy)
    
    # Determine orientation: if w_m > h_m, wall is likely horizontal or door opens along X
    # Let's inspect the longest line in the cluster to get door leaf orientation
    longest_len = 0
    longest_ang = 0
    for pts, closed in cl['paths']:
        for i in range(len(pts) - 1):
            dx = pts[i+1][0] - pts[i][0]
            dy = pts[i+1][1] - pts[i][1]
            l = math.hypot(dx, dy)
            if l > longest_len:
                longest_len = l
                longest_ang = math.atan2(-dy, dx) # in 3D space
    
    door_type = "single"
    if max(w_m, h_m) > 1.4:
        door_type = "double"
    if max(w_m, h_m) > 2.3:
        door_type = "sliding_or_shutter"

    door_info = {
        "id": f"D0_{len(door_list)+1:02d}",
        "x": p3d[0],
        "y": p3d[1],
        "width_m": round(max(w_m, h_m), 2),
        "depth_m": round(min(w_m, h_m), 2),
        "type": door_type,
        "leaf_angle": round(longest_ang, 2),
        "paths_count": len(cl['paths'])
    }
    door_list.append(door_info)

print(f"Detected {len(door_list)} architectural doors:")
for d in sorted(door_list, key=lambda x: (x['y'], x['x'])):
    print(f"  {d['id']}: 3D=({d['x']:6.2f}, {d['y']:6.2f}), w={d['width_m']:.2f}m, type={d['type']}")


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

# Target wall layers for Floor 00:
# A-wall: primary architectural interior/exterior walls
# P-1 (0.50): heavy boundary/demising walls (East boundary, South core boundary)
# P-2 (0.15): partition walls
# P-3: North utility room walls & inner parking perimeter
# P-4 (0.10) & P-4: WC partitions and service room divisions
wall_layers = {'A-wall', 'P-1 (0.50)', 'P-2 (0.15)', 'P-3', 'P-4 (0.10)', 'P-4'}

raw_wall_segs = []

for lyr in layers:
    lname = lyr.get('name')
    if lname not in wall_layers and lname != 'A-col':
        continue
    paths = collect_paths(lyr.get('kind', {}).get('children', []))
    for idx, (pts, closed) in enumerate(paths):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        w_pt = max(xs) - min(xs)
        h_pt = max(ys) - min(ys)
        
        # A-col contains yellow northern structural room walls if max(w_pt, h_pt) > 70
        if lname == 'A-col':
            if max(w_pt, h_pt) > 70.0:
                for j in range(len(pts) - 1):
                    p1 = pdf_to_3d(pts[j][0], pts[j][1])
                    p2 = pdf_to_3d(pts[j+1][0], pts[j+1][1])
                    raw_wall_segs.append({'p1': p1, 'p2': p2, 'layer': 'A-col-wall'})
            continue
        
        # In P-3, skip small equipment pads inside room (w_pt < 45)
        if lname == 'P-3' and max(w_pt, h_pt) < 45.0:
            continue
            
        for j in range(len(pts) - 1):
            p1 = pdf_to_3d(pts[j][0], pts[j][1])
            p2 = pdf_to_3d(pts[j+1][0], pts[j+1][1])
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            l = math.hypot(dx, dy)
            if l >= 0.8: # keep walls >= 0.8m
                raw_wall_segs.append({'p1': p1, 'p2': p2, 'layer': lname})

print(f"Total raw wall segments gathered: {len(raw_wall_segs)}")

# Deduplicate double-line CAD walls (walls in CAD are drawn with 2 parallel lines 0.15-0.20m apart)
def deduplicate_cad_walls(raw_segments, tol_dist=0.35):
    kept = []
    # Sort longest first
    raw_segments.sort(key=lambda s: math.hypot(s["p2"][0] - s["p1"][0], s["p2"][1] - s["p1"][1]), reverse=True)
    for seg in raw_segments:
        p1, p2 = seg["p1"], seg["p2"]
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        if length < 0.8:
            continue
        mx, my = 0.5 * (p1[0] + p2[0]), 0.5 * (p1[1] + p2[1])
        ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0]) % math.pi
        is_dup = False
        for k in kept:
            kmx, kmy = 0.5 * (k["p1"][0] + k["p2"][0]), 0.5 * (k["p1"][1] + k["p2"][1])
            kang = math.atan2(k["p2"][1] - k["p1"][1], k["p2"][0] - k["p1"][0]) % math.pi
            ang_diff = min(abs(ang - kang), math.pi - abs(ang - kang))
            if ang_diff < 0.15 and math.hypot(mx - kmx, my - kmy) < tol_dist:
                is_dup = True
                break
        if not is_dup:
            kept.append(seg)
    return kept

clean_walls = deduplicate_cad_walls(raw_wall_segs)
print(f"Clean single-line centerline walls: {len(clean_walls)}")

# Print by layer
layer_summary = {}
for w in clean_walls:
    layer_summary[w['layer']] = layer_summary.get(w['layer'], 0) + 1
print("Clean walls by layer:", layer_summary)

for w in sorted(clean_walls, key=lambda x: -math.hypot(x['p2'][0]-x['p1'][0], x['p2'][1]-x['p1'][1]))[:30]:
    l = math.hypot(w['p2'][0]-w['p1'][0], w['p2'][1]-w['p1'][1])
    print(f"  [{w['layer']}] {l:.2f}m: {w['p1']} -> {w['p2']}")


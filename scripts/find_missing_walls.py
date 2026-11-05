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

with open(r"c:\Coding Projects\Digital Twin\scripts\extracted_geometry.json", "r", encoding="utf-8") as f:
    cad_json = json.load(f)

extracted_f0_walls = cad_json["floors"]["00"]["wall_segments"]
print(f"Already extracted walls on F0: {len(extracted_f0_walls)}")

# Check EVERY layer for lines longer than 1.8m that are NOT in extracted_f0_walls
all_missed_walls = []
skip_layers = {'GRID', 'DIMENSION', 'H-1', 'H-2', 'SANI-DETL', 'SANITARY', 'WC-DET2', 'WC-DET1', 'WC-OUTL', 'FIXT', 'A-HATCH', 'AR_HATCH', 'HATCH', 'HATCH2', 'SYMBOL', 'D&W', 'P-5'}

for lyr in layers:
    lname = lyr.get('name')
    if lname in skip_layers:
        continue
    paths = collect_paths(lyr.get('kind', {}).get('children', []))
    for idx, (pts, closed) in enumerate(paths):
        for j in range(len(pts) - 1):
            p1 = pdf_to_3d(pts[j][0], pts[j][1])
            p2 = pdf_to_3d(pts[j+1][0], pts[j+1][1])
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            l = math.hypot(dx, dy)
            if l >= 1.8:
                # Check if this segment is already represented in extracted_f0_walls
                mx, my = 0.5 * (p1[0] + p2[0]), 0.5 * (p1[1] + p2[1])
                matched = False
                for ew in extracted_f0_walls:
                    ep1, ep2 = ew['p1'], ew['p2']
                    emx, emy = 0.5 * (ep1[0] + ep2[0]), 0.5 * (ep1[1] + ep2[1])
                    if math.hypot(mx - emx, my - emy) < 0.6:
                        matched = True
                        break
                if not matched:
                    all_missed_walls.append({
                        'layer': lname,
                        'p1': p1, 'p2': p2,
                        'len': round(l, 2),
                        'idx': idx
                    })

print(f"\nPotential missing wall segments (len >= 1.8m): {len(all_missed_walls)}")
# Group by layer
by_l = {}
for mw in all_missed_walls:
    by_l[mw['layer']] = by_l.get(mw['layer'], 0) + 1
print("Missing segments count by layer:", by_l)

for mw in sorted(all_missed_walls, key=lambda x: -x['len'])[:40]:
    print(f"  [{mw['layer']}] len={mw['len']}m: {mw['p1']} -> {mw['p2']}")


import pypdf
import json
import math
from collections import defaultdict

reader = pypdf.PdfReader(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf')
data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
doc = json.loads(data.decode('utf-8'))['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

def get_subpaths(c):
    res = []
    if not isinstance(c, dict): return res
    kind = c.get('kind', {})
    if isinstance(kind, dict):
        if kind.get('type') == 'path' and 'path' in kind:
            res.extend(kind['path'].get('subpaths', []))
        if 'children' in kind:
            for ch in kind['children']: res.extend(get_subpaths(ch))
    if 'children' in c:
        for ch in c['children']: res.extend(get_subpaths(ch))
    return res

# Collect all 2-point line segments in the entire document
segments = []
for l in doc['layers']:
    lname = l['name']
    # skip hatching layers that contain thousands of tiny lines
    if lname in ['H-1', 'H-2', 'H-3', 'HATCH', 'AR_HATCH', 'A-HATCH', 'Potplant']:
        continue
    for elem in l['kind']['children']:
        for sp in get_subpaths(elem):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) == 2:
                p1, p2 = pts[0], pts[1]
                dx, dy = p2[0] - p1[0], p2[1] - p1[1]
                length = math.hypot(dx, dy)
                if 0.60 <= length <= 8.0: # stair tread width between 0.60m and 8.0m
                    angle = math.degrees(math.atan2(dy, dx))
                    if angle > 90: angle -= 180
                    elif angle < -90: angle += 180
                    cx, cy = (p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0
                    segments.append({
                        'layer': lname,
                        'p1': p1, 'p2': p2,
                        'length': round(length, 3),
                        'angle': round(angle, 2),
                        'center': (round(cx, 3), round(cy, 3))
                    })

print(f"Total potential stair tread segments extracted: {len(segments)}")

# Group parallel segments by angle (bin 5 deg) and proximity (bin 3 meters)
tread_groups = []
used = set()

for i, s1 in enumerate(segments):
    if i in used: continue
    grp = [s1]
    used.add(i)
    c1 = s1['center']
    a1 = s1['angle']
    l1 = s1['length']
    
    for j, s2 in enumerate(segments):
        if j in used: continue
        c2 = s2['center']
        a2 = s2['angle']
        l2 = s2['length']
        
        # Parallel within 4 degrees
        if abs(a1 - a2) <= 4.0 or abs(abs(a1 - a2) - 180) <= 4.0:
            # Similar length (within 30%)
            if abs(l1 - l2) / max(l1, l2) <= 0.35:
                # Proximity within 5 meters
                dist = math.hypot(c1[0] - c2[0], c1[1] - c2[1])
                if dist <= 6.0:
                    grp.append(s2)
                    used.add(j)
    
    if len(grp) >= 3: # at least 3 parallel steps
        tread_groups.append(grp)

print(f"\nFound {len(tread_groups)} parallel stair tread systems in 01-First_Floor-Clean.pdf:")
tread_groups.sort(key=lambda g: g[0]['center'][0])

summary = []
for idx, grp in enumerate(tread_groups):
    xs = [s['center'][0] for s in grp]
    ys = [s['center'][1] for s in grp]
    layers = set(s['layer'] for s in grp)
    avg_len = sum(s['length'] for s in grp) / len(grp)
    avg_ang = sum(s['angle'] for s in grp) / len(grp)
    info = {
        'id': idx + 1,
        'count': len(grp),
        'center': (round(sum(xs)/len(xs), 2), round(sum(ys)/len(ys), 2)),
        'bounds': (round(min(xs), 2), round(min(ys), 2), round(max(xs), 2), round(max(ys), 2)),
        'avg_width': round(avg_len, 2),
        'avg_angle': round(avg_ang, 1),
        'layers': list(layers)
    }
    summary.append(info)
    print(f"Stair {idx+1}: {len(grp)} treads | Center: {info['center']} | Width: {info['avg_width']}m | Angle: {info['avg_angle']} deg | Layers: {info['layers']}")

with open('scripts/all_detected_stairs.json', 'w') as f:
    json.dump(summary, f, indent=2)


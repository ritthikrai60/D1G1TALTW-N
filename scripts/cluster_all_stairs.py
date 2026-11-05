import pypdf
import json
import numpy as np

reader = pypdf.PdfReader('01-First_Floor-Clean.pdf')
data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
doc = json.loads(data.decode('utf-8'))['document']
layers = doc.get('layers', [])

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

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Scan ALL layers for line segments between 0.6m and 6.0m
all_lines = []
for l_idx, l in enumerate(layers):
    lname = l.get('name', f'layer_{l_idx}')
    children = l.get('kind', {}).get('children', [])
    for c in children:
        for sp in get_subpaths(c):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) == 2:
                length = np.hypot(pts[1][0]-pts[0][0], pts[1][1]-pts[0][1])
                if 0.5 <= length <= 6.5:
                    all_lines.append({
                        'layer': lname,
                        'p0': pts[0],
                        'p1': pts[1],
                        'len': round(length, 3),
                        'cx': round((pts[0][0]+pts[1][0])/2, 2),
                        'cy': round((pts[0][1]+pts[1][1])/2, 2)
                    })

print(f"Total candidate lines across ALL layers: {len(all_lines)}")

# Cluster by 2D proximity (within 3 meters)
clusters = []
for line in all_lines:
    found = False
    for cl in clusters:
        # if distance between cluster center and line center < 3.0m
        ccx = sum(l['cx'] for l in cl) / len(cl)
        ccy = sum(l['cy'] for l in cl) / len(cl)
        if np.hypot(line['cx'] - ccx, line['cy'] - ccy) < 3.5:
            cl.append(line)
            found = True
            break
    if not found:
        clusters.append([line])

# Filter clusters with >= 4 lines (stair candidates)
stair_clusters = [cl for cl in clusters if len(cl) >= 4]
print(f"Found {len(stair_clusters)} clusters with >= 4 parallel/stair-like lines:")

for idx, cl in enumerate(stair_clusters):
    cx = round(sum(l['cx'] for l in cl) / len(cl), 2)
    cy = round(sum(l['cy'] for l in cl) / len(cl), 2)
    layers_used = set(l['layer'] for l in cl)
    lengths = [l['len'] for l in cl]
    print(f"\nCluster {idx+1}: Center=({cx:6.2f}, {cy:6.2f}) | Count={len(cl)} lines | Layers={layers_used} | Lengths={min(lengths):.2f}m..{max(lengths):.2f}m")
    for l in cl[:6]:
        print(f"   {l['layer']}: len={l['len']:4.2f}m, center=({l['cx']:5.2f}, {l['cy']:5.2f}) : {l['p0']} -> {l['p1']}")
    if len(cl) > 6:
        print(f"   ... and {len(cl)-6} more lines")


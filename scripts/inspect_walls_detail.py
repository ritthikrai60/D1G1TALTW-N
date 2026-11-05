import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc

def extract_subpaths(item):
    paths = []
    kind = item.get('kind', {})
    if kind.get('type') == 'path':
        p = kind.get('path', {})
        for sp in p.get('subpaths', []):
            anchors = [a.get('p') for a in sp.get('anchors', []) if 'p' in a]
            closed = sp.get('closed', False)
            if len(anchors) > 0:
                paths.append({'anchors': anchors, 'closed': closed})
    elif kind.get('type') == 'group':
        for child in kind.get('children', []):
            paths.extend(extract_subpaths(child))
    return paths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

wall_layer_names = ['P-1 (0.50)', 'P-1', 'P-2 (0.15)', 'P-2', 'P-3 (0.25)', 'P-3', 'P-4 (0.10)', 'P-4', 'A-wall', 'AR_HATCH']

for name in wall_layer_names:
    l = layers.get(name)
    if not l: continue
    children = l.get('kind', {}).get('children', [])
    all_sp = []
    for c in children:
        all_sp.extend(extract_subpaths(c))
    print(f"\n=== Layer: {name} (total {len(all_sp)} subpaths) ===")
    closed_sps = [sp for sp in all_sp if sp['closed'] or (len(sp['anchors']) > 2 and sp['anchors'][0] == sp['anchors'][-1])]
    open_sps = [sp for sp in all_sp if sp not in closed_sps]
    print(f"  Closed loops: {len(closed_sps)}, Open paths: {len(open_sps)}")
    for i, sp in enumerate(closed_sps[:8]):
        anchors = sp['anchors']
        xs = [pt[0] for pt in anchors]
        ys = [pt[1] for pt in anchors]
        w, h = (max(xs) - min(xs))/28.3465, (max(ys) - min(ys))/28.3465
        cx, cy = (min(xs) + max(xs))/2.0, (min(ys) + max(ys))/2.0
        print(f"    Closed [{i}] anchors={len(anchors)}: cx={cx:.1f}, cy={cy:.1f}, w={w:.2f}m, h={h:.2f}m")
    for i, sp in enumerate(open_sps[:8]):
        anchors = sp['anchors']
        xs = [pt[0] for pt in anchors]
        ys = [pt[1] for pt in anchors]
        w, h = (max(xs) - min(xs))/28.3465, (max(ys) - min(ys))/28.3465
        print(f"    Open [{i}] anchors={len(anchors)}: from ({anchors[0][0]:.1f},{anchors[0][1]:.1f}) to ({anchors[-1][0]:.1f},{anchors[-1][1]:.1f}) w={w:.2f}m, h={h:.2f}m")

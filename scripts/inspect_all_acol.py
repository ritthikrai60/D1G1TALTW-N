import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
acol = layers.get('A-col')

print(f"Total children in A-col: {len(acol['kind']['children'])}")
for i, c in enumerate(acol['kind']['children']):
    p = c.get('kind', {}).get('path', {})
    sps = p.get('subpaths', [])
    for sp in sps:
        anchors = [a.get('p') for a in sp.get('anchors', []) if 'p' in a]
        xs = [pt[0] for pt in anchors]
        ys = [pt[1] for pt in anchors]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w, h = (max_x - min_x)/28.3465, (max_y - min_y)/28.3465
        cx, cy = (min_x + max_x)/2.0, (min_y + max_y)/2.0
        print(f"[{i:02d}] anchors={len(anchors)}: cx={cx:.1f}, cy={cy:.1f}, w={w:.2f}m, h={h:.2f}m")


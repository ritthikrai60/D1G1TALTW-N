import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
acol = layers.get('A-col')

for i, c in enumerate(acol['kind']['children']):
    p = c.get('kind', {}).get('path', {})
    for sp in p.get('subpaths', []):
        anchors = [a.get('p') for a in sp.get('anchors', []) if 'p' in a]
        xs = [pt[0] for pt in anchors]
        ys = [pt[1] for pt in anchors]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w, h = (max_x - min_x)/28.3465, (max_y - min_y)/28.3465
        if w > 2.0 or h > 2.0:
            print(f"Child {i:2d}: anchors={len(anchors)}, w={w:.2f}m, h={h:.2f}m, X=[{min_x:.1f},{max_x:.1f}], Y=[{min_y:.1f},{max_y:.1f}]")


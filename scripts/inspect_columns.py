import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
acol = layers.get('A-col')

cols = []
for i, c in enumerate(acol['kind']['children']):
    p = c.get('kind', {}).get('path', {})
    for sp in p.get('subpaths', []):
        anchors = [a.get('p') for a in sp.get('anchors', []) if 'p' in a]
        if len(anchors) >= 4:
            xs = [pt[0] for pt in anchors]
            ys = [pt[1] for pt in anchors]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            cx, cy = (min_x + max_x)/2.0, (min_y + max_y)/2.0
            w, h = max_x - min_x, max_y - min_y
            cols.append({'idx': i, 'cx': cx, 'cy': cy, 'w': w, 'h': h, 'anchors': anchors})

print(f"Total columns found: {len(cols)}")
# Sort columns by Y, then X
cols.sort(key=lambda c: (round(c['cy'], -1), round(c['cx'], -1)))
print("First 10 columns (pt):")
for c in cols[:10]:
    print(f"  Col {c['idx']:2d}: cx={c['cx']:.2f}, cy={c['cy']:.2f}, w={c['w']:.2f}, h={c['h']:.2f} (w_m={c['w']/28.3465:.2f}, h_m={c['h']/28.3465:.2f})")

print("\nLast 10 columns (pt):")
for c in cols[-10:]:
    print(f"  Col {c['idx']:2d}: cx={c['cx']:.2f}, cy={c['cy']:.2f}, w={c['w']:.2f}, h={c['h']:.2f} (w_m={c['w']/28.3465:.2f}, h_m={c['h']/28.3465:.2f})")


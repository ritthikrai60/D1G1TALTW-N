import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import json

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Check all 72 items in A-col
acol = layers['A-col']
cols = []
non_cols = []
for i, c in enumerate(acol.get('kind', {}).get('children', [])):
    sps = extract_subpaths(c)
    for sp in sps:
        pts = sp['anchors']
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        w = (max(xs) - min(xs))/28.3465
        h = (max(ys) - min(ys))/28.3465
        cx = sum(xs)/len(xs)
        cy = sum(ys)/len(ys)
        if len(pts) >= 4 and w < 1.5 and h < 1.5 and w > 0.15 and h > 0.15:
            cols.append({'idx': i, 'cx': cx, 'cy': cy, 'w': w, 'h': h, 'pts': pts, 'anchors_len': len(pts)})
        else:
            non_cols.append({'idx': i, 'cx': cx, 'cy': cy, 'w': w, 'h': h, 'pts': pts, 'anchors_len': len(pts)})

print(f"Total columns meeting size criteria: {len(cols)}")
print(f"Non-column items in A-col: {len(non_cols)}")
for nc in non_cols:
    print(f"  Non-col {nc['idx']:2d}: anchors={nc['anchors_len']}, w={nc['w']:.2f}m, h={nc['h']:.2f}m, at ({nc['cx']:.1f}, {nc['cy']:.1f})")

print("\nAll columns found:")
for c in cols:
    print(f"  Col {c['idx']:2d}: anchors={c['anchors_len']}, w={c['w']:.2f}m, h={c['h']:.2f}m, at ({c['cx']:.1f}, {c['cy']:.1f})")


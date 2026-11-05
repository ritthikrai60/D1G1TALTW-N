import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
stair = layers.get('A-stair')
for i, c in enumerate(stair.get('kind', {}).get('children', [])):
    sps = extract_subpaths(c)
    for j, sp in enumerate(sps):
        pts = sp['anchors']
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        closed = sp['closed']
        print(f"Child {i:2d}.{j}: len={len(pts):2d}, closed={str(closed):5s}, X=[{min(xs):6.1f}, {max(xs):6.1f}], Y=[{min(ys):6.1f}, {max(ys):6.1f}]")


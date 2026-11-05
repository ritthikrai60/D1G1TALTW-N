import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
print("Doc loaded successfully!")
layers = {l['name']: l for l in doc.get('layers', [])}
print(f"Total layers: {len(layers)}")
for name, l in layers.items():
    ch = l.get('kind', {}).get('children', [])
    print(f"  {name:25s}: {len(ch)} children")

stair = layers.get('A-stair')
if stair:
    ch = stair.get('kind', {}).get('children', [])
    print(f"\n--- A-stair details ({len(ch)} children) ---")
    for i, c in enumerate(ch):
        sps = extract_subpaths(c)
        for j, sp in enumerate(sps):
            pts = sp['anchors']
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            print(f"Child {i:2d}.{j}: len={len(pts):2d}, closed={sp['closed']}, X=[{min(xs):6.1f}, {max(xs):6.1f}], Y=[{min(ys):6.1f}, {max(ys):6.1f}]")


import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
stair = layers['A-stair']

print("=== INSPECTING ALL ITEMS IN CORE REGION (X: [7, 12], Y: [-14, -6]) ===")
for i, c in enumerate(stair['kind']['children']):
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        cx = sum(xs)/len(xs)
        cy = sum(ys)/len(ys)
        if 6.0 <= cx <= 13.0 and -15.0 <= cy <= -5.0:
            print(f"Child {i:3d}: len={len(pts):2d}, closed={sp['closed']}, cx={cx:.2f}, cy={cy:.2f}, X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}]")
            if len(pts) <= 8:
                print(f"   pts: {pts}")


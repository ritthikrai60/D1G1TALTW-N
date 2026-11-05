import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m

doc = load_pdf_doc()['document']
stair = {l['name']: l for l in doc['layers']}['A-stair']

print("=== CHECKING 'OTHER' ITEMS IN A-stair ===")
for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 225]:
    c = stair['kind']['children'][i]
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        print(f"Child {i:3d}: len={len(pts):2d}, closed={sp['closed']}, X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}]")
        if len(pts) <= 6:
            print(f"   pts: {pts}")


import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m

doc = load_pdf_doc()['document']
stair = {l['name']: l for l in doc['layers']}['A-stair']

print("=== INSPECTING SOUTH STAIR ITEMS ===")
for i in [0, 34, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 224]:
    c = stair['kind']['children'][i]
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        print(f"Child {i:3d}: len={len(pts):2d}, closed={sp['closed']}, X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}]")
        if len(pts) <= 4:
            print(f"   pts: {pts}")


import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m

doc = load_pdf_doc()['document']
stair = {l['name']: l for l in doc['layers']}['A-stair']

print("=== CHECKING ALL NORTH ITEMS IN A-stair ===")
north_items = []
for i, c in enumerate(stair['kind']['children']):
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        min_y = min(ys)
        max_y = max(ys)
        min_x = min(xs)
        max_x = max(xs)
        if min_y > 10.0:  # in meters, Y > 10m is north (since Y0=1500, Y < 1100 in CAD pt is Y > 14m in meters)
            north_items.append((i, len(pts), sp['closed'], (round(min_x, 2), round(max_x, 2)), (round(min_y, 2), round(max_y, 2))))

print(f"Total north items found: {len(north_items)}")
# Check if there are stair-like groups (e.g. series of parallel lines with 0.25-0.30m spacing)
for item in north_items[:20]:
    print(f"Child {item[0]:3d}: pts={item[1]}, closed={item[2]}, X={item[3]}, Y={item[4]}")


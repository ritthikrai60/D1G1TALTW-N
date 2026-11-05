import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m

doc = load_pdf_doc()['document']
stair = {l['name']: l for l in doc['layers']}['A-stair']

print(f"Total children in A-stair: {len(stair['kind']['children'])}")

# Let's inspect all subpaths
all_items = []
for i, c in enumerate(stair['kind']['children']):
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        all_items.append({
            'child_id': i,
            'pts': pts,
            'len': len(pts),
            'closed': sp['closed'],
            'cx': sum(xs)/len(xs),
            'cy': sum(ys)/len(ys),
            'min_x': min(xs), 'max_x': max(xs),
            'min_y': min(ys), 'max_y': max(ys),
        })

print(f"Total subpaths: {len(all_items)}")

# Let's cluster by location
# 1. Core Area: cx in [7, 12], cy in [-14, -6]
core_items = [it for it in all_items if 7.0 <= it['cx'] <= 12.0 and -14.0 <= it['cy'] <= -6.0]
print(f"\n=== CORE AREA ITEMS ({len(core_items)}) ===")
for it in core_items:
    print(f"Child {it['child_id']:3d}: len={it['len']}, closed={it['closed']}, cx={it['cx']:.2f}, cy={it['cy']:.2f}, X=[{it['min_x']:.2f}, {it['max_x']:.2f}], Y=[{it['min_y']:.2f}, {it['max_y']:.2f}]")

# 2. South Area: cx in [1, 15], cy in [-23, -15]
south_items = [it for it in all_items if 1.0 <= it['cx'] <= 15.0 and -23.0 <= it['cy'] <= -15.0]
print(f"\n=== SOUTH AREA ITEMS ({len(south_items)}) ===")
for it in south_items:
    print(f"Child {it['child_id']:3d}: len={it['len']}, closed={it['closed']}, cx={it['cx']:.2f}, cy={it['cy']:.2f}, X=[{it['min_x']:.2f}, {it['max_x']:.2f}], Y=[{it['min_y']:.2f}, {it['max_y']:.2f}]")

# 3. North/West Area
north_items = [it for it in all_items if it not in core_items and it not in south_items]
print(f"\n=== REMAINING ITEMS ({len(north_items)}) ===")
for it in north_items:
    print(f"Child {it['child_id']:3d}: len={it['len']}, closed={it['closed']}, cx={it['cx']:.2f}, cy={it['cy']:.2f}, X=[{it['min_x']:.2f}, {it['max_x']:.2f}], Y=[{it['min_y']:.2f}, {it['max_y']:.2f}]")


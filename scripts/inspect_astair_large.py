import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
stair = layers['A-stair']

print("=== A-stair items (Y >= 900) ===")
for i, c in enumerate(stair.get('kind', {}).get('children', [])):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        ys = [p[1] for p in pts]
        if min(ys) >= 900:
            xs = [p[0] for p in pts]
            w = (max(xs) - min(xs))/28.3465
            h = (max(ys) - min(ys))/28.3465
            cx = sum(xs)/len(xs)
            cy = sum(ys)/len(ys)
            if w > 2.0 or h > 2.0 or len(pts) > 4:
                print(f"Stair item {i:3d}: pts={len(pts):3d}, closed={sp['closed']}, size={w:.2f}x{h:.2f}m, cx={cx:.1f}, cy={cy:.1f}")


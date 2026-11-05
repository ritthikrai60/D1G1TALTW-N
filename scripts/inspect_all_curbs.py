import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
stair = layers['A-stair']

X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

print("Checking all curb/island paths in A-stair:")
for i, c in enumerate(stair['kind']['children']):
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        w = max(xs) - min(xs)
        h = max(ys) - min(ys)
        cx = sum(xs)/len(xs)
        cy = sum(ys)/len(ys)
        # Curbs/islands around parking
        if (w > 5.0 or h > 5.0) and len(pts) > 2:
            print(f"Item {i:3d}: pts={len(pts):3d}, closed={sp['closed']}, size={w:.2f}x{h:.2f}m, at ({cx:.1f}, {cy:.1f}), ends: {pts[0]} -> {pts[-1]}")


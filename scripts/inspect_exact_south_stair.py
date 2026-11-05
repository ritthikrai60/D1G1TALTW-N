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

print("=== SOUTH ENTRANCE OUTDOOR STAIRS ===")
for i in range(88, 107):
    c = stair['kind']['children'][i]
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        cx = sum(xs)/len(xs)
        cy = sum(ys)/len(ys)
        print(f"Item {i:3d}: pts={len(pts)}, cx={cx:.2f}, cy={cy:.2f}, pts={pts}")

# Item 106 and 105
for i in [105, 106, 228, 229]:
    c = stair['kind']['children'][i]
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        print(f"Boundary Item {i:3d}: pts={len(pts)}, pts={pts}")


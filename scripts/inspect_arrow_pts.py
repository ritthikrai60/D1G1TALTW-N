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

print("Looking for arrow and breakline points around Y in [1730, 1780]:")
for i in range(10, 60):
    c = stair['kind']['children'][i]
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if any(1220 <= p[0] <= 1300 and 1730 <= p[1] <= 1780 for p in pts):
            pts_m = [to_m(p) for p in pts]
            print(f"Item {i:2d}: pts={len(pts)}, closed={sp['closed']}, anchors={pts_m}")


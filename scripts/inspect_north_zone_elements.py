import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

target_layers = ['A-col', 'A-wall', 'WALL', 'P-1 (0.50)', 'P-1', 'D&W', 'SYMBOL', 'LABEL']
for lname in target_layers:
    l = next((x for x in doc['layers'] if x['name'] == lname), None)
    if not l: continue
    print(f'=== Layer {lname} ===')
    for i, c in enumerate(l['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if not xs or not ys: continue
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            if max_x >= -2.0 and min_x <= 15.0 and max_y >= 20.0 and min_y <= 44.0:
                print(f'  i={i}: closed={sp.get("closed", False)}, len={len(pts)}, pts={pts}')


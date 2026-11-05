import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

print("=== CHECKING SYMBOLS & ARROWS NEAR CORE STAIR ===")
for lname in ['SYMBOL', 'DIMENSION', '0', 'เส้นบาง', 'A-stair']:
    l = layers.get(lname)
    if not l: continue
    for i, c in enumerate(l.get('kind', {}).get('children', [])):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
            if 7.5 <= cx <= 11.5 and -13.5 <= cy <= -7.0:
                print(f"[{lname}] Child {i:2d}: pts={len(pts)}, closed={sp['closed']}, cx={cx:.2f}, cy={cy:.2f}, pts={pts}")


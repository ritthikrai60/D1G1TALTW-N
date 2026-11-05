import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

print("=== CHECKING ALL ITEMS IN 'DIMENSION' ===")
dim = layers.get('DIMENSION')
if dim:
    for i, c in enumerate(dim.get('kind', {}).get('children', [])):
        sps = extract_subpaths(c)
        for sp in sps:
            pts = [to_m(p) for p in sp['anchors']]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            print(f"DIM {i:2d}: pts={len(pts)}, closed={sp['closed']}, X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}]")

print("\n=== CHECKING ALL ITEMS IN 'SYMBOL' ===")
sym = layers.get('SYMBOL')
if sym:
    for i, c in enumerate(sym.get('kind', {}).get('children', [])):
        sps = extract_subpaths(c)
        for sp in sps:
            pts = [to_m(p) for p in sp['anchors']]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            print(f"SYM {i:2d}: pts={len(pts)}, closed={sp['closed']}, X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}]")


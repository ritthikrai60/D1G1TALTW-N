import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Look at symbols 29 and 30 in DIMENSION or SYMBOL or 1-BLOCK
for lname in ['DIMENSION', 'SYMBOL', '1-BLOCK', 'SN-RL', '0']:
    l = layers.get(lname)
    if not l: continue
    for i, c in enumerate(l.get('kind', {}).get('children', [])):
        sps = extract_subpaths(c)
        for sp in sps:
            pts = sp['anchors']
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            # Near south entrance: X in [900, 1300], Y in [1800, 2200]
            if any(900 <= p[0] <= 1300 and 1800 <= p[1] <= 2200 for p in pts):
                print(f"[{lname}] Child {i}: closed={sp['closed']}, pts={len(pts)}, X=[{min(xs):.1f},{max(xs):.1f}], Y=[{min(ys):.1f},{max(ys):.1f}]")


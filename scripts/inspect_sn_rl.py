import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
sn_rl = layers.get('SN-RL')
if sn_rl:
    ch = sn_rl.get('kind', {}).get('children', [])
    print(f"=== SN-RL ({len(ch)} children) ===")
    for i, c in enumerate(ch):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            print(f"SN-RL Child {i:2d}: pts={len(pts)}, X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}], pts={pts[:4]}")


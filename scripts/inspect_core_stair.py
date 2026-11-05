import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
stair = layers['A-stair']

core_stairs = []
for i, c in enumerate(stair.get('kind', {}).get('children', [])):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        cx = sum(xs)/len(xs)
        cy = sum(ys)/len(ys)
        # Check area of internal stair: cx in [1200, 1350], cy in [1650, 1850]
        if 1200 <= cx <= 1350 and 1650 <= cy <= 1850:
            core_stairs.append({'idx': i, 'pts': pts, 'cx': cx, 'cy': cy})

print(f"Internal Core Stairs in A-stair: {len(core_stairs)} paths")
for s in core_stairs[:15]:
    print(f"  Item {s['idx']:3d}: pts={len(s['pts'])}, at ({s['cx']:.1f}, {s['cy']:.1f})")


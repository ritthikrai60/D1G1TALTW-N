import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

print("=== CHECKING LINES IN SOUTH EXTENSION X: [8.5, 23.0], Y: [-22.0, -11.0] ===")
for lname, l in layers.items():
    ch = l.get('kind', {}).get('children', [])
    found = []
    for i, c in enumerate(ch):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
            if 8.5 <= cx <= 23.0 and -22.0 <= cy <= -11.0:
                found.append((i, len(pts), pts))
    if found:
        print(f"Layer '{lname}': {len(found)} items found")
        for f in found[:10]:
            print(f"  Child {f[0]}: pts={f[1]}, pts={f[2]}")


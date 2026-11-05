import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
sym = {l['name']: l for l in doc['layers']}['SYMBOL']

for i, c in enumerate(sym['kind']['children']):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        print(f"Letter {i:2d}: pts={len(pts)}, bbox X=[{min(p[0] for p in pts):.1f}, {max(p[0] for p in pts):.1f}], Y=[{min(p[1] for p in pts):.1f}, {max(p[1] for p in pts):.1f}]")


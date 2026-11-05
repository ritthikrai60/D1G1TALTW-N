import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import math

doc = load_pdf_doc()['document']

for lname in ['P-4', 'P-4 (0.10)', 'P-2 (0.15)', '0', 'P-3 (0.25)', 'WALL', 'A-wall']:
    layer = [l for l in doc['layers'] if l['name'] == lname][0]
    children = layer['kind'].get('children', [])
    print(f"\n=== Layer {lname} ({len(children)} children) ===")
    for i, c in enumerate(children[:5]):
        sps = extract_subpaths(c)
        if sps:
            pts = sps[0]['anchors']
            xm = [(p[0]-1133.858)/28.346456692913385 for p in pts]
            ym = [(p[1]-1417.323)/28.346456692913385 for p in pts]
            print(f"  c{i}: pts={len(pts)}, X=[{min(xm):.2f}, {max(xm):.2f}], Y=[{min(ym):.2f}, {max(ym):.2f}], closed={sps[0]['closed']}")

import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import json

doc = load_pdf_doc()['document']
stair_layer = [l for l in doc['layers'] if l['name'] == 'A-stair'][0]
children = stair_layer['kind']['children']

print("=== Child 11 to 22 ===")
for i in range(11, 23):
    c = children[i]
    sps = extract_subpaths(c)
    pts = sps[0]['anchors'] if sps else []
    print(f"Child {i:2d}: type={c.get('type')}, color={c.get('strokeColor') or c.get('color')}, pts={len(pts)}")
    for p in pts:
        xm = (p[0]-1133.858)/28.346456692913385
        ym = (p[1]-1417.323)/28.346456692913385
        print(f"   pt: ({xm:.4f}, {ym:.4f})")

print("\n=== Child 66 to 84 ===")
for i in range(66, 85):
    c = children[i]
    sps = extract_subpaths(c)
    pts = sps[0]['anchors'] if sps else []
    print(f"Child {i:2d}: type={c.get('type')}, color={c.get('strokeColor') or c.get('color')}, pts={len(pts)}")
    for p in pts:
        xm = (p[0]-1133.858)/28.346456692913385
        ym = (p[1]-1417.323)/28.346456692913385
        print(f"   pt: ({xm:.4f}, {ym:.4f})")


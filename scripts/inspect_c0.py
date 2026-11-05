import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
stair = {l['name']: l for l in doc['layers']}['A-stair']
c0 = stair['kind']['children'][0]
sps = extract_subpaths(c0)
print('c0 num subpaths:', len(sps))
for i, sp in enumerate(sps):
    print(f'subpath {i}: len={len(sp["anchors"])}, closed={sp["closed"]}')
    for pt in sp["anchors"]:
        print(f"  ({pt[0]:.2f}, {pt[1]:.2f})")


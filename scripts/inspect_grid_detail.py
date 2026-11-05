import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
grid = layers.get('GRID')
for i, c in enumerate(grid['kind']['children'][:10]):
    kind = c.get('kind', {})
    print(f"Child {i}: type={kind.get('type')}")
    if kind.get('type') == 'path':
        p = kind.get('path', {})
        sps = p.get('subpaths', [])
        for sp in sps:
            anchors = [a.get('p') for a in sp.get('anchors', []) if 'p' in a]
            print(f"   subpath closed={sp.get('closed')} len={len(anchors)} anchors={anchors[:2]}")

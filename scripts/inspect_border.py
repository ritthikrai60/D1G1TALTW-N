import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

for name in ['head-a3$0$BORDER A1$0$SYM', 'head-a3$0$BORDER A1$0$1-wall', 'head-a3$0$BORDER A1$0$line1-logo']:
    l = layers.get(name)
    if l:
        all_sp = []
        for c in l.get('kind', {}).get('children', []):
            all_sp.extend(extract_subpaths(c))
        xs = [pt[0] for sp in all_sp for pt in sp['anchors']]
        ys = [pt[1] for sp in all_sp for pt in sp['anchors']]
        if xs and ys:
            print(f"Layer {name}: X=[{min(xs):.1f}, {max(xs):.1f}], Y=[{min(ys):.1f}, {max(ys):.1f}]")


import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Check SYMBOL layer
sym = layers.get('SYMBOL')
if sym:
    print(f"SYMBOL items: {len(sym['kind']['children'])}")
    for i, c in enumerate(sym['kind']['children']):
        sps = extract_subpaths(c)
        for sp in sps:
            pts = sp['anchors']
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            print(f"  Symbol {i}: pts={len(pts)}, closed={sp['closed']}, X=[{min(xs):.1f},{max(xs):.1f}], Y=[{min(ys):.1f},{max(ys):.1f}]")

# Check all layers that might have columns or areas
print("\nChecking layers for columns:")
for lname, l in layers.items():
    children = l.get('kind', {}).get('children', [])
    col_like = 0
    for c in children:
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if len(pts) >= 4:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                w = (max(xs) - min(xs))/28.3465
                h = (max(ys) - min(ys))/28.3465
                if 0.2 <= w <= 1.5 and 0.2 <= h <= 1.5:
                    col_like += 1
    if col_like > 0:
        print(f"  Layer {lname:20s}: {col_like} column-sized shapes")


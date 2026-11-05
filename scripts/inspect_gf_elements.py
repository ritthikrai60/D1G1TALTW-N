import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Focus on Ground Floor built region: Y >= 900 pt
print("=== Ground Floor Columns (Y >= 900) ===")
acol = layers['A-col']
gf_cols = []
for i, c in enumerate(acol['kind']['children']):
    for sp in extract_subpaths(c):
        anchors = sp['anchors']
        if len(anchors) >= 4:
            xs = [p[0] for p in anchors]
            ys = [p[1] for p in anchors]
            cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
            w, h = (max(xs) - min(xs))/28.3465, (max(ys) - min(ys))/28.3465
            # Columns on ground floor parking & core
            # Note: columns on the far right (X > 1650) are outdoor slope columns
            if cy >= 900 and w < 1.5 and h < 1.5:
                gf_cols.append({'cx': cx, 'cy': cy, 'w': w, 'h': h, 'anchors': anchors, 'outdoor': cx > 1650})

print(f"Found {len(gf_cols)} columns (indoor/parking: {sum(1 for c in gf_cols if not c['outdoor'])}, outdoor slope: {sum(1 for c in gf_cols if c['outdoor'])})")
for c in gf_cols:
    tag = "OUTDOOR" if c['outdoor'] else "GF_COL "
    print(f"  {tag} cx={c['cx']:.1f}, cy={c['cy']:.1f}, size={c['w']:.2f}x{c['h']:.2f}m")


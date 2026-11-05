import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Retaining wall
p1_050 = layers['P-1 (0.50)']
print("=== Retaining Wall P-1 (0.50) ===")
for c in p1_050.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        print(f"Retaining wall subpath closed={sp['closed']} len={len(sp['anchors'])}")
        for pt in sp['anchors']:
            print(f"   pt: ({pt[0]:.2f}, {pt[1]:.2f})")

print("\n=== AR_HATCH Walls (Y >= 900) ===")
ar_hatch = layers['AR_HATCH']
hatch_loops = []
for c in ar_hatch.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        ys = [p[1] for p in pts]
        if min(ys) >= 900:
            xs = [p[0] for p in pts]
            cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
            w, h = (max(xs) - min(xs))/28.3465, (max(ys) - min(ys))/28.3465
            hatch_loops.append({'cx': cx, 'cy': cy, 'w': w, 'h': h, 'pts': pts})

print(f"Found {len(hatch_loops)} AR_HATCH wall loops in Ground Floor core:")
for i, hl in enumerate(hatch_loops):
    print(f"  WallLoop {i:2d}: cx={hl['cx']:.1f}, cy={hl['cy']:.1f}, size={hl['w']:.2f}x{hl['h']:.2f}m, pts={len(hl['pts'])}")


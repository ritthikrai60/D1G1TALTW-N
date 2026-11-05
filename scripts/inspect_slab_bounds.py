import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Look at lines in เส้นบาง or WALL or 0 around parking: X in [200, 1100], Y in [900, 2000]
candidates = []
for lname in ['WALL', 'เส้นบาง', 'SN-RL', '0']:
    l = layers.get(lname)
    if not l: continue
    for c in l.get('kind', {}).get('children', []):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if len(pts) >= 4:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
                w, h = (max(xs) - min(xs))/28.3465, (max(ys) - min(ys))/28.3465
                if cy >= 900 and (w > 3.0 or h > 3.0):
                    candidates.append({'layer': lname, 'w': w, 'h': h, 'cx': cx, 'cy': cy, 'pts': len(pts), 'closed': sp['closed']})

print(f"Large paths found in Ground Floor: {len(candidates)}")
for c in candidates[:20]:
    print(f"  [{c['layer']:10s}] pts={c['pts']:3d}, closed={c['closed']}, size={c['w']:.1f}x{c['h']:.1f}m, at ({c['cx']:.1f}, {c['cy']:.1f})")


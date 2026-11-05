import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
stair = layers['A-stair']

gf_stairs = []
for c in stair.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        ys = [p[1] for p in pts]
        if min(ys) >= 900:
            xs = [p[0] for p in pts]
            cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
            gf_stairs.append({'cx': cx, 'cy': cy, 'pts': pts, 'len': len(pts)})

print(f"Total stair paths in Ground Floor (Y >= 900): {len(gf_stairs)}")
# Group into Entrance Stair vs Core Internal Stair
entrance_stairs = [s for s in gf_stairs if s['cy'] >= 1850]
core_stairs = [s for s in gf_stairs if s['cy'] < 1850]
print(f"  Grand Entrance Stairs (bottom, Y >= 1850): {len(entrance_stairs)} paths")
print(f"  Internal Core Stairs (Y < 1850): {len(core_stairs)} paths")

if entrance_stairs:
    xs = [p[0] for s in entrance_stairs for p in s['pts']]
    ys = [p[1] for s in entrance_stairs for p in s['pts']]
    print(f"  Entrance Stairs bounds: X=[{min(xs):.1f}, {max(xs):.1f}], Y=[{min(ys):.1f}, {max(ys):.1f}]")

if core_stairs:
    xs = [p[0] for s in core_stairs for p in s['pts']]
    ys = [p[1] for s in core_stairs for p in s['pts']]
    print(f"  Core Stairs bounds: X=[{min(xs):.1f}, {max(xs):.1f}], Y=[{min(ys):.1f}, {max(ys):.1f}]")


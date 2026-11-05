import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Check all layers for words or symbols like STAIR, UP, DN, บันได
print("Checking text/labels and dimensions across all layers:")
for lname in ['LABEL', 'SYMBOL', 'DIMENSION', '1-BLOCK', 'SN-RL']:
    l = layers.get(lname)
    if not l: continue
    for i, c in enumerate(l.get('kind', {}).get('children', [])):
        kind = c.get('kind', {})
        t = kind.get('type')
        text = kind.get('text', '')
        if text:
            print(f"[{lname}] Text: {text}")

# Let's inspect all subpaths of A-stair with their exact endpoints and geometry
stair = layers['A-stair']
print(f"\nA-stair children count: {len(stair['kind']['children'])}")

# Categorize every child of A-stair
for i, c in enumerate(stair['kind']['children']):
    sps = extract_subpaths(c)
    for sp in sps:
        pts = sp['anchors']
        if len(pts) == 2:
            dx = abs(pts[1][0] - pts[0][0])
            dy = abs(pts[1][1] - pts[0][1])
            length = (dx**2 + dy**2)**0.5 / 28.3465
            cx = (pts[0][0] + pts[1][0])/2.0
            cy = (pts[0][1] + pts[1][1])/2.0
            # If length is between 0.8m and 3.0m, could be a tread!
            if 0.8 <= length <= 3.0:
                print(f"  Line {i:3d}: len={length:.2f}m, at pt=({cx:.1f}, {cy:.1f}), p0=({pts[0][0]:.1f},{pts[0][1]:.1f}) p1=({pts[1][0]:.1f},{pts[1][1]:.1f})")


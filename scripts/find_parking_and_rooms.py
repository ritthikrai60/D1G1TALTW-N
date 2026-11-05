import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

stalls = []
for l in doc['layers']:
    lname = l['name']
    for i, c in enumerate(l['kind']['children']):
        items = c.get('appearance', {}).get('items', [])
        for item in items:
            col = item.get('paint', {}).get('color', {})
            r, g, b = col.get('r', 0), col.get('g', 0), col.get('b', 0)
            if r > 0.8 and b > 0.8 and g < 0.2:
                for sp in extract_subpaths(c):
                    pts = [to_m(p) for p in sp['anchors']]
                    if pts:
                        xs = [p[0] for p in pts]
                        ys = [p[1] for p in pts]
                        stalls.append((lname, i, min(xs), max(xs), min(ys), max(ys)))

print(f"Total magenta stall paths: {len(stalls)}")
for s in stalls:
    print(f"Stall in {s[0]} child {s[1]}: X=[{s[2]:.2f}, {s[3]:.2f}], Y=[{s[4]:.2f}, {s[5]:.2f}]")

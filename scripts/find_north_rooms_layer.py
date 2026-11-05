import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Stalls 6-12 are at:
# In pt: X around 800-1400, Y around 700-1200
# In meter:
# X_pt = 1000 + xm * 28.346 -> xm = (X_pt - 1000) / 28.346
# Y_pt = 1500 - ym * 28.346 -> ym = -(Y_pt - 1500) / 28.346
# For Y_pt = 700 to 1100: ym = -(700 - 1500)/28.346 = +28m to +14m!
# For X_pt = 800 to 1400: xm = -7m to +14m!

print("Scanning for elements in North Parking Zone: X in [-10, 15], Y in [14, 38]...")

found_layers = {}
for l in doc['layers']:
    lname = l['name']
    items = []
    for i, c in enumerate(l['kind'].get('children', [])):
        sps = extract_subpaths(c)
        for sp in sps:
            pts = [to_m(p) for p in sp['anchors']]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if min(xs) < 15.0 and max(xs) > -10.0 and min(ys) < 42.0 and max(ys) > 14.0:
                items.append((i, pts, sp['closed'], len(pts)))
    if items:
        found_layers[lname] = len(items)

print("Layers with elements in this zone:")
for k, v in sorted(found_layers.items(), key=lambda x: -x[1]):
    print(f"  {k:25s}: {v} items")


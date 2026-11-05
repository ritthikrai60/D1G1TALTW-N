import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import math

doc = load_pdf_doc()['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Stalls 9-12 are at: X in [0.0, 12.0], Y in [15.0, 38.0]
# Let's inspect all items in 'เส้นบาง', '0', 'P-1', 'P-3', 'P-4', 'P-5', 'A-wall' in this exact bounding box!
test_layers = ['เส้นบาง', '0', 'P-1', 'P-3', 'P-4', 'P-5', 'A-wall', 'P-1 (0.50)']

print("=== INSPECTING LINES BEHIND PARKING 6-12 ===")
for lname in test_layers:
    l = [x for x in doc['layers'] if x['name'] == lname][0]
    matched = []
    for i, c in enumerate(l['kind'].get('children', [])):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if 0.0 <= min(xs) <= 12.0 and 15.0 <= min(ys) <= 38.0:
                p0, p1 = pts[0], pts[-1]
                length = math.hypot(p1[0]-p0[0], p1[1]-p0[1])
                matched.append((i, len(pts), length, p0, p1, sp['closed']))
    if matched:
        print(f"\nLayer '{lname}': {len(matched)} matched items")
        for i, npts, length, p0, p1, closed in matched[:10]:
            print(f"  item {i:3d}: pts={npts:2d}, len={length:5.2f}m, closed={closed}, {p0} -> {p1}")



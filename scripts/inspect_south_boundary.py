import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from shapely.geometry import LineString

doc = load_pdf_doc()['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

print("Inspecting paths with Y < -18.0 in 00-Ground_Floor-Clean.pdf:")
for l in doc['layers']:
    lname = l['name']
    for i, c in enumerate(l['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            ys = [p[1] for p in pts]
            if not ys: continue
            if min(ys) < -18.0:
                xs = [p[0] for p in pts]
                print(f"Layer {lname:15s} child {i:2d}: pts={len(pts)}, X=[{min(xs):6.2f}, {max(xs):6.2f}], Y=[{min(ys):6.2f}, {max(ys):6.2f}]")


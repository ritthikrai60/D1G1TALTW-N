import sys
sys.path.insert(0, '.')
from scripts.inspect_exact_core_stair import to_m, load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import ensure_ccw, poly_area

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
stair = layers['A-stair']

# Flight 1 lines (4 steps going East)
f1_lines = []
for idx in [43, 39, 37, 35]:
    c = stair['kind']['children'][idx]
    pts = [to_m(p) for p in extract_subpaths(c)[0]['anchors']]
    if pts[0][1] < pts[1][1]: pts = [pts[1], pts[0]]
    f1_lines.append(pts)

start_l1 = [(8.075, -11.678), (8.075, -13.159)]
f1_polys = []
for i in range(len(f1_lines)):
    prev_l = start_l1 if i == 0 else f1_lines[i-1]
    curr_l = f1_lines[i]
    poly = [prev_l[0], curr_l[0], curr_l[1], prev_l[1]]
    f1_polys.append(ensure_ccw(poly))

print(f"Flight 1 step polygons: {len(f1_polys)}")

# Flight 2 lines (10 steps going North on East side)
f2_lines = []
for idx in [11, 14, 15, 16, 17, 18, 19, 20, 21, 22]:
    c = stair['kind']['children'][idx]
    pts = [to_m(p) for p in extract_subpaths(c)[0]['anchors']]
    # sort by X: pts[0] is at center divider (~9.6m), pts[1] is at east wall (~10.6m)
    if pts[0][0] > pts[1][0]: pts = [pts[1], pts[0]]
    f2_lines.append(pts)

# start line for flight 2 at north edge of lower landing
start_l2 = [(9.60, -11.45), (10.60, -11.45)]
f2_polys = []
for i in range(len(f2_lines)):
    prev_l = start_l2 if i == 0 else f2_lines[i-1]
    curr_l = f2_lines[i]
    poly = [prev_l[0], curr_l[0], curr_l[1], prev_l[1]]
    f2_polys.append(ensure_ccw(poly))

print(f"Flight 2 step polygons: {len(f2_polys)}")

# Lower landing polygon
lower_landing_poly = ensure_ccw([
    (8.934, -13.039), (10.619, -12.80), (10.60, -11.45), (8.711, -11.45)
])
print(f"Lower landing area: {abs(poly_area(lower_landing_poly)):.2f} m2")

# Upper landing polygon
upper_landing_poly = ensure_ccw([
    (8.877, -9.025), (10.259, -9.025), (10.259, -7.80), (8.877, -7.80)
])
print(f"Upper landing area: {abs(poly_area(upper_landing_poly)):.2f} m2")


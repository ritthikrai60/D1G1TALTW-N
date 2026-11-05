import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m, ensure_ccw, poly_area

doc = load_pdf_doc()['document']
stair = {l['name']: l for l in doc['layers']}['A-stair']

# Flight 2 lines (East side, climbing North):
# Child 12, 66, 68, 70, 72, 74, 76, 78, 80, 82
f2_line_indices = [12, 66, 68, 70, 72, 74, 76, 78, 80, 82]
f2_lines = []
for idx in f2_line_indices:
    c = stair['kind']['children'][idx]
    pts = [to_m(p) for p in extract_subpaths(c)[0]['anchors']]
    if pts[0][0] > pts[1][0]: pts = [pts[1], pts[0]]
    f2_lines.append(pts)

# Flight 3 lines (West side, returning South):
# Child 84, 83, 81, 79, 77, 75, 73, 71, 69, 67, 13
f3_line_indices = [84, 83, 81, 79, 77, 75, 73, 71, 69, 67, 13]
f3_lines = []
for idx in f3_line_indices:
    c = stair['kind']['children'][idx]
    pts = [to_m(p) for p in extract_subpaths(c)[0]['anchors']]
    if pts[0][0] > pts[1][0]: pts = [pts[1], pts[0]]
    f3_lines.append(pts)

print(f"Flight 2 lines: {len(f2_lines)}")
for i, l in enumerate(f2_lines):
    print(f"  F2 line {i:2d}: {l}")

print(f"\nFlight 3 lines: {len(f3_lines)}")
for i, l in enumerate(f3_lines):
    print(f"  F3 line {i:2d}: {l}")

# Build 10 steps for Flight 3 from consecutive pairs of f3_lines
f3_full_polys = []
for i in range(len(f3_lines) - 1):
    l0 = f3_lines[i]
    l1 = f3_lines[i+1]
    poly = ensure_ccw([l0[0], l1[0], l1[1], l0[1]])
    f3_full_polys.append(poly)
    print(f"  F3 Step {i:2d}: area={poly_area(poly):.3f} m2, corners={poly}")


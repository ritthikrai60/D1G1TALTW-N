import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
stair = layers['A-stair']

X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

def poly_area(pts):
    return 0.5 * sum(pts[i][0]*pts[(i+1)%len(pts)][1] - pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))

def ensure_ccw(pts):
    if poly_area(pts) < 0:
        return pts[::-1]
    return pts

# 1. SOUTH OUTDOOR STAIRS: 16 STEPS
# Extract consecutive pairs of step lines to form exact 4-corner step polygons!
step_lines = []
for idx in range(89, 105):
    c = stair['kind']['children'][idx]
    pts = [to_m(p) for p in extract_subpaths(c)[0]['anchors']]
    # ensure p0 is at north end, p1 is at south end
    if pts[0][1] < pts[1][1]:
        pts = [pts[1], pts[0]]
    step_lines.append(pts)

# Add west landing edge as the start line (step 0 starts at west landing)
landing_edge = [(4.125, -18.687), (4.427, -21.168)]

outdoor_step_polys = []
for i in range(len(step_lines)):
    if i == 0:
        prev_l = [(3.828, -18.723), (4.13, -21.204)] # landing edge
    else:
        prev_l = step_lines[i-1]
    curr_l = step_lines[i]
    # 4 corners: prev_p0 -> curr_p0 -> curr_p1 -> prev_p1
    poly = [prev_l[0], curr_l[0], curr_l[1], prev_l[1]]
    outdoor_step_polys.append(ensure_ccw(poly))

print(f"Constructed {len(outdoor_step_polys)} exact 4-corner outdoor step polygons:")
for i, poly in enumerate(outdoor_step_polys):
    print(f"  Step {i:2d}: area={abs(poly_area(poly)):.2f} m2, corners={poly}")


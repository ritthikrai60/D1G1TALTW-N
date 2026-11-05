import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Retaining wall points in meters (origin X0=1000, Y0=1500)
X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Look at core walls extent
ar_hatch = layers['AR_HATCH']
core_pts = []
for c in ar_hatch.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if min(p[1] for p in pts) >= 900:
            core_pts.extend([to_m(p) for p in pts])

xs = [p[0] for p in core_pts]
ys = [p[1] for p in core_pts]
print(f"Service core walls bounding box (m): X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}]")

# Look at columns extent
acol = layers['A-col']
col_pts = []
for c in acol.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if len(pts) >= 4 and min(p[1] for p in pts) >= 900 and sum(p[0] for p in pts)/len(pts) < 1650:
            col_pts.extend([to_m(p) for p in pts])

xs_col = [p[0] for p in col_pts]
ys_col = [p[1] for p in col_pts]
print(f"Parking & Core columns bounding box (m): X=[{min(xs_col):.2f}, {max(xs_col):.2f}], Y=[{min(ys_col):.2f}, {max(ys_col):.2f}]")


import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

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

# Extract all 77 columns
all_cols = []
acol = layers['A-col']
for i, c in enumerate(acol.get('kind', {}).get('children', [])):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if len(pts) >= 4:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            w = (max(xs) - min(xs))/SCALE
            h = (max(ys) - min(ys))/SCALE
            cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
            if 0.15 <= w <= 1.5 and 0.15 <= h <= 1.5:
                pts_m = [to_m(p) for p in pts]
                if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
                all_cols.append({'poly': ensure_ccw(pts_m), 'center': to_m((cx, cy)), 'src': f'A-col_{i}'})

p1 = layers.get('P-1')
if p1:
    for i, c in enumerate(p1.get('kind', {}).get('children', [])):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if len(pts) >= 4:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                w = (max(xs) - min(xs))/SCALE
                h = (max(ys) - min(ys))/SCALE
                cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
                if 0.2 <= w <= 1.5 and 0.2 <= h <= 1.5:
                    pts_m = [to_m(p) for p in pts]
                    if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
                    all_cols.append({'poly': ensure_ccw(pts_m), 'center': to_m((cx, cy)), 'src': f'P-1_{i}'})

# Remove duplicates
unique_cols = []
for c in all_cols:
    cx, cy = c['center']
    if not any((cx - uc['center'][0])**2 + (cy - uc['center'][1])**2 < 0.2**2 for uc in unique_cols):
        unique_cols.append(c)

print(f"Verified Unique Columns: {len(unique_cols)}")
for idx, c in enumerate(unique_cols):
    print(f"  Col {idx:02d} [{c['src']:8s}]: center={c['center']}, pts={len(c['poly'])}")


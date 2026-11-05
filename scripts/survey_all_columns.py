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

all_cols = []

# 1. A-col columns
acol = layers['A-col']
for i, c in enumerate(acol.get('kind', {}).get('children', [])):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if len(pts) >= 4:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            w = (max(xs) - min(xs))/SCALE
            h = (max(ys) - min(ys))/SCALE
            cx = sum(xs)/len(xs)
            cy = sum(ys)/len(ys)
            if 0.15 <= w <= 1.5 and 0.15 <= h <= 1.5:
                pts_m = [to_m(p) for p in pts]
                if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
                all_cols.append({
                    'source': 'A-col',
                    'idx': i,
                    'center': to_m((cx, cy)),
                    'w': round(w, 2),
                    'h': round(h, 2),
                    'poly': ensure_ccw(pts_m)
                })

# 2. P-1 columns (Northern zone)
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
                cx = sum(xs)/len(xs)
                cy = sum(ys)/len(ys)
                if 0.2 <= w <= 1.5 and 0.2 <= h <= 1.5:
                    pts_m = [to_m(p) for p in pts]
                    if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
                    all_cols.append({
                        'source': 'P-1',
                        'idx': i,
                        'center': to_m((cx, cy)),
                        'w': round(w, 2),
                        'h': round(h, 2),
                        'poly': ensure_ccw(pts_m)
                    })

print(f"Total columns extracted: {len(all_cols)}")
# Check for duplicates by center distance
unique_cols = []
for c in all_cols:
    cx, cy = c['center']
    is_dup = False
    for uc in unique_cols:
        ux, uy = uc['center']
        if (cx - ux)**2 + (cy - uy)**2 < 0.2**2:
            is_dup = True
            break
    if not is_dup:
        unique_cols.append(c)

print(f"Unique columns: {len(unique_cols)}")
# Group unique columns by zone:
# 1. Parking undercroft
# 2. Service core
# 3. North expansion / building block
# 4. East hillside terrace
zones = {'parking': 0, 'core': 0, 'north': 0, 'east_slope': 0}
for c in unique_cols:
    cx, cy = c['center']
    if cy > 22.0:
        zones['north'] += 1
    elif cx > 22.0:
        zones['east_slope'] += 1
    elif cx >= -0.5 and cy <= 10.0:
        zones['core'] += 1
    else:
        zones['parking'] += 1

print("Columns by zone:", zones)


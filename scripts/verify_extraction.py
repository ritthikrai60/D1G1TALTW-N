import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import json

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

# 1. Structural Columns
acol = layers['A-col']
columns = []
for c in acol.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if len(pts) >= 4:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
            w, h = (max(xs) - min(xs))/SCALE, (max(ys) - min(ys))/SCALE
            if cy >= 900 and cx < 1650 and w < 1.5 and h < 1.5:
                pts_m = [to_m(p) for p in pts]
                if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
                pts_m = ensure_ccw(pts_m)
                columns.append({'poly': pts_m, 'center': to_m((cx, cy))})

# 2. Retaining wall P-1 (0.50)
p1_050 = layers['P-1 (0.50)']
retaining_wall = []
for c in p1_050.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if len(pts) >= 8:
            pts_m = [to_m(p) for p in pts]
            if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
            retaining_wall = ensure_ccw(pts_m)

# 3. Core Walls (AR_HATCH)
ar_hatch = layers['AR_HATCH']
core_walls = []
for c in ar_hatch.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if min(p[1] for p in pts) >= 900:
            pts_m = [to_m(p) for p in pts]
            if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
            if len(pts_m) >= 3 and abs(poly_area(pts_m)) > 0.005:
                pts_m = ensure_ccw(pts_m)
                core_walls.append(pts_m)

# 4. Restroom Partitions from P-2 and P-4 (0.10)
partitions = []
for lname in ['P-2 (0.15)', 'P-4 (0.10)']:
    l = layers.get(lname)
    if not l: continue
    for c in l.get('kind', {}).get('children', []):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if min(p[1] for p in pts) >= 900:
                pts_m = [to_m(p) for p in pts]
                if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
                if len(pts_m) >= 3 and abs(poly_area(pts_m)) > 0.01:
                    pts_m = ensure_ccw(pts_m)
                    partitions.append(pts_m)

# 5. Grand Entrance Stairs
stair = layers['A-stair']
entrance_steps = []
for idx in range(89, 105):
    c = stair['kind']['children'][idx]
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        if len(pts) == 2:
            entrance_steps.append(pts)

# 6. Slabs
# Parking curved curb points
south_curb = stair['kind']['children'][6]
curb_pts = [to_m(p) for p in extract_subpaths(south_curb)[0]['anchors']]

print("=== SUMMARY OF EXTRACTED GROUND FLOOR CAD GEOMETRY ===")
print(f"Columns: {len(columns)}")
print(f"Retaining wall points: {len(retaining_wall)}")
print(f"Core walls (AR_HATCH): {len(core_walls)}")
print(f"Partitions (P-2, P-4): {len(partitions)}")
print(f"Entrance stairs step lines: {len(entrance_steps)}")
print(f"Parking south curb points: {len(curb_pts)}")


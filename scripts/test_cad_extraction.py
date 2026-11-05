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

# Check columns
cols_m = []
acol = layers['A-col']
for c in acol.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if len(pts) >= 4:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            cy = sum(ys)/len(ys)
            cx = sum(xs)/len(xs)
            w = (max(xs) - min(xs))/SCALE
            h = (max(ys) - min(ys))/SCALE
            # filter to ground floor parking & core
            if cy >= 900 and cx < 1650 and w < 1.5 and h < 1.5:
                pts_m = [to_m(p) for p in pts]
                # remove duplicate closing point if present
                if pts_m[0] == pts_m[-1]:
                    pts_m = pts_m[:-1]
                cols_m.append({'center': to_m((cx, cy)), 'w': round(w, 2), 'h': round(h, 2), 'poly': pts_m})

print(f"Ground floor columns extracted: {len(cols_m)}")

# Check retaining wall
retaining_poly = []
p1_050 = layers['P-1 (0.50)']
for c in p1_050.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if len(pts) >= 8: # main closed loop
            pts_m = [to_m(p) for p in pts]
            if pts_m[0] == pts_m[-1]:
                pts_m = pts_m[:-1]
            retaining_poly = pts_m

print(f"Retaining wall polygon points: {len(retaining_poly)}")
print("Retaining wall poly:", retaining_poly)

# Check core walls
core_walls = []
ar_hatch = layers['AR_HATCH']
for c in ar_hatch.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        ys = [p[1] for p in pts]
        if min(ys) >= 900:
            pts_m = [to_m(p) for p in pts]
            if pts_m[0] == pts_m[-1]:
                pts_m = pts_m[:-1]
            if len(pts_m) >= 3:
                core_walls.append(pts_m)

print(f"Ground floor core walls (AR_HATCH): {len(core_walls)}")


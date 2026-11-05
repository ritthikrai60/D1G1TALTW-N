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

# Check walls in North zone: AR_HATCH and A-wall
north_walls = []
for lname in ['AR_HATCH', 'A-wall']:
    l = layers.get(lname)
    if not l: continue
    for c in l.get('kind', {}).get('children', []):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if max(p[1] for p in pts) < 900:
                pts_m = [to_m(p) for p in pts]
                if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
                area = abs(poly_area(pts_m))
                if len(pts_m) >= 3 and area > 0.01:
                    north_walls.append((lname, pts_m, area))

print(f"Total north walls extracted: {len(north_walls)}")
for lname, pts_m, a in north_walls[:10]:
    xs = [p[0] for p in pts_m]
    ys = [p[1] for p in pts_m]
    print(f"  [{lname:10s}] area={a:.2f} m2, pts={len(pts_m)}, X=[{min(xs):.1f},{max(xs):.1f}], Y=[{min(ys):.1f},{max(ys):.1f}]")


import sys
sys.path.insert(0, '.')
from scripts.verify_all_77_cols import unique_cols, to_m, ensure_ccw, poly_area, load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Core walls (South)
core_walls_south = []
for c in layers['AR_HATCH'].get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if min(p[1] for p in pts) >= 900:
            pts_m = [to_m(p) for p in pts]
            if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
            if len(pts_m) >= 3 and abs(poly_area(pts_m)) > 0.005:
                core_walls_south.append(ensure_ccw(pts_m))

# North walls (North wing)
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
                if len(pts_m) >= 3 and abs(poly_area(pts_m)) > 0.01:
                    north_walls.append(ensure_ccw(pts_m))

print(f"South core walls: {len(core_walls_south)}")
print(f"North wing walls: {len(north_walls)}")
print(f"Total columns: {len(unique_cols)}")


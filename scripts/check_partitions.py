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

for lname in ['P-2', 'P-2 (0.15)', 'P-4 (0.10)', 'WC-OUTL']:
    l = layers.get(lname)
    if not l: continue
    loops = []
    for c in l.get('kind', {}).get('children', []):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if min(p[1] for p in pts) >= 900:
                pts_m = [to_m(p) for p in pts]
                if pts_m[0] == pts_m[-1]: pts_m = pts_m[:-1]
                if len(pts_m) >= 3:
                    area = abs(poly_area(pts_m))
                    if area > 0.01:
                        loops.append((pts_m, area))
    print(f"Layer {lname:15s}: {len(loops)} closed loops with area > 0.01 m2")
    for pts_m, a in loops[:5]:
        print(f"   area={a:.3f} m2, pts={len(pts_m)}, bbox=X:[{min(p[0] for p in pts_m):.2f}, {max(p[0] for p in pts_m):.2f}], Y:[{min(p[1] for p in pts_m):.2f}, {max(p[1] for p in pts_m):.2f}]")


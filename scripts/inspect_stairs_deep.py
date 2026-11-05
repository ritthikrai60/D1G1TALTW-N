import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import json

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
stair = layers['A-stair']

X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

print(f"Total children in A-stair: {len(stair['kind']['children'])}")

# Group stair elements by location
groups = {}
for i, c in enumerate(stair['kind']['children']):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        cx = sum(xs)/len(xs)
        cy = sum(ys)/len(ys)
        w = (max(xs) - min(xs))/SCALE
        h = (max(ys) - min(ys))/SCALE
        
        # Categorize region
        # 1. South entrance (cy > 1850)
        # 2. Service core (cy in [1200, 1850] and cx in [1100, 1400])
        # 3. Restroom / corridor stairs (cy in [1200, 1500])
        # 4. North wing stairs (cy < 1000)
        # 5. Curb / island (not stairs)
        region = "other"
        if cy > 1850:
            region = "south_entrance"
        elif 1650 <= cy <= 1850 and 1200 <= cx <= 1350:
            region = "core_stair_dogleg"
        elif 1200 <= cy <= 1500 and 1200 <= cx <= 1350:
            region = "core_upper_stair"
        elif cy < 1000:
            region = "north_stair"
        elif cx < 500:
            region = "west_curb"
        
        groups.setdefault(region, []).append({
            'idx': i,
            'pts_len': len(pts),
            'closed': sp['closed'],
            'cx': cx,
            'cy': cy,
            'cx_m': to_m((cx, cy))[0],
            'cy_m': to_m((cx, cy))[1],
            'w': w,
            'h': h,
            'pts': pts
        })

print("\nSummary of A-stair by region:")
for reg, items in groups.items():
    print(f"  Region '{reg}': {len(items)} paths")


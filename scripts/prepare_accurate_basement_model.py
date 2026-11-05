import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import json
import math

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Coordinate transform constants (consistent with previous accurate column extraction)
X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    # Match previous transformation
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# 1. SLAB POLYGON (from previous perimeter calculation)
with open('scripts/build_full_ingetrazo_ground_floor.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract slab_poly from build_full_ingetrazo_ground_floor.py
import re
slab_match = re.search(r'slab_poly\s*=\s*(\[.*?\])\n', text, re.DOTALL)
slab_poly = eval(slab_match.group(1))
print(f"Loaded slab polygon: {len(slab_poly)} points")

# 2. COLUMNS (all 77 columns)
cols = []
for lname in ['A-col', 'P-1']:
    l = layers.get(lname)
    if not l: continue
    for i, c in enumerate(l['kind']['children']):
        sps = extract_subpaths(c)
        for sp in sps:
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4:
                # check bounding box
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                dx = max(xs) - min(xs)
                dy = max(ys) - min(ys)
                # valid structural column dimensions (0.3m to 1.5m)
                if 0.25 <= dx <= 2.0 and 0.25 <= dy <= 2.0:
                    cols.append({
                        'name': f"Col_{len(cols):02d}_{lname}_{i}",
                        'pts': pts,
                        'bbox': (min(xs), min(ys), max(xs), max(ys))
                    })
print(f"Total valid structural columns: {len(cols)}")

# 3. ST-1: PRIMARY FIRE EGRESS STAIR (P-2 (0.15))
# Children in P-2 (0.15):
# c0..c9: East flight steps (X in [3.0, 4.7], Y in [-3.0, -0.6])
# c14..c18: West flight steps (X in [1.4, 3.0], Y in [-3.2, -1.7])
p2_layer = layers['P-2 (0.15)']
st1_east_steps = []
st1_west_steps = []
for i, c in enumerate(p2_layer['kind']['children']):
    sps = extract_subpaths(c)
    for sp in sps:
        pts = [to_m(p) for p in sp['anchors']]
        if len(pts) == 2:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if 6.0 <= min(xs) <= 12.0 and -14.0 <= min(ys) <= -4.0:
                pass
print("Analyzing exact coordinate mapping for ST-1, ST-2, ST-3...")


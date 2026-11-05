import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import shapely
from shapely.geometry import Polygon, MultiPolygon, Point
import re

# Load payload
with open('scripts/flawless_basement_final_payload.py', 'r', encoding='utf-8') as f:
    text = f.read()

slab_match = re.search(r'slab_poly\s*=\s*(\[.*?\])', text, re.DOTALL)
slab_pts = eval(slab_match.group(1))
p_slab = Polygon(slab_pts)

# Find all columns
col_pattern = re.compile(r"g_(\d+)\s*=\s*(?:extrude|prism)\((\[.*?\]),.*?name='(.*?)'", re.DOTALL)
matches = col_pattern.findall(text)

print(f"Slab vertices: {len(slab_pts)}, valid: {p_slab.is_valid}")
if not p_slab.is_valid:
    from shapely.validation import explain_validity
    print("Validity issue:", explain_validity(p_slab))

# Check every column and every assembly
poking = []
for idx_str, poly_str, name in matches:
    coords = eval(poly_str)
    pts_2d = [(round(p[0], 3), round(p[1], 3)) for p in coords]
    if len(pts_2d) < 3: continue
    
    # Check each vertex of this element against the slab polygon
    pts_outside = []
    for pt in pts_2d:
        p_pt = Point(pt)
        # Check distance to slab: if outside, distance > 0
        if not p_slab.buffer(1e-4).contains(p_pt):
            pts_outside.append(pt)
    
    if pts_outside:
        poking.append((name, pts_outside, pts_2d))

print(f"\nTotal elements with vertices OUTSIDE the slab: {len(poking)}")
for name, outside_pts, all_pts in poking:
    print(f"\nElement: {name}")
    print(f"  Total vertices: {len(all_pts)}, Outside vertices: {len(outside_pts)}")
    for op in outside_pts:
        print(f"    Outside vertex: {op}")


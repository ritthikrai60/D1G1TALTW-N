import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import shapely
from shapely.geometry import Polygon, MultiPolygon, Point
import re

# 1. Load current slab poly from payload
with open('scripts/flawless_basement_final_payload.py', 'r', encoding='utf-8') as f:
    text = f.read()

slab_match = re.search(r'slab_poly\s*=\s*(\[.*?\])', text, re.DOTALL)
slab_pts = eval(slab_match.group(1))
p_slab = Polygon(slab_pts)

print(f"Slab valid: {p_slab.is_valid}, Area: {p_slab.area:.2f} m^2, Bounds: {p_slab.bounds}")

# 2. Extract all assemblies / columns from payload
pattern = re.compile(r"g_(\d+)\s*=\s*(?:extrude|prism)\((\[.*?\]),.*?name='(.*?)'", re.DOTALL)
matches = pattern.findall(text)
print(f"Found {len(matches)} assemblies in payload")

poking_elements = []
for idx_str, poly_str, name in matches:
    coords = eval(poly_str)
    # If 3D coordinates (from prism), take x, y
    pts_2d = [(p[0], p[1]) for p in coords]
    if len(pts_2d) < 3: continue
    try:
        p_elem = Polygon(pts_2d)
        if not p_elem.is_valid:
            p_elem = p_elem.buffer(0)
        
        # Check if polygon is inside slab
        if not p_slab.contains(p_elem):
            # Find the difference (the part outside the slab)
            diff = p_elem.difference(p_slab)
            if diff.area > 1e-4:
                poking_elements.append((name, diff.area, diff.bounds, p_elem.bounds))
    except Exception as e:
        print(f"Error parsing {name}: {e}")

print(f"\nTotal elements with parts outside the slab: {len(poking_elements)}")
for name, diff_area, diff_bounds, elem_bounds in poking_elements:
    print(f"  {name:25s}: outside_area={diff_area:6.3f}m2, outside_bounds={diff_bounds}, elem_bounds={elem_bounds}")


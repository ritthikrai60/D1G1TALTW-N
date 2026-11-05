import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from shapely.geometry import Polygon
import shapely.ops

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Collect all column polygons (77 columns)
cols = []
for lname in ['A-col', 'P-1']:
    l = layers.get(lname)
    if not l: continue
    for i, c in enumerate(l['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4:
                try:
                    p = Polygon(pts)
                    if p.is_valid and 0.04 <= p.area <= 4.0:
                        cols.append(p)
                except: pass

print(f"Valid Column Polygons: {len(cols)}")

# Collect all A-wall polygons
walls = []
l_wall = layers.get('A-wall')
for i, c in enumerate(l_wall['kind']['children']):
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        if len(pts) >= 4:
            try:
                p = Polygon(pts)
                if p.is_valid and p.area > 0.005:
                    walls.append(p)
            except: pass

print(f"Valid Wall Polygons: {len(walls)}")

# Check intersections: Which walls touch or overlap with columns?
touching_pairs = 0
for w in walls:
    for c in cols:
        if w.intersects(c):
            touching_pairs += 1

print(f"Total Wall-Column Intersections / Contacts: {touching_pairs}")

# Test 2D Boolean Union of all intersecting Walls and Columns!
# Using shapely.ops.unary_union
combined = cols + walls
print(f"Total shapes to union: {len(combined)}")

union_result = shapely.ops.unary_union(combined)
print(f"\n=== MONOLITHIC UNION RESULT ===")
print(f"Result geometry type: {union_result.geom_type}")
if union_result.geom_type == 'MultiPolygon':
    print(f"Result has {len(union_result.geoms)} monolithic polygon components:")
    # Breakdown by component: standalone columns vs monolithic wall-column clusters
    monolithic_clusters = []
    standalone_items = []
    for g in union_result.geoms:
        if g.area > 0.8: # Wall-column assemblies
            monolithic_clusters.append(g)
        else: # standalone columns or small wall piers
            standalone_items.append(g)
    print(f"  - Monolithic Wall+Column Assemblies: {len(monolithic_clusters)} components")
    print(f"  - Standalone Columns/Piers: {len(standalone_items)} components")
    for idx, g in enumerate(monolithic_clusters[:5]):
        print(f"    Cluster {idx}: Area={g.area:.2f} m^2, Vertices={len(g.exterior.coords)}, Holes={len(g.interiors)}")


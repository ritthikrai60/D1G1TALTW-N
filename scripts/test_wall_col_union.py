import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import shapely
from shapely.geometry import Polygon, MultiPolygon, LineString, box
import shapely.ops

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Let's pick 2 columns near the core and the wall connecting them:
# Columns: Col near (9.2, 3.5) and (6.1, 7.4)
# Let's inspect columns near X in [5.0, 10.0], Y in [2.0, 8.0]
col_polys = []
for lname in ['A-col', 'P-1']:
    l = layers.get(lname)
    if not l: continue
    for i, c in enumerate(l['kind']['children']):
        sps = extract_subpaths(c)
        for sp in sps:
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4 and sp['closed']:
                p = Polygon(pts)
                if p.is_valid and p.area > 0.05:
                    b = p.bounds
                    if 5.0 <= b[0] <= 11.0 and 2.0 <= b[1] <= 9.0:
                        col_polys.append((f"{lname}_{i}", p))

print(f"Core area columns found: {len(col_polys)}")
for name, cp in col_polys:
    print(f"  {name}: center=({cp.centroid.x:.2f}, {cp.centroid.y:.2f}), area={cp.area:.3f} m^2")

# Let's find walls connecting these columns
a_wall = layers['A-wall']
wall_polys = []
for i, c in enumerate(a_wall['kind']['children']):
    sps = extract_subpaths(c)
    for sp in sps:
        pts = [to_m(p) for p in sp['anchors']]
        if len(pts) >= 4 and sp['closed']:
            p = Polygon(pts)
            if p.is_valid and p.area > 0.01:
                b = p.bounds
                if 5.0 <= b[0] <= 11.0 and 2.0 <= b[1] <= 9.0:
                    wall_polys.append((f"wall_{i}", p))

print(f"Core area closed walls found: {len(wall_polys)}")

# Now test Boolean Union between columns and connecting walls!
all_shapes = [p for _, p in col_polys] + [p for _, p in wall_polys]
if all_shapes:
    unified = shapely.ops.unary_union(all_shapes)
    print("\n=== BOOLEAN UNION RESULT ===")
    print(f"Input shapes count: {len(all_shapes)}")
    print(f"Unified shape type: {unified.geom_type}")
    if unified.geom_type == 'Polygon':
        print(f"Unified Polygon: exterior vertices = {len(unified.exterior.coords)}, holes = {len(unified.interiors)}")
    elif unified.geom_type == 'MultiPolygon':
        print(f"Unified MultiPolygon: {len(unified.geoms)} separate monolithic blocks")
        for idx, g in enumerate(unified.geoms):
            print(f"  Block {idx}: vertices={len(g.exterior.coords)}, area={g.area:.2f} m^2, holes={len(g.interiors)}")


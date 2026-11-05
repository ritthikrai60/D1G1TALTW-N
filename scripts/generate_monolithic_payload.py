import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import shapely
from shapely.geometry import Polygon, MultiPolygon
import shapely.ops
import json
import math

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# 1. LOAD SLAB POLYGON
with open('scripts/generated_basement_updated_payload.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
slab_match = re.search(r'g_slab\s*=\s*extrude\((\[.*?\]),', text, re.DOTALL)
slab_poly = eval(slab_match.group(1))

# 2. LOAD ALL 77 STRUCTURAL COLUMNS
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
                    if p.is_valid and 0.04 <= p.area <= 3.0:
                        xs = [pt[0] for pt in pts]
                        ys = [pt[1] for pt in pts]
                        dx = max(xs) - min(xs)
                        dy = max(ys) - min(ys)
                        if 0.20 <= dx <= 2.0 and 0.20 <= dy <= 2.0:
                            cols.append(p)
                except: pass

# Deduplicate
unique_cols = []
seen = set()
for cp in cols:
    center = (round(cp.centroid.x, 2), round(cp.centroid.y, 2))
    if center not in seen:
        seen.add(center)
        unique_cols.append(cp)

print(f"Unique columns: {len(unique_cols)}")

# 3. LOAD ALL WALLS
wall_polys = []
l_wall = layers.get('A-wall')
for i, c in enumerate(l_wall['kind']['children']):
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        if len(pts) >= 4:
            try:
                p = Polygon(pts)
                if p.is_valid and p.area > 0.005:
                    wall_polys.append(p)
            except: pass

p1_50 = layers.get('P-1 (0.50)')
if p1_50:
    for i, c in enumerate(p1_50['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4:
                try:
                    p = Polygon(pts)
                    if p.is_valid and p.area > 0.5:
                        wall_polys.append(p)
                except: pass

print(f"Full-height walls: {len(wall_polys)}")

# 4. PERFORM MONOLITHIC 2D BOOLEAN UNION
combined_shapes = unique_cols + wall_polys
monolithic_union = shapely.ops.unary_union(combined_shapes)

if monolithic_union.geom_type == 'MultiPolygon':
    assemblies = list(monolithic_union.geoms)
elif monolithic_union.geom_type == 'Polygon':
    assemblies = [monolithic_union]

print(f"Total monolithic assemblies: {len(assemblies)}")

# 5. RESTROOM PARTITIONS (P-4 (0.10))
partitions = []
l_part = layers.get('P-4 (0.10)')
if l_part:
    for i, c in enumerate(l_part['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) == 2:
                p0, p1 = pts[0], pts[1]
                length = math.hypot(p1[0]-p0[0], p1[1]-p0[1])
                if 0.40 <= length <= 3.5:
                    partitions.append((p0, p1))

print(f"Partitions: {len(partitions)}")

# GENERATE PYTHON SCRIPT
lines = [
    "# === MONOLITHIC INTEGRATED BASEMENT MODEL ===",
    "# Single Flat Slab + Monolithically Unified Columns & Walls + Partitions + 3 Authentic Stairs",
    "groups.clear()",
    "",
    "# Ensure layers exist",
    "layer_names = [l.name for l in layers]",
    "for lname in ['Slabs', 'Structure_and_Walls', 'Partitions', 'Stairs']:",
    "    if lname not in layer_names:",
    "        layers.append(Layer(lname))",
    "",
    "# 1. SINGLE UNIFIED FLAT BASEMENT SLAB (Z = 0.00m, thickness 0.20m, 4043.59 m^2)",
    f"slab_poly = {slab_poly}",
    "g_slab = extrude(slab_poly, -0.20, 0.0, name='Basement_Floor_Slab', color=(0.78, 0.80, 0.82, 1.0))",
    "g_slab.layer = 'Slabs'",
    "",
    "# 2. MONOLITHIC COLUMNS AND WALLS (Height: 3.50m, perfectly dissolved seams)"
]

for idx, poly in enumerate(assemblies):
    # Simplify slightly to avoid collinear CAD micro-artifacts
    p_clean = poly.simplify(0.005, preserve_topology=True)
    ext_coords = [(round(x, 3), round(y, 3)) for x, y in p_clean.exterior.coords]
    
    # Check if this assembly is a monolithic wall+column cluster or a standalone column
    name = f"Monolithic_Core_Assembly_{idx:02d}" if poly.area > 0.8 else f"Structural_Column_{idx:02d}"
    color = "(0.84, 0.82, 0.79, 1.0)" if poly.area > 0.8 else "(0.88, 0.86, 0.84, 1.0)"
    
    if len(p_clean.interiors) == 0:
        lines.append(f"g_{idx} = extrude({ext_coords}, 0.0, 3.50, name='{name}', color={color})")
        lines.append(f"g_{idx}.layer = 'Structure_and_Walls'")
    else:
        # Polygon with holes: use prism
        pts3d = [f"QVector3D({x}, {y}, 0.0)" for x, y in ext_coords]
        holes_code = []
        for h in p_clean.interiors:
            h_coords = [(round(hx, 3), round(hy, 3)) for hx, hy in h.coords]
            h_3d = [f"QVector3D({hx}, {hy}, 0.0)" for hx, hy in h_coords]
            holes_code.append(f"[{', '.join(h_3d)}]")
        
        lines.append(f"pts3d_{idx} = [{', '.join(pts3d)}]")
        lines.append(f"holes_{idx} = [{', '.join(holes_code)}]")
        lines.append(f"g_{idx} = prism(pts3d_{idx}, QVector3D(0, 0, 3.50), holes=holes_{idx}, name='{name}', color={color})")
        lines.append(f"g_{idx}.layer = 'Structure_and_Walls'")

lines.extend([
    "",
    "# 3. RESTROOM PARTITIONS (Height: 2.20m, Thickness: 0.10m)"
])

for i, (p0, p1) in enumerate(partitions):
    lines.append(f"p_{i} = wall(({p0[0]}, {p0[1]}), ({p1[0]}, {p1[1]}), height=2.20, thickness=0.10, name='Partition_{i:02d}', color=(0.76, 0.79, 0.83, 1.0))")
    lines.append(f"p_{i}.layer = 'Partitions'")

lines.extend([
    "",
    "# 4. ST-1: PRIMARY FIRE EGRESS STAIR CORE (Layer P-2 (0.15))",
    "for s in range(5):",
    "    z = round(s * 0.175, 3)",
    "    y_pos = round(5.05 + s * 0.25, 3)",
    "    st = box((6.15, y_pos, 0.00), (1.50, 0.28, z + 0.175), name=f'ST1_West_Step_{s+1}', color=(0.82, 0.76, 0.70, 1.0))",
    "    st.layer = 'Stairs'",
    "st1_mid = box((6.15, 6.28, 0.00), (3.30, 1.25, 0.875), name='ST1_Mid_Landing', color=(0.82, 0.76, 0.70, 1.0))",
    "st1_mid.layer = 'Stairs'",
    "st1_rail = box((7.65, 3.50, 0.00), (0.10, 2.75, 1.20), name='ST1_Center_Rail', color=(0.50, 0.52, 0.55, 1.0))",
    "st1_rail.layer = 'Stairs'",
    "for s in range(10):",
    "    z = round(0.875 + s * 0.175, 3)",
    "    y_pos = round(6.00 - s * 0.25, 3)",
    "    st = box((7.75, y_pos, 0.00), (1.50, 0.28, z + 0.175), name=f'ST1_East_Step_{s+1}', color=(0.82, 0.76, 0.70, 1.0))",
    "    st.layer = 'Stairs'",
    "",
    "# 5. ST-2: CENTRAL OPEN STAIR NEAR LOCKERS (Layer A-stair)",
    "for s in range(4):",
    "    z = round(s * 0.175, 3)",
    "    x_pos = round(8.00 + s * 0.25, 3)",
    "    st = box((x_pos, -13.15, 0.00), (0.28, 1.45, z + 0.175), name=f'ST2_Entrance_Step_{s+1}', color=(0.75, 0.78, 0.85, 1.0))",
    "    st.layer = 'Stairs'",
    "st2_low = box((8.85, -13.15, 0.00), (1.50, 1.65, 0.70), name='ST2_Lower_Landing', color=(0.75, 0.78, 0.85, 1.0))",
    "st2_low.layer = 'Stairs'",
    "for s in range(10):",
    "    z = round(0.70 + s * 0.175, 3)",
    "    y_pos = round(-11.45 + s * 0.25, 3)",
    "    st = box((8.90, y_pos, 0.00), (1.45, 0.28, z + 0.175), name=f'ST2_Main_Step_{s+1}', color=(0.75, 0.78, 0.85, 1.0))",
    "    st.layer = 'Stairs'",
    "st2_mid = box((8.90, -8.95, 0.00), (1.50, 1.20, 2.45), name='ST2_Mid_Landing', color=(0.75, 0.78, 0.85, 1.0))",
    "st2_mid.layer = 'Stairs'",
    "",
    "# 6. ST-3: SOUTH OUTDOOR LANDSCAPE STAIR (Layer A-stair)",
    "for s in range(16):",
    "    z = round((s + 1) * 0.15, 3)",
    "    x_pos = round(4.15 + s * 0.30, 3)",
    "    y_pos = round(-21.15 + s * 0.038, 3)",
    "    st = box((x_pos, y_pos, 0.00), (0.33, 2.60, z), name=f'ST3_Landscape_Step_{s+1:02d}', color=(0.86, 0.82, 0.76, 1.0))",
    "    st.layer = 'Stairs'",
    "",
    "# 7. VIEWPORT CAMERA & UPDATE",
    "viewport.camera.target = QVector3D(8.0, -3.0, 1.5)",
    "viewport.camera.distance = 55.0",
    "viewport.camera.yaw = -0.75",
    "viewport.camera.pitch = 0.55",
    "viewport.update()",
    "print('Monolithic Integrated Basement Model built successfully! Total groups:', len(groups))"
])

full_script = "\n".join(lines)
with open('scripts/monolithic_basement_payload.py', 'w', encoding='utf-8') as f:
    f.write(full_script)

print(f"Generated monolithic_basement_payload.py: {len(lines)} lines, {len(full_script)} bytes")


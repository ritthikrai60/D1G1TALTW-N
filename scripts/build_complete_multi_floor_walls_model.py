import math
import uuid
import json
import sys
sys.path.insert(0, '.')
from shapely.geometry import Polygon
from shapely.ops import triangulate

# 1. IMPORT COLUMNS
from scripts.extract_f00_columns import pure_cols as f00_cols
from scripts.extract_pure_columns import pure_cols as f01_cols

# 2. IMPORT WALLS
from scripts.test_extract_all_walls import f00_walls, f01_walls, f02_walls

# 3. DEFINE SLAB POLYGON
slab_pts = [
    (-26.5, 44.0), (-26.5, -17.5), (2.5, -17.5), (2.5, -23.0),
    (10.5, -23.0), (10.5, -18.0), (17.5, -18.0), (22.5, -14.5),
    (32.0, -10.0), (42.5, -6.0), (53.0, -1.5), (66.5, 3.5),
    (68.5, 7.5), (68.5, 23.5), (33.0, 23.5), (33.0, 44.0), (-26.5, 44.0)
]

def polygon_to_group(pts_2d, z0, z1, name, layer_name, color=(0.82, 0.80, 0.78, 1.0)):
    if len(pts_2d) > 1 and pts_2d[0] == pts_2d[-1]:
        pts_2d = pts_2d[:-1]
    n = len(pts_2d)
    faces = []
    edges = []
    
    # Bottom face
    v_bot = [[pt[0], pt[1], z0] for pt in reversed(pts_2d)]
    faces.append({'vertices': v_bot, 'color': list(color)})
    
    # Top face
    v_top = [[pt[0], pt[1], z1] for pt in pts_2d]
    faces.append({'vertices': v_top, 'color': list(color)})
    
    # Side faces and edges
    for i in range(n):
        p1 = pts_2d[i]
        p2 = pts_2d[(i + 1) % n]
        quad = [
            [p1[0], p1[1], z0],
            [p2[0], p2[1], z0],
            [p2[0], p2[1], z1],
            [p1[0], p1[1], z1]
        ]
        faces.append({'vertices': quad, 'color': list(color)})
        edges.append({'a': [p1[0], p1[1], z0], 'b': [p2[0], p2[1], z0]})
        edges.append({'a': [p1[0], p1[1], z1], 'b': [p2[0], p2[1], z1]})
        edges.append({'a': [p1[0], p1[1], z0], 'b': [p1[0], p1[1], z1]})
        
    return {
        'name': name,
        'layer': layer_name,
        'uid': uuid.uuid4().hex[:16],
        'faces': faces,
        'edges': edges
    }

def polygon_with_holes_to_group(poly, z0, z1, name, layer_name, color=(0.92, 0.90, 0.86, 1.0)):
    faces = []
    edges = []
    triangles = [t for t in triangulate(poly) if poly.contains(t.centroid)]
    
    # Bottom faces
    for t in triangles:
        coords = list(t.exterior.coords)[:-1]
        v_bot = [[pt[0], pt[1], z0] for pt in reversed(coords)]
        faces.append({'vertices': v_bot, 'color': list(color)})
        
    # Top faces
    for t in triangles:
        coords = list(t.exterior.coords)[:-1]
        v_top = [[pt[0], pt[1], z1] for pt in coords]
        faces.append({'vertices': v_top, 'color': list(color)})
        
    # Exterior sides
    ext_coords = list(poly.exterior.coords)[:-1]
    n_ext = len(ext_coords)
    for i in range(n_ext):
        p1 = ext_coords[i]
        p2 = ext_coords[(i + 1) % n_ext]
        quad = [
            [p1[0], p1[1], z0],
            [p2[0], p2[1], z0],
            [p2[0], p2[1], z1],
            [p1[0], p1[1], z1]
        ]
        faces.append({'vertices': quad, 'color': list(color)})
        edges.append({'a': [p1[0], p1[1], z0], 'b': [p2[0], p2[1], z0]})
        edges.append({'a': [p1[0], p1[1], z1], 'b': [p2[0], p2[1], z1]})
        edges.append({'a': [p1[0], p1[1], z0], 'b': [p1[0], p1[1], z1]})
        
    # Interior sides (holes)
    for interior in poly.interiors:
        int_coords = list(interior.coords)[:-1]
        n_int = len(int_coords)
        for i in range(n_int):
            p1 = int_coords[i]
            p2 = int_coords[(i + 1) % n_int]
            quad = [
                [p1[0], p1[1], z0],
                [p1[0], p1[1], z1],
                [p2[0], p2[1], z1],
                [p2[0], p2[1], z0]
            ]
            faces.append({'vertices': quad, 'color': list(color)})
            edges.append({'a': [p1[0], p1[1], z0], 'b': [p2[0], p2[1], z0]})
            edges.append({'a': [p1[0], p1[1], z1], 'b': [p2[0], p2[1], z1]})
            edges.append({'a': [p1[0], p1[1], z0], 'b': [p1[0], p1[1], z1]})
            
    return {
        'name': name,
        'layer': layer_name,
        'uid': uuid.uuid4().hex[:16],
        'faces': faces,
        'edges': edges
    }

def make_box_prism_mesh(center_x, center_y, width, depth, z_bottom, z_top, angle_deg, name, layer_name, color=(0.85, 0.82, 0.78, 1.0)):
    rad = math.radians(angle_deg)
    c, s = math.cos(rad), math.sin(rad)
    hw, hd = width / 2.0, depth / 2.0
    corners = [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)]
    pts = [(round(center_x + x * c - y * s, 3), round(center_y + x * s + y * c, 3)) for x, y in corners]
    return polygon_to_group(pts, z_bottom, z_top, name, layer_name, color)

def make_box_prism_code(center_x, center_y, width, depth, z_bottom, z_top, angle_deg, name, color=(0.85, 0.82, 0.78, 1.0)):
    rad = math.radians(angle_deg)
    c, s = math.cos(rad), math.sin(rad)
    hw, hd = width / 2.0, depth / 2.0
    corners = [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)]
    rot_pts = [(round(center_x + x * c - y * s, 3), round(center_y + x * s + y * c, 3)) for x, y in corners]
    rot_pts.append(rot_pts[0])
    return f"g = extrude({rot_pts}, {z_bottom:.2f}, {z_top:.2f}, name='{name}', color={color})\ng.layer = 'Stairs'"

all_groups = []
py_lines = [
    "# === MASTER MULTI-FLOOR DIGITAL TWIN WITH COMPLETE WALLS ===",
    "# Slabs + Columns + Complete Wall Architecture for All Floors + Authenticated Stairs",
    "groups.clear()",
    "layer_names = [l.name for l in layers]",
    "for lname in ['Slabs', 'F00_Structure', 'F01_Structure', 'F00_Walls', 'F01_Walls', 'F02_Walls', 'Stairs']:",
    "    if lname not in layer_names:",
    "        layers.append(Layer(lname))",
    ""
]

# --- 1. SLABS (F00, F01, F02, F03) ---
py_lines.append("# --- FLOOR SLABS ---")
slab_configs = [
    ('F00_Ground_Slab', -0.25, 0.00, (0.70, 0.72, 0.75, 1.0)),
    ('F01_First_Floor_Slab', 3.30, 3.50, (0.72, 0.74, 0.77, 1.0)),
    ('F02_Second_Floor_Slab', 7.30, 7.50, (0.74, 0.76, 0.79, 1.0)),
    ('F03_Roof_Slab', 11.30, 11.50, (0.76, 0.78, 0.80, 1.0))
]
for sname, zb, zt, col in slab_configs:
    g = polygon_to_group(slab_pts, zb, zt, sname, 'Slabs', col)
    all_groups.append(g)
    py_lines.append(f"g = extrude({slab_pts}, {zb:.2f}, {zt:.2f}, name='{sname}', color={col})\ng.layer = 'Slabs'")

# --- 2. COLUMNS ---
py_lines.append("\n# --- STRUCTURAL COLUMNS ---")
# F00 Columns
for idx, (pts, cx, cy, dx, dy, area) in enumerate(f00_cols):
    name = f"F00_Structural_Column_{idx:02d}"
    g = polygon_to_group(pts, 0.00, 3.50, name, 'F00_Structure', color=(0.82, 0.80, 0.78, 1.0))
    all_groups.append(g)
    py_lines.append(f"c0_{idx} = extrude({pts}, 0.00, 3.50, name='{name}', color=(0.82, 0.80, 0.78, 1.0))\nc0_{idx}.layer = 'F00_Structure'")

# F01 Columns
for idx, (pts, cx, cy, dx, dy, area) in enumerate(f01_cols):
    name = f"F01_Structural_Column_{idx:02d}"
    g = polygon_to_group(pts, 3.50, 7.50, name, 'F01_Structure', color=(0.88, 0.85, 0.80, 1.0))
    all_groups.append(g)
    py_lines.append(f"c1_{idx} = extrude({pts}, 3.50, 7.50, name='{name}', color=(0.88, 0.85, 0.80, 1.0))\nc1_{idx}.layer = 'F01_Structure'")

# --- 3. WALLS FOR EVERY FLOOR ---
def add_floor_walls(wall_polys, z0, z1, prefix, layer_name, color=(0.92, 0.90, 0.86, 1.0)):
    py_lines.append(f"\n# --- {layer_name} (Z: {z0:.2f}m to {z1:.2f}m) ---")
    dz = z1 - z0
    for idx, poly in enumerate(wall_polys):
        name = f"{prefix}_{idx:02d}"
        g = polygon_with_holes_to_group(poly, z0, z1, name, layer_name, color)
        all_groups.append(g)
        
        # Python representation
        ext_pts = [tuple(round(v, 3) for v in pt) for pt in poly.exterior.coords]
        if len(poly.interiors) == 0:
            py_lines.append(f"w = extrude({ext_pts}, {z0:.2f}, {z1:.2f}, name='{name}', color={color})\nw.layer = '{layer_name}'")
        else:
            holes_pts = [[tuple(round(v, 3) for v in pt) for pt in hole.coords] for hole in poly.interiors]
            ext_pts_3d = [(p[0], p[1], z0) for p in ext_pts]
            holes_pts_3d = [[(p[0], p[1], z0) for p in h] for h in holes_pts]
            py_lines.append(f"w = prism({ext_pts_3d}, (0, 0, {dz:.2f}), holes={holes_pts_3d}, name='{name}', color={color})\nw.layer = '{layer_name}'")

# Floor 00 Walls (Height: 3.50m)
add_floor_walls(f00_walls, 0.00, 3.50, 'F00_Wall', 'F00_Walls', color=(0.91, 0.89, 0.85, 1.0))

# Floor 01 Walls (Height: 4.00m)
add_floor_walls(f01_walls, 3.50, 7.50, 'F01_Wall', 'F01_Walls', color=(0.93, 0.91, 0.88, 1.0))

# Floor 02 Walls (Height: 4.00m)
add_floor_walls(f02_walls, 7.50, 11.50, 'F02_Wall', 'F02_Walls', color=(0.95, 0.93, 0.90, 1.0))

# --- 4. ALL 11 STAIRS ---
py_lines.append("\n# --- ALL 11 AUTHENTICATED STAIR SYSTEMS ---")

def add_stair_element(mesh_g, code_str):
    all_groups.append(mesh_g)
    py_lines.append(code_str)

# STAIR 1: STAIR 3 (`บันได 3`) North Core Shaft at (7.60, 4.50)
st3_east_x, st3_west_x = 8.50, 6.75
st3_y_start = 3.15
run_st3 = 0.25
n_treads = 11

for step in range(n_treads):
    sy = round(st3_y_start + step * run_st3 + run_st3 / 2.0, 3)
    z_b = round(step * (1.75 / n_treads), 3)
    z_t = round((step + 1) * (1.75 / n_treads), 3)
    name = f"F00_Stair3_East_Tread_{step+1:02d}"
    g = make_box_prism_mesh(st3_east_x, sy, 1.50, run_st3, z_b, z_t, 0.0, name, 'Stairs')
    c = make_box_prism_code(st3_east_x, sy, 1.50, run_st3, z_b, z_t, 0.0, name)
    add_stair_element(g, c)

st3_land_y = round(st3_y_start + n_treads * run_st3 + 0.80, 3)
g_l0 = make_box_prism_mesh(7.625, st3_land_y, 3.25, 1.60, 1.55, 1.75, 0.0, 'F00_Stair3_Mid_Landing', 'Stairs', color=(0.80, 0.78, 0.75, 1.0))
c_l0 = make_box_prism_code(7.625, st3_land_y, 3.25, 1.60, 1.55, 1.75, 0.0, 'F00_Stair3_Mid_Landing', color=(0.80, 0.78, 0.75, 1.0))
add_stair_element(g_l0, c_l0)

for step in range(n_treads):
    sy = round(st3_y_start + (n_treads - 1 - step) * run_st3 + run_st3 / 2.0, 3)
    z_b = round(1.75 + step * (1.75 / n_treads), 3)
    z_t = round(1.75 + (step + 1) * (1.75 / n_treads), 3)
    name = f"F00_Stair3_West_Tread_{step+1:02d}"
    g = make_box_prism_mesh(st3_west_x, sy, 1.50, run_st3, z_b, z_t, 0.0, name, 'Stairs')
    c = make_box_prism_code(st3_west_x, sy, 1.50, run_st3, z_b, z_t, 0.0, name)
    add_stair_element(g, c)

for step in range(n_treads):
    sy = round(st3_y_start + step * run_st3 + run_st3 / 2.0, 3)
    z_b = round(3.50 + step * (1.75 / n_treads), 3)
    z_t = round(3.50 + (step + 1) * (1.75 / n_treads), 3)
    name = f"F01_Stair3_East_Tread_{step+1:02d}"
    g = make_box_prism_mesh(st3_east_x, sy, 1.50, run_st3, z_b, z_t, 0.0, name, 'Stairs')
    c = make_box_prism_code(st3_east_x, sy, 1.50, run_st3, z_b, z_t, 0.0, name)
    add_stair_element(g, c)

g_l1 = make_box_prism_mesh(7.625, st3_land_y, 3.25, 1.60, 5.05, 5.25, 0.0, 'F01_Stair3_Mid_Landing', 'Stairs', color=(0.80, 0.78, 0.75, 1.0))
c_l1 = make_box_prism_code(7.625, st3_land_y, 3.25, 1.60, 5.05, 5.25, 0.0, 'F01_Stair3_Mid_Landing', color=(0.80, 0.78, 0.75, 1.0))
add_stair_element(g_l1, c_l1)

for step in range(n_treads):
    sy = round(st3_y_start + (n_treads - 1 - step) * run_st3 + run_st3 / 2.0, 3)
    z_b = round(5.25 + step * (1.75 / n_treads), 3)
    z_t = round(5.25 + (step + 1) * (1.75 / n_treads), 3)
    name = f"F01_Stair3_West_Tread_{step+1:02d}"
    g = make_box_prism_mesh(st3_west_x, sy, 1.50, run_st3, z_b, z_t, 0.0, name, 'Stairs')
    c = make_box_prism_code(st3_west_x, sy, 1.50, run_st3, z_b, z_t, 0.0, name)
    add_stair_element(g, c)

# STAIR 2: STAIR 5 / ST-1
for step in range(4):
    ex = round(8.55 + step * 0.28, 3)
    z_b = round(step * 0.175, 3)
    z_t = round((step + 1) * 0.175, 3)
    name = f"F00_Stair5_Entry_Step_{step+1}"
    g = make_box_prism_mesh(ex, -12.35, 0.28, 1.50, z_b, z_t, 0.0, name, 'Stairs')
    c = make_box_prism_code(ex, -12.35, 0.28, 1.50, z_b, z_t, 0.0, name)
    add_stair_element(g, c)

for step in range(17):
    sy = round(-11.25 + step * 0.25 + 0.125, 3)
    z_b = round(3.50 + step * (1.75 / 17), 3)
    z_t = round(3.50 + (step + 1) * (1.75 / 17), 3)
    name = f"F01_Stair5_Tread_{step+1:02d}"
    g = make_box_prism_mesh(9.83, sy, 1.50, 0.25, z_b, z_t, 0.0, name, 'Stairs')
    c = make_box_prism_code(9.83, sy, 1.50, 0.25, z_b, z_t, 0.0, name)
    add_stair_element(g, c)

# STAIR 3: ST-2 Portico
n_portico = 17
dx_port = 5.59 / n_portico
for step in range(n_portico):
    sx = round(3.50 + step * dx_port + dx_port / 2.0, 3)
    z_b = round(0.35 + step * (3.15 / n_portico), 3)
    z_t = round(0.35 + (step + 1) * (3.15 / n_portico), 3)
    name = f"South_Portico_Step_{step+1:02d}"
    g = make_box_prism_mesh(sx, -19.45, dx_port, 4.20, z_b, z_t, 0.0, name, 'Stairs', color=(0.86, 0.84, 0.80, 1.0))
    c = make_box_prism_code(sx, -19.45, dx_port, 4.20, z_b, z_t, 0.0, name, color=(0.86, 0.84, 0.80, 1.0))
    add_stair_element(g, c)

for step in range(3):
    sy = round(-18.75 - step * 0.40, 3)
    z_b = round(2.90 + step * 0.20, 3)
    z_t = round(2.90 + (step + 1) * 0.20, 3)
    name = f"Facade_Porch_Step_{step+1}"
    g = make_box_prism_mesh(12.80, sy, 7.40, 0.40, z_b, z_t, 0.0, name, 'Stairs', color=(0.86, 0.84, 0.80, 1.0))
    c = make_box_prism_code(12.80, sy, 7.40, 0.40, z_b, z_t, 0.0, name, color=(0.86, 0.84, 0.80, 1.0))
    add_stair_element(g, c)

# STAIR 4: Fan Steps
n_fan = 10
for step in range(n_fan):
    r_in = 2.40 + step * 0.24
    r_out = r_in + 0.25
    z_b = round(3.50 + step * (1.00 / n_fan), 3)
    z_t = round(3.50 + (step + 1) * (1.00 / n_fan), 3)
    arc_pts = []
    for a_deg in range(90, 215, 15):
        rad = math.radians(a_deg)
        arc_pts.append((round(11.0 + r_out * math.cos(rad), 3), round(1.5 + r_out * math.sin(rad), 3)))
    for a_deg in range(210, 85, -15):
        rad = math.radians(a_deg)
        arc_pts.append((round(11.0 + r_in * math.cos(rad), 3), round(1.5 + r_in * math.sin(rad), 3)))
    name = f"Foyer_Fan_Step_{step+1:02d}"
    g = polygon_to_group(arc_pts, z_b, z_t, name, 'Stairs', color=(0.87, 0.85, 0.82, 1.0))
    arc_code = arc_pts + [arc_pts[0]]
    c = f"g = extrude({arc_code}, {z_b:.2f}, {z_t:.2f}, name='{name}', color=(0.87, 0.85, 0.82, 1.0))\ng.layer = 'Stairs'"
    add_stair_element(g, c)

# STAIR 5: Spiral
n_spiral = 16
for step in range(n_spiral):
    ang1 = 180.0 + step * (220.0 / n_spiral)
    ang2 = ang1 + (220.0 / n_spiral)
    r1, r2 = math.radians(ang1), math.radians(ang2)
    pts = [
        (round(17.50 + 1.00 * math.cos(r1), 3), round(-4.50 + 1.00 * math.sin(r1), 3)),
        (round(17.50 + 2.25 * math.cos(r1), 3), round(-4.50 + 2.25 * math.sin(r1), 3)),
        (round(17.50 + 2.25 * math.cos(r2), 3), round(-4.50 + 2.25 * math.sin(r2), 3)),
        (round(17.50 + 1.00 * math.cos(r2), 3), round(-4.50 + 1.00 * math.sin(r2), 3))
    ]
    z_b = round(3.50 + step * (3.20 / n_spiral), 3)
    z_t = round(z_b + 0.12, 3)
    name = f"Spiral_Stair_Tread_{step+1:02d}"
    g = polygon_to_group(pts, z_b, z_t, name, 'Stairs', color=(0.90, 0.88, 0.85, 1.0))
    pts_code = pts + [pts[0]]
    c = f"g = extrude({pts_code}, {z_b:.2f}, {z_t:.2f}, name='{name}', color=(0.90, 0.88, 0.85, 1.0))\ng.layer = 'Stairs'"
    add_stair_element(g, c)

# STAIR 6: Pro Shop
for step in range(8):
    sy = round(-6.20 + step * 0.28, 3)
    z_b = round(3.50 + step * (1.30 / 8), 3)
    z_t = round(3.50 + (step + 1) * (1.30 / 8), 3)
    name = f"Retail_Shop_Step_{step+1}"
    g = make_box_prism_mesh(20.00, sy, 1.40, 0.28, z_b, z_t, 0.0, name, 'Stairs')
    c = make_box_prism_code(20.00, sy, 1.40, 0.28, z_b, z_t, 0.0, name)
    add_stair_element(g, c)

# STAIR 7: East 33 deg
for step in range(10):
    dist = step * 0.28
    cx = round(54.63 - dist * math.cos(math.radians(33)), 3)
    cy = round(18.77 - dist * math.sin(math.radians(33)), 3)
    z_b = round(3.50 + step * 0.20, 3)
    z_t = round(3.50 + (step + 1) * 0.20, 3)
    name = f"East_Wall_Stair_Step_{step+1:02d}"
    g = make_box_prism_mesh(cx, cy, 1.23, 0.28, z_b, z_t, 33.0, name, 'Stairs')
    c = make_box_prism_code(cx, cy, 1.23, 0.28, z_b, z_t, 33.0, name)
    add_stair_element(g, c)

# STAIR 8: Kitchen Dock
for step in range(9):
    sy = round(9.70 - step * 0.28, 3)
    z_b = round(3.50 - (step + 1) * (1.50 / 9), 3)
    z_t = round(3.50 - step * (1.50 / 9), 3)
    name = f"Kitchen_Dock_Step_{step+1}"
    g = make_box_prism_mesh(61.50, sy, 1.50, 0.28, z_b, z_t, 0.0, name, 'Stairs')
    c = make_box_prism_code(61.50, sy, 1.50, 0.28, z_b, z_t, 0.0, name)
    add_stair_element(g, c)

# STAIR 9: Outdoor Terrace
for step in range(7):
    dist = step * 0.35
    cx = round(64.50 - dist * math.cos(math.radians(33)), 3)
    cy = round(3.50 - dist * math.sin(math.radians(33)), 3)
    z_b = round(3.80 + step * (1.20 / 7), 3)
    z_t = round(3.80 + (step + 1) * (1.20 / 7), 3)
    name = f"Terrace_Outdoor_Step_{step+1}"
    g = make_box_prism_mesh(cx, cy, 3.80, 0.35, z_b, z_t, 33.0, name, 'Stairs')
    c = make_box_prism_code(cx, cy, 3.80, 0.35, z_b, z_t, 33.0, name)
    add_stair_element(g, c)

# STAIR 10: North Restroom
for step in range(3):
    sy = round(25.00 - step * 0.28, 3)
    z_b = round(3.50 + step * 0.10, 3)
    z_t = round(3.50 + (step + 1) * 0.10, 3)
    name = f"Restroom_Entrance_Step_{step+1}"
    g = make_box_prism_mesh(32.20, sy, 1.80, 0.28, z_b, z_t, 0.0, name, 'Stairs')
    c = make_box_prism_code(32.20, sy, 1.80, 0.28, z_b, z_t, 0.0, name)
    add_stair_element(g, c)

# STAIR 11: West Gym
for step in range(12):
    sy = round(38.00 + step * 0.28, 3)
    z_b = round(2.00 + step * (2.00 / 12), 3)
    z_t = round(2.00 + (step + 1) * (2.00 / 12), 3)
    name = f"Gym_Arena_Step_{step+1:02d}"
    g = make_box_prism_mesh(-16.50, sy, 1.50, 0.28, z_b, z_t, 0.0, name, 'Stairs')
    c = make_box_prism_code(-16.50, sy, 1.50, 0.28, z_b, z_t, 0.0, name)
    add_stair_element(g, c)

# 5. WRITE PYTHON PAYLOAD
with open('scripts/master_all_floors_walls_payload.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(py_lines) + '\n')
print(f"Generated scripts/master_all_floors_walls_payload.py: {len(py_lines)} lines.")

# 6. WRITE DIRECT .IGZ FILE
igz_data = {
    'igz_format': 1,
    'app_version': '0.6.0',
    'scene': {
        'edges': [],
        'faces': [],
        'groups': all_groups,
        'layers': [
            {'name': 'Layer 0'},
            {'name': 'Slabs'},
            {'name': 'F00_Structure'},
            {'name': 'F01_Structure'},
            {'name': 'F00_Walls'},
            {'name': 'F01_Walls'},
            {'name': 'F02_Walls'},
            {'name': 'Stairs'}
        ],
        'dimension_style': {
            'decimals': 2,
            'units': 'm',
            'font_size': 9,
            'color': [45, 55, 75],
            'norma': 'iso',
            'base_step_mm': 8.0,
            'ends': 'arrow',
            'show_unit': True
        },
        'camera': {
            'target': [18.0, 10.0, 5.5],
            'distance': 75.0,
            'yaw': -0.75,
            'pitch': 0.65,
            'fov_deg': 45.0,
            'perspective': True,
            'two_point': False
        }
    }
}

with open('01_Master_All_Floors_Walls.igz', 'w', encoding='utf-8') as f:
    json.dump(igz_data, f, indent=2)
print(f"Generated 01_Master_All_Floors_Walls.igz: {len(all_groups)} groups in scene.")

# Also update 01_First_Floor_Master.igz with the full multi-floor walls model
with open('01_First_Floor_Master.igz', 'w', encoding='utf-8') as f:
    json.dump(igz_data, f, indent=2)
print("Updated 01_First_Floor_Master.igz successfully.")


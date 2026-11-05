import bpy
import bmesh
import json
import math
import os
from mathutils import Matrix

ROOT_DIR = r"c:\Coding Projects\Digital Twin"
EXTRACTED_JSON = os.path.join(ROOT_DIR, "scripts", "extracted_geometry.json")
BLEND_OUT = os.path.join(ROOT_DIR, "building_digital_twin.blend")
GLB_OUT = os.path.join(ROOT_DIR, "public", "models", "building.glb")

# ---------------------------------------------------------------------------
# Low-Poly Helpers
# ---------------------------------------------------------------------------

def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)

def get_or_create_collection(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

def make_material(name, rgba, metallic=0.0, roughness=0.65, alpha=1.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (rgba[0], rgba[1], rgba[2], 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1.0 and hasattr(mat, "surface_render_method"):
        mat.surface_render_method = 'BLENDED'
    return mat

def add_box(bm, center, size, rot_z=0.0):
    mat = Matrix.Translation(center) @ Matrix.Rotation(rot_z, 4, 'Z') @ Matrix.Diagonal((size[0], size[1], size[2], 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat)

def add_wall_seg(bm, p1, p2, z_bottom, height, thickness=0.20):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length < 0.4:
        return
    cx = (p1[0] + p2[0]) * 0.5
    cy = (p1[1] + p2[1]) * 0.5
    cz = z_bottom + height * 0.5
    add_box(bm, (cx, cy, cz), (length, thickness, height), math.atan2(dy, dx))

def add_lowpoly_bay(bm_wall, bm_glass, p1, p2, z_base, height, wall_thick=0.32, is_arched=False):
    """Ultra-lightweight facade bay: 1 pillar + 1 header + 1 glass quad (only 3 boxes per bay)."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    bay_w = math.hypot(dx, dy)
    if bay_w < 0.8:
        return
    angle = math.atan2(dy, dx)
    cx, cy = (p1[0] + p2[0]) * 0.5, (p1[1] + p2[1]) * 0.5

    # Pillar at p1
    pil_w = 0.50
    add_box(bm_wall, (p1[0], p1[1], z_base + height * 0.5), (pil_w, wall_thick + 0.08, height), angle)

    # Top lintel / low-poly arch header
    head_h = 0.75 if is_arched else 0.50
    add_box(bm_wall, (cx, cy, z_base + height - head_h * 0.5), (bay_w, wall_thick, head_h), angle)

    # Single low-poly glass sheet
    open_h = height - head_h - 0.30
    add_box(bm_glass, (cx, cy, z_base + 0.30 + open_h * 0.5), (bay_w - pil_w, 0.06, open_h), angle)

def bmesh_to_object(bm, name, col, mat):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj

# ---------------------------------------------------------------------------
# Main Low-Poly Builder
# ---------------------------------------------------------------------------

def build_digital_twin():
    clear_scene()

    with open(EXTRACTED_JSON, "r", encoding="utf-8") as fp:
        cad_data = json.load(fp)

    col_f0 = get_or_create_collection("Floor_00_Ground")
    col_f1 = get_or_create_collection("Floor_01_First")
    col_f2 = get_or_create_collection("Floor_02_Second")
    col_f3 = get_or_create_collection("Floor_03_Roof")

    mat_terracotta = make_material("Mat_Terracotta_Main", (0.85, 0.58, 0.42), roughness=0.65)
    mat_trim       = make_material("Mat_Terracotta_Trim", (0.91, 0.70, 0.54), roughness=0.55)
    mat_int_wall   = make_material("Mat_Interior_Wall",   (0.95, 0.93, 0.90), roughness=0.75)
    mat_slab       = make_material("Mat_Floor_Slab",      (0.86, 0.83, 0.79), roughness=0.55)
    mat_asphalt    = make_material("Mat_Parking_Asphalt", (0.23, 0.25, 0.28), roughness=0.85)
    mat_glass      = make_material("Mat_Glass_Facade",    (0.15, 0.28, 0.38), metallic=0.1, roughness=0.2, alpha=0.45)
    mat_steel      = make_material("Mat_Steel_Dark",      (0.18, 0.20, 0.24), metallic=0.6, roughness=0.4)
    mat_roof_deck  = make_material("Mat_Roof_Deck",       (0.76, 0.72, 0.67), roughness=0.65)
    mat_door       = make_material("Mat_Door_Wood",       (0.55, 0.38, 0.26), roughness=0.55)

    # Main Spine Coordinates (Low-Poly: 8 West Bays, Central Portico, 6 East Curved Segments)
    west_front_pts = [
        (-44.04 + i * ((-16.37 - (-44.04)) / 8.0), -26.25 + i * ((-25.50 - (-26.25)) / 8.0))
        for i in range(9)
    ]
    west_rear_pts = [(-39.52, 9.87), (-9.62, 7.50)]

    portico_pts = [
        (-16.37, -25.50),
        (-12.50, -24.95),
        (-6.20, -23.75),
        (0.11, -22.48),
    ]

    # 6 clean segments along the East Curve (matches exact CAD anchor columns!)
    east_front_pts = [
        (0.11, -22.48),
        (10.87, -19.49),
        (21.33, -15.54),
        (31.44, -10.78),
        (37.75, -7.28),
        (43.96, -3.40),
    ]
    east_rear_pts = [
        (-3.36, -8.35),
        (6.22, -5.48),
        (15.58, -1.95),
        (24.62, 2.31),
        (30.26, 5.44),
        (35.82, 8.91),
    ]

    # =========================================================================
    # FLOOR 00: GROUND FLOOR (Z = 0.00m to 3.50m)
    # Authentic layout: Open undercroft parking lot on West, enclosed Core on East
    # No walls in unbuilt zone (Y > 10m), no slab on East hillside slope
    # =========================================================================
    Z0, H0 = 0.0, 3.50

    bm_f0_parking = bmesh.new()
    # Open Under-croft Parking Lot (stalls #1–#30 and driveways): X=-45.5..-17.0, Y=-28.0..+10.5
    add_box(bm_f0_parking, (-31.25, -8.75, Z0 - 0.12), (28.5, 38.5, 0.24))
    bmesh_to_object(bm_f0_parking, "F0_Slab_Parking", col_f0, mat_asphalt)

    bm_f0_core = bmesh.new()
    # South Core & Service Rooms (Restrooms, M&E, Stair Core): X=-19.0..-5.8, Y=-26.0..+8.5
    add_box(bm_f0_core, (-12.4, -8.75, Z0 - 0.10), (13.2, 34.5, 0.24))
    bmesh_to_object(bm_f0_core, "F0_Slab_Core", col_f0, mat_slab)

    bm_f0_cols = bmesh.new()
    for c in cad_data["floors"]["00"]["columns"]:
        if c.get("y", 0) <= 10.5:
            cw = c.get("w", 0.50)
            cd = c.get("d", 0.50)
            add_box(bm_f0_cols, (c["x"], c["y"], Z0 + H0 * 0.5), (cw, cd, H0))
    bmesh_to_object(bm_f0_cols, "F0_Col_Structure", col_f0, mat_terracotta)

    bm_f0_walls = bmesh.new()
    # Authentic Core Walls & Retaining Wall P-1 only (Y <= 8.5m, no walls in parking or unbuilt area)
    for seg in cad_data["floors"]["00"]["wall_segments"]:
        p1, p2 = seg["p1"], seg["p2"]
        if max(p1[1], p2[1]) <= 8.5:
            layer = seg.get("layer", "")
            thick = 0.50 if ("0.50" in layer or layer == "P-1") else (0.10 if ("0.10" in layer or layer == "P-4") else 0.20)
            add_wall_seg(bm_f0_walls, p1, p2, Z0, H0 - 0.15, thickness=thick)
    
    # Add Retaining Wall P-1 along east boundary
    add_wall_seg(bm_f0_walls, (-10.59, -25.09), (-5.82, -24.12), Z0, H0 - 0.15, thickness=0.50)
    add_wall_seg(bm_f0_walls, (-5.82, -24.12), (-9.43, -1.83), Z0, H0 - 0.15, thickness=0.50)
    add_wall_seg(bm_f0_walls, (-9.43, -1.83), (-9.43, 7.82), Z0, H0 - 0.15, thickness=0.50)
    add_wall_seg(bm_f0_walls, (-16.14, -25.89), (-11.04, -25.17), Z0, H0 - 0.15, thickness=0.50)
    bmesh_to_object(bm_f0_walls, "F0_Wall_Int_Partitions", col_f0, mat_int_wall)

    # 3D Low-Poly Door Assemblies
    bm_f0_doors = bmesh.new()
    for d in cad_data["floors"]["00"].get("doors", []):
        dw = d["width_m"]
        dx, dy = d["x"], d["y"]
        is_h = d.get("is_horizontal", True)
        dtype = d.get("type", "single")
        dz = Z0 + door_h * 0.5
        if dtype == "sliding_or_shutter":
            if is_h:
                add_box(bm_f0_doors, (dx, dy, dz), (dw - 0.10, 0.08, door_h))
            else:
                add_box(bm_f0_doors, (dx, dy, dz), (0.08, dw - 0.10, door_h))
        elif dtype == "double":
            half_w = (dw - 0.08) * 0.5
            if is_h:
                add_box(bm_f0_doors, (dx - half_w * 0.5 - 0.01, dy, dz), (half_w - 0.02, 0.06, door_h))
                add_box(bm_f0_doors, (dx + half_w * 0.5 + 0.01, dy, dz), (half_w - 0.02, 0.06, door_h))
            else:
                add_box(bm_f0_doors, (dx, dy - half_w * 0.5 - 0.01, dz), (0.06, half_w - 0.02, door_h))
                add_box(bm_f0_doors, (dx, dy + half_w * 0.5 + 0.01, dz), (0.06, half_w - 0.02, door_h))
        else:
            if is_h:
                add_box(bm_f0_doors, (dx, dy, dz), (dw - 0.08, 0.06, door_h))
            else:
                add_box(bm_f0_doors, (dx, dy, dz), (0.06, dw - 0.08, door_h))
    bmesh_to_object(bm_f0_doors, "F0_Door_Assemblies", col_f0, mat_door)

    # Low-Poly Main Entrance Stairs (aligned to CAD X=-14.34, Y=-32.0 to -25.5)
    bm_f0_stairs = bmesh.new()
    for s in range(6):
        t = (s + 0.5) / 6.0
        sy = -32.0 + t * 6.5
        sh = (s + 1) * (H0 / 6.0)
        add_box(bm_f0_stairs, (-14.34, sy, Z0 + sh * 0.5), (6.5, 1.05, sh), rot_z=0.12)
    bmesh_to_object(bm_f0_stairs, "F0_Stair_MainEntrance", col_f0, mat_trim)

    # =========================================================================
    # FLOOR 01: FIRST FLOOR (Z = 3.50m to 7.50m)
    # =========================================================================
    Z1, H1 = 3.50, 4.00

    bm_f1_slab = bmesh.new()
    west_slab_poly = [
        (-44.8, -28.0), (-16.37, -27.5), (0.11, -24.5),
        (-3.36, -8.35), (-9.62, 7.50), (-39.52, 9.87)
    ]
    v_bot = [bm_f1_slab.verts.new((p[0], p[1], Z1 - 0.22)) for p in west_slab_poly]
    v_top = [bm_f1_slab.verts.new((p[0], p[1], Z1)) for p in west_slab_poly]
    bm_f1_slab.faces.new(v_bot[::-1])
    bm_f1_slab.faces.new(v_top)
    for i in range(len(v_bot)):
        j = (i + 1) % len(v_bot)
        bm_f1_slab.faces.new([v_bot[i], v_bot[j], v_top[j], v_top[i]])

    for i in range(len(east_front_pts) - 1):
        quad = [east_front_pts[i], east_front_pts[i+1], east_rear_pts[i+1], east_rear_pts[i]]
        qb = [bm_f1_slab.verts.new((p[0], p[1], Z1 - 0.22)) for p in quad]
        qt = [bm_f1_slab.verts.new((p[0], p[1], Z1)) for p in quad]
        bm_f1_slab.faces.new(qb[::-1])
        bm_f1_slab.faces.new(qt)
        for k in range(4):
            m = (k + 1) % 4
            bm_f1_slab.faces.new([qb[k], qb[m], qt[m], qt[k]])
    bmesh_to_object(bm_f1_slab, "F1_Slab_Main", col_f1, mat_slab)

    bm_f1_ext = bmesh.new()
    bm_f1_glass = bmesh.new()
    for i in range(8):
        add_lowpoly_bay(bm_f1_ext, bm_f1_glass, west_front_pts[i], west_front_pts[i+1], Z1, H1, is_arched=False)
    add_wall_seg(bm_f1_ext, west_front_pts[0], west_rear_pts[0], Z1, H1, thickness=0.30)
    add_wall_seg(bm_f1_ext, west_rear_pts[0], west_rear_pts[1], Z1, H1, thickness=0.30)

    for i in range(3):
        add_lowpoly_bay(bm_f1_ext, bm_f1_glass, portico_pts[i], portico_pts[i+1], Z1, H1, is_arched=(i != 1))

    for i in range(len(east_front_pts) - 1):
        add_lowpoly_bay(bm_f1_ext, bm_f1_glass, east_front_pts[i], east_front_pts[i+1], Z1, H1, is_arched=False)
        add_wall_seg(bm_f1_ext, east_rear_pts[i], east_rear_pts[i+1], Z1, H1, thickness=0.30)
    add_wall_seg(bm_f1_ext, east_front_pts[-1], east_rear_pts[-1], Z1, H1, thickness=0.30)

    bmesh_to_object(bm_f1_ext, "F1_Wall_Ext_Facade", col_f1, mat_terracotta)
    bmesh_to_object(bm_f1_glass, "F1_Glass_Windows", col_f1, mat_glass)

    # Low-Poly Front Railing (2 simple parapet bars)
    bm_f1_rail = bmesh.new()
    add_wall_seg(bm_f1_rail, (-44.5, -27.8), (-12.5, -27.2), Z1, 1.0, thickness=0.20)
    add_wall_seg(bm_f1_rail, (-3.8, -25.2), (0.11, -24.2), Z1, 1.0, thickness=0.20)
    bmesh_to_object(bm_f1_rail, "F1_Railing_And_Trim", col_f1, mat_trim)

    bm_f1_cols = bmesh.new()
    for c in cad_data["floors"]["01"]["columns"]:
        add_box(bm_f1_cols, (c["x"], c["y"], Z1 + H1 * 0.5), (0.50, 0.50, H1))
    bmesh_to_object(bm_f1_cols, "F1_Col_Structure", col_f1, mat_terracotta)

    bm_f1_int = bmesh.new()
    for seg in cad_data["floors"]["01"]["wall_segments"]:
        if seg["p1"][1] > 10.5 and seg["p2"][1] > 10.5:
            continue
        add_wall_seg(bm_f1_int, seg["p1"], seg["p2"], Z1, H1 - 0.15, thickness=0.18)
    # Low-Poly Octagonal Circular Lounge Wall (8 segments instead of 24)
    circ_cx, circ_cy, circ_r = -33.2, -17.6, 5.1
    for s in range(8):
        if s in (2, 6):
            continue
        a0 = 2 * math.pi * s / 8.0
        a1 = 2 * math.pi * (s + 1) / 8.0
        add_wall_seg(
            bm_f1_int,
            (circ_cx + circ_r * math.cos(a0), circ_cy + circ_r * math.sin(a0)),
            (circ_cx + circ_r * math.cos(a1), circ_cy + circ_r * math.sin(a1)),
            Z1, H1 - 0.15, thickness=0.20
        )
    bmesh_to_object(bm_f1_int, "F1_Wall_Int_Partitions", col_f1, mat_int_wall)

    # Low-Poly Spiral Staircase (center post + 8 steps)
    bm_f1_spiral = bmesh.new()
    sp_cx, sp_cy = -7.95, -10.80
    add_box(bm_f1_spiral, (sp_cx, sp_cy, Z1 + H1 * 0.5), (0.60, 0.60, H1))
    for s in range(8):
        ang = math.radians(-20 + s * 32.0)
        sz = Z1 + (s + 1) * (H1 / 8.0)
        add_box(bm_f1_spiral, (sp_cx + 1.5 * math.cos(ang), sp_cy + 1.5 * math.sin(ang), sz), (2.2, 0.65, 0.18), rot_z=ang)
    bmesh_to_object(bm_f1_spiral, "F1_Stair_Spiral", col_f1, mat_trim)

    # =========================================================================
    # FLOOR 02: SECOND FLOOR (Z = 7.50m to 11.50m)
    # =========================================================================
    Z2, H2 = 7.50, 4.00

    bm_f2_slab = bmesh.new()
    west_f2_poly = [
        (-44.04, -26.25), (-16.37, -25.50), (0.11, -22.48),
        (-3.36, -8.35), (-9.62, 7.50), (-39.52, 9.87)
    ]
    v2_bot = [bm_f2_slab.verts.new((p[0], p[1], Z2 - 0.22)) for p in west_f2_poly]
    v2_top = [bm_f2_slab.verts.new((p[0], p[1], Z2)) for p in west_f2_poly]
    bm_f2_slab.faces.new(v2_bot[::-1])
    bm_f2_slab.faces.new(v2_top)
    for i in range(len(v2_bot)):
        j = (i + 1) % len(v2_bot)
        bm_f2_slab.faces.new([v2_bot[i], v2_bot[j], v2_top[j], v2_top[i]])

    for i in range(len(east_front_pts) - 1):
        quad = [east_front_pts[i], east_front_pts[i+1], east_rear_pts[i+1], east_rear_pts[i]]
        qb = [bm_f2_slab.verts.new((p[0], p[1], Z2 - 0.22)) for p in quad]
        qt = [bm_f2_slab.verts.new((p[0], p[1], Z2)) for p in quad]
        bm_f2_slab.faces.new(qb[::-1])
        bm_f2_slab.faces.new(qt)
        for k in range(4):
            m = (k + 1) % 4
            bm_f2_slab.faces.new([qb[k], qb[m], qt[m], qt[k]])
    bmesh_to_object(bm_f2_slab, "F2_Slab_Main", col_f2, mat_slab)

    bm_f2_ext = bmesh.new()
    bm_f2_glass = bmesh.new()
    for i in range(8):
        add_lowpoly_bay(bm_f2_ext, bm_f2_glass, west_front_pts[i], west_front_pts[i+1], Z2, H2, is_arched=True)
    add_wall_seg(bm_f2_ext, west_front_pts[0], west_rear_pts[0], Z2, H2, thickness=0.30)
    add_wall_seg(bm_f2_ext, west_rear_pts[0], west_rear_pts[1], Z2, H2, thickness=0.30)

    # Central Portico Arch Pediment (Low-Poly)
    add_lowpoly_bay(bm_f2_ext, bm_f2_glass, portico_pts[0], portico_pts[1], Z2, H2 + 0.3, is_arched=False)
    add_lowpoly_bay(bm_f2_ext, bm_f2_glass, portico_pts[1], portico_pts[2], Z2, H2 + 1.0, wall_thick=0.45, is_arched=True)
    add_lowpoly_bay(bm_f2_ext, bm_f2_glass, portico_pts[2], portico_pts[3], Z2, H2 + 0.3, is_arched=False)

    for i in range(len(east_front_pts) - 1):
        add_lowpoly_bay(bm_f2_ext, bm_f2_glass, east_front_pts[i], east_front_pts[i+1], Z2, H2, is_arched=True)
        add_wall_seg(bm_f2_ext, east_rear_pts[i], east_rear_pts[i+1], Z2, H2, thickness=0.30)
    add_wall_seg(bm_f2_ext, east_front_pts[-1], east_rear_pts[-1], Z2, H2, thickness=0.30)

    bmesh_to_object(bm_f2_ext, "F2_Wall_Ext_ArchedFacade", col_f2, mat_terracotta)
    bmesh_to_object(bm_f2_glass, "F2_Glass_ArchedWindows", col_f2, mat_glass)

    bm_f2_cols = bmesh.new()
    for c in cad_data["floors"]["01"]["columns"][::2]:
        add_box(bm_f2_cols, (c["x"], c["y"], Z2 + H2 * 0.5), (0.50, 0.50, H2))
    bmesh_to_object(bm_f2_cols, "F2_Col_Structure", col_f2, mat_terracotta)

    bm_f2_int = bmesh.new()
    for seg in cad_data["floors"]["02"]["wall_segments"]:
        if seg["p1"][1] > 10.5 and seg["p2"][1] > 10.5:
            continue
        add_wall_seg(bm_f2_int, seg["p1"], seg["p2"], Z2, H2 - 0.15, thickness=0.18)
    bmesh_to_object(bm_f2_int, "F2_Wall_Int_Partitions", col_f2, mat_int_wall)

    # =========================================================================
    # FLOOR 03: ROOF FLOOR (Z = 11.50m to 19.50m)
    # =========================================================================
    Z3, H3 = 11.50, 3.50

    bm_f3_slab = bmesh.new()
    v3_bot = [bm_f3_slab.verts.new((p[0], p[1], Z3 - 0.22)) for p in west_f2_poly]
    v3_top = [bm_f3_slab.verts.new((p[0], p[1], Z3)) for p in west_f2_poly]
    bm_f3_slab.faces.new(v3_bot[::-1])
    bm_f3_slab.faces.new(v3_top)
    for i in range(len(v3_bot)):
        j = (i + 1) % len(v3_bot)
        bm_f3_slab.faces.new([v3_bot[i], v3_bot[j], v3_top[j], v3_top[i]])

    for i in range(len(east_front_pts) - 1):
        quad = [east_front_pts[i], east_front_pts[i+1], east_rear_pts[i+1], east_rear_pts[i]]
        qb = [bm_f3_slab.verts.new((p[0], p[1], Z3 - 0.22)) for p in quad]
        qt = [bm_f3_slab.verts.new((p[0], p[1], Z3)) for p in quad]
        bm_f3_slab.faces.new(qb[::-1])
        bm_f3_slab.faces.new(qt)
        for k in range(4):
            m = (k + 1) % 4
            bm_f3_slab.faces.new([qb[k], qb[m], qt[m], qt[k]])
    bmesh_to_object(bm_f3_slab, "F3_Slab_RoofDeck", col_f3, mat_roof_deck)

    # Low-Poly Roof Parapet Railings (simple continuous bars)
    bm_f3_rail = bmesh.new()
    for i in range(len(east_front_pts) - 1):
        add_wall_seg(bm_f3_rail, east_front_pts[i], east_front_pts[i+1], Z3, 0.95, thickness=0.22)
    add_wall_seg(bm_f3_rail, west_front_pts[0], west_front_pts[-1], Z3, 0.95, thickness=0.22)
    bmesh_to_object(bm_f3_rail, "F3_Railing_Balustrade", col_f3, mat_trim)

    bm_f3_walls = bmesh.new()
    for seg in cad_data["floors"]["03"]["wall_segments"]:
        add_wall_seg(bm_f3_walls, seg["p1"], seg["p2"], Z3, H3 * 0.85, thickness=0.20)
    add_box(bm_f3_walls, (1.5, -13.8, Z3 + H3 * 0.5), (8.2, 11.5, H3), rot_z=0.25)
    add_box(bm_f3_walls, (35.8, -0.5, Z3 + H3 * 0.5), (10.5, 12.0, H3), rot_z=0.48)
    bmesh_to_object(bm_f3_walls, "F3_Wall_Penthouses", col_f3, mat_terracotta)

    bm_f3_glass = bmesh.new()
    add_box(bm_f3_glass, (-7.95, -10.80, Z3 + 0.8), (6.0, 4.0, 1.6), rot_z=0.15)
    bmesh_to_object(bm_f3_glass, "F3_Glass_Skylight", col_f3, mat_glass)

    # Low-Poly Rooftop Steel Canopy (East Wing)
    bm_f3_canopy = bmesh.new()
    canopy_z_top = Z3 + 3.2
    for i in range(1, len(east_front_pts) - 1):
        f_pt = east_front_pts[i]
        r_pt = east_rear_pts[i]
        p_front = (f_pt[0] * 0.82 + r_pt[0] * 0.18, f_pt[1] * 0.82 + r_pt[1] * 0.18)
        p_rear  = (f_pt[0] * 0.18 + r_pt[0] * 0.82, f_pt[1] * 0.18 + r_pt[1] * 0.82)
        add_box(bm_f3_canopy, (p_front[0], p_front[1], Z3 + 1.6), (0.25, 0.25, 3.2))
        add_box(bm_f3_canopy, (p_rear[0], p_rear[1], Z3 + 1.6), (0.25, 0.25, 3.2))
        add_wall_seg(bm_f3_canopy, p_front, p_rear, canopy_z_top - 0.20, 0.22, thickness=0.22)
        if i < len(east_front_pts) - 2:
            nf_pt = east_front_pts[i+1]
            nr_pt = east_rear_pts[i+1]
            np_front = (nf_pt[0] * 0.82 + nr_pt[0] * 0.18, nf_pt[1] * 0.82 + nr_pt[1] * 0.18)
            np_rear  = (nf_pt[0] * 0.18 + nr_pt[0] * 0.82, nf_pt[1] * 0.18 + nr_pt[1] * 0.82)
            add_wall_seg(bm_f3_canopy, p_front, np_front, canopy_z_top - 0.15, 0.18, thickness=0.18)
            add_wall_seg(bm_f3_canopy, p_rear, np_rear, canopy_z_top - 0.15, 0.18, thickness=0.18)
    bmesh_to_object(bm_f3_canopy, "F3_Canopy_Steel", col_f3, mat_steel)

    # Low-Poly Rear-Left Steel Arch Frame (5 X-lines x 4 Y-rows)
    bm_f3_cage = bmesh.new()
    cage_z_top = Z3 + 8.0
    cage_x_cols = [-41.5, -34.5, -27.5, -20.5, -13.5]
    cage_y_rows = [-18.0, 0.0, 14.0, 29.0]

    for cx in cage_x_cols:
        for cy in cage_y_rows:
            col_z0 = Z0 if cy >= 10.0 else Z3
            col_h = cage_z_top - col_z0
            add_box(bm_f3_cage, (cx, cy, col_z0 + col_h * 0.5), (0.28, 0.28, col_h))
        add_wall_seg(bm_f3_cage, (cx, cage_y_rows[0]), (cx, cage_y_rows[-1]), cage_z_top - 0.2, 0.22, thickness=0.20)

    for cy in cage_y_rows:
        add_wall_seg(bm_f3_cage, (cage_x_cols[0], cy), (cage_x_cols[-1], cy), cage_z_top - 0.2, 0.22, thickness=0.20)
    bmesh_to_object(bm_f3_cage, "F3_SteelCage_Frame", col_f3, mat_steel)

    total_verts = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')
    total_faces = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH')

    os.makedirs(os.path.dirname(GLB_OUT), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    bpy.ops.export_scene.gltf(
        filepath=GLB_OUT,
        export_format='GLB',
        export_yup=True,
        export_apply=True,
        export_materials='EXPORT',
        export_cameras=False,
        export_lights=False,
    )
    return {
        "status": "built_lowpoly",
        "objects_count": len(bpy.data.objects),
        "total_vertices": total_verts,
        "total_faces": total_faces,
        "glb_size_bytes": os.path.getsize(GLB_OUT),
    }

if __name__ == "__main__":
    print(build_digital_twin())

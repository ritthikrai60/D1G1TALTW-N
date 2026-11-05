import os, sys, json, math, struct, zipfile
import numpy as np
import shapely
from shapely.geometry import Polygon
from PIL import Image

IGZ_PATH = r"c:\Coding Projects\Digital Twin\LUDUS_Building_No_Glass.igz"
OUT_GLB_PUBLIC = r"c:\Coding Projects\Digital Twin\public\models\building.glb"
OUT_GLB_DIST = r"c:\Coding Projects\Digital Twin\dist\models\building.glb"

def triangulate_3d_ring(verts_3d, holes_3d=None):
    """Triangulate a planar 3D polygon (with optional holes) into 3D triangles + normal."""
    pts = [tuple(p) for p in verts_3d]
    # Remove consecutive duplicates
    clean_pts = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, clean_pts[-1]) > 1e-5:
            clean_pts.append(p)
    if len(clean_pts) > 1 and math.dist(clean_pts[0], clean_pts[-1]) <= 1e-5:
        clean_pts.pop()
    if len(clean_pts) < 3:
        return [], (0.0, 1.0, 0.0)

    # Compute Newell normal in Z-up space
    nx, ny, nz = 0.0, 0.0, 0.0
    n = len(clean_pts)
    for i in range(n):
        x1, y1, z1 = clean_pts[i]
        x2, y2, z2 = clean_pts[(i + 1) % n]
        nx += (y1 - y2) * (z1 + z2)
        ny += (z1 - z2) * (x1 + x2)
        nz += (x1 - x2) * (y1 + y2)
    norm_len = math.sqrt(nx*nx + ny*ny + nz*nz)
    if norm_len < 1e-9:
        return [], (0.0, 1.0, 0.0)
    nx, ny, nz = nx / norm_len, ny / norm_len, nz / norm_len

    # Fast fan triangulation for simple convex quads/triangles without holes
    if not holes_3d and len(clean_pts) <= 4:
        tris = []
        for i in range(1, len(clean_pts) - 1):
            tris.append((clean_pts[0], clean_pts[i], clean_pts[i + 1]))
        return tris, (nx, ny, nz)

    # Project onto 2D plane perpendicular to dominant normal axis
    ax, ay, az = abs(nx), abs(ny), abs(nz)
    if az >= ax and az >= ay:
        # Project to XY
        u_vec = (1.0, 0.0, 0.0) if nz > 0 else (-1.0, 0.0, 0.0)
        v_vec = (0.0, 1.0, 0.0)
    elif ax >= ay and ax >= az:
        # Project to YZ
        u_vec = (0.0, 1.0, 0.0) if nx > 0 else (0.0, -1.0, 0.0)
        v_vec = (0.0, 0.0, 1.0)
    else:
        # Project to XZ
        u_vec = (-1.0, 0.0, 0.0) if ny > 0 else (1.0, 0.0, 0.0)
        v_vec = (0.0, 0.0, 1.0)

    p0 = clean_pts[0]
    def to_2d(p):
        dx, dy, dz = p[0] - p0[0], p[1] - p0[1], p[2] - p0[2]
        u = dx * u_vec[0] + dy * u_vec[1] + dz * u_vec[2]
        v = dx * v_vec[0] + dy * v_vec[1] + dz * v_vec[2]
        return (round(u, 5), round(v, 5))

    def to_3d(u, v):
        return (
            p0[0] + u * u_vec[0] + v * v_vec[0],
            p0[1] + u * u_vec[1] + v * v_vec[1],
            p0[2] + u * u_vec[2] + v * v_vec[2],
        )

    ext_2d = [to_2d(p) for p in clean_pts]
    holes_2d = []
    if holes_3d:
        for h in holes_3d:
            if len(h) >= 3:
                holes_2d.append([to_2d(p) for p in h])

    try:
        poly = Polygon(ext_2d, holes_2d)
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.is_empty:
            return [], (nx, ny, nz)
        tri_geoms = shapely.constrained_delaunay_triangles(poly)
        geoms = tri_geoms.geoms if hasattr(tri_geoms, "geoms") else [tri_geoms]
        tris = []
        for g in geoms:
            if isinstance(g, Polygon):
                coords = list(g.exterior.coords)[:-1]
                if len(coords) == 3:
                    # Ensure CCW in (u, v) so normal points along +(nx, ny, nz)
                    (u0, v0), (u1, v1), (u2, v2) = coords
                    cross = (u1 - u0) * (v2 - v0) - (v1 - v0) * (u2 - u0)
                    if cross < 0:
                        coords = [coords[0], coords[2], coords[1]]
                    tris.append((to_3d(*coords[0]), to_3d(*coords[1]), to_3d(*coords[2])))
        return tris, (nx, ny, nz)
    except Exception:
        # Fallback fan
        tris = []
        for i in range(1, len(clean_pts) - 1):
            tris.append((clean_pts[0], clean_pts[i], clean_pts[i + 1]))
        return tris, (nx, ny, nz)

def classify_group(g_name, g_layer, z_min):
    """Map an IngeTrazo group to (floor_idx, category)."""
    name_low = g_name.lower()
    # Determine floor_idx (0, 1, 2, 3)
    if g_layer == "00_Ground_Floor" or name_low.startswith("00_ground"):
        floor_idx = 0
    elif g_layer == "01_First_Floor" or name_low.startswith("01_first"):
        floor_idx = 1
    elif g_layer == "02_Second_Floor" or name_low.startswith("02_second"):
        floor_idx = 2
    elif g_layer == "03_Rooftop" or name_low.startswith("03_rooftop") or name_low.startswith("basketball"):
        floor_idx = 3
    elif g_name == "North_Warehouse_Gable_Roof":
        floor_idx = 2
    elif g_name.startswith("Rooftop_Pergola") or g_name == "Central_Curved_Glass_Skylight":
        floor_idx = 3
    else:
        # Stairs & other elements by base elevation z_min
        if z_min < 2.2:
            floor_idx = 0
        elif z_min < 6.5:
            floor_idx = 1
        elif z_min < 10.5:
            floor_idx = 2
        else:
            floor_idx = 3

    # Determine semantic category
    if g_layer == "Glass_And_Skylight" or "_glass_" in name_low or "skylight" in name_low:
        cat = "Glass"
    elif g_layer == "Roofs_And_Skylight" or "pergola" in name_low or "roof" in name_low:
        cat = "Roof"
    elif "arrow" in name_low:
        cat = "Arrow"
    elif g_layer == "Stairs_And_Directions" or "stair" in name_low:
        cat = "Stair"
    elif "basketball" in name_low:
        cat = "Basketball"
    elif "_slab_" in name_low or "apron" in name_low or "terrace" in name_low:
        cat = "Slab"
    elif "_col_" in name_low or "pillar" in name_low:
        cat = "Column"
    elif "parapet" in name_low:
        cat = "Parapet"
    else:
        cat = "Wall"

    return floor_idx, cat

print("Reading LUDUS_Building_No_Glass.igz...")
batches = {}  # key: (floor_idx, cat, rgba_tuple) -> {"pos": [], "norm": []}

with zipfile.ZipFile(IGZ_PATH, "r") as z:
    doc = json.loads(z.read("document.json"))
    groups = list(doc["scene"].get("groups", []))
    loose_faces = doc["scene"].get("faces", [])
    if loose_faces:
        for lf_idx, lf in enumerate(loose_faces):
            groups.append({
                "name": f"Loose_Scene_Face_{lf_idx}",
                "layer": lf.get("layer") or "Layer 0",
                "faces": [lf],
            })
    for g in groups:
        g_name = g.get("name", "")
        if g_name in ("Ingeniero", "Engineer"):
            continue
        g_layer = g.get("layer", "Layer 0")
        mat = g.get("material", {})
        mat_opacity = float(mat.get("opacity", 1.0)) if mat else 1.0
        mat_color = mat.get("color", None) if mat else None
        axes = g.get("axes", None)
        tf_mat = None
        if axes and len(axes) == 16:
            tf_mat = np.array(axes, dtype=np.float64).reshape((4, 4))

        def apply_tf(pts_list):
            if tf_mat is None:
                return pts_list
            arr = np.array(pts_list, dtype=np.float64)
            out = arr @ tf_mat[:3, :3] + tf_mat[3, :3]
            return out.tolist()

        faces_to_process = []
        z_vals = []

        if "geom" in g:
            gm = g["geom"]
            buf = z.read(gm["member"])
            arrs = {}
            for k, (dt, shape, off) in gm["arrays"].items():
                count = int(np.prod(shape))
                arrs[k] = np.frombuffer(buf, dtype=dt, count=count, offset=off).reshape(shape)
            pos = arrs["pos"]
            if tf_mat is not None:
                pos = (pos.astype(np.float64) @ tf_mat[:3, :3] + tf_mat[3, :3]).astype(np.float32)
            rings = arrs["rings"]
            ring_sizes = arrs["ring_sizes"]
            ring_counts = arrs["ring_counts"]
            face_attr = arrs["face_attr"]
            face_attrs = gm.get("face_attrs", [{"color": [0.85, 0.85, 0.85, 1.0]}])

            z_vals.extend(pos[:, 2].tolist())
            r_idx = 0
            v_cursor = 0
            for f_i, r_cnt in enumerate(ring_counts):
                f_color = face_attrs[face_attr[f_i]].get("color", [0.85, 0.85, 0.85, 1.0])
                ext_3d = None
                holes_3d = []
                for sub_r in range(r_cnt):
                    r_sz = ring_sizes[r_idx]
                    r_idx += 1
                    ring_v_indices = rings[v_cursor : v_cursor + r_sz]
                    v_cursor += r_sz
                    pts_3d = pos[ring_v_indices].tolist()
                    if sub_r == 0:
                        ext_3d = pts_3d
                    else:
                        holes_3d.append(pts_3d)
                if ext_3d:
                    faces_to_process.append((ext_3d, holes_3d, f_color))
        else:
            for f in g.get("faces", []):
                verts = f.get("vertices", [])
                if len(verts) >= 3:
                    verts = apply_tf(verts)
                    for v in verts:
                        z_vals.append(v[2])
                    raw_holes = f.get("holes") or []
                    holes_3d = [apply_tf(h) for h in raw_holes if len(h) >= 3] if raw_holes else None
                    f_color = f.get("color", [0.88, 0.88, 0.88, 1.0])
                    faces_to_process.append((verts, holes_3d, f_color))

        if not faces_to_process:
            continue

        z_min = min(z_vals) if z_vals else 0.0
        floor_idx, cat = classify_group(g_name, g_layer, z_min)

        for ext_3d, holes_3d, f_color in faces_to_process:
            if mat_color and len(mat_color) == 3:
                rgba = (round(mat_color[0], 3), round(mat_color[1], 3), round(mat_color[2], 3), round(mat_opacity, 3))
            else:
                alpha = f_color[3] if len(f_color) > 3 else 1.0
                if mat_opacity < 0.99:
                    alpha = mat_opacity
                rgba = (round(f_color[0], 3), round(f_color[1], 3), round(f_color[2], 3), round(alpha, 3))

            tris, (nx, ny, nz) = triangulate_3d_ring(ext_3d, holes_3d)
            if not tris:
                continue

            # Convert normal from Z-up (nx, ny, nz) to glTF Y-up (nx, nz, -ny)
            gnx, gny, gnz = nx, nz, -ny
            bkey = (floor_idx, cat, rgba)
            if bkey not in batches:
                batches[bkey] = {"pos": [], "norm": []}
            b_pos = batches[bkey]["pos"]
            b_norm = batches[bkey]["norm"]

            for p0, p1, p2 in tris:
                # Convert vertex (x, y, z) -> glTF Y-up (x, z, -y)
                for px, py, pz in (p0, p1, p2):
                    b_pos.append((px, pz, -py))
                    b_norm.append((gnx, gny, gnz))

print(f"Created {len(batches)} optimized mesh batches from 1,129 IGZ groups.")

# Build binary glTF 2.0 (.glb)
buffer_views = []
accessors = []
materials = []
meshes = []
nodes = []
bin_chunks = bytearray()

mat_cache = {}
def get_or_create_material(rgba, cat):
    if rgba in mat_cache:
        return mat_cache[rgba]
    r, g, b, a = rgba
    # Convert sRGB-like colors to linear for glTF PBR
    lr, lg, lb = r**2.2, g**2.2, b**2.2
    m = {
        "name": f"Mat_{cat}_{len(materials)}",
        "pbrMetallicRoughness": {
            "baseColorFactor": [round(lr, 4), round(lg, 4), round(lb, 4), round(a, 4)],
            "metallicFactor": 0.15 if cat in ("Glass", "Column", "Roof") else 0.05,
            "roughnessFactor": 0.25 if cat == "Glass" else 0.78,
        },
        "doubleSided": True,
    }
    if a < 0.98 or cat == "Glass":
        m["alphaMode"] = "BLEND"
    idx = len(materials)
    materials.append(m)
    mat_cache[rgba] = idx
    return idx

for idx, ((floor_idx, cat, rgba), data) in enumerate(sorted(batches.items(), key=lambda x: (x[0][0], x[0][1]))):
    pos_arr = np.array(data["pos"], dtype=np.float32)
    norm_arr = np.array(data["norm"], dtype=np.float32)
    v_count = len(pos_arr)
    if v_count == 0:
        continue

    pos_bytes = pos_arr.tobytes()
    norm_bytes = norm_arr.tobytes()

    # Position BufferView & Accessor
    pos_offset = len(bin_chunks)
    bin_chunks.extend(pos_bytes)
    while len(bin_chunks) % 4 != 0:
        bin_chunks.append(0)
    bv_pos_idx = len(buffer_views)
    buffer_views.append({
        "buffer": 0,
        "byteOffset": pos_offset,
        "byteLength": len(pos_bytes),
        "target": 34962,
    })
    acc_pos_idx = len(accessors)
    accessors.append({
        "bufferView": bv_pos_idx,
        "byteOffset": 0,
        "componentType": 5126,
        "count": v_count,
        "type": "VEC3",
        "min": pos_arr.min(axis=0).tolist(),
        "max": pos_arr.max(axis=0).tolist(),
    })

    # Normal BufferView & Accessor
    norm_offset = len(bin_chunks)
    bin_chunks.extend(norm_bytes)
    while len(bin_chunks) % 4 != 0:
        bin_chunks.append(0)
    bv_norm_idx = len(buffer_views)
    buffer_views.append({
        "buffer": 0,
        "byteOffset": norm_offset,
        "byteLength": len(norm_bytes),
        "target": 34962,
    })
    acc_norm_idx = len(accessors)
    accessors.append({
        "bufferView": bv_norm_idx,
        "byteOffset": 0,
        "componentType": 5126,
        "count": v_count,
        "type": "VEC3",
    })

    mat_idx = get_or_create_material(rgba, cat)
    mesh_name = f"F{floor_idx}_{cat}_{idx}"
    mesh_idx = len(meshes)
    meshes.append({
        "name": mesh_name,
        "primitives": [{
            "attributes": {"POSITION": acc_pos_idx, "NORMAL": acc_norm_idx},
            "material": mat_idx,
            "mode": 4,
        }],
    })
    nodes.append({
        "name": mesh_name,
        "mesh": mesh_idx,
    })

gltf_dict = {
    "asset": {"version": "2.0", "generator": "IngeTrazo-to-DigitalTwin-GLB"},
    "scene": 0,
    "scenes": [{"name": "LUDUS_Building", "nodes": list(range(len(nodes)))}],
    "nodes": nodes,
    "meshes": meshes,
    "materials": materials,
    "accessors": accessors,
    "bufferViews": buffer_views,
    "buffers": [{"byteLength": len(bin_chunks)}],
}

json_bytes = json.dumps(gltf_dict, separators=(",", ":")).encode("utf-8")
while len(json_bytes) % 4 != 0:
    json_bytes += b" "

total_len = 12 + 8 + len(json_bytes) + 8 + len(bin_chunks)
glb_bytes = bytearray()
glb_bytes.extend(struct.pack("<III", 0x46546C67, 2, total_len))
glb_bytes.extend(struct.pack("<II", len(json_bytes), 0x4E4F534A))
glb_bytes.extend(json_bytes)
glb_bytes.extend(struct.pack("<II", len(bin_chunks), 0x004E4942))
glb_bytes.extend(bin_chunks)

os.makedirs(os.path.dirname(OUT_GLB_PUBLIC), exist_ok=True)
with open(OUT_GLB_PUBLIC, "wb") as f:
    f.write(glb_bytes)
if os.path.exists(os.path.dirname(OUT_GLB_DIST)):
    with open(OUT_GLB_DIST, "wb") as f:
        f.write(glb_bytes)

print(f"Wrote {OUT_GLB_PUBLIC} ({len(glb_bytes)/1024:.1f} KB, {len(nodes)} nodes)")

# Also generate aligned transparent 2D CAD Plan PNGs in public/plans/floor_00..03.png
crops_dir = r"C:\Users\ritth\.gemini\antigravity\brain\a6d28dc8-b642-4a1d-9a41-fb00b0fa4a78\scratch\crops"
plans_map = [
    ("00_ground_full.png", "floor_00.png"),
    ("01_first_full.png",  "floor_01.png"),
    ("02_second_full.png", "floor_02.png"),
    ("03_rooftop_full.png","floor_03.png"),
]
for src_name, dst_name in plans_map:
    src_p = os.path.join(crops_dir, src_name)
    if os.path.exists(src_p):
        im = Image.open(src_p).convert("RGBA")
        arr = np.array(im)
        # Turn near-white background pixels (>242) transparent, make CAD lines crisp
        white_mask = (arr[:, :, 0] > 242) & (arr[:, :, 1] > 242) & (arr[:, :, 2] > 242)
        arr[white_mask, 3] = 0
        out_im = Image.fromarray(arr)
        for folder in [r"c:\Coding Projects\Digital Twin\public\plans", r"c:\Coding Projects\Digital Twin\dist\plans"]:
            if os.path.exists(folder):
                out_im.save(os.path.join(folder, dst_name))
        print("Updated aligned 2D CAD plan:", dst_name)


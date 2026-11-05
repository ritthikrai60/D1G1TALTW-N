import json
import math
import numpy as np
from PIL import Image, ImageDraw

with open('01_Master_All_Floors_Walls.igz', 'r', encoding='utf-8') as f:
    data = json.load(f)

groups = data['scene']['groups']
print(f"Loaded {len(groups)} groups for 3D multi-floor rendering.")

def project_iso(x, y, z, cx, cy, cz, scale, img_w, img_h, yaw_deg=-45.0, pitch_deg=35.0):
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    dx = x - cx
    dy = y - cy
    dz = z - cz
    rx = dx * math.cos(yaw) - dy * math.sin(yaw)
    ry = dx * math.sin(yaw) + dy * math.cos(yaw)
    rz = dz
    px = rx
    py = ry * math.sin(pitch) - rz * math.cos(pitch)
    depth = ry * math.cos(pitch) + rz * math.sin(pitch)
    screen_x = int(img_w / 2.0 + px * scale)
    screen_y = int(img_h / 2.0 + py * scale)
    return screen_x, screen_y, depth

def render_scene(groups_to_render, cx, cy, cz, scale, img_w, img_h, out_path, title, yaw_deg=-45.0, pitch_deg=35.0, render_slabs=True):
    img = Image.new('RGB', (img_w, img_h), (248, 250, 252))
    draw = ImageDraw.Draw(img)
    
    # 1. Slabs
    if render_slabs:
        for g in groups_to_render:
            if g.get('layer') == 'Slabs':
                for face in g['faces']:
                    verts = face['vertices']
                    pts = [project_iso(v[0], v[1], v[2], cx, cy, cz, scale, img_w, img_h, yaw_deg, pitch_deg)[:2] for v in verts]
                    draw.polygon(pts, fill=(232, 236, 242), outline=(170, 180, 195))
                    
    # 2. Solid elements (Columns, Walls, Stairs)
    solid_faces = []
    light_dir = np.array([0.4, -0.6, 0.75])
    light_dir = light_dir / np.linalg.norm(light_dir)
    
    for g in groups_to_render:
        g_layer = g.get('layer', '')
        if g_layer == 'Slabs': continue
        
        for face in g.get('faces', []):
            verts = face.get('vertices', [])
            if len(verts) < 3: continue
            v0, v1, v2 = np.array(verts[0]), np.array(verts[1]), np.array(verts[2])
            normal = np.cross(v1 - v0, v2 - v0)
            norm_len = np.linalg.norm(normal)
            if norm_len > 1e-6: normal = normal / norm_len
            else: normal = np.array([0, 0, 1])
            
            proj_pts = []
            depths = []
            for v in verts:
                sx, sy, d = project_iso(v[0], v[1], v[2], cx, cy, cz, scale, img_w, img_h, yaw_deg, pitch_deg)
                proj_pts.append((sx, sy))
                depths.append(d)
            avg_d = sum(depths) / len(depths)
            
            dot = max(0.25, float(np.dot(normal, light_dir)))
            base_col = face.get('color', [0.85, 0.85, 0.85, 1.0])
            r = int(min(255, base_col[0] * 255 * (0.55 + 0.45 * dot)))
            gc = int(min(255, base_col[1] * 255 * (0.55 + 0.45 * dot)))
            b = int(min(255, base_col[2] * 255 * (0.55 + 0.45 * dot)))
            
            if 'Walls' in g_layer:
                edge_col = (140, 135, 125)
                fill_col = (r, gc, b)
            elif 'Structure' in g_layer:
                edge_col = (70, 75, 85)
                fill_col = (int(r * 0.9), int(gc * 0.9), int(b * 0.9))
            elif g_layer == 'Stairs':
                edge_col = (180, 40, 30)
                fill_col = (int(min(255, r * 1.15)), int(gc * 0.85), int(b * 0.85))
            else:
                edge_col = (120, 120, 120)
                fill_col = (r, gc, b)
                
            solid_faces.append((avg_d, proj_pts, fill_col, edge_col))
            
    solid_faces.sort(key=lambda x: x[0], reverse=True)
    for d, pts, fill_col, edge_col in solid_faces:
        draw.polygon(pts, fill=fill_col, outline=edge_col)
        
    draw.text((30, 25), title, fill=(20, 25, 35))
    img.save(out_path)
    print(f"Saved {out_path}")

brain_dir = r"C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8"

# 1. Overall Multi-Floor View with All Walls
render_scene(groups, 20.0, 10.0, 5.5, 14.0, 1920, 1080, f"{brain_dir}/render_3d_all_floors_walls_master.png", "Digital Twin: Complete Multi-Floor Architecture (Slabs + Columns + All Floor Walls + Stairs)", -45.0, 32.0, render_slabs=True)

# 2. Floor 00 Walls & Columns Cutaway
f00_elements = [g for g in groups if 'F00' in g.get('layer', '') or g.get('name') == 'F00_Ground_Slab' or 'F00_Stair' in g.get('name', '')]
render_scene(f00_elements, 20.0, 10.0, 1.75, 16.0, 1600, 950, f"{brain_dir}/render_3d_floor00_walls_cutaway.png", "Floor 00 (Ground Floor): Complete Wall Architecture, Structural Columns & Slabs", -45.0, 32.0, render_slabs=True)

# 3. Floor 01 Walls & Columns Cutaway
f01_elements = [g for g in groups if 'F01' in g.get('layer', '') or g.get('name') == 'F01_First_Floor_Slab' or 'F01_Stair' in g.get('name', '') or 'Fan' in g.get('name', '') or 'Spiral' in g.get('name', '')]
render_scene(f01_elements, 20.0, 10.0, 5.5, 16.0, 1600, 950, f"{brain_dir}/render_3d_floor01_walls_cutaway.png", "Floor 01 (First Floor): Complete Wall Architecture, Structural Columns & Slabs", -45.0, 32.0, render_slabs=True)

# 4. Floor 02 Walls Cutaway
f02_elements = [g for g in groups if 'F02' in g.get('layer', '') or g.get('name') == 'F02_Second_Floor_Slab']
render_scene(f02_elements, 20.0, 10.0, 9.5, 16.0, 1600, 950, f"{brain_dir}/render_3d_floor02_walls_cutaway.png", "Floor 02 (Second Floor): Complete Wall Partitions & Mezzanine Architecture", -45.0, 32.0, render_slabs=True)


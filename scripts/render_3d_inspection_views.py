import json
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Load the compiled 01_First_Floor_Master.igz
with open('01_First_Floor_Master.igz', 'r', encoding='utf-8') as f:
    data = json.load(f)

groups = data['scene']['groups']
print(f"Loaded {len(groups)} groups for 3D rendering.")

def project_iso(x, y, z, cx, cy, cz, scale, img_w, img_h, yaw_deg=-35.0, pitch_deg=30.0):
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    
    # Translate relative to center
    dx = x - cx
    dy = y - cy
    dz = z - cz
    
    # Rotate yaw around Z
    rx = dx * math.cos(yaw) - dy * math.sin(yaw)
    ry = dx * math.sin(yaw) + dy * math.cos(yaw)
    rz = dz
    
    # Rotate pitch around X'
    px = rx
    py = ry * math.sin(pitch) - rz * math.cos(pitch)
    depth = ry * math.cos(pitch) + rz * math.sin(pitch)
    
    screen_x = int(img_w / 2.0 + px * scale)
    screen_y = int(img_h / 2.0 + py * scale)
    return screen_x, screen_y, depth

def render_view(groups_to_render, cx, cy, cz, scale, img_w, img_h, out_path, title="", yaw_deg=-35.0, pitch_deg=30.0):
    img = Image.new('RGB', (img_w, img_h), (245, 247, 250))
    draw = ImageDraw.Draw(img)
    
    # Collect all faces
    all_faces = []
    for g in groups_to_render:
        g_name = g.get('name', '')
        g_layer = g.get('layer', '')
        for face in g.get('faces', []):
            verts = face.get('vertices', [])
            if len(verts) < 3: continue
            # compute center and normal
            v0, v1, v2 = np.array(verts[0]), np.array(verts[1]), np.array(verts[2])
            normal = np.cross(v1 - v0, v2 - v0)
            norm_len = np.linalg.norm(normal)
            if norm_len > 1e-6:
                normal = normal / norm_len
            else:
                normal = np.array([0, 0, 1])
                
            center = np.mean(verts, axis=0)
            proj_pts = []
            depths = []
            for v in verts:
                sx, sy, d = project_iso(v[0], v[1], v[2], cx, cy, cz, scale, img_w, img_h, yaw_deg, pitch_deg)
                proj_pts.append((sx, sy))
                depths.append(d)
                
            avg_depth = sum(depths) / len(depths)
            
            # Simple directional lighting from top-front-left (0.4, -0.6, 0.7)
            light_dir = np.array([0.4, -0.6, 0.7])
            light_dir = light_dir / np.linalg.norm(light_dir)
            dot = max(0.2, float(np.dot(normal, light_dir)))
            
            base_col = face.get('color', [0.8, 0.8, 0.8, 1.0])
            r = int(min(255, base_col[0] * 255 * (0.5 + 0.5 * dot)))
            g_col = int(min(255, base_col[1] * 255 * (0.5 + 0.5 * dot)))
            b = int(min(255, base_col[2] * 255 * (0.5 + 0.5 * dot)))
            
            # Layer styling
            edge_col = (100, 105, 115)
            if g_layer == 'Stairs':
                edge_col = (180, 50, 40)
            elif 'Slab' in g_layer:
                edge_col = (120, 130, 140)
            elif 'Structure' in g_layer:
                edge_col = (70, 75, 85)
                
            all_faces.append((avg_depth, proj_pts, (r, g_col, b), edge_col))
            
    # Sort faces Painter's algorithm (deepest first)
    all_faces.sort(key=lambda x: x[0], reverse=True)
    
    for avg_depth, pts, fill_col, edge_col in all_faces:
        draw.polygon(pts, fill=fill_col, outline=edge_col)
        
    # Draw title
    draw.text((20, 20), title, fill=(30, 35, 45))
    img.save(out_path)
    print(f"Saved {out_path} ({img_w}x{img_h})")

brain_dir = r"C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8"

# 1. OVERALL 3D VIEW
render_view(groups, 20.0, 12.0, 3.5, 15.0, 1600, 1000, f"{brain_dir}/render_3d_overall_master.png", "Digital Twin: Floor 00 + Floor 01 Structural & All 11 Stairs Model", -40.0, 32.0)

# 2. STAIR 3 (บันได 3) NORTH CORE CLOSE-UP
st3_groups = [g for g in groups if 'Stair3' in g['name'] or 'Column' in g['name'] and math.hypot(g['faces'][0]['vertices'][0][0] - 7.6, g['faces'][0]['vertices'][0][1] - 4.5) < 7.0]
render_view(st3_groups, 7.6, 5.0, 3.5, 75.0, 1000, 800, f"{brain_dir}/render_3d_stair3_core.png", "STAIR 3 (บันได 3) - North Core Circulation Shaft at (7.6, 4.5)", -35.0, 30.0)

# 3. STAIR 5 / ST-1 SOUTH LOCKER CLOSE-UP
st5_groups = [g for g in groups if 'Stair5' in g['name'] or 'Column' in g['name'] and math.hypot(g['faces'][0]['vertices'][0][0] - 9.8, g['faces'][0]['vertices'][0][1] - (-10.0)) < 7.0]
render_view(st5_groups, 9.8, -10.0, 3.0, 65.0, 1000, 800, f"{brain_dir}/render_3d_stair5_south_locker.png", "STAIR 5 / ST-1 (บันได 5) - South Locker Stair at (9.8, -10.0)", -35.0, 28.0)

# 4. SOUTH PORTICO STEPS CLOSE-UP
port_groups = [g for g in groups if 'Portico' in g['name'] or 'Facade' in g['name'] or ('Column' in g['name'] and -23.0 <= g['faces'][0]['vertices'][0][1] <= -16.0)]
render_view(port_groups, 8.0, -19.5, 2.0, 55.0, 1000, 700, f"{brain_dir}/render_3d_south_portico.png", "ST-2 South Portico Entrance Steps (Span 5.59m West-to-East UP)", -45.0, 25.0)

# 5. FOYER FAN & SPIRAL STAIR CLOSE-UP
foyer_groups = [g for g in groups if 'Fan' in g['name'] or 'Spiral' in g['name'] or 'Retail' in g['name']]
render_view(foyer_groups, 14.5, -2.0, 4.0, 60.0, 1100, 800, f"{brain_dir}/render_3d_foyer_fan_and_spiral.png", "Foyer Fan Steps (บันได 4) & Lobby Spiral Stair (บันไดวน A6-01)", -35.0, 32.0)

# 6. EAST WING STAIRS CLOSE-UP
east_groups = [g for g in groups if 'East' in g['name'] or 'Terrace' in g['name'] or 'Kitchen' in g['name']]
render_view(east_groups, 58.0, 12.0, 3.5, 45.0, 1100, 800, f"{brain_dir}/render_3d_east_wing_stairs.png", "East Wing Stairs (บันได 2 North Wall, Kitchen Dock, Outdoor Terrace)", -35.0, 28.0)


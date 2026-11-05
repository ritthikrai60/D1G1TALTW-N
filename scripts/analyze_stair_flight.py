import pypdf
import json
import math

def analyze_stair_geometry(pdf_path, name):
    reader = pypdf.PdfReader(pdf_path)
    data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
    doc = json.loads(data.decode('utf-8'))['document']
    X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
    def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))
    
    layer = next((l for l in doc['layers'] if l['name'] == 'A-stair'), None)
    if not layer: return
    
    def get_subpaths(c):
        res = []
        if not isinstance(c, dict): return res
        kind = c.get('kind', {})
        if isinstance(kind, dict):
            if kind.get('type') == 'path' and 'path' in kind:
                res.extend(kind['path'].get('subpaths', []))
            if 'children' in kind:
                for ch in kind['children']: res.extend(get_subpaths(ch))
        if 'children' in c:
            for ch in c['children']: res.extend(get_subpaths(ch))
        return res

    lines = []
    for elem in layer['kind']['children']:
        for sp in get_subpaths(elem):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) >= 2:
                if any(7.0 <= p[0] <= 13.0 and -15.0 <= p[1] <= -6.0 for p in pts):
                    lines.append(pts)
    
    print(f"\n--- {name} Stair Geometry Analysis ({len(lines)} lines) ---")
    
    # Separate treads (mostly short parallel lines) vs bounding box / walk arrows
    treads = []
    for pts in lines:
        if len(pts) == 2:
            p1, p2 = pts[0], pts[1]
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            length = math.hypot(dx, dy)
            angle = math.degrees(math.atan2(dy, dx))
            # Normalize angle to [-90, 90]
            if angle > 90: angle -= 180
            elif angle < -90: angle += 180
            if 0.8 <= length <= 2.2: # Typical stair tread width ~1.0m to 1.8m
                treads.append((p1, p2, length, angle))
    
    print(f"Identified {len(treads)} stair tread lines:")
    angles = [t[3] for t in treads]
    avg_angle = sum(angles) / len(angles) if angles else 0
    print(f"Average tread angle: {avg_angle:.2f} degrees")
    
    # Sort treads along flight direction (perpendicular to tread angle)
    flight_rad = math.radians(avg_angle + 90)
    fx, fy = math.cos(flight_rad), math.sin(flight_rad)
    
    sorted_treads = sorted(treads, key=lambda t: ((t[0][0]+t[1][0])/2)*fx + ((t[0][1]+t[1][1])/2)*fy)
    print("First 3 treads center:", [((t[0][0]+t[1][0])/2, (t[0][1]+t[1][1])/2) for t in sorted_treads[:3]])
    print("Last 3 treads center:", [((t[0][0]+t[1][0])/2, (t[0][1]+t[1][1])/2) for t in sorted_treads[-3:]])

analyze_stair_geometry('00-Ground_Floor-Clean.pdf', 'F00 Core Stair')
analyze_stair_geometry('01-First_Floor-Clean.pdf', 'F01 Core Stair')


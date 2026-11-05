import pypdf
import json
import numpy as np
from shapely.geometry import Polygon, LineString

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

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

for flabel, fname, wall_lnames in [
    ('Floor 00', '00-Ground_Floor-Clean.pdf', ['A-wall', 'WALL']),
    ('Floor 01', '01-First_Floor-Clean.pdf', ['WALL', 'A-wall']),
    ('Floor 02', '02-Second_Floor-Clean.pdf', ['WALL', 'A-wall']),
]:
    reader = pypdf.PdfReader(fname)
    data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
    doc = json.loads(data.decode('utf-8'))['document']
    layers = doc.get('layers', [])
    
    print(f"\n=================== {flabel} ({fname}) ===================")
    closed_polys = []
    real_lines = []
    hatch_count = 0
    
    for lname in wall_lnames:
        l = next((x for x in layers if x['name'] == lname), None)
        if not l: continue
        children = l.get('kind', {}).get('children', [])
        for c in children:
            for sp in get_subpaths(c):
                pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
                is_closed = sp.get('closed', False)
                if len(pts) >= 4 and (is_closed or pts[0] == pts[-1]):
                    try:
                        p = Polygon(pts)
                        if p.is_valid and p.area > 0.01:
                            closed_polys.append((lname, p))
                    except: pass
                elif len(pts) == 2:
                    length = np.hypot(pts[1][0]-pts[0][0], pts[1][1]-pts[0][1])
                    if length < 0.25:
                        hatch_count += 1
                    else:
                        real_lines.append((lname, pts, length))
                elif len(pts) > 2:
                    real_lines.append((lname, pts, 0.0))
                    
    print(f"Hatch lines detected & filtered: {hatch_count}")
    print(f"Closed wall polygons: {len(closed_polys)}")
    print(f"Real wall lines (>0.25m): {len(real_lines)}")
    
    # Analyze closed wall polygons
    # Check total wall area
    total_area = sum(p.area for _, p in closed_polys)
    print(f"Total closed wall area: {total_area:.2f} m^2")
    
    # Sample real wall lines
    print("Sample real wall lines:")
    for lname, pts, length in real_lines[:8]:
        if len(pts) == 2:
            print(f"  [{lname}] len={length:.2f}m | {pts[0]} -> {pts[1]}")
        else:
            print(f"  [{lname}] polyline {len(pts)} pts | {pts[0]} -> ... -> {pts[-1]}")


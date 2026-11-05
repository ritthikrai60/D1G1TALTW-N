import pypdf
import json
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPolygon, LineString
import shapely.ops

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

def extract_floor_walls(fname, wall_layer_names):
    reader = pypdf.PdfReader(fname)
    data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
    doc = json.loads(data.decode('utf-8'))['document']
    layers = doc.get('layers', [])
    
    wall_polys = []
    open_lines = []
    
    for lname in wall_layer_names:
        l = next((x for x in layers if x['name'] == lname), None)
        if not l: continue
        for c in l.get('kind', {}).get('children', []):
            for sp in get_subpaths(c):
                pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
                is_closed = sp.get('closed', False)
                if len(pts) >= 4 and (is_closed or pts[0] == pts[-1]):
                    try:
                        p = Polygon(pts)
                        if p.is_valid and p.area > 0.01:
                            wall_polys.append(p)
                    except: pass
                elif len(pts) >= 2:
                    # check length
                    length = np.hypot(pts[-1][0]-pts[0][0], pts[-1][1]-pts[0][1])
                    if length >= 0.50:
                        open_lines.append(pts)
                        
    # Buffer long open wall lines into 0.15m thick walls
    for pts in open_lines:
        try:
            ls = LineString(pts)
            if ls.length >= 0.80:
                p = ls.buffer(0.08, cap_style=2) # 0.16m wall
                if p.is_valid and p.area > 0.05:
                    wall_polys.append(p)
        except: pass
        
    # Unary union to merge overlapping wall segments and clean geometry
    merged = shapely.ops.unary_union(wall_polys)
    
    # Filter out tiny specks (< 0.04 m2)
    cleaned = []
    if merged.geom_type == 'MultiPolygon':
        for p in merged.geoms:
            if p.area >= 0.04:
                cleaned.append(p)
    elif merged.geom_type == 'Polygon':
        if merged.area >= 0.04:
            cleaned.append(merged)
            
    return cleaned

f00_walls = extract_floor_walls('00-Ground_Floor-Clean.pdf', ['A-wall', 'WALL', 'P-1 (0.50)'])
f01_walls = extract_floor_walls('01-First_Floor-Clean.pdf', ['WALL', 'A-wall', 'ПЕРЕГОРОดКИ ВНУТРЕННИЕ.Н_Ноม._pera__5'])
f02_walls = extract_floor_walls('02-Second_Floor-Clean.pdf', ['WALL', 'A-wall'])

print(f"Floor 00 Cleaned Wall Polygons: {len(f00_walls)}, Total Area: {sum(p.area for p in f00_walls):.2f} m2")
print(f"Floor 01 Cleaned Wall Polygons: {len(f01_walls)}, Total Area: {sum(p.area for p in f01_walls):.2f} m2")
print(f"Floor 02 Cleaned Wall Polygons: {len(f02_walls)}, Total Area: {sum(p.area for p in f02_walls):.2f} m2")


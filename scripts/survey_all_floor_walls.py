import pypdf
import json
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
    ('Floor 01', '01-First_Floor-Clean.pdf', ['WALL', 'A-wall', 'ПЕРЕГОРОДКИ ВНУТРЕННИЕ.Н_Ноม._pera__5']),
    ('Floor 02', '02-Second_Floor-Clean.pdf', ['WALL', 'A-wall']),
]:
    reader = pypdf.PdfReader(fname)
    data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
    doc = json.loads(data.decode('utf-8'))['document']
    layers = doc.get('layers', [])
    
    print(f"\n=================== {flabel} ({fname}) ===================")
    closed_polys = []
    open_lines = []
    
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
                        if p.is_valid and p.area > 0.005:
                            closed_polys.append((lname, p))
                    except: pass
                elif len(pts) >= 2:
                    open_lines.append((lname, pts))
                    
    print(f"Closed wall polygons: {len(closed_polys)}")
    print(f"Open lines/polylines: {len(open_lines)}")
    
    # Inspect closed polys
    areas = [p.area for _, p in closed_polys]
    if areas:
        print(f"  Closed poly areas: min={min(areas):.3f}, median={sorted(areas)[len(areas)//2]:.3f}, max={max(areas):.3f}")
        # sample a few
        for lname, p in closed_polys[:5]:
            minx, miny, maxx, maxy = p.bounds
            print(f"    [{lname}] bounds: ({minx:.2f},{miny:.2f}) to ({maxx:.2f},{maxy:.2f}) | size={maxx-minx:.2f}x{maxy-miny:.2f}m area={p.area:.3f}m2")


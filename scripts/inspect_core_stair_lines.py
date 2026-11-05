import pypdf
import json

def get_layer_lines(pdf_path, lname, bbox):
    reader = pypdf.PdfReader(pdf_path)
    data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
    doc = json.loads(data.decode('utf-8'))['document']
    X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
    def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))
    
    layer = next((l for l in doc['layers'] if l['name'] == lname), None)
    if not layer: return []
    
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
    minx, miny, maxx, maxy = bbox
    for elem in layer['kind']['children']:
        for sp in get_subpaths(elem):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) >= 2:
                # check if any point in bbox
                if any(minx <= p[0] <= maxx and miny <= p[1] <= maxy for p in pts):
                    lines.append(pts)
    return lines

print('=== F00 A-stair lines in Core Stair (X: 7 to 13, Y: -15 to -6) ===')
f00_lines = get_layer_lines('00-Ground_Floor-Clean.pdf', 'A-stair', (7.0, -15.0, 13.0, -6.0))
print(f'F00 has {len(f00_lines)} stair lines')

print('=== F01 A-stair lines in Core Stair (X: 7 to 13, Y: -15 to -6) ===')
f01_lines = get_layer_lines('01-First_Floor-Clean.pdf', 'A-stair', (7.0, -15.0, 13.0, -6.0))
print(f'F01 has {len(f01_lines)} stair lines')


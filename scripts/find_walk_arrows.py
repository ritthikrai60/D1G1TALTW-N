import pypdf
import json
import math

def find_walk_arrows(pdf_path, name):
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
    circles = []
    for elem in layer['kind']['children']:
        for sp in get_subpaths(elem):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) >= 2:
                if any(7.0 <= p[0] <= 13.0 and -15.0 <= p[1] <= -6.0 for p in pts):
                    lines.append(pts)
            # check for small circle
            if len(pts) >= 4:
                # check circle perimeter/bounds
                xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                if max(xs)-min(xs) < 0.3 and max(ys)-min(ys) < 0.3:
                    circles.append((sum(xs)/len(xs), sum(ys)/len(ys)))
    
    print(f"\n--- {name} Walk Arrow & Symbols ---")
    print(f"Small start circles: {circles}")
    # Arrow lines typically have acute angles or short branch lines
    short_lines = [pts for pts in lines if len(pts)==2 and math.hypot(pts[1][0]-pts[0][0], pts[1][1]-pts[0][1]) < 0.5]
    print(f"Short detail segments (arrowhead candidates): {len(short_lines)}")
    for sl in short_lines[:10]:
        print("  ", sl)

find_walk_arrows('00-Ground_Floor-Clean.pdf', 'F00 Core Stair')
find_walk_arrows('01-First_Floor-Clean.pdf', 'F01 Core Stair')


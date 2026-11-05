import pypdf
import json
import math
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

reader = pypdf.PdfReader('01-First_Floor-Clean.pdf')
data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
doc = json.loads(data.decode('utf-8'))['document']

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

col_polys = []
for lname in ['A-col', '01-AE-Floor Post', 'P-1']:
    l = next((x for x in doc['layers'] if x['name'] == lname), None)
    if not l: continue
    for c in l['kind']['children']:
        for sp in get_subpaths(c):
            pts = [to_m(a['p']) for a in sp.get('anchors', []) if 'p' in a]
            if len(pts) >= 4:
                try:
                    p = Polygon(pts)
                    if p.is_valid and 0.04 <= p.area <= 3.0:
                        xs = [pt[0] for pt in pts]
                        ys = [pt[1] for pt in pts]
                        dx = max(xs) - min(xs)
                        dy = max(ys) - min(ys)
                        if 0.20 <= dx <= 2.2 and 0.20 <= dy <= 2.2:
                            col_polys.append(p)
                except: pass

unique_cols = []
seen = set()
for cp in col_polys:
    cx, cy = round(cp.centroid.x, 2), round(cp.centroid.y, 2)
    if (cx, cy) not in seen:
        seen.add((cx, cy))
        unique_cols.append(cp)

print(f"Total unique columns found on F01: {len(unique_cols)}")

# Load F00 columns from checkpoint
import re
with open('scripts/checkpoint_basement_v3_perfect_slab.py', 'r', encoding='utf-8') as f:
    f00_text = f.read()

f00_col_matches = re.findall(r'extrude\(\[([^\]]+)\].*?name=\'(COL_[^\']+)\'', f00_text)
f00_cols = []
for pts_str, cname in f00_col_matches:
    pts = eval(f"[{pts_str}]")
    poly = Polygon(pts)
    f00_cols.append((cname, poly))

print(f"Total F00 columns loaded: {len(f00_cols)}")

# Compare stacking: F01 columns vs F00 columns
matching = 0
for cp in unique_cols:
    cx, cy = cp.centroid.x, cp.centroid.y
    # find closest F00 col
    dist, closest = min((math.hypot(cx - fp.centroid.x, cy - fp.centroid.y), fname) for fname, fp in f00_cols)
    if dist < 0.3:
        matching += 1

print(f"F01 columns that stack directly on F00 columns: {matching} / {len(unique_cols)} ({matching/len(unique_cols)*100:.1f}%)")

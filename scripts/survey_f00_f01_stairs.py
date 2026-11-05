import pypdf
import json
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from shapely.ops import unary_union

def get_doc(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
    return json.loads(data.decode('utf-8'))['document']

doc0 = get_doc('00-Ground_Floor-Clean.pdf')
doc1 = get_doc('01-First_Floor-Clean.pdf')

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

def extract_subpaths(c):
    if 'data' in c and 'subpaths' in c['data']:
        return c['data']['subpaths']
    if 'children' in c:
        res = []
        for ch in c['children']: res.extend(extract_subpaths(ch))
        return res
    if 'kind' in c and 'children' in c['kind']:
        res = []
        for ch in c['kind']['children']: res.extend(extract_subpaths(ch))
        return res
    return []

print('=== F00 Layers with STAIR ===')
for l in doc0['layers']:
    if any(k in l['name'].lower() for k in ['stair', 'step', 'sn-rl']):
        print(f"F00: {l['name']} - {len(l['kind']['children'])} elements")

print('=== F01 Layers with STAIR ===')
for l in doc1['layers']:
    if any(k in l['name'].lower() for k in ['stair', 'step', 'sn-rl']):
        print(f"F01: {l['name']} - {len(l['kind']['children'])} elements")


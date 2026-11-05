import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import shapely
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, box
import shapely.ops

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Wall layers
wall_layer_names = ['A-wall', 'WALL', 'P-1 (0.50)', 'P-4 (0.10)', 'P-2 (0.15)', 'P-3 (0.25)', 'P-4', 'P-2']

print("=== WALL SURVEY IN 00-Ground_Floor-Clean.pdf ===")
wall_stats = {}

for lname in wall_layer_names:
    l = layers.get(lname)
    if not l: continue
    children = l['kind'].get('children', [])
    polys = []
    lines = []
    for c in children:
        sps = extract_subpaths(c)
        for sp in sps:
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4 and sp['closed']:
                polys.append(pts)
            elif len(pts) >= 2:
                lines.append(pts)
    wall_stats[lname] = {'closed_polys': len(polys), 'lines': len(lines)}
    print(f"Layer '{lname:12s}': {len(polys):3d} closed polygons, {len(lines):3d} open polylines/segments")



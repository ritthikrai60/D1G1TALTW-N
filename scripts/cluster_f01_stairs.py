import pypdf
import json
from shapely.geometry import Point, LineString, Polygon, box
from shapely.ops import unary_union
from PIL import Image

reader = pypdf.PdfReader('01-First_Floor-Clean.pdf')
data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
doc = json.loads(data.decode('utf-8'))['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))
def m_to_px(xm, ym):
    pt_x = X0 + xm * SCALE
    pt_y = Y0 - ym * SCALE
    return int(pt_x * 3.0), int(pt_y * 3.0)

def get_subpaths(c):
    res = []
    if not isinstance(c, dict):
        return res
    kind = c.get('kind', {})
    if isinstance(kind, dict):
        if kind.get('type') == 'path' and 'path' in kind:
            res.extend(kind['path'].get('subpaths', []))
        if 'children' in kind:
            for ch in kind['children']:
                res.extend(get_subpaths(ch))
    if 'children' in c:
        for ch in c['children']:
            res.extend(get_subpaths(ch))
    return res

# Collect all geometries from A-stair and SN-RL
geoms = []
for lname in ['A-stair', 'SN-RL']:
    layer = next((l for l in doc['layers'] if l['name'] == lname), None)
    if not layer: continue
    for elem in layer['kind']['children']:
        for sp in get_subpaths(elem):
            anchors = sp.get('anchors', [])
            pts = []
            for a in anchors:
                if isinstance(a, dict) and 'p' in a:
                    pts.append(to_m(a['p']))
                elif isinstance(a, (list, tuple)) and len(a) >= 2:
                    pts.append(to_m(a))
            if len(pts) >= 2:
                try:
                    line = LineString(pts)
                    if line.is_valid and line.length > 0.01:
                        geoms.append((lname, line))
                except Exception as e:
                    pass

print(f"Total extracted stair line segments: {len(geoms)}")

# Cluster geometries by proximity (buffer 1.2m)
buffered = [g[1].buffer(1.2) for g in geoms]
merged_clusters = unary_union(buffered)
if merged_clusters.geom_type == 'Polygon':
    clusters = [merged_clusters]
else:
    clusters = list(merged_clusters.geoms)

# Filter out tiny noise clusters (area < 0.5 m^2)
stair_clusters = [c for c in clusters if c.area >= 1.0]
stair_clusters.sort(key=lambda c: c.centroid.x)

print(f"Identified {len(stair_clusters)} distinct stair clusters on F01:")

art_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
im_3x = Image.open('f01_clean_3x.png')

cluster_info = []
for i, c in enumerate(stair_clusters):
    minx, miny, maxx, maxy = c.bounds
    cx, cy = c.centroid.x, c.centroid.y
    in_count = sum(1 for _, g in geoms if c.intersects(g))
    info = {
        'id': i + 1,
        'center': (round(cx, 2), round(cy, 2)),
        'bounds': (round(minx, 2), round(miny, 2), round(maxx, 2), round(maxy, 2)),
        'width': round(maxx - minx, 2),
        'height': round(maxy - miny, 2),
        'elements': in_count
    }
    cluster_info.append(info)
    print(f"Cluster {i+1}: Center=({cx:.2f}, {cy:.2f}), Size={maxx-minx:.2f}x{maxy-miny:.2f}m, Segments={in_count}")
    
    # Crop high-res image of this stair
    pad = 3.0 # 3m padding
    px1, py1 = m_to_px(minx - pad, maxy + pad)
    px2, py2 = m_to_px(maxx + pad, miny - pad)
    left, right = min(px1, px2), max(px1, px2)
    top, bottom = min(py1, py2), max(py1, py2)
    crop = im_3x.crop((left, top, right, bottom))
    crop_name = f"f01_clean_stair_cluster_{i+1}.png"
    crop.save(f"{art_dir}\\{crop_name}")

with open('scripts/f01_stair_clusters.json', 'w') as f:
    json.dump(cluster_info, f, indent=2)

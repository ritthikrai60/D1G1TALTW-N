import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Check item 6 in A-stair (southern curb) and item 24 (western curb)
stair = layers['A-stair']
south_curb = stair['kind']['children'][6]
sps = extract_subpaths(south_curb)
pts_south = [to_m(p) for p in sps[0]['anchors']]
print("South curb points:", len(pts_south))
print("From:", pts_south[0], "to:", pts_south[-1])

west_island = stair['kind']['children'][24]
sps_w = extract_subpaths(west_island)
pts_west = [to_m(p) for p in sps_w[0]['anchors']]
print("West island points:", len(pts_west))
print("From:", pts_west[0], "to:", pts_west[-1])


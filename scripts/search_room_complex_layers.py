import zlib, re
from PIL import Image, ImageDraw
import os
import math

with open(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf', 'rb') as f:
    data = f.read()

streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s0 = zlib.decompress(streams[0]).decode('latin1', errors='ignore')

# In VectorCraft stream 1:
# Let's see what layer contains these exact coordinates:
# X_pt in [1000, 1350], Y_pt in [400, 1000]
s1 = zlib.decompress(streams[1]).decode('utf-8')
import json
vc_doc = json.loads(s1)['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

print("=== SEARCHING VECTORCRAFT LAYERS FOR WALLS IN ROOM COMPLEX ===")
for l in vc_doc['layers']:
    lname = l['name']
    matched = []
    for i, c in enumerate(l['kind'].get('children', [])):
        # Recursively find anchors
        def get_all_pts(node):
            pts = []
            if isinstance(node, dict):
                if 'subpaths' in node:
                    for sp in node['subpaths']:
                        pts.extend([p['anchor'] for p in sp.get('points', []) if 'anchor' in p])
                for k, v in node.items():
                    if k != 'subpaths': pts.extend(get_all_pts(v))
            elif isinstance(node, list):
                for x in node: pts.extend(get_all_pts(x))
            return pts
        
        pts = [to_m(p) for p in get_all_pts(c)]
        if pts:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            # Check if inside the room complex: X in [0.0, 11.0], Y in [20.0, 38.0]
            if min(xs) >= -1.0 and max(xs) <= 12.0 and min(ys) >= 20.0 and max(ys) <= 38.0:
                matched.append((i, pts))
    if matched:
        print(f"Layer '{lname}': {len(matched)} elements inside the room complex!")



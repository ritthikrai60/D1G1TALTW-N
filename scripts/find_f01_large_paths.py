import zlib, re, json
import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths
from shapely.geometry import LineString

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

print("=== Large Paths (dx > 15 or dy > 10) Across All Layers ===")
for l in doc['layers']:
    lname = l['name']
    if lname in ['H-1', 'H-3', 'Potplant', 'AR_HATCH', 'WC-DET2', 'SANI-DETL', 'SANITARY']: continue
    for idx, c in enumerate(l['kind']['children']):
        for sp_idx, sp in enumerate(extract_subpaths(c)):
            pts = [to_m(p) for p in sp['anchors']]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            dx = max(xs) - min(xs)
            dy = max(ys) - min(ys)
            if dx > 15 or dy > 10:
                print(f"Layer '{lname:15s}' child {idx:3d} (sp {sp_idx}): len={len(pts):2d}, dx={dx:.2f}, dy={dy:.2f}, X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}]")


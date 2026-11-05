import sys, zlib, re, json
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths
from shapely.geometry import Polygon, LineString

# Let's inspect the red line on F01
with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

print("Searching for building boundary in F01:")
for l in doc['layers']:
    for i, c in enumerate(l['kind']['children']):
        items = c.get('appearance', {}).get('items', [])
        for item in items:
            col = item.get('paint', {}).get('color', {})
            r, g, b = col.get('r', 0), col.get('g', 0), col.get('b', 0)
            if r > 0.8 and g < 0.2 and b < 0.2: # Red!
                for sp in extract_subpaths(c):
                    pts = [to_m(p) for p in sp['anchors']]
                    if len(pts) >= 5:
                        xs = [p[0] for p in pts]
                        ys = [p[1] for p in pts]
                        dx = max(xs) - min(xs)
                        dy = max(ys) - min(ys)
                        if dx > 20.0 or dy > 20.0:
                            print(f"Red boundary in {l['name']} child {i}: pts={len(pts)}, dx={dx:.1f}, dy={dy:.1f}, X=[{min(xs):.1f}, {max(xs):.1f}], Y=[{min(ys):.1f}, {max(ys):.1f}]")


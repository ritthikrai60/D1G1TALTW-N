import zlib, re, json
import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths
from shapely.geometry import Polygon

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

l_p2_15 = next((x for x in doc['layers'] if x['name'] == 'P-2 (0.15)'), None)
c75_pts = [to_m(p) for p in extract_subpaths(l_p2_15['kind']['children'][75])[0]['anchors']]
p75 = Polygon(c75_pts)
print(f"Child 75: is_valid={p75.is_valid}, area={p75.area:.2f} m2, bounds={p75.bounds}")
for i, pt in enumerate(c75_pts[:15]):
    print(f"  pt {i}: {pt}")


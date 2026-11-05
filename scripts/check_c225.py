import zlib, re, json
import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

l_p2 = next((x for x in doc['layers'] if x['name'] == 'P-2'), None)
c225_pts = [to_m(p) for p in extract_subpaths(l_p2['kind']['children'][225])[0]['anchors']]
print("=== P-2 Child 225 points ===")
for p in c225_pts:
    print(f"  {p}")


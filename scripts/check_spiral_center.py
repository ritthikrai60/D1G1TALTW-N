import zlib, re, json, sys, math
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths

f = open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb')
data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
doc = json.loads(zlib.decompress(streams[1]).decode('utf-8'))['document']
xc, yc = 22.586, -4.264

for l in doc['layers']:
    for idx, c in enumerate(l['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [(round((p[0]-1000)/28.3465, 3), round(-(p[1]-1500)/28.3465, 3)) for p in sp['anchors']]
            dists = [math.hypot(p[0]-xc, p[1]-yc) for p in pts]
            if dists and min(dists) < 0.6:
                print(f"{l['name']} child {idx}: len={len(pts)}, closed={sp['closed']}, min_d={min(dists):.3f}")


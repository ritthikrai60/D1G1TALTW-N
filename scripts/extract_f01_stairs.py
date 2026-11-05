import zlib, re, json
import numpy as np

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths

l_stair = next((x for x in doc['layers'] if x['name'] == 'A-stair'), None)

# ST-1 risers: children 9 to 61
st1_lines = []
for idx in range(9, 62):
    c = l_stair['kind']['children'][idx]
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        if len(pts) == 2:
            st1_lines.append(pts)

print(f"ST-1 lines: {len(st1_lines)}")

# ST-2 risers: children 62 to 79
st2_lines = []
for idx in range(62, 79):
    c = l_stair['kind']['children'][idx]
    for sp in extract_subpaths(c):
        pts = [to_m(p) for p in sp['anchors']]
        if len(pts) == 2:
            st2_lines.append(pts)

print(f"ST-2 lines: {len(st2_lines)}")
for i, l in enumerate(st2_lines[:5]):
    print(f"  st2 {i}: {l[0]} -> {l[1]}")


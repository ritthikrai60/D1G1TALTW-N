with open(r'c:\Coding Projects\Digital Twin\scripts\checkpoint_basement_v3_perfect_slab.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'p_slab = Polygon\(\[(.*?)\]\)', text, re.DOTALL)
if m:
    pts_str = m.group(1)
    pts = [eval(p.strip()) for p in pts_str.strip().split('\n') if p.strip()]
    print(f"Floor 00 slab: {len(pts)} points")
    for i, pt in enumerate(pts):
        print(f"  {i:2d}: {pt}")


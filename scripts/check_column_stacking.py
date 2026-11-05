import json
import numpy as np
import re

with open('scripts/f01_columns.json', 'r') as f:
    f01_cols = json.load(f)

with open('scripts/basement_pure_columns_clean_slab.py', 'r') as f:
    code0 = f.read()

f00_col_blocks = re.findall(r'extrude\(\[(.*?)\], 0\.0, 3\.5', code0)
f00_cols = []
for block in f00_col_blocks:
    coords = re.findall(r'\(\s*([-0-9.]+)\s*,\s*([-0-9.]+)\s*\)', block)
    if coords:
        xs = [float(c[0]) for c in coords]
        ys = [float(c[1]) for c in coords]
        f00_cols.append((np.mean(xs), np.mean(ys)))

print(f"Floor 00 columns: {len(f00_cols)}")
print(f"Floor 01 columns: {len(f01_cols)}")

matches = 0
unmatched_f01 = []
for c1 in f01_cols:
    cx1, cy1 = c1['center']
    dists = [np.hypot(cx1 - c0[0], cy1 - c0[1]) for c0 in f00_cols]
    min_d = min(dists) if dists else 999.0
    if min_d < 0.15:
        matches += 1
    else:
        unmatched_f01.append((c1['id'], (cx1, cy1), min_d))

print(f"\nStacked Column Alignment:")
print(f"  Exact matching columns (sitting directly above Floor 00 columns): {matches} / {len(f01_cols)} ({matches/len(f01_cols)*100:.1f}%)")
print(f"  Floor 01 specific columns (entrance portico / colonnade): {len(unmatched_f01)}")
for u in unmatched_f01:
    print(f"     {u[0]} at {u[1]}, nearest F00 col dist = {u[2]:.2f}m")

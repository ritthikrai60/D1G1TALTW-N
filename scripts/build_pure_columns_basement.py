import re
from shapely.geometry import Polygon, box

with open('scripts/checkpoint_basement_v1_base.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract the 77 column code blocks from checkpoint v1
lines = text.splitlines()
col_lines = []
in_cols = False
for l in lines:
    if '# 2. ACCURATE BASEMENT STRUCTURAL COLUMNS' in l or 'Structural_Column_00' in l:
        in_cols = True
    if '# === 3. ST-1' in l:
        in_cols = False
    if in_cols:
        col_lines.append(l)

print(f"Extracted {len(col_lines)} lines of pure standalone columns.")

# Check the coordinates of all 77 columns:
pattern = re.compile(r"extrude\((\[.*?\]),", re.DOTALL)
col_polys = []
for l in col_lines:
    m = pattern.search(l)
    if m:
        pts = eval(m.group(1))
        col_polys.append(Polygon(pts))

print(f"Total unique column polygons: {len(col_polys)}")
import shapely.ops
u = shapely.ops.unary_union(col_polys)
print(f"Bounding box of all columns: {u.bounds}")


import sys
sys.path.insert(0, '.')
from scripts.verify_all_77_cols import unique_cols

xs = [c['center'][0] for c in unique_cols]
ys = [c['center'][1] for c in unique_cols]

min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)

print(f"Col BBox: X=[{min_x}, {max_x}], Y=[{min_y}, {max_y}]")

# Let's inspect the outer perimeter of the CAD lines in 'เส้นบาง', 'A-wall', 'P-1', etc.
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Check perimeter lines in drawing
print("Checking border or site lines...")
for lname in ['เส้นบาง', 'GRID', 'A-wall']:
    l = layers.get(lname)
    if not l: continue
    sps = []
    for c in l.get('kind', {}).get('children', []):
        sps.extend(extract_subpaths(c))
    print(f"Layer {lname}: {len(sps)} subpaths")


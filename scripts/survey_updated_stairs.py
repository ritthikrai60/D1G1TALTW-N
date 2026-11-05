import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

print("=== CHECKING ALL STAIR ITEMS AND LABELS ===")
stair = layers.get('A-stair')
print("A-stair total children:", len(stair.get('kind', {}).get('children', [])))

# Group children by spatial region
regions = {'core': [], 'south': [], 'north': [], 'other': []}

for i, c in enumerate(stair.get('kind', {}).get('children', [])):
    sps = extract_subpaths(c)
    if not sps: continue
    all_pts = []
    for sp in sps: all_pts.extend(sp['anchors'])
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    if 1150 <= min_x <= 1350 and 1650 <= min_y <= 1900:
        regions['core'].append((i, len(sps), len(all_pts), (round(min_x,1), round(max_x,1)), (round(min_y,1), round(max_y,1))))
    elif 1000 <= min_x <= 1650 and 1800 <= min_y <= 2150:
        regions['south'].append((i, len(sps), len(all_pts), (round(min_x,1), round(max_x,1)), (round(min_y,1), round(max_y,1))))
    elif min_y < 1100:
        regions['north'].append((i, len(sps), len(all_pts), (round(min_x,1), round(max_x,1)), (round(min_y,1), round(max_y,1))))
    else:
        regions['other'].append((i, len(sps), len(all_pts), (round(min_x,1), round(max_x,1)), (round(min_y,1), round(max_y,1))))

print(f"Core items: {len(regions['core'])}")
print(f"South items: {len(regions['south'])}")
print(f"North items: {len(regions['north'])}")
print(f"Other items: {len(regions['other'])}")

print("\n--- Core items detail ---")
for item in regions['core']:
    print(f"Child {item[0]:3d}: sps={item[1]}, pts={item[2]}, X={item[3]}, Y={item[4]}")

print("\n--- South items detail ---")
for item in regions['south']:
    print(f"Child {item[0]:3d}: sps={item[1]}, pts={item[2]}, X={item[3]}, Y={item[4]}")

print("\n--- Other items detail ---")
for item in regions['other']:
    print(f"Child {item[0]:3d}: sps={item[1]}, pts={item[2]}, X={item[3]}, Y={item[4]}")


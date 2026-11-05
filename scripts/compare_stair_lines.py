import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m

doc = load_pdf_doc()['document']
stair = {l['name']: l for l in doc['layers']}['A-stair']

print("=== COMPARING CHILD 11..22 AND CHILD 66..84 ===")
for i in [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]:
    c = stair['kind']['children'][i]
    pts = [to_m(p) for p in extract_subpaths(c)[0]['anchors']]
    print(f"Child {i:2d}: pts={pts}")

print("\n--- Half lines ---")
for i in range(66, 85):
    c = stair['kind']['children'][i]
    pts = [to_m(p) for p in extract_subpaths(c)[0]['anchors']]
    print(f"Child {i:2d}: pts={pts}")


import sys
sys.path.insert(0, '.')
from scripts.inspect_exact_core_stair import to_m, load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
stair = layers['A-stair']

# Flight 1 steps
f1_indices = [43, 39, 37, 35]
f1_steps = []
for idx in f1_indices:
    c = stair['kind']['children'][idx]
    pts = [to_m(p) for p in extract_subpaths(c)[0]['anchors']]
    f1_steps.append(pts)

# Flight 2 steps
f2_indices = [11, 14, 15, 16, 17, 18, 19, 20, 21, 22]
f2_steps = []
for idx in f2_indices:
    c = stair['kind']['children'][idx]
    pts = [to_m(p) for p in extract_subpaths(c)[0]['anchors']]
    f2_steps.append(pts)

# South outdoor steps (89..104)
outdoor_steps = []
for idx in range(89, 105):
    c = stair['kind']['children'][idx]
    pts = [to_m(p) for p in extract_subpaths(c)[0]['anchors']]
    outdoor_steps.append(pts)

print(f"Flight 1 steps: {len(f1_steps)}")
print(f"Flight 2 steps: {len(f2_steps)}")
print(f"Outdoor steps: {len(outdoor_steps)}")


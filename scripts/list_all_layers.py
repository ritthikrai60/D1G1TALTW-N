import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
print("Layers in document:")
for l in doc['layers']:
    children = l['kind'].get('children', [])
    print(f"Layer: '{l['name']}', visible={l.get('visible')}, children_count={len(children)}")
    if 'stair' in l['name'].lower() or 'str' in l['name'].lower() or 'step' in l['name'].lower():
        print(f"  --> FOUND STAIR LAYER: {l['name']}")


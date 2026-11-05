import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc

doc = load_pdf_doc()['document']
artboards = doc.get('artboards', [])
print("Artboards:", artboards)
grid = doc.get('grid', {})
print("Grid:", grid)
metadata = doc.get('metadata', {})
print("Metadata:", metadata)


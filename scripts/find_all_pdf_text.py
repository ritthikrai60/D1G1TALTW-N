import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc

doc = load_pdf_doc()['document']
text_items = []

def find_text(item):
    if isinstance(item, dict):
        kind = item.get('kind')
        if isinstance(kind, dict) and kind.get('type') == 'text':
            text_items.append(item)
        elif 'text' in item or 'characters' in item:
            text_items.append(item)
        for v in item.values():
            find_text(v)
    elif isinstance(item, list):
        for elem in item:
            find_text(elem)

find_text(doc)
print(f"Total text items found: {len(text_items)}")
for t in text_items[:30]:
    print(t)

import pypdf
import json

reader = pypdf.PdfReader('01-First_Floor-Clean.pdf')
data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
doc = json.loads(data.decode('utf-8'))['document']
layers = doc.get('layers', [])
print(f'Total layers: {len(layers)}')
for i, l in enumerate(layers):
    name = l.get('name')
    visible = l.get('visible')
    children = l.get('kind', {}).get('children', [])
    print(f'{i:2d}: name={name!r:<30} visible={visible} children={len(children)}')


import pypdf
import json

reader = pypdf.PdfReader('02-Second_Floor-Clean.pdf')
data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
doc = json.loads(data.decode('utf-8'))['document']
layers = doc.get('layers', [])

print(f"Total layers in F02: {len(layers)}")
for i, l in enumerate(layers):
    n = len(l.get('kind', {}).get('children', []))
    if n > 0:
        print(f"  {i:2d}: {l.get('name')!r} -> {n} children")


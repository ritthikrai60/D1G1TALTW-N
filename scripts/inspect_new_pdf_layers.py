import pypdf
import json
import math

reader = pypdf.PdfReader(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf')
print("Page count:", len(reader.pages))
data = reader.attachments['vectorcraft-editing.vectorcraft'][0]
doc = json.loads(data.decode('utf-8'))['document']

print(f"Total layers: {len(doc['layers'])}")
for i, l in enumerate(doc['layers']):
    count = len(l['kind']['children'])
    if count > 0:
        print(f"  [{i}] '{l['name']}': {count} elements")


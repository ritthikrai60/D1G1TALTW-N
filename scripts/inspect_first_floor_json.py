import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import pypdf

# Let's extract all paths from 01-First_Floor-Clean.pdf as well!
# In 01-First_Floor-Clean.pdf, let's see if VectorCraft stream exists
with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f:
    data1 = f.read()

import re, zlib, json
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data1, re.DOTALL)
print("01-First_Floor streams:", len(streams))
for i, s in enumerate(streams):
    try:
        dec = zlib.decompress(s)
        if b'VectorCraft' in dec or b'layers' in dec:
            print(f"Stream {i} has VectorCraft JSON! Length {len(dec)}")
            vc1 = json.loads(dec.decode('utf-8'))
            print("Layers in 01:", [l['name'] for l in vc1['document']['layers']])
    except Exception as e:
        pass


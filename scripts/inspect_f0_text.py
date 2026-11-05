import json
import zlib
import re

pdf_path = r"c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf"
with open(pdf_path, "rb") as f:
    raw = f.read()

streams = re.findall(rb'stream\r?\n(.*?)\r?\nendstream', raw, re.S)
layers = []
for s in streams:
    try:
        dec = zlib.decompress(s)
        if dec.startswith(b'{"format"'):
            layers = json.loads(dec.decode('utf-8'))['document'].get('layers', [])
            break
    except Exception:
        pass

# Check text items in all layers or pdf text
# Let's search raw uncompressed streams for strings / Tj / TJ
text_fragments = []
for s in streams:
    try:
        dec = zlib.decompress(s).decode('latin1')
        for m in re.finditer(r'\((.*?)\)\s*Tj', dec):
            text_fragments.append(m.group(1))
        for m in re.finditer(r'\[(.*?)\]\s*TJ', dec):
            text_fragments.append(m.group(1))
    except Exception:
        pass

print(f"Text fragments found in PDF: {len(text_fragments)}")
print("Sample texts:", text_fragments[:30])


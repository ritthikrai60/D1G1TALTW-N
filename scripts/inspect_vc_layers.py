import json
import zlib
import re

pdf_path = r"c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf"
with open(pdf_path, "rb") as f:
    raw = f.read()

streams = re.findall(rb'stream\r?\n(.*?)\r?\nendstream', raw, re.S)
for s in streams:
    try:
        dec = zlib.decompress(s)
        if dec.startswith(b'{"format"'):
            data = json.loads(dec.decode('utf-8'))
            print("Format:", data.get('format'))
            doc = data.get('document', {})
            layers = doc.get('layers', [])
            print("Layers count:", len(layers))
            for lyr in layers:
                name = lyr.get('name')
                children = lyr.get('kind', {}).get('children', [])
                types = set()
                for c in children:
                    types.add(c.get('kind', {}).get('type'))
                print(f"  Layer '{name}': {len(children)} items, types={types}")
            break
    except Exception as e:
        pass


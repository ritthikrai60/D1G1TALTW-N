import zlib
import json

pdf_path = '00-Ground_Floor-Clean.pdf'
with open(pdf_path, 'rb') as f:
    data = f.read()

pos = 0
found_json = None
while True:
    idx = data.find(b'stream', pos)
    if idx == -1: break
    end_idx = data.find(b'endstream', idx)
    if end_idx == -1: break
    s_start = idx + 6
    while s_start < end_idx and data[s_start:s_start+1] in (b'\r', b'\n'): s_start += 1
    s_end = end_idx
    while s_end > s_start and data[s_end-1:s_end] in (b'\r', b'\n'): s_end -= 1
    stream_bytes = data[s_start:s_end]
    try:
        decomp = zlib.decompress(stream_bytes)
        if b'VectorCraft' in decomp or b'"layers"' in decomp:
            found_json = json.loads(decomp.decode('utf-8'))
            break
    except Exception:
        pass
    pos = end_idx + 9

doc = found_json['document']
layers = doc.get('layers', [])
print(f"Layer summary (total {len(layers)}):")
for i, l in enumerate(layers):
    name = l.get('name')
    kind = l.get('kind', {})
    children = kind.get('children', [])
    child_types = {}
    for c in children:
        t = c.get('kind', {}).get('type', c.get('type', 'unknown'))
        child_types[t] = child_types.get(t, 0) + 1
    if len(children) > 0:
        print(f"[{i:02d}] {name:30s} : {len(children):4d} items, types={child_types}")

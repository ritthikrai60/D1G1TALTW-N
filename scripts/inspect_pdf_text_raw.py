import zlib

with open('00-Ground_Floor-Clean.pdf', 'rb') as f:
    raw = f.read()

# Look for standard PDF text strings or FlateDecode streams containing text
pos = 0
found_texts = []
while True:
    idx = raw.find(b'stream', pos)
    if idx == -1: break
    end_idx = raw.find(b'endstream', idx)
    if end_idx == -1: break
    s_start = idx + 6
    while s_start < end_idx and raw[s_start:s_start+1] in (b'\r', b'\n'): s_start += 1
    s_end = end_idx
    while s_end > s_start and raw[s_end-1:s_end] in (b'\r', b'\n'): s_end -= 1
    try:
        decomp = zlib.decompress(raw[s_start:s_end])
        # search for (Text) Tj or 'text'
        if b'Tj' in decomp or b'TJ' in decomp:
            for line in decomp.split(b'\n'):
                if b'Tj' in line or b'TJ' in line:
                    found_texts.append(line)
    except:
        pass
    pos = end_idx + 9

print(f"Found {len(found_texts)} raw PDF text commands:")
for t in found_texts[:20]:
    print(t[:100])


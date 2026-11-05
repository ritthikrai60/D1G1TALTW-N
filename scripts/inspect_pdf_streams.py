with open('01-First_Floor-Clean.pdf', 'rb') as f:
    data = f.read()

print("File size:", len(data))
# look for objects
pos = 0
streams = []
while True:
    idx = data.find(b'stream', pos)
    if idx == -1: break
    end_idx = data.find(b'endstream', idx)
    if end_idx == -1: break
    # check dict before stream
    dict_start = data.rfind(b'<<', 0, idx)
    dict_text = data[dict_start:idx].decode('latin1', errors='ignore') if dict_start != -1 else ''
    s_start = idx + 6
    while s_start < end_idx and data[s_start:s_start+1] in (b'\r', b'\n'): s_start += 1
    s_end = end_idx
    while s_end > s_start and data[s_end-1:s_end] in (b'\r', b'\n'): s_end -= 1
    stream_bytes = data[s_start:s_end]
    streams.append((dict_text.strip().replace('\n', ' '), len(stream_bytes), s_start, s_end))
    pos = end_idx + 9

print(f"Total streams: {len(streams)}")
for i, (d, l, s, e) in enumerate(streams):
    print(f"Stream {i}: len={l}, dict={d[:80]}")


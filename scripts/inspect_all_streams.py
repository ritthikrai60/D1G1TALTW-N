import zlib
import re

with open('00-Ground_Floor-Clean.pdf', 'rb') as f:
    data = f.read()

pos = 0
stream_idx = 0
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
    stream_idx += 1
    print(f"\n--- Stream {stream_idx} (raw length: {len(stream_bytes)}) ---")
    
    # Try decompression
    try:
        decomp = zlib.decompress(stream_bytes)
        print(f"Decompressed length: {len(decomp)}")
        print(f"Sample: {decomp[:200]}")
    except Exception as e:
        print(f"Not zlib / error: {e}")
        print(f"Raw sample: {stream_bytes[:200]}")
    
    pos = end_idx + 9


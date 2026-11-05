import zlib, re

data = open('01-First_Floor-Clean.pdf', 'rb').read()

# Let's find every occurrence of b'stream' followed by binary data
matches = list(re.finditer(b'stream\r?\n', data))
print(f"Found {len(matches)} stream start markers")

for i, m in enumerate(matches):
    start = m.end()
    end = data.find(b'endstream', start)
    raw = data[start:end].rstrip(b'\r\n')
    print(f"\nStream {i}: start={start}, end={end}, len={len(raw)}")
    # Try different decompression
    for wbits in [15, -15, 31, 47]:
        try:
            d = zlib.decompress(raw, wbits)
            print(f"  Success with wbits={wbits}! Decompressed size={len(d)}")
            if b'layers' in d or b'document' in d:
                print(f"  *** CONTAINS LAYERS/DOCUMENT! ***")
                with open(f'decomp_stream_{i}.json', 'wb') as out_f:
                    out_f.write(d)
                print(f"  Saved to decomp_stream_{i}.json")
            else:
                print(f"  Preview: {d[:80]}")
            break
        except Exception as e:
            pass


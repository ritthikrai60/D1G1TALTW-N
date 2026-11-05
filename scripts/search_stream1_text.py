import zlib
import re

with open('00-Ground_Floor-Clean.pdf', 'rb') as f:
    data = f.read()

idx = data.find(b'stream')
end_idx = data.find(b'endstream')
stream_bytes = data[idx+6:end_idx].strip()
content = zlib.decompress(stream_bytes)

print("Stream 1 size:", len(content))
bt_matches = list(re.finditer(b'BT(.*?)ET', content, re.DOTALL))
print("BT...ET blocks found:", len(bt_matches))
for i, m in enumerate(bt_matches[:20]):
    print(f"Block {i}: {m.group(0)[:150]}")

# Also search for text strings in parentheses ( ... ) Tj
tj_matches = list(re.finditer(rb'\((.*?)\)\s*Tj', content))
print("Tj strings found:", len(tj_matches))
for i, m in enumerate(tj_matches[:30]):
    print(f"Tj {i}: {m.group(1)}")


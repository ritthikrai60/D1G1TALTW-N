import zlib
import re
from PIL import Image
import os

# Let's read the PDF stream directly to get the exact matrix / coordinates
with open(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf', 'rb') as f:
    data = f.read()

# Let's find stream 1 (PDF drawing operators)
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
print(f"Found {len(streams)} streams")

# Stream 1 decompressed:
decompressed_ops = []
for i, s in enumerate(streams):
    try:
        dec = zlib.decompress(s)
        print(f"Stream {i}: {len(dec)} bytes decompressed")
        decompressed_ops.append(dec)
    except Exception as e:
        pass

# In stream 1, let's search for text or numbers
s1 = decompressed_ops[0].decode('latin1', errors='ignore')
print(f"Stream 1 text length: {len(s1)}")

# Let's find the transformation matrix in Stream 1: e.g. cm operator [a b c d e f] cm
cms = re.findall(r'([-\d\.]+\s+[-\d\.]+\s+[-\d\.]+\s+[-\d\.]+\s+[-\d\.]+\s+[-\d\.]+\s+cm)', s1)
print("Transform matrices (cm):", cms[:10])


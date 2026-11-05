import zlib, re

with open(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf', 'rb') as f:
    data = f.read()

streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s0 = zlib.decompress(streams[0]).decode('latin1', errors='ignore')

# Search for color operators like '1 1 0 RG' (yellow stroke) or '1 1 0 rg' (yellow fill)
# Yellow in RGB is (1, 1, 0) or close to it (e.g. yellow in AutoCAD is 1 1 0 or similar)
yellow_ops = re.findall(r'(\d*\.?\d+\s+\d*\.?\d+\s+\d*\.?\d+\s+[rR][gG])', s0)
print("Unique color operators in PDF Stream 0:")
import collections
print(collections.Counter(yellow_ops))


import zlib
import json

def load_pdf_doc(pdf_path='00-Ground_Floor-Clean.pdf'):
    with open(pdf_path, 'rb') as f:
        data = f.read()
    pos = 0
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
                return json.loads(decomp.decode('utf-8'))
        except Exception:
            pass
        pos = end_idx + 9
    return None

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

grid = layers.get('GRID')
print("GRID layer:")
long_lines_x = []
long_lines_y = []

for c in grid['kind']['children']:
    p = c.get('kind', {}).get('path', {})
    for sp in p.get('subpaths', []):
        anchors = [a.get('p') for a in sp.get('anchors', []) if 'p' in a]
        if len(anchors) == 2:
            p0, p1 = anchors[0], anchors[1]
            dx = abs(p1[0] - p0[0])
            dy = abs(p1[1] - p0[1])
            # Vertical grid line (constant X, large dy)
            if dx < 1.0 and dy > 200:
                long_lines_x.append(p0[0])
            # Horizontal grid line (constant Y, large dx)
            if dy < 1.0 and dx > 200:
                long_lines_y.append(p0[1])

long_lines_x = sorted(list(set([round(x, 1) for x in long_lines_x])))
long_lines_y = sorted(list(set([round(y, 1) for y in long_lines_y])))

print("Vertical grid lines (X):", long_lines_x)
if len(long_lines_x) > 1:
    diffs = [round(long_lines_x[i+1] - long_lines_x[i], 2) for i in range(len(long_lines_x)-1)]
    print("X diffs:", diffs)

print("\nHorizontal grid lines (Y):", long_lines_y)
if len(long_lines_y) > 1:
    diffs_y = [round(long_lines_y[i+1] - long_lines_y[i], 2) for i in range(len(long_lines_y)-1)]
    print("Y diffs:", diffs_y)


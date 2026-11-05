import zlib, re, json, math
import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths

# We know streams in 01-First_Floor-Clean.pdf:
# Let's write a robust reader for 01-First_Floor-Clean.pdf
with open(r'01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()

# find streams
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
print(f"Streams found: {len(streams)}")

meta = None
for idx, s in enumerate(streams):
    for wbits in [15, -15, 31, 47]:
        try:
            decomp = zlib.decompress(s, wbits)
            if b'document' in decomp:
                print(f"Found document in stream {idx} (wbits={wbits})!")
                meta = json.loads(decomp.decode('utf-8'))
                break
        except: pass
    if meta: break

if meta:
    doc = meta['document']
    X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
    def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

    l_stair = next((x for x in doc['layers'] if x['name'] == 'A-stair'), None)
    print(f"\nA-stair children count: {len(l_stair['kind']['children'])}")
    
    # ST-1 is children 9 to 61
    print("\n--- ST-1 risers and boundary lines ---")
    st1_children = []
    for idx in range(9, 62):
        c = l_stair['kind']['children'][idx]
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            st1_children.append((idx, sp['closed'], pts))
            if idx in [9, 10, 11, 27, 28, 29, 30, 31, 60, 61]:
                print(f"  Child {idx:2d}: closed={sp['closed']}, pts={pts}")

    # Inspect East Wing stairs in A-stair or WALL/A-wall
    print("\n--- East Wing stair search (X > 50, Y > 5) ---")
    for idx, c in enumerate(l_stair['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if any(x > 50 and y > 5 for x, y in zip(xs, ys)):
                print(f"  A-stair Child {idx:2d}: closed={sp['closed']}, len={len(pts)}, X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}]")


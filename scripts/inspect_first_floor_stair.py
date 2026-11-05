import zlib, re, json

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f:
    data1 = f.read()

streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data1, re.DOTALL)
for s in streams:
    try:
        dec = zlib.decompress(s)
        if b'VectorCraft' in dec:
            doc1 = json.loads(dec.decode('utf-8'))['document']
            break
    except:
        pass

stair1 = [l for l in doc1['layers'] if l['name'] == 'A-stair'][0]
print(f"01 A-stair children count: {len(stair1['kind']['children'])}")

def extract_subpaths(node):
    subpaths = []
    if isinstance(node, dict):
        if 'subpaths' in node:
            for sp in node['subpaths']:
                anchors = [p['anchor'] for p in sp.get('points', []) if 'anchor' in p]
                if anchors:
                    subpaths.append({'anchors': anchors, 'closed': sp.get('closed', False)})
        for k, v in node.items():
            if k != 'subpaths':
                subpaths.extend(extract_subpaths(v))
    elif isinstance(node, list):
        for item in node:
            subpaths.extend(extract_subpaths(item))
    return subpaths

for i, c in enumerate(stair1['kind']['children']):
    sps = extract_subpaths(c)
    for sp in sps:
        pts = sp['anchors']
        if not pts: continue
        xm = [(p[0]-1133.858)/28.346456692913385 for p in pts]
        ym = [(p[1]-1417.323)/28.346456692913385 for p in pts]
        if min(xm) > 2.0 and max(xm) < 8.0 and min(ym) > 10.0 and max(ym) < 18.0:
            print(f"c{i:2d}: pts={len(pts)}, X=[{min(xm):.2f}, {max(xm):.2f}], Y=[{min(ym):.2f}, {max(ym):.2f}], closed={sp['closed']}")

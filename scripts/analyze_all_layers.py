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

def extract_subpaths(item):
    paths = []
    kind = item.get('kind', {})
    if kind.get('type') == 'path':
        p = kind.get('path', {})
        for sp in p.get('subpaths', []):
            anchors = [a.get('p') for a in sp.get('anchors', []) if 'p' in a]
            closed = sp.get('closed', False)
            if len(anchors) > 0:
                paths.append({'anchors': anchors, 'closed': closed})
    elif kind.get('type') == 'group':
        for child in kind.get('children', []):
            paths.extend(extract_subpaths(child))
    return paths

if __name__ == '__main__':
    doc = load_pdf_doc()['document']
    layers = {l['name']: l for l in doc['layers']}
    
    # Check key layers
    check_layers = ['A-col', 'P-1 (0.50)', 'P-1', 'P-2 (0.15)', 'P-2', 'P-3 (0.25)', 'P-3', 'P-4 (0.10)', 'P-4', 'A-wall', 'AR_HATCH', 'A-stair', 'SANITARY', 'WC-OUTL']
    for name in check_layers:
        l = layers.get(name)
        if not l: continue
        children = l.get('kind', {}).get('children', [])
        all_sp = []
        for c in children:
            all_sp.extend(extract_subpaths(c))
        
        # calculate bounding box
        xs = [pt[0] for sp in all_sp for pt in sp['anchors']]
        ys = [pt[1] for sp in all_sp for pt in sp['anchors']]
        closed_cnt = sum(1 for sp in all_sp if sp['closed'])
        if xs and ys:
            print(f"Layer {name:15s}: {len(children):4d} items, {len(all_sp):4d} subpaths ({closed_cnt} closed), X=[{min(xs):.1f}, {max(xs):.1f}], Y=[{min(ys):.1f}, {max(ys):.1f}]")
        else:
            print(f"Layer {name:15s}: {len(children):4d} items, 0 subpaths")


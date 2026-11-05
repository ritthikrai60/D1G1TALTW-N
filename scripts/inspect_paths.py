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

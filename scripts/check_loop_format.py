import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

ar_hatch = layers['AR_HATCH']
loops = []
for c in ar_hatch.get('kind', {}).get('children', []):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if min(p[1] for p in pts) >= 900:
            pts_m = [to_m(p) for p in pts]
            if pts_m[0] == pts_m[-1]:
                pts_m = pts_m[:-1]
            if len(pts_m) >= 3:
                loops.append(pts_m)

print(f"Sample loop 0: {loops[0]}")
print(f"Sample loop 1: {loops[1]}")


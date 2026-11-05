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

print("=== Checking walls in North zone (Y < 900 pt) ===")
for lname in ['A-wall', 'AR_HATCH', 'P-1', 'P-2', 'P-3', 'P-4', 'WALL']:
    l = layers.get(lname)
    if not l: continue
    loops = []
    lines = []
    for c in l.get('kind', {}).get('children', []):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if max(p[1] for p in pts) < 900:
                pts_m = [to_m(p) for p in pts]
                if pts_m[0] == pts_m[-1] or sp['closed']:
                    loops.append(pts_m)
                else:
                    lines.append(pts_m)
    if len(loops) > 0 or len(lines) > 0:
        print(f"Layer {lname:15s}: {len(loops)} closed loops, {len(lines)} open lines in North zone")


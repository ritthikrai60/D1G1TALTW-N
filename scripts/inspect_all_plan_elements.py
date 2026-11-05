import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import json

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

print("=== 1. COLUMNS IN A-col ===")
acol = layers['A-col']
for i, c in enumerate(acol.get('kind', {}).get('children', [])):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if len(pts) >= 4:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            w = (max(xs) - min(xs))/SCALE
            h = (max(ys) - min(ys))/SCALE
            cx = sum(xs)/len(xs)
            cy = sum(ys)/len(ys)
            if 0.15 <= w <= 1.5 and 0.15 <= h <= 1.5:
                print(f"A-col [{i:2d}]: ({cx:.1f}, {cy:.1f}) -> m: {to_m((cx,cy))} size={w:.2f}x{h:.2f}m")

print("\n=== 2. COLUMNS IN P-1 ===")
p1 = layers.get('P-1')
if p1:
    for i, c in enumerate(p1.get('kind', {}).get('children', [])):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if len(pts) >= 4:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                w = (max(xs) - min(xs))/SCALE
                h = (max(ys) - min(ys))/SCALE
                cx = sum(xs)/len(xs)
                cy = sum(ys)/len(ys)
                if 0.2 <= w <= 1.5 and 0.2 <= h <= 1.5:
                    print(f"P-1 [{i:2d}]: ({cx:.1f}, {cy:.1f}) -> m: {to_m((cx,cy))} size={w:.2f}x{h:.2f}m")

print("\n=== 3. ALL BOUNDARIES / SLAB OUTLINES IN DRAWING ===")
# Search all closed paths across all layers with area > 10 m2
for lname, l in layers.items():
    children = l.get('kind', {}).get('children', [])
    for i, c in enumerate(children):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if len(pts) >= 4:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                w = (max(xs) - min(xs))/SCALE
                h = (max(ys) - min(ys))/SCALE
                cx = sum(xs)/len(xs)
                cy = sum(ys)/len(ys)
                if w > 5.0 and h > 5.0:
                    print(f"Layer {lname:15s} child {i:3d}: closed={sp['closed']} pts={len(pts)} size={w:.1f}x{h:.1f}m at ({cx:.1f}, {cy:.1f}) m={to_m((cx,cy))}")


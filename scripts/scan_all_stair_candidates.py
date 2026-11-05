import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import math

doc = load_pdf_doc()['document']

# Scan all layers for candidate stair treads:
# A stair tread is typically a line segment of length 0.8m to 3.0m, spaced 0.25m to 0.35m apart
print("Scanning all layers for stairs / steps...")

stair_candidates = {}

for layer in doc['layers']:
    lname = layer['name']
    children = layer['kind'].get('children', [])
    segments = []
    for c in children:
        sps = extract_subpaths(c)
        for sp in sps:
            pts = sp['anchors']
            if len(pts) == 2:
                p0, p1 = pts[0], pts[1]
                x0 = (p0[0]-1133.858)/28.346456692913385
                y0 = (p0[1]-1417.323)/28.346456692913385
                x1 = (p1[0]-1133.858)/28.346456692913385
                y1 = (p1[1]-1417.323)/28.346456692913385
                length = math.hypot(x1 - x0, y1 - y0)
                if 0.6 <= length <= 6.0:
                    segments.append(((x0, y0), (x1, y1), length))
            elif len(pts) > 2:
                # check polylines
                pass
    if len(segments) >= 3:
        stair_candidates[lname] = len(segments)

print("Layers with 3+ line segments (0.6m - 6.0m):")
for k, v in sorted(stair_candidates.items(), key=lambda x: -x[1]):
    print(f"  {k:20s}: {v} segments")


import pypdfium2 as pdfium
from PIL import Image, ImageDraw
import os

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
doc = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf')
bm = doc[0].render(scale=2)
img = bm.to_pil()

# Let's write a script that scans the whole image and highlights all known stair areas:
# 1. Core Stair near locker: X_pt ~ 1250, Y_pt ~ 1800
# 2. South Outdoor Stair: X_pt ~ 1160, Y_pt ~ 2030
# 3. Fire Stair (mystery stair in P-2): X_pt ~ 1220, Y_pt ~ 1380
# Let's find out if there are stairs in other corners: West wing? North wing? East wing?

draw = ImageDraw.Draw(img)

# Let's check what other layers have parallel lines:
import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths

vc_doc = load_pdf_doc()['document']

print("=== Scanning ALL layers for parallel line clusters (stairs) ===")

all_lines = []
for layer in vc_doc['layers']:
    lname = layer['name']
    for c in layer['kind'].get('children', []):
        sps = extract_subpaths(c)
        for sp in sps:
            pts = sp['anchors']
            if len(pts) == 2:
                all_lines.append((pts[0], pts[1], lname))

print(f"Total 2-point line segments in entire drawing: {len(all_lines)}")

# Find clusters of lines spaced around 0.2m - 0.4m (5.6 to 11.3 pt)
# Group lines by their center coordinates
clusters = []
for p0, p1, lname in all_lines:
    cx = (p0[0] + p1[0]) / 2
    cy = (p0[1] + p1[1]) / 2
    xm = (cx - 1133.858) / 28.346456692913385
    ym = (cy - 1417.323) / 28.346456692913385
    clusters.append((cx, cy, xm, ym, lname))

# Let's print regions with high density of line segments:
import collections
grid = collections.defaultdict(list)
for cx, cy, xm, ym, lname in clusters:
    gx = int(xm // 5) * 5
    gy = int(ym // 5) * 5
    grid[(gx, gy)].append(lname)

print("\nLine segment density by 5mx5m cell:")
for (gx, gy), lnames in sorted(grid.items()):
    counts = collections.Counter(lnames)
    if len(lnames) > 10:
        print(f"Cell X=[{gx:3d}, {gx+5:3d}], Y=[{gy:3d}, {gy+5:3d}]: total {len(lnames):3d} lines -> {dict(counts)}")


import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from PIL import Image, ImageDraw

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Focus strictly on the south outdoor stair: X from 1050 to 1280 pt, Y from 1950 to 2180 pt
x0, y0, x1, y1 = 1050, 1950, 1280, 2180
scale = 5 # 5x zoom
w = int((x1 - x0) * scale)
h = int((y1 - y0) * scale)
img = Image.new('RGB', (w, h), (255, 255, 255))
draw = ImageDraw.Draw(img)

# Layers to draw
layer_colors = [
    ('A-wall', (0, 0, 0), 2),
    ('P-1 (0.50)', (200, 0, 0), 3),
    ('A-col', (255, 140, 0), 3),
    ('D&W', (0, 180, 0), 2),
    ('SYMBOL', (255, 0, 0), 2),
    ('LABEL', (0, 0, 255), 2),
    ('DIMENSION', (100, 100, 100), 2),
    ('A-stair', (0, 0, 220), 2),
    ('0', (150, 0, 150), 2),
]

for lname, color, width in layer_colors:
    l = layers.get(lname)
    if not l: continue
    for c in l.get('kind', {}).get('children', []):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if len(pts) < 2: continue
            if any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in pts):
                canvas_pts = [((p[0] - x0)*scale, (p[1] - y0)*scale) for p in pts]
                if sp['closed'] or (len(canvas_pts) > 2 and canvas_pts[0] == canvas_pts[-1]):
                    draw.polygon(canvas_pts, outline=color, width=width)
                else:
                    draw.line(canvas_pts, fill=color, width=width)

zoom_path = 'C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/zoom_south_stair_5x.png'
img.save(zoom_path)
print("Saved 5x zoom of south stair to", zoom_path)


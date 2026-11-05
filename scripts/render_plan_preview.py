import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from PIL import Image, ImageDraw

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Image size: 3370 x 2384
W, H = 3370, 2384
img = Image.new('RGB', (W, H), (255, 255, 255))
draw = ImageDraw.Draw(img)

# Layer styling
# (layer_name, stroke_color, stroke_width, fill_color)
style_map = [
    ('GRID', (220, 220, 220), 1, None),
    ('เส้นบาง', (210, 210, 210), 1, None),
    ('A-stair', (0, 180, 0), 2, None),
    ('SANITARY', (0, 150, 220), 1, None),
    ('WC-OUTL', (0, 100, 200), 2, None),
    ('P-2 (0.15)', (180, 0, 180), 2, None),
    ('P-2', (180, 0, 180), 2, None),
    ('P-3 (0.25)', (200, 100, 0), 2, None),
    ('P-3', (200, 100, 0), 2, None),
    ('P-4 (0.10)', (120, 120, 0), 2, None),
    ('P-4', (120, 120, 0), 2, None),
    ('P-1 (0.50)', (220, 0, 0), 3, (255, 200, 200)),
    ('P-1', (200, 0, 0), 2, None),
    ('A-wall', (30, 30, 30), 2, None),
    ('AR_HATCH', (50, 50, 50), 2, (180, 180, 180)),
    ('A-col', (255, 140, 0), 2, (255, 200, 50)),
]

for lname, stroke, width, fill in style_map:
    l = layers.get(lname)
    if not l: continue
    all_sp = []
    for c in l.get('kind', {}).get('children', []):
        all_sp.extend(extract_subpaths(c))
    for sp in all_sp:
        anchors = sp['anchors']
        if len(anchors) < 2: continue
        pts = [(p[0], p[1]) for p in anchors]
        is_closed = sp['closed'] or (len(pts) > 2 and pts[0] == pts[-1])
        if is_closed and fill:
            draw.polygon(pts, fill=fill, outline=stroke, width=width)
        else:
            draw.line(pts, fill=stroke, width=width)

preview_path = 'C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/cad_direct_preview.png'
img.save(preview_path)
print(f"Saved direct CAD render preview to {preview_path}")


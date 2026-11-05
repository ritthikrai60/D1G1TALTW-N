import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from PIL import Image, ImageDraw, ImageFont

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# High-resolution rendering of Core Area: X in [1100, 1400], Y in [1650, 1950]
scale_factor = 4.0
ox, oy = 1100.0, 1650.0
w_px = int((1400 - ox) * scale_factor)
h_px = int((1950 - oy) * scale_factor)

img_core = Image.new('RGB', (w_px, h_px), (255, 255, 255))
draw_c = ImageDraw.Draw(img_core)

# Render layers in order
layer_order = [
    ('GRID', (220, 220, 220), 1),
    ('เส้นบาง', (180, 180, 180), 1),
    ('SANITARY', (150, 200, 240), 1),
    ('WC-OUTL', (100, 180, 240), 1),
    ('P-2 (0.15)', (180, 120, 180), 2),
    ('P-4 (0.10)', (180, 150, 80), 2),
    ('AR_HATCH', (60, 60, 60), 2),
    ('A-wall', (40, 40, 40), 2),
    ('P-1 (0.50)', (200, 30, 30), 3),
    ('A-col', (255, 120, 0), 2),
    ('A-stair', (0, 150, 255), 2),
    ('SYMBOL', (255, 0, 0), 2),
    ('DIMENSION', (100, 100, 100), 1),
    ('0', (0, 0, 0), 1),
]

for lname, col, width in layer_order:
    l = layers.get(lname)
    if not l: continue
    for c in l.get('kind', {}).get('children', []):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if any(1100 <= p[0] <= 1400 and 1650 <= p[1] <= 1950 for p in pts):
                px = [((p[0] - ox) * scale_factor, (p[1] - oy) * scale_factor) for p in pts]
                if sp['closed']:
                    draw_c.polygon(px, outline=col, width=width)
                else:
                    draw_c.line(px, fill=col, width=width)

core_zoom_path = 'C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/pure_cad_core_zoom_4x.png'
img_core.save(core_zoom_path)
print(f"Saved Core Zoom to {core_zoom_path}")

# High-resolution rendering of South Area: X in [1000, 1700], Y in [1800, 2200]
ox_s, oy_s = 1000.0, 1800.0
w_s = int((1700 - ox_s) * scale_factor)
h_s = int((2200 - oy_s) * scale_factor)

img_south = Image.new('RGB', (w_s, h_s), (255, 255, 255))
draw_s = ImageDraw.Draw(img_south)

for lname, col, width in layer_order:
    l = layers.get(lname)
    if not l: continue
    for c in l.get('kind', {}).get('children', []):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if any(1000 <= p[0] <= 1700 and 1800 <= p[1] <= 2200 for p in pts):
                px = [((p[0] - ox_s) * scale_factor, (p[1] - oy_s) * scale_factor) for p in pts]
                if sp['closed']:
                    draw_s.polygon(px, outline=col, width=width)
                else:
                    draw_s.line(px, fill=col, width=width)

south_zoom_path = 'C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/pure_cad_south_zoom_4x.png'
img_south.save(south_zoom_path)
print(f"Saved South Zoom to {south_zoom_path}")


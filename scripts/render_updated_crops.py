import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from PIL import Image, ImageDraw, ImageFont

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Render full drawing to an image
W, H = 3370, 2384
img = Image.new('RGB', (W, H), (255, 255, 255))
draw = ImageDraw.Draw(img)

# Layer styling
style_map = [
    ('GRID', (230, 230, 230), 1),
    ('เส้นบาง', (220, 220, 220), 1),
    ('P-2 (0.15)', (200, 150, 200), 2),
    ('P-4 (0.10)', (200, 180, 100), 2),
    ('P-1 (0.50)', (220, 100, 100), 3),
    ('A-wall', (80, 80, 80), 2),
    ('AR_HATCH', (100, 100, 100), 2),
    ('A-col', (255, 140, 0), 2),
    ('A-stair', (0, 150, 255), 3),  # Bright cyan/blue for stairs!
    ('SYMBOL', (255, 0, 0), 2),
    ('DIMENSION', (150, 150, 150), 1),
]

for lname, stroke, width in style_map:
    l = layers.get(lname)
    if not l: continue
    for c in l.get('kind', {}).get('children', []):
        for sp in extract_subpaths(c):
            anchors = sp['anchors']
            if len(anchors) < 2: continue
            pts = [(p[0], p[1]) for p in anchors]
            if sp['closed']:
                draw.polygon(pts, outline=stroke, width=width)
            else:
                draw.line(pts, fill=stroke, width=width)

# Now crop Core stair
# In CAD coords, Core stair is around X: [1200, 1350], Y: [1700, 1900]
crop_core = img.crop((1150, 1680, 1380, 1920)).resize((1150, 1200), Image.Resampling.NEAREST)
crop_core.save('C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/updated_crop_core_stair.png')

# South stair is around X: [1050, 1650], Y: [1800, 2150]
crop_south = img.crop((1050, 1800, 1650, 2150)).resize((1200, 700), Image.Resampling.NEAREST)
crop_south.save('C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/updated_crop_south_stair.png')

# North area around X: [1250, 1900], Y: [200, 1000]
crop_north = img.crop((1250, 200, 1900, 1000)).resize((1300, 1600), Image.Resampling.NEAREST)
crop_north.save('C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/updated_crop_north_area.png')

print("Saved updated crops successfully!")


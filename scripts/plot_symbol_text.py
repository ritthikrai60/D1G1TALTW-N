import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from PIL import Image, ImageDraw

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
sym = layers['SYMBOL']

img = Image.new('RGB', (800, 300), (255, 255, 255))
draw = ImageDraw.Draw(img)

# Coords X: 6.56 to 7.44, Y: -6.28 to -6.10
# Map to pixel canvas
for c in sym['kind']['children']:
    for sp in extract_subpaths(c):
        pts = sp['anchors'] # raw CAD pt
        # raw CAD pt X: [1185, 1215], Y: [1670, 1680]
        px = [((p[0] - 1180) * 20, (p[1] - 1665) * 20) for p in pts]
        if len(px) >= 2:
            draw.line(px, fill=(0, 0, 0), width=2)

img.save('C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/symbol_text_preview.png')
print("Saved symbol text preview")


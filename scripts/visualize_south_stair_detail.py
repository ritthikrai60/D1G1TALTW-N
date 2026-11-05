import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from PIL import Image, ImageDraw, ImageFont

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
stair = layers['A-stair']

# Zoom tightly into South stair in CAD pixels:
# X in [1050, 1650], Y in [1800, 2150]
crop_w = 1400
crop_h = 1000
img = Image.new('RGB', (crop_w, crop_h), (255, 255, 255))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype('arial.ttf', 16)
font_big = ImageFont.truetype('arial.ttf', 22)

# X range: 1050 to 1650 (span 600 pt) -> 600 * 2 = 1200 px
# Y range: 1800 to 2150 (span 350 pt) -> 350 * 2 = 700 px
ox = 1050.0
oy = 1800.0
s = 2.0

def to_px(pt):
    return (100 + (pt[0] - ox) * s, 100 + (pt[1] - oy) * s)

# Draw other layers in light gray
for lname in ['AR_HATCH', 'A-wall', 'P-1 (0.50)', 'P-2 (0.15)', 'P-4 (0.10)', 'GRID', 'เส้นบาง']:
    l = layers.get(lname)
    if not l: continue
    for c in l.get('kind', {}).get('children', []):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if any(1050 <= p[0] <= 1650 and 1800 <= p[1] <= 2150 for p in pts):
                px_pts = [to_px(p) for p in pts]
                draw.line(px_pts, fill=(220, 220, 220), width=1)

colors = [(220, 0, 0), (0, 150, 0), (0, 0, 220), (200, 100, 0), (150, 0, 150), (0, 150, 150)]
for i, c in enumerate(stair['kind']['children']):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if any(1050 <= p[0] <= 1650 and 1800 <= p[1] <= 2150 for p in pts):
            px_pts = [to_px(p) for p in pts]
            col = colors[i % len(colors)]
            if len(px_pts) == 2:
                draw.line(px_pts, fill=col, width=3)
                mx = (px_pts[0][0] + px_pts[1][0])/2
                my = (px_pts[0][1] + px_pts[1][1])/2
                draw.text((mx + 4, my - 8), f"{i}", font=font, fill=(50, 50, 50))
            else:
                draw.line(px_pts, fill=col, width=3)
                for pt in px_pts:
                    draw.ellipse([pt[0]-3, pt[1]-3, pt[0]+3, pt[1]+3], fill=(0, 0, 0))
                draw.text((px_pts[0][0] + 5, px_pts[0][1] + 5), f"{i}(len={len(pts)})", font=font_big, fill=col)

out_path = 'C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/south_stair_detailed_map.png'
img.save(out_path)
print(f"Saved detailed south stair map: {out_path}")


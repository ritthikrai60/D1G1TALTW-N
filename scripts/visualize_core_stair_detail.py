import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from PIL import Image, ImageDraw, ImageFont

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}
stair = layers['A-stair']

# Zoom tightly into Core stair in CAD pixels:
# X in [1180, 1320], Y in [1720, 1900]
crop_w = 1200
crop_h = 1400
img = Image.new('RGB', (crop_w, crop_h), (255, 255, 255))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype('arial.ttf', 16)
font_big = ImageFont.truetype('arial.ttf', 24)

# Map CAD coords (1180, 1720) -> (100, 100), scale up by ~7x
# X range: 1180 to 1320 (span 140 pt) -> 140 * 7 = 980 px
# Y range: 1720 to 1900 (span 180 pt) -> 180 * 7 = 1260 px
ox = 1180.0
oy = 1720.0
s = 7.0

def to_px(pt):
    return (100 + (pt[0] - ox) * s, 70 + (pt[1] - oy) * s)

# Draw all other layers in light gray
for lname in ['AR_HATCH', 'A-wall', 'P-1 (0.50)', 'P-2 (0.15)', 'P-4 (0.10)']:
    l = layers.get(lname)
    if not l: continue
    for c in l.get('kind', {}).get('children', []):
        for sp in extract_subpaths(c):
            pts = sp['anchors']
            if any(1180 <= p[0] <= 1320 and 1720 <= p[1] <= 1900 for p in pts):
                px_pts = [to_px(p) for p in pts]
                draw.line(px_pts, fill=(210, 210, 210), width=2)

# Draw all A-stair items in the region with their Child ID
colors = [(220, 0, 0), (0, 150, 0), (0, 0, 220), (200, 100, 0), (150, 0, 150), (0, 150, 150)]
for i, c in enumerate(stair['kind']['children']):
    for sp in extract_subpaths(c):
        pts = sp['anchors']
        if any(1170 <= p[0] <= 1330 and 1710 <= p[1] <= 1910 for p in pts):
            px_pts = [to_px(p) for p in pts]
            col = colors[i % len(colors)]
            if len(px_pts) == 2:
                draw.line(px_pts, fill=col, width=3)
                # Label at midpoint
                mx = (px_pts[0][0] + px_pts[1][0])/2
                my = (px_pts[0][1] + px_pts[1][1])/2
                draw.text((mx + 4, my - 8), f"{i}", font=font, fill=(50, 50, 50))
            else:
                draw.line(px_pts, fill=col, width=4)
                for pt in px_pts:
                    draw.ellipse([pt[0]-3, pt[1]-3, pt[0]+3, pt[1]+3], fill=(0, 0, 0))
                draw.text((px_pts[0][0] + 5, px_pts[0][1] + 5), f"{i}(len={len(pts)})", font=font_big, fill=col)

out_path = 'C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/core_stair_detailed_map.png'
img.save(out_path)
print(f"Saved detailed core stair map: {out_path}")


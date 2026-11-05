import pypdfium2 as pdfium
from PIL import Image, ImageDraw
import os

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

# Stair 1 (Fire / Egress Stair) bounds in meter: X in [1.0, 5.0], Y in [-4.0, 0.5]
# Let's crop Stair 1 from 00-Ground, 01-First, 02-Second, 03-Roof!
pdf_list = [
    '00-Ground_Floor-Clean.pdf',
    '01-First_Floor-Clean.pdf',
    '02-Second_Floor-Clean.pdf',
    '03-Roof_Floor-Clean.pdf'
]

min_x_pt = 1133.858 + 0.8 * 28.346
max_x_pt = 1133.858 + 5.2 * 28.346
# In VectorCraft stream: Y is negative, so pt was 1417.323 + ym * 28.346
min_y_pt = 1417.323 - 4.5 * 28.346
max_y_pt = 1417.323 + 1.0 * 28.346

print(f"Stair 1 crop box (pt): X=[{min_x_pt:.1f}, {max_x_pt:.1f}], Y=[{min_y_pt:.1f}, {max_y_pt:.1f}]")

crops = []
for p in pdf_list:
    path = os.path.join(r'c:\Coding Projects\Digital Twin', p)
    if not os.path.exists(path):
        continue
    doc = pdfium.PdfDocument(path)
    bm = doc[0].render(scale=4)
    img = bm.to_pil()
    box = (int(min_x_pt * 4), int(min_y_pt * 4), int(max_x_pt * 4), int(max_y_pt * 4))
    crop = img.crop(box)
    fname = f"stair1_{p.replace('.pdf', '')}.png"
    crop.save(os.path.join(out_dir, fname))
    crops.append((p.replace('.pdf', ''), crop))
    print(f"Saved {fname}")

# Combine into a 4-floor comparison board!
if crops:
    w, h = crops[0][1].size
    board = Image.new('RGB', (w * len(crops) + 20 * (len(crops) + 1), h + 80), (255, 255, 255))
    draw = ImageDraw.Draw(board)
    draw.rectangle([(0, 0), (board.width, 60)], fill=(15, 23, 42))
    
    for i, (name, c) in enumerate(crops):
        x_pos = 20 + i * (w + 20)
        board.paste(c, (x_pos, 70))
        draw.text((x_pos + 10, 20), f"FLOOR: {name}", fill=(255, 255, 255))
    
    board.save(os.path.join(out_dir, 'stair1_all_floors_comparison.png'))
    print("Saved stair1_all_floors_comparison.png")


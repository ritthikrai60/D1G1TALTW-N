import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont
import os

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

# Let's create high quality annotated crops for both stairs
doc0 = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf')
doc1 = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf')

bm0 = doc0[0].render(scale=5)
img0 = bm0.to_pil()

bm1 = doc1[0].render(scale=5)
img1 = bm1.to_pil()

# Core stair bounds: pt [1210, 1740, 1310, 1890]
box_c = (int(1210 * 5), int(1730 * 5), int(1315 * 5), int(1890 * 5))
c0 = img0.crop(box_c)
c1 = img1.crop(box_c)

# South stair bounds: pt [1050, 1950, 1260, 2120]
box_s = (int(1050 * 5), int(1940 * 5), int(1270 * 5), int(2120 * 5))
s0 = img0.crop(box_s)
s1 = img1.crop(box_s)

# Combine into side-by-side comparison boards:
# 1. Core Stair Comparison: Ground Floor vs First Floor
w, h = c0.size
board_core = Image.new('RGB', (w * 2 + 40, h + 100), (255, 255, 255))
board_core.paste(c0, (10, 80))
board_core.paste(c1, (w + 30, 80))

draw = ImageDraw.Draw(board_core)
# Add titles
draw.rectangle([(0, 0), (board_core.width, 70)], fill=(30, 41, 59))
draw.text((30, 20), "GROUND FLOOR (Basement): Core Stair", fill=(255, 255, 255))
draw.text((w + 50, 20), "FIRST FLOOR: Core Stair (Arrival & Spiral Stair above)", fill=(255, 255, 255))

board_core.save(os.path.join(out_dir, 'stair_core_side_by_side_forensic.png'))

# 2. South Stair Comparison: Ground Floor vs First Floor
ws, hs = s0.size
board_south = Image.new('RGB', (ws * 2 + 40, hs + 100), (255, 255, 255))
board_south.paste(s0, (10, 80))
board_south.paste(s1, (ws + 30, 80))

draw_s = ImageDraw.Draw(board_south)
draw_s.rectangle([(0, 0), (board_south.width, 70)], fill=(30, 41, 59))
draw_s.text((30, 20), "GROUND FLOOR (Basement): South Stair & Corridor", fill=(255, 255, 255))
draw_s.text((ws + 50, 20), "FIRST FLOOR: South Stair arrives at Outdoor Terrace", fill=(255, 255, 255))

board_south.save(os.path.join(out_dir, 'stair_south_side_by_side_forensic.png'))
print("Saved forensic side-by-side boards")


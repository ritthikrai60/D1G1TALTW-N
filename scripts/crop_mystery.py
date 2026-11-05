import pypdfium2 as pdfium
from PIL import Image
import os

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
doc = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf')
bm = doc[0].render(scale=5)
img = bm.to_pil()

# X in [0.0, 6.0], Y in [-5.0, 2.0]
# pt: x_pt = 1133.858 + xm * 28.346
# pt: y_pt = 1417.323 + ym * 28.346
min_x_pt = 1133.858 + 0.0 * 28.346
max_x_pt = 1133.858 + 6.0 * 28.346
min_y_pt = 1417.323 - 5.0 * 28.346
max_y_pt = 1417.323 + 2.0 * 28.346

box = (int(min_x_pt * 5), int(min_y_pt * 5), int(max_x_pt * 5), int(max_y_pt * 5))
crop = img.crop(box)
crop.save(os.path.join(out_dir, 'mystery_stair_p2.png'))
print(f"Saved mystery_stair_p2.png: {crop.size}")


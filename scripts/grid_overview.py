import pypdfium2 as pdfium
from PIL import Image
import os

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
doc = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf')
bm = doc[0].render(scale=2)
img = bm.to_pil()
w, h = img.size
print("Size at scale 2:", w, h)

# Let's save a grid of 3x3 crops covering the entire building
cols = 3
rows = 3
cw = w // cols
ch = h // rows

for r in range(rows):
    for c in range(cols):
        box = (c * cw, r * ch, (c + 1) * cw, (r + 1) * ch)
        crop = img.crop(box)
        crop.save(os.path.join(out_dir, f'grid_r{r}_c{c}.png'))

print("Saved 3x3 grid overview")


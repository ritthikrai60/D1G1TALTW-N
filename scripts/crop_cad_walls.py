import pypdfium2 as pdfium
from PIL import Image, ImageDraw
import os

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
doc = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf')

# Render CAD at scale 3
bm = doc[0].render(scale=3)
cad_img = bm.to_pil()

# Crop the core and north wing areas
# pt X in [1000, 1500], Y in [1100, 2000]
box_core = (int(1000 * 3), int(1100 * 3), int(1500 * 3), int(2000 * 3))
cad_core = cad_img.crop(box_core)
cad_core.save(os.path.join(out_dir, 'cad_core_walls_detail.png'))
print(f"Saved cad_core_walls_detail.png: {cad_core.size}")


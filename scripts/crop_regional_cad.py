import pypdfium2 as pdfium
from PIL import Image
import os

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
doc = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf')
bm = doc[0].render(scale=3)
img = bm.to_pil()

# Crop West wing: X in [200, 1000], Y in [1000, 1800]
crop_west = img.crop((int(200 * 3), int(1000 * 3), int(1100 * 3), int(1800 * 3)))
crop_west.save(os.path.join(out_dir, 'cad_west_wing.png'))

# Crop North wing: X in [800, 1800], Y in [500, 1300]
crop_north = img.crop((int(800 * 3), int(500 * 3), int(1800 * 3), int(1300 * 3)))
crop_north.save(os.path.join(out_dir, 'cad_north_wing.png'))

# Crop East wing: X in [1400, 2600], Y in [1000, 2000]
crop_east = img.crop((int(1400 * 3), int(1000 * 3), int(2600 * 3), int(2000 * 3)))
crop_east.save(os.path.join(out_dir, 'cad_east_wing.png'))

print("Saved regional CAD crops")


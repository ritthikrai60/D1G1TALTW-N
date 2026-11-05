import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont
import os

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

doc0 = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf')
doc1 = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf')

# Render at scale 6 (approx 432 DPI) for super high definition inspection!
bm0 = doc0[0].render(scale=6)
img0 = bm0.to_pil()

bm1 = doc1[0].render(scale=6)
img1 = bm1.to_pil()

# Core stair pt bounds in doc: [1225, 1748, 1301, 1873]
# At scale 6:
pad = 60
box_core = (int((1220 - pad) * 6), int((1740 - pad) * 6), int((1310 + pad) * 6), int((1880 + pad) * 6))

crop0 = img0.crop(box_core)
crop1 = img1.crop(box_core)

crop0.save(os.path.join(out_dir, 'core_stair_ground_hd.png'))
crop1.save(os.path.join(out_dir, 'core_stair_first_hd.png'))
print("Saved HD crops:", crop0.size, crop1.size)


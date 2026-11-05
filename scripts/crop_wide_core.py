import pypdfium2 as pdfium
from PIL import Image
import os

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

# Let's inspect the entire core area of Ground Floor and First Floor
# Let's crop a wider area around the core: including the elevator, corridors, doors, labels
doc0 = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf')
doc1 = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf')

bm0 = doc0[0].render(scale=4)
img0 = bm0.to_pil()

bm1 = doc1[0].render(scale=4)
img1 = bm1.to_pil()

# Let's crop a wide area: X in [1100, 1500], Y in [1500, 2000] at scale 4
box_wide = (int(1100 * 4), int(1500 * 4), int(1500 * 4), int(2000 * 4))

crop0_wide = img0.crop(box_wide)
crop1_wide = img1.crop(box_wide)

crop0_wide.save(os.path.join(out_dir, 'ground_floor_core_wide.png'))
crop1_wide.save(os.path.join(out_dir, 'first_floor_core_wide.png'))
print("Saved wide crops")


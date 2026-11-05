import pypdfium2 as pdfium
from PIL import Image
import os

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
doc = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf')
bm = doc[0].render(scale=4)
img = bm.to_pil()

# X in [-3, 14] m -> Xpt in [900, 1400]
# Y in [18, 45] m -> Yvc in [220, 1050]
crop_box = (int(900 * 4), int(220 * 4), int(1400 * 4), int(1050 * 4))
crop_img = img.crop(crop_box)
crop_img.save(os.path.join(out_dir, 'cad_north_parking_room_complex_hd.png'))

# Also let's crop with wider view including parking stalls 1 to 14
# X in [-5, 25] m -> Xpt in [850, 1750]
# Y in [10, 45] m -> Yvc in [220, 1250]
crop_box_wide = (int(850 * 4), int(220 * 4), int(1750 * 4), int(1250 * 4))
crop_img_wide = img.crop(crop_box_wide)
crop_img_wide.save(os.path.join(out_dir, 'cad_north_parking_room_complex_wide.png'))

print("Saved HD CAD crops of north parking room complex!")


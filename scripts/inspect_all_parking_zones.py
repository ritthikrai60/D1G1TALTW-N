import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import pypdfium2 as pdfium
from PIL import Image
import os

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Let's inspect where parking numbers are located
print("Inspecting parking stalls and surrounding rooms...")

# Render high-resolution crops around all parking areas:
pdf_doc = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf')
bm = pdf_doc[0].render(scale=3)
img = bm.to_pil()
out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

# 1. Zone behind North Parking (Stalls 1-12)
# pt: X in [800, 1500], Y in [400, 1200]
crop_north_parking = img.crop((int(800 * 3), int(300 * 3), int(1600 * 3), int(1200 * 3)))
crop_north_parking.save(os.path.join(out_dir, 'inspect_behind_north_parking.png'))

# 2. Zone behind West Parking (Stalls 13-14, 15-20)
# pt: X in [300, 1100], Y in [1100, 1900]
crop_west_parking = img.crop((int(300 * 3), int(1100 * 3), int(1100 * 3), int(1900 * 3)))
crop_west_parking.save(os.path.join(out_dir, 'inspect_behind_west_parking.png'))

# 3. Zone behind South Parking (Stalls 23-30)
# pt: X in [300, 1100], Y in [1800, 2300]
crop_south_parking = img.crop((int(300 * 3), int(1800 * 3), int(1100 * 3), int(2350 * 3)))
crop_south_parking.save(os.path.join(out_dir, 'inspect_behind_south_parking.png'))

# 4. Far North edge of the building
crop_far_north = img.crop((int(500 * 3), int(100 * 3), int(1800 * 3), int(700 * 3)))
crop_far_north.save(os.path.join(out_dir, 'inspect_far_north.png'))

print("Saved inspection crops for all parking zones")


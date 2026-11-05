import pypdfium2 as pdfium
from PIL import Image
import os

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
doc = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf')
bm = doc[0].render(scale=3)
img = bm.to_pil()

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567

def crop_meters(xmin, ymin, xmax, ymax, filename):
    # VectorCraft: xc = X0 + xm * SCALE, yc = Y0 - ym * SCALE
    # In PIL (rendered at scale 3):
    left = int((X0 + xmin * SCALE) * 3)
    right = int((X0 + xmax * SCALE) * 3)
    # ymin in meters has higher yc:
    top = int((Y0 - ymax * SCALE) * 3)
    bottom = int((Y0 - ymin * SCALE) * 3)
    
    # clamp
    left = max(0, min(img.width, left))
    right = max(0, min(img.width, right))
    top = max(0, min(img.height, top))
    bottom = max(0, min(img.height, bottom))
    
    crop = img.crop((left, top, right, bottom))
    crop.save(os.path.join(out_dir, filename))
    print(f"Saved {filename}: {crop.size}")

# 1. South-West corner (around Col 02)
crop_meters(-28.0, -18.0, -15.0, -5.0, "cad_sw_col02_perimeter.png")

# 2. South-East diagonal columns (Cols 56, 57, 58, 61)
crop_meters(15.0, -15.0, 65.0, 5.0, "cad_se_diagonal_perimeter.png")

# 3. Far East wing (around Cols 18, 19, 20, 21, 24)
crop_meters(45.0, 5.0, 70.0, 25.0, "cad_east_wing_perimeter.png")

# 4. Far North perimeter
crop_meters(-28.0, 35.0, 35.0, 48.0, "cad_north_boundary_perimeter.png")


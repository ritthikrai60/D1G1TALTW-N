import pypdfium2 as pdfium
from PIL import Image
import os
import json

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
full_img_path = os.path.join(out_dir, 'pdfium_ground_floor_full.png')
img = Image.open(full_img_path)
W, H = img.size

# In PDF coordinates: width=3370, height=2384
# In VectorCraft stream: we had affine transform:
# x_pt = 1133.858 + x_m * 28.346456692913385
# y_pt = 2384 - (1417.323 + y_m * 28.346456692913385)  (assuming standard PDF origin bottom-left vs top-left)
# Let's inspect where core stair and south stair are in PDF pt:

def to_pixel(x_pt, y_pt):
    # PDF coordinates usually (0,0) at bottom-left or top-left depending on renderer
    # In pypdfium, (0,0) is top-left in the rendered PIL image!
    # In PDF spec, y=0 is bottom-left, so y_pix = (2384 - y_pt) * (H / 2384) = (2384 - y_pt) * 3
    # Let's check both or verify
    pass

# Let's find out how pypdfium maps PDF coordinates to image coordinates
# VectorCraft:
# x_origin_m = (pt - 1133.858) / 28.346456692913385
# Let's inspect the actual bbox of drawing elements in the image by finding non-white regions
print("Image size:", W, H)

# Let's crop candidate regions around the center
# Core area in meter coordinates: X around 8 to 14, Y around -15 to -6
# In pt: X = 1133.858 + 10 * 28.346 = 1417 pt -> at scale 3: X_pix = 1417 * 3 = 4251
# Y_pt: let's verify if Y is inverted
# In PDF: Y_pt was around 1100 to 1400.
# At scale 3: Y_pix could be around (2384 - 1300) * 3 = 3250 or 1300 * 3 = 3900.
# Let's crop a 2000x2000 box around (4250, 3500)

crop_core = img.crop((3800, 2800, 5200, 4200))
crop_core.save(os.path.join(out_dir, 'pdfium_crop_test_core.png'))
print("Saved pdfium_crop_test_core.png")


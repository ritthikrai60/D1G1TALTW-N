import pypdfium2 as pdfium
from PIL import Image

pdf = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf')
page = pdf[0]
img = page.render(scale=3.0).to_pil() # 3x scale

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def m_to_px(xm, ym):
    pt_x = X0 + xm * SCALE
    pt_y = Y0 - ym * SCALE
    return int(pt_x * 3.0), int(pt_y * 3.0)

art_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

# 4 columns (X: -30 to 70), 3 rows (Y: -25 to 50)
x_slices = [
    (-30.0, -5.0, "col1_west"),
    (-5.0, 20.0, "col2_center_west"),
    (20.0, 45.0, "col3_center_east"),
    (45.0, 70.0, "col4_east")
]

y_slices = [
    (20.0, 50.0, "row1_north"),
    (-5.0, 25.0, "row2_mid"),
    (-25.0, 0.0, "row3_south")
]

grid_crops = []
for y1, y2, yname in y_slices:
    for x1, x2, xname in x_slices:
        out_name = f"scan_{yname}_{xname}.png"
        px1, py1 = m_to_px(x1, y2)
        px2, py2 = m_to_px(x2, y1)
        l, r = min(px1, px2), max(px1, px2)
        t, b = min(py1, py2), max(py1, py2)
        # clamp to image bounds
        l, t = max(0, l), max(0, t)
        r, b = min(img.width, r), min(img.height, b)
        crop = img.crop((l, t, r, b))
        crop.save(f"{art_dir}\\{out_name}")
        grid_crops.append(out_name)
        print(f"Saved {out_name}: {crop.size}")

print(f"Total grid crops: {len(grid_crops)}")


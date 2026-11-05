import pypdfium2 as pdfium
from PIL import Image

pdf0 = pdfium.PdfDocument('00-Ground_Floor-Clean.pdf')
page0 = pdf0[0]
img0 = page0.render(scale=3.0).to_pil()

pdf1 = pdfium.PdfDocument('01-First_Floor-Clean.pdf')
page1 = pdf1[0]
img1 = page1.render(scale=3.0).to_pil()

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def m_to_px(xm, ym):
    pt_x = X0 + xm * SCALE
    pt_y = Y0 - ym * SCALE
    return int(pt_x * 3.0), int(pt_y * 3.0)

art_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

# Compare the exact same stairwell on F00 and F01:
# Core Stair (X: 7 to 13, Y: -15 to -6)
for fl_name, img in [('f00', img0), ('f01', img1)]:
    px1, py1 = m_to_px(7.0, -6.0)
    px2, py2 = m_to_px(13.0, -15.0)
    left, right = min(px1, px2), max(px1, px2)
    top, bottom = min(py1, py2), max(py1, py2)
    crop = img.crop((left, top, right, bottom))
    crop.save(f"{art_dir}\\{fl_name}_core_stair_compare.png")
    print(f"Saved {fl_name}_core_stair_compare.png")

# Compare the spiral/rotunda lobby area (X: 15 to 27, Y: -8 to 4)
for fl_name, img in [('f00', img0), ('f01', img1)]:
    px1, py1 = m_to_px(15.0, 4.0)
    px2, py2 = m_to_px(27.0, -8.0)
    left, right = min(px1, px2), max(px1, px2)
    top, bottom = min(py1, py2), max(py1, py2)
    crop = img.crop((left, top, right, bottom))
    crop.save(f"{art_dir}\\{fl_name}_lobby_compare.png")
    print(f"Saved {fl_name}_lobby_compare.png")


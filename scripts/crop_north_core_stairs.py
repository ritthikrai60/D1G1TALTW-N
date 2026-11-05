import pypdfium2 as pdfium
from PIL import Image

art_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def m_to_px(xm, ym):
    pt_x = X0 + xm * SCALE
    pt_y = Y0 - ym * SCALE
    return int(pt_x * 3.0), int(pt_y * 3.0)

for fl_idx, fn in [(0, '00-Ground_Floor-Model.pdf'), (1, '01-First_Floor-Model.pdf'), (2, '02-Second_Floor-Model.pdf')]:
    pdf = pdfium.PdfDocument(f'C:\\Users\\ritth\\Downloads\\Telegram Desktop\\{fn}')
    img = pdf[0].render(scale=3.0).to_pil()
    # Crop the shaft above the rotunda (X: 5 to 13, Y: 1 to 11)
    px1, py1 = m_to_px(5.0, 11.0)
    px2, py2 = m_to_px(13.0, 1.0)
    left, right = min(px1, px2), max(px1, px2)
    top, bottom = min(py1, py2), max(py1, py2)
    crop = img.crop((left, top, right, bottom))
    crop.save(f"{art_dir}\\f{fl_idx:02d}_north_core_stair.png")
    print(f"Saved f{fl_idx:02d}_north_core_stair.png")


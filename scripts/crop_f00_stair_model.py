import pypdfium2 as pdfium
from PIL import Image

pdf0 = pdfium.PdfDocument(r'C:\Users\ritth\Downloads\Telegram Desktop\00-Ground_Floor-Model.pdf')
page0 = pdf0[0]
img0 = page0.render(scale=3.0).to_pil()

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def m_to_px(xm, ym):
    pt_x = X0 + xm * SCALE
    pt_y = Y0 - ym * SCALE
    return int(pt_x * 3.0), int(pt_y * 3.0)

art_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

crops0 = {
    'f00_stair_core.png': (5.0, -16.0, 15.0, -4.0),
    'f00_stair_foyer.png': (5.0, -6.0, 22.0, 10.0),
    'f00_stair_south.png': (0.0, -25.0, 12.0, -14.0),
    'f00_stair_east.png': (48.0, 4.0, 66.0, 20.0),
    'f00_stair_west.png': (-26.0, -16.0, -12.0, 10.0)
}

for name, (x1, y1, x2, y2) in crops0.items():
    px1, py1 = m_to_px(x1, y2)
    px2, py2 = m_to_px(x2, y1)
    left, right = min(px1, px2), max(px1, px2)
    top, bottom = min(py1, py2), max(py1, py2)
    crop = img0.crop((left, top, right, bottom))
    crop.save(f"{art_dir}\\{name}")
    print(f"Saved {name}: size={crop.size}")


import pypdfium2 as pdfium
from PIL import Image

pdf2 = pdfium.PdfDocument(r'C:\Users\ritth\Downloads\Telegram Desktop\02-Second_Floor-Model.pdf')
page2 = pdf2[0]
img2 = page2.render(scale=3.0).to_pil()

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def m_to_px(xm, ym):
    pt_x = X0 + xm * SCALE
    pt_y = Y0 - ym * SCALE
    return int(pt_x * 3.0), int(pt_y * 3.0)

art_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

px1, py1 = m_to_px(5.0, -4.0)
px2, py2 = m_to_px(15.0, -16.0)
left, right = min(px1, px2), max(px1, px2)
top, bottom = min(py1, py2), max(py1, py2)
crop = img2.crop((left, top, right, bottom))
crop.save(f"{art_dir}\\f02_stair_core.png")
print("Saved f02_stair_core.png")


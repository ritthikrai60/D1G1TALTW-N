import pypdfium2 as pdfium
from PIL import Image

art_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def m_to_px(xm, ym):
    pt_x = X0 + xm * SCALE
    pt_y = Y0 - ym * SCALE
    return int(pt_x * 4.0), int(pt_y * 4.0)

pdf1 = pdfium.PdfDocument(r'C:\Users\ritth\Downloads\Telegram Desktop\01-First_Floor-Model.pdf')
img1 = pdf1[0].render(scale=4.0).to_pil()

# Crop arena grandstand stairs (X: -15 to 0, Y: 22 to 38)
px1, py1 = m_to_px(-15.0, 38.0)
px2, py2 = m_to_px(0.0, 22.0)
crop = img1.crop((min(px1, px2), min(py1, py2), max(px1, px2), max(py1, py2)))
crop.save(f"{art_dir}\\zoom_f01_sports_stair.png")
print("Saved zoom_f01_sports_stair.png")


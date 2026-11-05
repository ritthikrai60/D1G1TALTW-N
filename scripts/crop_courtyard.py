import pypdfium2 as pdfium
from PIL import Image

pdf = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf')
page = pdf[0]
bitmap = page.render(scale=2.0)
img = bitmap.to_pil()

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def m_to_px(xm, ym):
    pt_x = X0 + xm * SCALE
    pt_y = Y0 - ym * SCALE
    return int(pt_x * 2.0), int(pt_y * 2.0)

# Crop north central courtyard
px1, py1 = m_to_px(10, 35)
px2, py2 = m_to_px(45, 5)
cropped = img.crop((min(px1, px2), min(py1, py2), max(px1, px2), max(py1, py2)))
cropped.save(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_crop_courtyard.png')
print("Saved f01_crop_courtyard.png")


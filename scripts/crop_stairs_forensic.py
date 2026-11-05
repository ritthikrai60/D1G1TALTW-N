import pypdfium2 as pdfium
from PIL import Image

pdf = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf')
page = pdf[0]
bitmap = page.render(scale=3.0) # ultra high res 3x
img = bitmap.to_pil()

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def m_to_px(xm, ym):
    pt_x = X0 + xm * SCALE
    pt_y = Y0 - ym * SCALE
    return int(pt_x * 3.0), int(pt_y * 3.0)

art_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

# Crops for forensic stair inspection:
# 1. Grand Spiral Stair in lobby (ultra close-up)
crops = {
    'stair_forensic_spiral.png': (20.5, -6.0, 25.0, -2.5),
    'stair_forensic_st1_core.png': (7.5, -14.0, 12.5, -6.5),
    'stair_forensic_st2_south.png': (1.5, -22.5, 10.0, -15.5),
    'stair_forensic_east_wing.png': (53.0, 7.0, 63.0, 17.0),
    'stair_forensic_lobby_wide.png': (15.0, -10.0, 30.0, 5.0),
}

for name, (x1, y1, x2, y2) in crops.items():
    px1, py1 = m_to_px(x1, y2)
    px2, py2 = m_to_px(x2, y1)
    left = min(px1, px2)
    right = max(px1, px2)
    top = min(py1, py2)
    bottom = max(py1, py2)
    cropped = img.crop((left, top, right, bottom))
    cropped.save(f"{art_dir}\\{name}")
    print(f"Saved {name}: size={cropped.size}")


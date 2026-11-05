import pypdfium2 as pdfium
from PIL import Image

pdf = pdfium.PdfDocument(r'C:\Users\ritth\Downloads\Telegram Desktop\01-First_Floor-Model.pdf')
page = pdf[0]
img = page.render(scale=3.0).to_pil() # 3x ultra-res

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def m_to_px(xm, ym):
    pt_x = X0 + xm * SCALE
    pt_y = Y0 - ym * SCALE
    return int(pt_x * 3.0), int(pt_y * 3.0)

art_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

# Crops for all possible stair locations across Floor 01:
crops = {
    'stair_model_st1_core.png': (5.0, -16.0, 15.0, -4.0),
    'stair_model_lobby_spiral.png': (18.0, -9.0, 28.0, 1.0),
    'stair_model_foyer_fan.png': (13.0, -4.0, 26.0, 9.0),
    'stair_model_south_portico.png': (0.0, -25.0, 12.0, -14.0),
    'stair_model_east_wing.png': (48.0, 4.0, 66.0, 20.0),
    'stair_model_west_wing.png': (-26.0, -16.0, -12.0, 10.0),
    'stair_model_north_terrace.png': (-25.0, 20.0, 35.0, 46.0),
    'stair_model_center_foyer.png': (5.0, -6.0, 22.0, 10.0)
}

for name, (x1, y1, x2, y2) in crops.items():
    px1, py1 = m_to_px(x1, y2)
    px2, py2 = m_to_px(x2, y1)
    left, right = min(px1, px2), max(px1, px2)
    top, bottom = min(py1, py2), max(py1, py2)
    crop = img.crop((left, top, right, bottom))
    crop.save(f"{art_dir}\\{name}")
    print(f"Saved {name}: size={crop.size}")


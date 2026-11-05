import pypdfium2 as pdfium
from PIL import Image

pdf = pdfium.PdfDocument('01-First_Floor-Clean.pdf')
page = pdf[0]
img = page.render(scale=3.0).to_pil()

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def m_to_px(xm, ym):
    pt_x = X0 + xm * SCALE
    pt_y = Y0 - ym * SCALE
    return int(pt_x * 3.0), int(pt_y * 3.0)

art_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

crops = {
    'audit_st1_core.png': (6.5, -15.5, 13.5, -5.5),
    'audit_spiral_lobby.png': (19.0, -8.0, 27.0, 0.0),
    'audit_fan_rotunda.png': (14.0, -3.0, 26.0, 9.0),
    'audit_st2_south.png': (0.0, -24.0, 11.0, -14.0),
    'audit_east_wing.png': (51.0, 5.0, 65.0, 19.0),
    'audit_north_terrace_west.png': (-24.0, 22.0, -5.0, 38.0),
    'audit_north_terrace_center.png': (-5.0, 22.0, 15.0, 38.0),
    'audit_north_terrace_east.png': (15.0, 22.0, 35.0, 38.0),
    'audit_west_entrance.png': (-26.0, -5.0, -18.0, 8.0)
}

for name, (x1, y1, x2, y2) in crops.items():
    px1, py1 = m_to_px(x1, y2)
    px2, py2 = m_to_px(x2, y1)
    left, right = min(px1, px2), max(px1, px2)
    top, bottom = min(py1, py2), max(py1, py2)
    cropped = img.crop((left, top, right, bottom))
    cropped.save(f"{art_dir}\\{name}")
    print(f"Saved {name}: size={cropped.size}")


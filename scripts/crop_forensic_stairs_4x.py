import pypdfium2 as pdfium
from PIL import Image

art_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def m_to_px(xm, ym):
    pt_x = X0 + xm * SCALE
    pt_y = Y0 - ym * SCALE
    return int(pt_x * 4.0), int(pt_y * 4.0) # 4x scale for forensic zoom

# Load 01-First_Floor-Model.pdf at 4x
pdf1 = pdfium.PdfDocument(r'C:\Users\ritth\Downloads\Telegram Desktop\01-First_Floor-Model.pdf')
img1 = pdf1[0].render(scale=4.0).to_pil()

# Load 00-Ground_Floor-Model.pdf at 4x
pdf0 = pdfium.PdfDocument(r'C:\Users\ritth\Downloads\Telegram Desktop\00-Ground_Floor-Model.pdf')
img0 = pdf0[0].render(scale=4.0).to_pil()

def crop_box(img, x1, y1, x2, y2, out_name):
    px1, py1 = m_to_px(x1, y2)
    px2, py2 = m_to_px(x2, y1)
    l, r = min(px1, px2), max(px1, px2)
    t, b = min(py1, py2), max(py1, py2)
    c = img.crop((l, t, r, b))
    c.save(f"{art_dir}\\{out_name}")
    print(f"Saved {out_name}: {c.size}")

# 1. Stair 3 (North Core Stair) on F00 and F01
crop_box(img0, 5.5, 2.0, 11.0, 10.5, "zoom_f00_stair3.png")
crop_box(img1, 5.5, 2.0, 11.0, 10.5, "zoom_f01_stair3.png")

# 2. Stair 1 / ST-2 (South Core Stair) on F00 and F01
crop_box(img0, 6.5, -15.5, 12.5, -7.5, "zoom_f00_stair1.png")
crop_box(img1, 6.5, -15.5, 12.5, -7.5, "zoom_f01_stair1.png")

# 3. Foyer Fan Steps on F01
crop_box(img1, 14.5, -2.5, 25.0, 6.5, "zoom_f01_fan_stair.png")

# 4. Lobby Spiral Stair on F01
crop_box(img1, 19.5, -7.5, 26.5, -0.5, "zoom_f01_spiral_stair.png")

# 5. South Portico Entrance Steps on F01 and F00
crop_box(img0, 1.0, -23.5, 12.0, -16.0, "zoom_f00_south_portico.png")
crop_box(img1, 1.0, -23.5, 12.0, -16.0, "zoom_f01_south_portico.png")

# 6. West Arena Grand Steps on F01
crop_box(img1, -22.0, 16.0, -14.0, 24.0, "zoom_f01_west_arena.png")

# 7. East Wing Kitchen Steps on F01
crop_box(img1, 52.0, 6.0, 65.0, 16.0, "zoom_f01_east_wing.png")


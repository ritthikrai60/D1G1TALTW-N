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

crops = {
    'f01_crop_lobby.png': (12, -15, 45, 10),
    'f01_crop_core_stair_st1.png': (6, -15, 14, -5),
    'f01_crop_south_stair_st2.png': (0, -24, 12, -14),
    'f01_crop_east_curved_wing.png': (40, 0, 75, 25),
    'f01_crop_west_wing.png': (-26, -15, 5, 10),
}

art_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

for name, (x1m, y1m, x2m, y2m) in crops.items():
    px1, py1 = m_to_px(x1m, y2m) # note y is inverted
    px2, py2 = m_to_px(x2m, y1m)
    left = min(px1, px2)
    right = max(px1, px2)
    top = min(py1, py2)
    bottom = max(py1, py2)
    cropped = img.crop((left, top, right, bottom))
    out_path = f"{art_dir}\\{name}"
    cropped.save(out_path)
    print(f"Saved {name}: bounds=({left},{top},{right},{bottom}), size={cropped.size}")


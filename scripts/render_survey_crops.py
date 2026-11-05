import pypdfium2 as pdfium
from PIL import Image

pdf01 = pdfium.PdfDocument(r'C:\Users\ritth\Downloads\Telegram Desktop\01-First_Floor-Model.pdf')
page01 = pdf01[0]
scale = 2.0
img01 = page01.render(scale=scale).to_pil()
w, h = img01.size

crops = [
    ("f01_west_gym_all", -15.0, 30.0, 30.0),
    ("f01_east_wing_all", 55.0, 15.0, 30.0),
    ("f01_lobby_center", 15.0, -5.0, 25.0),
    ("f01_south_entrance", 5.0, -15.0, 25.0),
    ("f01_center_core", 10.0, 10.0, 25.0),
    ("f01_north_area", 10.0, 35.0, 25.0),
    ("f01_far_east_terrace", 65.0, 5.0, 20.0),
]

for name, xm, ym, span in crops:
    pt_x = 1000.0 + 28.3464567 * xm
    pt_y = 1500.0 - 28.3464567 * ym
    px = pt_x * scale
    py = pt_y * scale
    r = (span * 28.3464567 / 2.0) * scale
    box = (int(px - r), int(py - r), int(px + r), int(py + r))
    box = (max(0, box[0]), max(0, box[1]), min(w, box[2]), min(h, box[3]))
    crop = img01.crop(box)
    out_path = f"C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/survey_{name}.png"
    crop.save(out_path)
    print(f"Saved {name}: {crop.size}")


import pypdfium2 as pdfium
from PIL import Image

pdf00 = pdfium.PdfDocument(r'C:\Users\ritth\Downloads\Telegram Desktop\00-Ground_Floor-Model.pdf')
page00 = pdf00[0]
scale = 2.0
img00 = page00.render(scale=scale).to_pil()
w, h = img00.size

locations = [
    ("f00_stair3_at_7_5", 7.6, 5.0, 10.0),
    ("f00_stair1_at_10_neg10", 9.8, -10.5, 10.0),
    ("f00_portico_at_6_neg19", 6.0, -19.0, 12.0),
    ("f00_spiral_at_11_neg2", 11.0, -2.0, 10.0),
    ("f00_sw_locker_area", -10.0, -10.0, 15.0),
]

for name, xm, ym, span in locations:
    pt_x = 1000.0 + 28.3464567 * xm
    pt_y = 1500.0 - 28.3464567 * ym
    px = pt_x * scale
    py = pt_y * scale
    r = (span * 28.3464567 / 2.0) * scale
    box = (int(px - r), int(py - r), int(px + r), int(py + r))
    box = (max(0, box[0]), max(0, box[1]), min(w, box[2]), min(h, box[3]))
    crop = img00.crop(box)
    out_path = f"C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/audit_{name}.png"
    crop.save(out_path)
    print(f"Saved {name}: {crop.size}")


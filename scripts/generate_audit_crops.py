import pypdfium2 as pdfium
from PIL import Image

pdf = pdfium.PdfDocument(r'C:\Users\ritth\Downloads\Telegram Desktop\01-First_Floor-Model.pdf')
page = pdf[0]
size = page.get_size()
print("Page size:", size)

# Render at scale 2.0 (span 6740 x 4768)
scale = 2.0
img = page.render(scale=scale).to_pil()
w, h = img.size
print(f"Rendered: {w} x {h}")

# In PDF, (0,0) is bottom-left or top-left depending on convention,
# but in pdfium render, image top-left (0,0) corresponds to PDF (rect[0], rect[3]).
# Let's verify by locating known grid lines or elements.
# In VectorCraft:
# X_cad, Y_cad where (1000, 1500) is (0m, 0m).
# SCALE = 28.3464567 pt/meter (which is 72 dpi / 2.54 cm).
# So in PDF points:
# pt_x = 1000.0 + 28.3464567 * xm
# pt_y = 1500.0 - 28.3464567 * ym  (or 1500 from top)

# Let's crop several key locations to confirm the exact mapping:
locations = [
    ("stair_cluster2_at_7_5", 7.6, 5.0, 10.0),
    ("stair_cluster1_at_32_25", 32.2, 25.8, 10.0),
    ("stair1_locker_at_10_neg10", 9.8, -10.5, 10.0),
    ("portico_at_6_neg19", 6.0, -19.0, 12.0),
    ("spiral_at_11_neg2", 11.0, -2.0, 10.0),
    ("east_stair_at_53_18", 53.5, 18.0, 10.0),
    ("gym_at_neg17_40", -16.0, 40.0, 12.0)
]

for name, xm, ym, span in locations:
    # Let's calculate pt_x, pt_y
    # In PDF points:
    # Since pt = (px - X0)/28.3464567
    pt_x = 1000.0 + 28.3464567 * xm
    pt_y = 1500.0 - 28.3464567 * ym
    # Convert to image pixels at scale 2.0:
    # If PDF origin (0,0) is at top-left:
    px = pt_x * scale
    py = pt_y * scale
    r = (span * 28.3464567 / 2.0) * scale
    box = (int(px - r), int(py - r), int(px + r), int(py + r))
    # Clip box
    box = (max(0, box[0]), max(0, box[1]), min(w, box[2]), min(h, box[3]))
    crop = img.crop(box)
    out_path = f"C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/audit_{name}.png"
    crop.save(out_path)
    print(f"Saved {name}: {crop.size} to {out_path}")

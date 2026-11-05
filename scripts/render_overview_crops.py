import pypdfium2 as pdfium
from PIL import Image

pdf = pdfium.PdfDocument(r'C:\Users\ritth\Downloads\Telegram Desktop\01-First_Floor-Model.pdf')
page = pdf[0]
# Render at scale 3 (approx 10,000 x 7,000)
full_img = page.render(scale=3.0).to_pil()
w, h = full_img.size
print(f"Full image rendered: {w} x {h}")

# The coordinate mapping from meter space (X, Y) to image pixels (px, py):
# Let's find the bounding box of the building on the page
# Let's save a thumbnail to inspect
thumb = full_img.resize((1200, int(1200 * h / w)))
thumb.save(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_overview_thumb.png')
print("Saved overview thumb")


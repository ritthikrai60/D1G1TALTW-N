import pypdfium2 as pdfium
from PIL import Image

pdf = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf')
page = pdf[0]
# Render at scale 2 (approx 150-200 dpi)
bitmap = page.render(scale=2.0)
pil_image = bitmap.to_pil()
w, h = pil_image.size
print(f"Rendered Floor 01: size={w}x{h}")

pil_image.save(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_highres_overview.png')

# Let's crop central lobby area:
# In PDF coords: X0=1000, Y0=1500, Scale=28.346
# In pixel coords: pixel_x = pt_x * 2.0
# The building center is around X_m=25 to 35 -> pt_x = 1000 + 30*28.35 = 1850 -> px = 3700
# Let's crop several key sections
# Let's find the bounding box of building content in pixels
print("Saved f01_highres_overview.png")


import fitz # PyMuPDF
import os

pdf_path = r'C:\Users\ritth\Downloads\Telegram Desktop\01-First_Floor-Model.pdf'
doc = fitz.open(pdf_path)
page = doc[0]

# CAD coordinates to PDF page points
# In our formula:
# pt_m = ((pt_cad - 1000.0) / 28.3464567, -(pt_cad - 1500.0) / 28.3464567)
# Let's check page.rect
print("Page rect:", page.rect)

# We can render the entire page at high DPI or crop
pix = page.get_pixmap(dpi=150)
out_png = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_model_full.png'
pix.save(out_png)
print("Saved full page pixmap:", pix.width, pix.height)


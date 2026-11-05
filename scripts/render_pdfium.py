import pypdfium2 as pdfium
import os

pdf_path = r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf'
pdf = pdfium.PdfDocument(pdf_path)
print(f"Page count: {len(pdf)}")
page = pdf[0]
width, height = page.get_size()
print(f"Page size (pt): {width} x {height}")

# Render full page at scale 3 (approx 216 DPI)
bitmap = page.render(scale=3)
img = bitmap.to_pil()
out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
full_path = os.path.join(out_dir, 'pdfium_ground_floor_full.png')
img.save(full_path)
print(f"Saved full page render to {full_path}, size {img.size}")


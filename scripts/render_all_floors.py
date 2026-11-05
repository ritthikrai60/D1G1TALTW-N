import pypdfium2 as pdfium
import os

pdf_paths = [
    r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf',
    r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf',
    r'c:\Coding Projects\Digital Twin\02-Second_Floor-Clean.pdf'
]

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

for p in pdf_paths:
    name = os.path.basename(p).replace('.pdf', '')
    doc = pdfium.PdfDocument(p)
    print(f"=== {name} ===")
    print(f"Pages: {len(doc)}, Size: {doc[0].get_size()}")
    bm = doc[0].render(scale=3)
    img = bm.to_pil()
    img_path = os.path.join(out_dir, f'pdfium_{name}_full.png')
    img.save(img_path)
    print(f"Saved {img_path}")


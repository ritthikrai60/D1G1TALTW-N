import pypdf
import json

# Check text in 01-First_Floor-Clean.pdf and 01-First_Floor-Model.pdf
for fname in ['01-First_Floor-Clean.pdf', '01-First_Floor-Model.pdf', '00-Ground_Floor-Model.pdf']:
    try:
        reader = pypdf.PdfReader(fname)
        print(f"=== {fname} ===")
        for p_idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                print(f"Page {p_idx} has {len(text)} chars")
                # print lines mentioning stair or บันได
                for line in text.split('\n'):
                    if any(w in line.lower() for w in ['stair', 'บันได', 'st-', 'up', 'dn']):
                        print("  MATCH:", line)
    except Exception as e:
        print(f"Error reading {fname}: {e}")


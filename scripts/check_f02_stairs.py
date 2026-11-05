import pypdfium2 as pdfium
from PIL import Image

pdf2 = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\02-Second_Floor-Clean.pdf')
print("Floor 02 pages:", len(pdf2))
page2 = pdf2[0]
bitmap2 = page2.render(scale=2.0)
img2 = bitmap2.to_pil()

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def m_to_px(xm, ym):
    pt_x = X0 + xm * SCALE
    pt_y = Y0 - ym * SCALE
    return int(pt_x * 2.0), int(pt_y * 2.0)

# Crop Core stair on Floor 02:
px1, py1 = m_to_px(6, -5)
px2, py2 = m_to_px(14, -15)
crop_f02_st1 = img2.crop((min(px1, px2), min(py1, py2), max(px1, px2), max(py1, py2)))
crop_f02_st1.save(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f02_st1_crop.png')
print("Saved f02_st1_crop.png")

# Also crop Lobby on Floor 02 to see if circular stair arrives there!
px1, py1 = m_to_px(18, 5)
px2, py2 = m_to_px(30, -10)
crop_f02_lobby = img2.crop((min(px1, px2), min(py1, py2), max(px1, px2), max(py1, py2)))
crop_f02_lobby.save(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f02_lobby_crop.png')
print("Saved f02_lobby_crop.png")


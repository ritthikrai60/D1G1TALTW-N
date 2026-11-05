import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont
import os

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
doc = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf')

bm = doc[0].render(scale=3)
img = bm.to_pil()
draw = ImageDraw.Draw(img)

# Coords in pt * 3
# ST-1: pt X=[1156, 1281], Y=[1289, 1445]
b1 = (int(1150 * 3), int(1280 * 3), int(1290 * 3), int(1455 * 3))
draw.rectangle(b1, outline=(239, 68, 68), width=8)

# ST-2: pt X=[1225, 1301], Y=[1748, 1873]
b2 = (int(1215 * 3), int(1735 * 3), int(1310 * 3), int(1885 * 3))
draw.rectangle(b2, outline=(59, 130, 246), width=8)

# ST-3: pt X=[1057, 1256], Y=[1959, 2106]
b3 = (int(1045 * 3), int(1945 * 3), int(1270 * 3), int(2120 * 3))
draw.rectangle(b3, outline=(16, 185, 129), width=8)

# Add text labels on the full plan
draw.text((b1[0] - 300, b1[1] - 40), "ST-1: Fire Egress Stair Core (P-2)", fill=(239, 68, 68))
draw.text((b2[2] + 40, b2[1] + 50), "ST-2: Central Open Stair (A-stair)", fill=(59, 130, 246))
draw.text((b3[0] - 300, b3[3] + 20), "ST-3: South Landscape Stair (A-stair)", fill=(16, 185, 129))

# Crop the relevant half of the building where stairs and columns are to make it readable
crop_overview = img.crop((int(500 * 3), int(1000 * 3), int(2500 * 3), int(2300 * 3)))
crop_path = os.path.join(out_dir, 'basement_all_3_stairs_map.png')
crop_overview.save(crop_path)
print("Saved basement_all_3_stairs_map.png")


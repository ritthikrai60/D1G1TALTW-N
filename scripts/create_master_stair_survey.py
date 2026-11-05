import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont
import os

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

doc0 = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf')
doc1 = pdfium.PdfDocument(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf')

bm0 = doc0[0].render(scale=4)
img0 = bm0.to_pil()

bm1 = doc1[0].render(scale=4)
img1 = bm1.to_pil()

# Crop ST-1 (Fire Stair): pt X=[1156, 1281], Y=[1289, 1445]
pad = 30
box_st1_0 = (int((1156 - pad) * 4), int((1289 - pad) * 4), int((1281 + pad) * 4), int((1445 + pad) * 4))
st1_0 = img0.crop(box_st1_0)
st1_1 = img1.crop(box_st1_0)

# Crop ST-2 (Central Stair): pt X=[1225, 1301], Y=[1748, 1873]
box_st2_0 = (int((1220 - pad) * 4), int((1740 - pad) * 4), int((1305 + pad) * 4), int((1880 + pad) * 4))
st2_0 = img0.crop(box_st2_0)
st2_1 = img1.crop(box_st2_0)

# Crop ST-3 (South Outdoor Stair): pt X=[1057, 1256], Y=[1959, 2106]
box_st3_0 = (int((1050 - pad) * 4), int((1950 - pad) * 4), int((1265 + pad) * 4), int((2115 + pad) * 4))
st3_0 = img0.crop(box_st3_0)
st3_1 = img1.crop(box_st3_0)

# Target height for uniform columns
target_h = 600
def resize_to_h(im, h):
    ratio = h / im.height
    return im.resize((int(im.width * ratio), h), Image.Resampling.LANCZOS)

st1_0_r = resize_to_h(st1_0, target_h)
st1_1_r = resize_to_h(st1_1, target_h)
st2_0_r = resize_to_h(st2_0, target_h)
st2_1_r = resize_to_h(st2_1, target_h)
st3_0_r = resize_to_h(st3_0, target_h)
st3_1_r = resize_to_h(st3_1, target_h)

# Create Master Forensic Board: 3 rows (ST-1, ST-2, ST-3), each with [Basement Plan] vs [1st Floor Plan]
row_w = max(st1_0_r.width + st1_1_r.width, st2_0_r.width + st2_1_r.width, st3_0_r.width + st3_1_r.width) + 80
board_h = target_h * 3 + 280

master_board = Image.new('RGB', (row_w, board_h), (248, 250, 252))
draw = ImageDraw.Draw(master_board)

# Header
draw.rectangle([(0, 0), (row_w, 70)], fill=(15, 23, 42))
draw.text((25, 22), "GROUND FLOOR (BASEMENT) - COMPLETE ARCHITECTURAL STAIR SURVEY", fill=(255, 255, 255))

# Draw Row 1: ST-1
y1 = 90
draw.rectangle([(10, y1), (row_w - 10, y1 + 35)], fill=(30, 41, 59))
draw.text((20, y1 + 8), "ST-1: Primary Fire Egress Stair Core (Layer P-2, A-wall) - Multi-floor Continuous", fill=(255, 255, 255))
master_board.paste(st1_0_r, (20, y1 + 45))
master_board.paste(st1_1_r, (st1_0_r.width + 50, y1 + 45))

# Draw Row 2: ST-2
y2 = y1 + target_h + 60
draw.rectangle([(10, y2), (row_w - 10, y2 + 35)], fill=(30, 41, 59))
draw.text((20, y2 + 8), "ST-2: Central Hallway Open Stair (Layer A-stair) - Connects Basement to 1st Floor Lobby", fill=(255, 255, 255))
master_board.paste(st2_0_r, (20, y2 + 45))
master_board.paste(st2_1_r, (st2_0_r.width + 50, y2 + 45))

# Draw Row 3: ST-3
y3 = y2 + target_h + 60
draw.rectangle([(10, y3), (row_w - 10, y3 + 35)], fill=(30, 41, 59))
draw.text((20, y3 + 8), "ST-3: South Outdoor Landscape Stair (Layer A-stair) - Connects Parking Path to 1st Floor Terrace", fill=(255, 255, 255))
master_board.paste(st3_0_r, (20, y3 + 45))
master_board.paste(st3_1_r, (st3_0_r.width + 50, y3 + 45))

out_path = os.path.join(out_dir, 'complete_stair_forensic_survey_master.png')
master_board.save(out_path)
print("Saved complete_stair_forensic_survey_master.png")


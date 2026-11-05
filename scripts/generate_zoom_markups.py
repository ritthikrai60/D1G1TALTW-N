import sys
import os
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from scripts.verify_all_77_cols import to_m, X0, Y0, SCALE

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Load full markup image
full_img = Image.open('C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/floor_plan_architectural_markup.png')

# 1. Zoom Core and Stairs: X in [700, 2400], Y in [1350, 2300]
crop_core = full_img.crop((700, 1350, 2400, 2300))
draw_c = ImageDraw.Draw(crop_core)
font_h = ImageFont.truetype('arial.ttf', 32)
font_b = ImageFont.truetype('arial.ttf', 20)

# Add title card on crop
draw_c.rectangle([30, 30, 680, 150], fill=(255, 255, 255, 245), outline=(30, 140, 60), width=2)
draw_c.rectangle([30, 30, 680, 75], fill=(30, 140, 60))
draw_c.text((45, 38), "ZOOM A: CORE & STAIRS ARCHITECTURE", font=font_h, fill=(255, 255, 255))
draw_c.text((45, 85), "• Flight 1 (4 steps East) -> Lower Landing (+0.86m)", font=font_b, fill=(30, 30, 30))
draw_c.text((45, 112), "• Flight 2 (10 steps North) -> Upper Landing (+2.76m)", font=font_b, fill=(30, 30, 30))
draw_c.text((45, 139), "• Flight 3 (4 steps South) -> Upper Floor (+3.50m)", font=font_b, fill=(30, 30, 30))

crop_core_path = 'C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/markup_core_and_stairs.png'
crop_core.save(crop_core_path, quality=95)

# 2. Zoom North Wing: X in [450, 2750], Y in [300, 1000]
crop_north = full_img.crop((450, 300, 2750, 1000))
draw_n = ImageDraw.Draw(crop_north)
draw_n.rectangle([30, 30, 680, 130], fill=(255, 255, 255, 245), outline=(70, 120, 180), width=2)
draw_n.rectangle([30, 30, 680, 75], fill=(70, 120, 180))
draw_n.text((45, 38), "ZOOM B: NORTH WING MULTI-ROOM", font=font_h, fill=(255, 255, 255))
draw_n.text((45, 85), "• 41 RC wall loops (Extrude +0.10 to +3.50m)", font=font_b, fill=(30, 30, 30))
draw_n.text((45, 112), "• Restroom partitions P-2 (0.15m) & P-4 (0.10m)", font=font_b, fill=(30, 30, 30))

crop_north_path = 'C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/markup_north_wing.png'
crop_north.save(crop_north_path, quality=95)

print("Saved zoomed crops successfully.")


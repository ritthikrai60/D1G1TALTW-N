from PIL import Image

Image.MAX_IMAGE_PIXELS = None
im = Image.open(r'C:\Users\ritth\Downloads\Telegram Desktop\NEW_NOTEXT\01-First_Floor-Clean.png')
w, h = im.size

art_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

# Divide into 6 large overlapping zones (3 cols x 2 rows)
zones = {
    'clean_zone_nw_sports.png': (0, 0, int(w * 0.45), int(h * 0.55)),
    'clean_zone_ne_terrace.png': (int(w * 0.35), 0, int(w * 0.75), int(h * 0.55)),
    'clean_zone_east_kitchen.png': (int(w * 0.65), 0, w, int(h * 0.65)),
    'clean_zone_sw_lockers.png': (0, int(h * 0.45), int(w * 0.45), h),
    'clean_zone_sc_foyer_portico.png': (int(w * 0.30), int(h * 0.45), int(w * 0.70), h),
    'clean_zone_se_retail.png': (int(w * 0.60), int(h * 0.45), w, h),
}

for name, box in zones.items():
    crop = im.crop(box)
    # resize by half so read_file and inspection are fast and sharp
    crop_resized = crop.resize((crop.width // 2, crop.height // 2), Image.Resampling.LANCZOS)
    crop_resized.save(f"{art_dir}\\{name}")
    print(f"Saved {name}: {crop_resized.size}")


from PIL import Image

img = Image.open(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_crop_core_stair_st1.png')
# Crop the stair flights tightly
w, h = img.size
# Top part where the circle/arrow is:
top_part = img.crop((100, 20, 300, 200)).resize((400, 360), Image.Resampling.NEAREST)
top_part.save(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_st1_top_zoom.png')

# Bottom part where the flight starts/ends:
bot_part = img.crop((120, 250, 300, 480)).resize((400, 460), Image.Resampling.NEAREST)
bot_part.save(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_st1_bot_zoom.png')
print("Saved st1 zoom crops")


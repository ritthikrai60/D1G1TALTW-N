from PIL import Image

img = Image.open(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_crop_east_curved_wing.png')
# Crop the stairs in the east wing:
# 1. Internal stair near elevator core (upper part)
# 2. Outdoor entrance stairs (lower right)
w, h = img.size
stair_east_inner = img.crop((500, 100, 1000, 500)).resize((500, 400), Image.Resampling.NEAREST)
stair_east_inner.save(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_stair_east_inner.png')

stair_east_outer = img.crop((1000, 900, 1500, 1400)).resize((500, 500), Image.Resampling.NEAREST)
stair_east_outer.save(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_stair_east_outer.png')

print("Saved east wing stair crops")


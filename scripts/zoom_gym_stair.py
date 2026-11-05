from PIL import Image

img = Image.open(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_crop_west_wing.png')
# Crop top left gym area
w, h = img.size
gym_stair = img.crop((150, 20, 600, 300)).resize((450, 280), Image.Resampling.NEAREST)
gym_stair.save(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_gym_stair.png')
print("Saved gym_stair")


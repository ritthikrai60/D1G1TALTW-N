from PIL import Image

# We already have f01_crop_lobby.png which has size (1871, 1417)
img = Image.open(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_crop_lobby.png')
w, h = img.size

# In f01_crop_lobby.png, the spiral stair is around:
# x: [500, 750], y: [500, 750]
# Let's crop tightly around it and save
crop_spiral = img.crop((450, 480, 750, 780))
crop_spiral.save(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_tight_spiral_crop.png')
print("Saved f01_tight_spiral_crop.png")


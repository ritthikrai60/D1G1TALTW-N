from PIL import Image

img = Image.open(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_crop_lobby.png')
crop_spiral = img.crop((450, 650, 750, 950))
crop_spiral.save(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_spiral_perfect.png')
print("Saved f01_spiral_perfect.png")

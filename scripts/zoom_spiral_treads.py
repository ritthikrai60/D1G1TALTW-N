from PIL import Image

img = Image.open(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_spiral_perfect.png')
# Crop the bottom tread arc
w, h = img.size
treads_zoom = img.crop((40, 100, 240, 260)).resize((400, 320), Image.Resampling.NEAREST)
treads_zoom.save(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_spiral_treads_zoom.png')
print("Saved f01_spiral_treads_zoom.png")


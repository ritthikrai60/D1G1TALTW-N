from PIL import Image

img = Image.open(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_crop_lobby.png')
# Crop the stairs to the right of the circular stair (bottom-right of lobby)
w, h = img.size
lobby_steps_right = img.crop((650, 700, 850, 950)).resize((400, 500), Image.Resampling.NEAREST)
lobby_steps_right.save(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_lobby_steps_right.png')
print("Saved lobby_steps_right")


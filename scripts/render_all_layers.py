import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from PIL import Image, ImageDraw

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

W, H = 3370, 2384
img = Image.new('RGB', (W, H), (255, 255, 255))
draw = ImageDraw.Draw(img)

# Print all layers with subpath counts
print("=== ALL LAYERS AND SUBPATH COUNTS ===")
layer_sps = {}
for name, l in layers.items():
    sps = []
    for c in l.get('kind', {}).get('children', []):
        sps.extend(extract_subpaths(c))
    layer_sps[name] = sps
    if len(sps) > 0:
        print(f"Layer '{name}': {len(sps)} subpaths")

# Color palette for rendering
import random
random.seed(42)

for name, sps in layer_sps.items():
    if not sps: continue
    # Skip huge hatch layers for speed
    if name in ['H-1', 'H-2']:
        continue
    
    # Pick distinctive color
    if name == 'A-stair':
        color = (255, 0, 0) # RED for stairs!
        width = 3
    elif name == 'A-col':
        color = (0, 0, 255) # BLUE for columns!
        width = 2
    elif name in ['P-1 (0.50)', 'P-1']:
        color = (180, 0, 180)
        width = 2
    elif name in ['AR_HATCH', 'A-wall', 'WALL']:
        color = (30, 30, 30)
        width = 2
    elif name in ['GRID', 'เส้นบาง']:
        color = (210, 210, 210)
        width = 1
    else:
        color = (random.randint(0, 180), random.randint(0, 180), random.randint(0, 180))
        width = 1
    
    for sp in sps:
        pts = [(p[0], p[1]) for p in sp['anchors']]
        if len(pts) < 2: continue
        if sp['closed'] or pts[0] == pts[-1]:
            draw.polygon(pts, outline=color, width=width)
        else:
            draw.line(pts, fill=color, width=width)

preview_all = 'C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/render_all_layers_complete.png'
img.save(preview_all)
print(f"Saved complete multi-layer render to {preview_all}")


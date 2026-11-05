import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from PIL import Image, ImageDraw

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

# Layers to render in close-ups
render_layers = [
    ('GRID', (230, 230, 230), 1),
    ('เส้นบาง', (200, 200, 200), 1),
    ('A-wall', (0, 0, 0), 2),
    ('AR_HATCH', (100, 100, 100), 2),
    ('P-1 (0.50)', (200, 0, 0), 3),
    ('P-1', (180, 0, 0), 2),
    ('P-2', (180, 0, 180), 2),
    ('P-3', (200, 100, 0), 2),
    ('P-4', (120, 120, 0), 2),
    ('D&W', (0, 150, 0), 1),
    ('SYMBOL', (255, 0, 0), 2),
    ('LABEL', (0, 0, 255), 2),
    ('DIMENSION', (150, 150, 150), 1),
    ('A-stair', (0, 0, 255), 2),
    ('A-col', (255, 140, 0), 2),
]

def render_crop(bbox, out_name):
    # bbox: (min_x, min_y, max_x, max_y)
    x0, y0, x1, y1 = bbox
    pad = 50
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = x1 + pad, y1 + pad
    w = int(x1 - x0)
    h = int(y1 - y0)
    scale = 2 # 2x zoom for clarity
    img = Image.new('RGB', (w * scale, h * scale), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    for lname, color, width in render_layers:
        l = layers.get(lname)
        if not l: continue
        for c in l.get('kind', {}).get('children', []):
            for sp in extract_subpaths(c):
                pts = sp['anchors']
                if len(pts) < 2: continue
                # check if any point is in bbox
                if any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in pts):
                    canvas_pts = [((p[0] - x0)*scale, (p[1] - y0)*scale) for p in pts]
                    if sp['closed'] or (len(canvas_pts) > 2 and canvas_pts[0] == canvas_pts[-1]):
                        draw.polygon(canvas_pts, outline=color, width=width*scale)
                    else:
                        draw.line(canvas_pts, fill=color, width=width*scale)
    
    out_path = f'C:/Users/ritth/.gemini/antigravity/brain/6c13c66f-33c4-4cae-a03d-a050b2641bb8/{out_name}.png'
    img.save(out_path)
    print(f"Saved crop {out_name} to {out_path} ({w*scale}x{h*scale})")

# 1. South Entrance Stairs
render_crop((1000, 1850, 1300, 2200), 'crop_stair_south_entrance')

# 2. Core Stairs
render_crop((1150, 1600, 1350, 1900), 'crop_stair_core')

# 3. North Stairs
render_crop((1000, 250, 1350, 750), 'crop_stair_north')


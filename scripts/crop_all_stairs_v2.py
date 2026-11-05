import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from PIL import Image
import os

doc = load_pdf_doc()['document']
stair_layer = [l for l in doc['layers'] if l['name'] == 'A-stair'][0]

core_pt_bounds = [float('inf'), float('inf'), float('-inf'), float('-inf')]
south_pt_bounds = [float('inf'), float('inf'), float('-inf'), float('-inf')]

for i, child in enumerate(stair_layer['kind']['children']):
    sps = extract_subpaths(child)
    for sp in sps:
        pts = sp['anchors']
        for p in pts:
            x_pt, y_pt = p[0], p[1]
            xm = (x_pt - 1133.858) / 28.346456692913385
            ym = (y_pt - 1417.323) / 28.346456692913385
            
            # Core: X in [3.0, 6.5], Y in [11.0, 16.5]
            if 3.0 <= xm <= 6.5 and 11.0 <= ym <= 16.5:
                core_pt_bounds[0] = min(core_pt_bounds[0], x_pt)
                core_pt_bounds[1] = min(core_pt_bounds[1], y_pt)
                core_pt_bounds[2] = max(core_pt_bounds[2], x_pt)
                core_pt_bounds[3] = max(core_pt_bounds[3], y_pt)
                
            # South: X in [-3.0, 5.0], Y in [18.0, 25.0]
            if -3.0 <= xm <= 5.0 and 18.0 <= ym <= 25.0:
                south_pt_bounds[0] = min(south_pt_bounds[0], x_pt)
                south_pt_bounds[1] = min(south_pt_bounds[1], y_pt)
                south_pt_bounds[2] = max(south_pt_bounds[2], x_pt)
                south_pt_bounds[3] = max(south_pt_bounds[3], y_pt)

print("Core pt bounds:", core_pt_bounds)
print("South pt bounds:", south_pt_bounds)

out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'
pad = 120 # pt padding to see surrounding context (walls, arrows, text)

for floor_name in ['00-Ground_Floor-Clean', '01-First_Floor-Clean', '02-Second_Floor-Clean']:
    img_path = os.path.join(out_dir, f'pdfium_{floor_name}_full.png')
    if not os.path.exists(img_path):
        continue
    img = Image.open(img_path)
    
    # Scale is 3
    box_c = (
        int((core_pt_bounds[0] - pad) * 3),
        int((core_pt_bounds[1] - pad) * 3),
        int((core_pt_bounds[2] + pad) * 3),
        int((core_pt_bounds[3] + pad) * 3)
    )
    crop_c = img.crop(box_c)
    crop_c.save(os.path.join(out_dir, f'{floor_name}_core_stair_context.png'))
    
    box_s = (
        int((south_pt_bounds[0] - pad) * 3),
        int((south_pt_bounds[1] - pad) * 3),
        int((south_pt_bounds[2] + pad) * 3),
        int((south_pt_bounds[3] + pad) * 3)
    )
    crop_s = img.crop(box_s)
    crop_s.save(os.path.join(out_dir, f'{floor_name}_south_stair_context.png'))
    print(f"Saved crops for {floor_name}: Core {crop_c.size}, South {crop_s.size}")


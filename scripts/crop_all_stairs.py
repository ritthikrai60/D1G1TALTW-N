import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
from PIL import Image
import os

doc = load_pdf_doc()['document']
stair_layer = [l for l in doc['layers'] if l['name'] == 'A-stair'][0]

all_pts = []
core_pts = []
south_pts = []

for i, child in enumerate(stair_layer['kind']['children']):
    sps = extract_subpaths(child)
    for sp in sps:
        pts = sp['anchors']
        # Convert to meter: (pt - 1133.858) / 28.346456692913385
        # but in pt:
        for p in pts:
            x_pt, y_pt = p[0], p[1]
            # meter coords:
            xm = (x_pt - 1133.858) / 28.346456692913385
            ym = (y_pt - 1417.323) / 28.346456692913385
            all_pts.append((x_pt, y_pt, xm, ym))
            if 7.0 <= xm <= 16.0 and -16.0 <= ym <= -5.0:
                core_pts.append((x_pt, y_pt, xm, ym))
            elif 2.0 <= xm <= 22.0 and -23.0 <= ym <= -10.0:
                south_pts.append((x_pt, y_pt, xm, ym))

print(f"Total stair pts: {len(all_pts)}")
print(f"Core stair pts: {len(core_pts)}")
print(f"South stair pts: {len(south_pts)}")

def get_bbox(pts):
    min_x = min(p[0] for p in pts)
    max_x = max(p[0] for p in pts)
    min_y = min(p[1] for p in pts)
    max_y = max(p[1] for p in pts)
    return min_x, min_y, max_x, max_y

c_min_x, c_min_y, c_max_x, c_max_y = get_bbox(core_pts)
s_min_x, s_min_y, s_max_x, s_max_y = get_bbox(south_pts)

print(f"Core bbox (pt): X=[{c_min_x:.1f}, {c_max_x:.1f}], Y=[{c_min_y:.1f}, {c_max_y:.1f}]")
print(f"South bbox (pt): X=[{s_min_x:.1f}, {s_max_x:.1f}], Y=[{s_min_y:.1f}, {s_max_y:.1f}]")

# Let's crop from the rendered images:
out_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

# At scale 3, pixel coordinate is pt * 3
# Let's add generous padding around them: e.g. 50 pt (150 px)
pad = 80 # pt

for floor_name in ['00-Ground_Floor-Clean', '01-First_Floor-Clean', '02-Second_Floor-Clean']:
    img_path = os.path.join(out_dir, f'pdfium_{floor_name}_full.png')
    if not os.path.exists(img_path):
        continue
    img = Image.open(img_path)
    
    # Core crop:
    box_c = (int((c_min_x - pad) * 3), int((c_min_y - pad) * 3), int((c_max_x + pad) * 3), int((c_max_y + pad) * 3))
    crop_c = img.crop(box_c)
    crop_c.save(os.path.join(out_dir, f'{floor_name}_core_stair_pypdfium.png'))
    
    # South crop:
    box_s = (int((s_min_x - pad) * 3), int((s_min_y - pad) * 3), int((s_max_x + pad) * 3), int((s_max_y + pad) * 3))
    crop_s = img.crop(box_s)
    crop_s.save(os.path.join(out_dir, f'{floor_name}_south_stair_pypdfium.png'))
    print(f"Saved crops for {floor_name}: Core {crop_c.size}, South {crop_s.size}")



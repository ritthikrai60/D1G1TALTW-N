from PIL import Image

img = Image.open(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\f01_highres_overview.png')
w, h = img.size

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def m_to_px(xm, ym):
    pt_x = X0 + xm * SCALE
    pt_y = Y0 - ym * SCALE
    return int(pt_x * 2.0), int(pt_y * 2.0)

art_dir = r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8'

# Let's inspect 6 specific zones where stairs might be located:
scan_zones = {
    # 1. Left of lobby: Grand Fan-Shaped Steps / Terrace Rotunda
    'f01_stair_fan_rotunda.png': (12.0, -5.0, 20.0, 5.0),
    # 2. North sports terrace bleachers / stairs (X: -20 to 35, Y: 35 to 45)
    'f01_stair_north_terrace_west.png': (-22.0, 32.0, -10.0, 46.0),
    'f01_stair_north_terrace_center.png': (-10.0, 32.0, 10.0, 46.0),
    'f01_stair_north_terrace_east.png': (10.0, 32.0, 32.0, 46.0),
    # 3. West wing main entrance / external perimeter
    'f01_stair_west_entry.png': (-26.0, -18.0, -15.0, -8.0),
    # 4. Portico / front drop-off steps
    'f01_stair_south_portico.png': (15.0, -18.0, 28.0, -10.0),
}

for name, (x1, y1, x2, y2) in scan_zones.items():
    px1, py1 = m_to_px(x1, y2)
    px2, py2 = m_to_px(x2, y1)
    cropped = img.crop((min(px1, px2), min(py1, py2), max(px1, px2), max(py1, py2)))
    cropped.save(f"{art_dir}\\{name}")
    print(f"Saved {name}: size={cropped.size}")


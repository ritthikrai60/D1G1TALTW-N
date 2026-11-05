import os
import re
import zlib
import json
import math
from PIL import Image, ImageDraw

PT_PER_METER = 28.3464567
ORIGIN_X_PT = 1570.0
ORIGIN_Y_PT = 1180.0

PDF_MIN_X = 220.0
PDF_MAX_X = 2920.0
PDF_MIN_Y = 200.0
PDF_MAX_Y = 2120.0

WORLD_MIN_X = (PDF_MIN_X - ORIGIN_X_PT) / PT_PER_METER
WORLD_MAX_X = (PDF_MAX_X - ORIGIN_X_PT) / PT_PER_METER
WORLD_MIN_Y = -(PDF_MAX_Y - ORIGIN_Y_PT) / PT_PER_METER
WORLD_MAX_Y = -(PDF_MIN_Y - ORIGIN_Y_PT) / PT_PER_METER

FLOOR_FILES = [
    ("00", "00-Ground_Floor-Clean.pdf"),
    ("01", "01-First_Floor-Clean.pdf"),
    ("02", "02-Second_Floor-Clean.pdf"),
    ("03", "03-Roof_Floor-Clean.pdf"),
]

def pdf_to_3d(x_pt, y_pt):
    return (
        round((x_pt - ORIGIN_X_PT) / PT_PER_METER, 2),
        round(-(y_pt - ORIGIN_Y_PT) / PT_PER_METER, 2),
    )

def parse_pdf_content_stream(raw_pdf_bytes):
    streams = re.findall(rb'stream\r?\n(.*?)\r?\nendstream', raw_pdf_bytes, re.S)
    if not streams:
        return []
    dec = zlib.decompress(streams[0]).decode('latin1')
    polylines = []
    for blk in dec.split('Q'):
        if 'm' not in blk:
            continue
        rgb = (0.85, 0.85, 0.85)
        m_rgb = re.search(r'([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+RG', blk)
        if m_rgb:
            rgb = (float(m_rgb.group(1)), float(m_rgb.group(2)), float(m_rgb.group(3)))
        else:
            m_g = re.search(r'([\d\.]+)\s+G', blk)
            if m_g:
                g = float(m_g.group(1))
                rgb = (g, g, g)
        pts = [(float(m.group(1)), float(m.group(2))) for m in re.finditer(r'([\d\.]+)\s+([\d\.]+)\s+[ml]', blk)]
        if len(pts) >= 2:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if min(xs) < 150 or max(xs) > 3000 or min(ys) < 120 or max(ys) > 2250:
                continue
            polylines.append((rgb, pts))
    return polylines

def extract_vectorcraft_layers(raw_pdf_bytes):
    streams = re.findall(rb'stream\r?\n(.*?)\r?\nendstream', raw_pdf_bytes, re.S)
    for s in streams:
        try:
            dec = zlib.decompress(s)
            if dec.startswith(b'{"format"'):
                return json.loads(dec.decode('utf-8'))['document'].get('layers', [])
        except Exception:
            pass
    return []

def collect_paths_from_items(items):
    paths = []
    for item in items:
        kind = item.get('kind', {})
        ktype = kind.get('type')
        if ktype == 'path':
            for sp in kind.get('path', {}).get('subpaths', []):
                anchors = sp.get('anchors', [])
                pts = [tuple(a['p']) for a in anchors if 'p' in a]
                if len(pts) >= 2:
                    if sp.get('closed') and pts[0] != pts[-1]:
                        pts.append(pts[0])
                    paths.append(pts)
        elif ktype == 'group':
            paths.extend(collect_paths_from_items(kind.get('children', [])))
    return paths

def render_plan_overlay(polylines, out_path, width_px=1600, height_px=1138):
    img = Image.new("RGBA", (width_px, height_px), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    span_x = PDF_MAX_X - PDF_MIN_X
    span_y = PDF_MAX_Y - PDF_MIN_Y

    def to_px(pt):
        return (
            (pt[0] - PDF_MIN_X) / span_x * width_px,
            (pt[1] - PDF_MIN_Y) / span_y * height_px,
        )

    for rgb, pts in polylines:
        r, g, b = int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
        if r < 60 and g < 60 and b < 60:
            r, g, b = 220, 230, 245
        line_w = 1
        if (rgb[0] == 0 and rgb[1] == 1 and rgb[2] == 1):
            line_w = 2
            r, g, b = 0, 240, 255
        elif (rgb[0] == 1 and rgb[1] == 0 and rgb[2] == 1):
            line_w = 2
            r, g, b = 255, 90, 220
        elif (rgb[0] == 1 and rgb[1] == 0 and rgb[2] == 0):
            line_w = 2
            r, g, b = 255, 95, 85
        elif (rgb[0] == 0 and rgb[1] >= 0.8 and rgb[2] == 0):
            line_w = 1
            r, g, b = 60, 235, 130
        elif (rgb[0] == 1 and rgb[1] == 1 and rgb[2] == 0):
            line_w = 2
            r, g, b = 255, 220, 60

        px_pts = [to_px(p) for p in pts]
        draw.line(px_pts, fill=(r, g, b, 235), width=line_w)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    print(f"Saved lightweight overlay: {out_path} ({width_px}x{height_px})")

def deduplicate_walls(raw_segments, min_len=1.8):
    kept = []
    raw_segments.sort(key=lambda s: math.hypot(s["p2"][0] - s["p1"][0], s["p2"][1] - s["p1"][1]), reverse=True)
    for seg in raw_segments:
        p1, p2 = seg["p1"], seg["p2"]
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        if length < min_len:
            continue
        mx, my = 0.5 * (p1[0] + p2[0]), 0.5 * (p1[1] + p2[1])
        ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0]) % math.pi
        is_dup = False
        for k in kept:
            kmx = 0.5 * (k["p1"][0] + k["p2"][0])
            kmy = 0.5 * (k["p1"][1] + k["p2"][1])
            kang = math.atan2(k["p2"][1] - k["p1"][1], k["p2"][0] - k["p1"][0]) % math.pi
            ang_diff = min(abs(ang - kang), math.pi - abs(ang - kang))
            if ang_diff < 0.15 and math.hypot(mx - kmx, my - kmy) < 0.85:
                is_dup = True
                break
        if not is_dup:
            kept.append(seg)
    return kept

def extract_doors(floor_id, layers):
    dw_paths = []
    for lyr in layers:
        if lyr.get('name') == 'D&W':
            dw_paths = collect_paths_from_items(lyr.get('kind', {}).get('children', []))
    if not dw_paths:
        return []

    door_clusters = []
    for pts in dw_paths:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        matched = False
        for cl in door_clusters:
            if math.hypot(cx - cl['cx'], cy - cl['cy']) < 45.0: # ~1.5m
                cl['xs'].extend(xs)
                cl['ys'].extend(ys)
                cl['cx'] = (min(cl['xs']) + max(cl['xs'])) / 2
                cl['cy'] = (min(cl['ys']) + max(cl['ys'])) / 2
                cl['paths'].append(pts)
                matched = True
                break
        if not matched:
            door_clusters.append({
                'cx': cx, 'cy': cy,
                'xs': list(xs), 'ys': list(ys),
                'paths': [pts]
            })

    door_list = []
    for idx, cl in enumerate(door_clusters):
        if len(cl['paths']) < 4:
            continue
        min_x, max_x = min(cl['xs']), max(cl['xs'])
        min_y, max_y = min(cl['ys']), max(cl['ys'])
        cx, cy = (min_x + max_x) / 2, (min_y + max_y) / 2
        w_m = (max_x - min_x) / PT_PER_METER
        h_m = (max_y - min_y) / PT_PER_METER
        p3d = pdf_to_3d(cx, cy)

        door_type = "single"
        if max(w_m, h_m) > 1.4:
            door_type = "double"
        if max(w_m, h_m) > 2.2:
            door_type = "sliding_or_shutter"

        door_list.append({
            "id": f"D{floor_id}_{len(door_list)+1:02d}",
            "x": p3d[0],
            "y": p3d[1],
            "width_m": round(max(w_m, h_m), 2),
            "depth_m": round(min(w_m, h_m), 2),
            "type": door_type,
            "is_horizontal": (w_m >= h_m),
        })
    return door_list

def clip_walls_with_doors(walls, doors, margin=0.08):
    split_walls = []
    for w in walls:
        p1 = list(w["p1"])
        p2 = list(w["p2"])
        layer = w.get("layer", "")
        vx = p2[0] - p1[0]
        vy = p2[1] - p1[1]
        seg_len = math.hypot(vx, vy)
        if seg_len < 0.4:
            continue

        cuts = []
        for d in doors:
            dx, dy = d["x"], d["y"]
            dw = d["width_m"] * 0.5 + margin
            t = ((dx - p1[0]) * vx + (dy - p1[1]) * vy) / (seg_len * seg_len)
            proj_x = p1[0] + t * vx
            proj_y = p1[1] + t * vy
            dist = math.hypot(dx - proj_x, dy - proj_y)
            if dist < 0.35 and 0.05 < t < 0.95:
                t_start = max(0.0, t - dw / seg_len)
                t_end = min(1.0, t + dw / seg_len)
                if t_end > t_start:
                    cuts.append((t_start, t_end))

        if not cuts:
            split_walls.append({"p1": p1, "p2": p2, "layer": layer})
        else:
            cuts.sort(key=lambda c: c[0])
            merged_cuts = []
            for c in cuts:
                if not merged_cuts:
                    merged_cuts.append(c)
                else:
                    if c[0] <= merged_cuts[-1][1]:
                        merged_cuts[-1] = (merged_cuts[-1][0], max(merged_cuts[-1][1], c[1]))
                    else:
                        merged_cuts.append(c)

            curr_t = 0.0
            for c_start, c_end in merged_cuts:
                if c_start > curr_t + 0.12:
                    split_walls.append({
                        "p1": [round(p1[0] + curr_t * vx, 2), round(p1[1] + curr_t * vy, 2)],
                        "p2": [round(p1[0] + c_start * vx, 2), round(p1[1] + c_start * vy, 2)],
                        "layer": layer
                    })
                curr_t = c_end
            if curr_t < 1.0 - 0.12:
                split_walls.append({
                    "p1": [round(p1[0] + curr_t * vx, 2), round(p1[1] + curr_t * vy, 2)],
                    "p2": [round(p1[0] + 1.0 * vx, 2), round(p1[1] + 1.0 * vy, 2)],
                    "layer": layer
                })
    return split_walls

def extract_structural_features(floor_id, layers):
    columns = []
    wall_segments = []

    # IMPORTANT: On Ground Floor ("00"), Layer 'WALL' is the upper-floor slab projection line
    # cutting across the parking driveway, NOT a physical wall!
    if floor_id == "00":
        primary_wall_layers = {'A-wall', 'P-1 (0.50)', 'P-2 (0.15)', 'P-3', 'P-4 (0.10)', 'P-4'}
        target_col_layers = ('A-col', 'H-2', 'H-1')
    else:
        primary_wall_layers = {'A-wall', 'WALL', 'P-2 (0.15)'}
        target_col_layers = ('A-col',)

    for lyr in layers:
        lname = lyr.get('name', '')
        children = lyr.get('kind', {}).get('children', [])
        if not children:
            continue
        paths = collect_paths_from_items(children)

        if lname in target_col_layers:
            for pts in paths:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                w_pt = max(xs) - min(xs)
                h_pt = max(ys) - min(ys)
                w_m = w_pt / PT_PER_METER
                h_m = h_pt / PT_PER_METER

                # Accurate structural column dimensions in CAD:
                # size between 0.35m and 1.35m, 4 to 6 vertices
                if 0.35 <= w_m <= 1.35 and 0.35 <= h_m <= 1.35 and len(pts) in (4, 5, 6):
                    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
                    x3d, y3d = pdf_to_3d(cx, cy)
                    columns.append({"x": x3d, "y": y3d, "w": round(w_m, 2), "d": round(h_m, 2), "layer": lname})

                elif floor_id == "00" and lname == 'A-col' and max(w_pt, h_pt) > 70.0:
                    # On Ground Floor, the yellow northern structural room walls (X=-20..-9.4, Y=7.8..31.8)
                    # were placed inside Layer 'A-col' by the CAD drafter!
                    for i in range(len(pts) - 1):
                        p1, p2 = pts[i], pts[i + 1]
                        x1, y1 = pdf_to_3d(p1[0], p1[1])
                        x2, y2 = pdf_to_3d(p2[0], p2[1])
                        wall_segments.append({"p1": [x1, y1], "p2": [x2, y2], "layer": "A-col-wall"})

        elif lname in primary_wall_layers:
            for pts in paths:
                # In P-3 on Floor 00, skip small 1mx1m equipment boxes inside the room; keep perimeter & partitions
                if floor_id == "00" and lname == 'P-3':
                    xs = [p[0] for p in pts]
                    ys = [p[1] for p in pts]
                    if max(max(xs) - min(xs), max(ys) - min(ys)) < 45.0:
                        continue
                min_seg_pt = 22.0 if (floor_id == "00" and 'P-4' in lname) else 40.0
                for i in range(len(pts) - 1):
                    p1 = pts[i]
                    p2 = pts[i + 1]
                    if min(p1[0], p2[0]) < 200 or max(p1[0], p2[0]) > 2950:
                        continue
                    if math.hypot(p2[0] - p1[0], p2[1] - p1[1]) < min_seg_pt:
                        continue
                    x1, y1 = pdf_to_3d(p1[0], p1[1])
                    x2, y2 = pdf_to_3d(p2[0], p2[1])
                    wall_segments.append({"p1": [x1, y1], "p2": [x2, y2], "layer": lname})

    # Exact column deduplication: prefer A-col or H-2 over hatch H-1
    unique_cols = []
    for c in columns:
        existing = None
        for u in unique_cols:
            if math.hypot(c['x'] - u['x'], c['y'] - u['y']) < 0.65:
                existing = u
                break
        if existing is None:
            unique_cols.append(c)
        elif c.get('layer') in ('A-col', 'H-2'):
            existing['w'] = c['w']
            existing['d'] = c['d']
            existing['layer'] = c['layer']

    clean_walls = deduplicate_walls(wall_segments, min_len=0.75 if floor_id == "00" else 1.8)
    doors = extract_doors(floor_id, layers)
    if doors:
        clean_walls = clip_walls_with_doors(clean_walls, doors)

    return {"columns": unique_cols, "wall_segments": clean_walls, "doors": doors}

def main():
    root_dir = r"c:\Coding Projects\Digital Twin"
    plans_dir = os.path.join(root_dir, "public", "plans")
    os.makedirs(plans_dir, exist_ok=True)

    summary_data = {
        "scale_pt_per_meter": PT_PER_METER,
        "origin_pt": [ORIGIN_X_PT, ORIGIN_Y_PT],
        "overlay_bounds_3d": {
            "min_x": round(WORLD_MIN_X, 3),
            "max_x": round(WORLD_MAX_X, 3),
            "min_y": round(WORLD_MIN_Y, 3),
            "max_y": round(WORLD_MAX_Y, 3),
            "width_m": round(WORLD_MAX_X - WORLD_MIN_X, 3),
            "depth_m": round(WORLD_MAX_Y - WORLD_MIN_Y, 3),
        },
        "floors": {}
    }

    for floor_id, filename in FLOOR_FILES:
        pdf_path = os.path.join(root_dir, filename)
        with open(pdf_path, "rb") as fp:
            raw_bytes = fp.read()

        polylines = parse_pdf_content_stream(raw_bytes)
        out_png = os.path.join(plans_dir, f"floor_{floor_id}.png")
        render_plan_overlay(polylines, out_png)

        layers = extract_vectorcraft_layers(raw_bytes)
        features = extract_structural_features(floor_id, layers)
        if floor_id == "03" and not features["wall_segments"]:
            roof_walls = []
            for rgb, pts in polylines:
                if (rgb[0] == 0.0 and rgb[1] == 1.0 and rgb[2] == 1.0):
                    for i in range(len(pts) - 1):
                        p1, p2 = pts[i], pts[i + 1]
                        roof_walls.append({"p1": list(pdf_to_3d(p1[0], p1[1])), "p2": list(pdf_to_3d(p2[0], p2[1])), "layer": "ROOF_WALL"})
            features["wall_segments"] = deduplicate_walls(roof_walls)
        summary_data["floors"][floor_id] = features
        print(f"Floor {floor_id}: {len(features['columns'])} cols, {len(features['wall_segments'])} major walls")

    out_json = os.path.join(root_dir, "scripts", "extracted_geometry.json")
    with open(out_json, "w", encoding="utf-8") as fp:
        json.dump(summary_data, fp, indent=2)
    print(f"Saved updated geometry JSON to {out_json}")

if __name__ == "__main__":
    main()

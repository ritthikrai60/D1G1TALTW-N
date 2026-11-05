import json
import zlib
import math
from pathlib import Path

# 1. Read PDF CAD JSON stream for exact AR_HATCH and P-1 geometry
pdf_path = Path(r"c:\Coding Projects\Digital Twin\00-Ground_Floor-Clean.pdf")
raw = pdf_path.read_bytes()

pos = 235622
nl = raw.find(b"\n", pos)
e_idx = raw.find(b"endstream", nl)
dec = zlib.decompress(raw[nl+1:e_idx].strip())
doc = json.loads(dec.decode("utf-8"))

PT_PER_METER = 28.3464567
ORIGIN_X_PT = 1570.0
ORIGIN_Y_PT = 1180.0

def pt_to_m(p):
    return (round((p[0] - ORIGIN_X_PT) / PT_PER_METER, 3), round(-(p[1] - ORIGIN_Y_PT) / PT_PER_METER, 3))

# Extract pure built core wall polygons (Y <= 8.5)
wall_polys = []
for l in doc["document"]["layers"]:
    if l.get("name") == "AR_HATCH":
        for item in l.get("kind", {}).get("children", []):
            k = item.get("kind", {})
            if k.get("type") == "path":
                for sp in k.get("path", {}).get("subpaths", []):
                    pts = [pt_to_m(a["p"]) for a in sp.get("anchors", []) if "p" in a]
                    if len(pts) >= 4 and pts[0] == pts[-1]:
                        pts = pts[:-1]
                    if len(pts) >= 3:
                        ys = [p[1] for p in pts]
                        if max(ys) <= 8.5:  # Only built ground floor area
                            # Calculate polygon area
                            area = 0.0
                            n = len(pts)
                            for i in range(n):
                                j = (i + 1) % n
                                area += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
                            if abs(area) * 0.5 > 0.01:
                                wall_polys.append(pts)

# Extract Ground Floor Columns from extracted_geometry.json (built area Y <= 10.5)
geom_file = Path(r"c:\Coding Projects\Digital Twin\scripts\extracted_geometry.json")
with open(geom_file, "r", encoding="utf-8") as f:
    geom_data = json.load(f)

cols = geom_data["floors"]["00"]["columns"]
# Filter columns for parking undercroft and core building (X <= -5.5, Y <= 10.5)
built_cols = [c for c in cols if c["x"] <= -5.5 and c["y"] <= 10.5]

code_lines = [
    "import math",
    "# 1. Clean existing building groups (keep Engineer scale figure)",
    "to_remove = [g for g in list(groups) if g.name.startswith('F0_')]",
    "for g in to_remove:",
    "    if g in groups:",
    "        groups.remove(g)",
    "",
    "# 2. Accurate Ground Slabs (Parking Undercroft & Service Core)",
    "# Parking Undercroft Slab (Open Car Park)",
    "box((-45.5, -28.0, -0.15), (28.5, 38.5, 0.15), name='F0_Slab_Parking_Open', color=(0.28, 0.30, 0.33, 1.0))",
    "# Service Core Slab (Restrooms, M&E, Stair Core)",
    "box((-19.0, -26.0, -0.05), (13.5, 34.5, 0.05), name='F0_Slab_ServiceCore', color=(0.86, 0.84, 0.80, 1.0))",
    "",
    "# 3. Structural Columns (Parking Undercroft & Core)",
]

for i, col in enumerate(built_cols):
    cx = col["x"]
    cy = col["y"]
    w = col["w"]
    d = col["d"]
    ox = round(cx - w / 2, 3)
    oy = round(cy - d / 2, 3)
    code_lines.append(
        f"box(({ox}, {oy}, 0.0), ({round(w,3)}, {round(d,3)}, 3.5), name='F0_Col_{i:02d}', color=(0.84, 0.82, 0.78, 1.0))"
    )

code_lines.append("")
code_lines.append("# 4. Built Core Wall Polygons (CAD AR_HATCH Polygons extruded to 3.5m)")
for i, poly in enumerate(wall_polys):
    pts_str = ", ".join(f"({p[0]}, {p[1]})" for p in poly)
    code_lines.append(
        f"extrude([{pts_str}], 0.0, 3.5, name='F0_Wall_Core_{i:02d}', color=(0.92, 0.90, 0.86, 1.0))"
    )

code_lines.append("")
code_lines.append("# 5. P-1 (0.50m) Retaining Wall and Portico Walls")
code_lines.append("wall((-10.59, -25.09), (-5.82, -24.12), height=3.5, thickness=0.50, z0=0.0, name='F0_Wall_Retaining_1', color=(0.88, 0.86, 0.82, 1.0))")
code_lines.append("wall((-5.82, -24.12), (-9.43, -1.83), height=3.5, thickness=0.50, z0=0.0, name='F0_Wall_Retaining_2', color=(0.88, 0.86, 0.82, 1.0))")
code_lines.append("wall((-9.43, -1.83), (-9.43, 7.82), height=3.5, thickness=0.50, z0=0.0, name='F0_Wall_Retaining_3', color=(0.88, 0.86, 0.82, 1.0))")
code_lines.append("wall((-16.14, -25.89), (-11.04, -25.17), height=3.5, thickness=0.50, z0=0.0, name='F0_Wall_Portico_South', color=(0.88, 0.86, 0.82, 1.0))")

code_lines.append("")
code_lines.append("# 6. Stairs")
code_lines.append("# Grand Monumental Entrance Stairs (8 steps rising to Z=3.5m)")
code_lines.append("steps_count = 8")
code_lines.append("stair_w = 6.0")
code_lines.append("stair_l = 8.99")
code_lines.append("step_len = stair_l / steps_count")
code_lines.append("step_h = 3.5 / steps_count")
code_lines.append("for s in range(steps_count):")
code_lines.append("    y_cur = -34.93 + s * step_len")
code_lines.append("    h_cur = (s + 1) * step_h")
code_lines.append("    box((-17.21, y_cur, 0.0), (stair_w, stair_l - s * step_len, step_h), name=f'F0_Stair_Main_{s}', color=(0.80, 0.76, 0.70, 1.0))")

code_lines.append("")
code_lines.append("# Internal Core Dogleg Stairs")
code_lines.append("flight_steps = 7")
code_lines.append("f_step_len = 3.2 / flight_steps")
code_lines.append("f_step_h = 1.75 / (flight_steps + 1)")
code_lines.append("for s in range(flight_steps):")
code_lines.append("    y_cur = -24.45 + s * f_step_len")
code_lines.append("    h_cur = (s + 1) * f_step_h")
code_lines.append("    box((-12.15, y_cur, 0.0), (1.20, f_step_len, h_cur), name=f'F0_Stair_Int_F1_{s}', color=(0.82, 0.78, 0.72, 1.0))")
code_lines.append("box((-12.15, -21.25, 0.0), (2.66, 1.20, 1.75), name='F0_Stair_Int_Landing', color=(0.80, 0.76, 0.70, 1.0))")
code_lines.append("for s in range(flight_steps):")
code_lines.append("    y_cur = -21.25 - (s + 1) * f_step_len")
code_lines.append("    h_cur = 1.75 + (s + 1) * f_step_h")
code_lines.append("    box((-10.69, y_cur, 1.75), (1.20, f_step_len, (s + 1) * f_step_h), name=f'F0_Stair_Int_F2_{s}', color=(0.82, 0.78, 0.72, 1.0))")

code_lines.append("")
code_lines.append("# 7. Camera Orbit & Viewport update")
code_lines.append("viewport.camera.target = QVector3D(-22.0, -10.0, 2.0)")
code_lines.append("viewport.camera.distance = 55.0")
code_lines.append("viewport.camera.yaw = math.radians(-45.0)")
code_lines.append("viewport.camera.pitch = math.radians(35.0)")
code_lines.append("viewport.update()")
code_lines.append("print('ACCURATE_GROUND_FLOOR_SUCCESS')")

payload = "\n".join(code_lines)
out_file = Path(r"c:\Coding Projects\Digital Twin\scripts\accurate_ingetrazo_payload.py")
out_file.write_text(payload, encoding="utf-8")
print(f"Generated accurate payload with {len(code_lines)} lines ({len(payload)} bytes).")
print(f"Built columns: {len(built_cols)}, Built wall polygons: {len(wall_polys)}")


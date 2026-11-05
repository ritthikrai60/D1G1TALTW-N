import json
import math
from pathlib import Path

# Load extracted CAD geometry
geom_file = Path(r"c:\Coding Projects\Digital Twin\scripts\extracted_geometry.json")
with open(geom_file, "r", encoding="utf-8") as f:
    data = json.load(f)

f0 = data["floors"]["00"]
columns = f0["columns"]
walls = f0["wall_segments"]

code_lines = [
    "import math",
    "# 1. Clean existing building groups if needed (keep Engineer scale figure)",
    "to_remove = [g for g in list(groups) if g.name.startswith('F0_')]",
    "for g in to_remove:",
    "    if g in groups:",
    "        groups.remove(g)",
    "",
    "# 2. Parking & Core Ground Slabs",
    "box((-48.0, -36.0, -0.2), (58.0, 72.0, 0.2), name='F0_Slab_Parking', color=(0.30, 0.32, 0.35, 1.0))",
    "box((-35.0, -26.0, -0.05), (46.0, 62.0, 0.05), name='F0_Slab_Core', color=(0.78, 0.76, 0.72, 1.0))",
    "",
    "# 3. Columns (78 Structural Columns)",
]

# Generate columns
for i, col in enumerate(columns):
    cx = col["x"]
    cy = col["y"]
    w = col["w"]
    d = col["d"]
    ox = round(cx - w / 2, 3)
    oy = round(cy - d / 2, 3)
    code_lines.append(
        f"box(({ox}, {oy}, 0.0), ({round(w,3)}, {round(d,3)}, 3.5), name='F0_Col_{i:02d}', color=(0.85, 0.82, 0.78, 1.0))"
    )

code_lines.append("")
code_lines.append("# 4. Wall Segments (118 CAD Extracted Walls)")

# Generate walls
for i, w_seg in enumerate(walls):
    p1 = w_seg["p1"]
    p2 = w_seg["p2"]
    layer = w_seg.get("layer", "")
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length < 0.08:
        continue
    
    thick = 0.20
    if "0.50" in layer or layer == "P-1":
        thick = 0.50
    elif "0.10" in layer or layer == "P-4":
        thick = 0.10
        
    code_lines.append(
        f"wall(({round(p1[0],3)}, {round(p1[1],3)}), ({round(p2[0],3)}, {round(p2[1],3)}), height=3.5, thickness={thick}, z0=0.0, name='F0_Wall_{i:03d}', color=(0.92, 0.90, 0.86, 1.0))"
    )

code_lines.append("")
code_lines.append("# 5. Stairs")
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
code_lines.append("# Flight 1: rising North to Landing at Z=1.75m")
code_lines.append("flight_steps = 7")
code_lines.append("f_step_len = 3.2 / flight_steps")
code_lines.append("f_step_h = 1.75 / (flight_steps + 1)")
code_lines.append("for s in range(flight_steps):")
code_lines.append("    y_cur = -24.45 + s * f_step_len")
code_lines.append("    h_cur = (s + 1) * f_step_h")
code_lines.append("    box((-12.15, y_cur, 0.0), (1.20, f_step_len, h_cur), name=f'F0_Stair_Int_F1_{s}', color=(0.82, 0.78, 0.72, 1.0))")
code_lines.append("# Landing at Y = -21.25 to -20.05, Z=1.75m")
code_lines.append("box((-12.15, -21.25, 0.0), (2.66, 1.20, 1.75), name='F0_Stair_Int_Landing', color=(0.80, 0.76, 0.70, 1.0))")
code_lines.append("# Flight 2: rising South to Level 1 (Z=3.50m)")
code_lines.append("for s in range(flight_steps):")
code_lines.append("    y_cur = -21.25 - (s + 1) * f_step_len")
code_lines.append("    h_cur = 1.75 + (s + 1) * f_step_h")
code_lines.append("    box((-10.69, y_cur, 1.75), (1.20, f_step_len, (s + 1) * f_step_h), name=f'F0_Stair_Int_F2_{s}', color=(0.82, 0.78, 0.72, 1.0))")

code_lines.append("")
code_lines.append("# 6. Camera Orbit & Viewport update")
code_lines.append("viewport.camera.target = QVector3D(-14.0, -2.0, 2.0)")
code_lines.append("viewport.camera.distance = 78.0")
code_lines.append("viewport.camera.yaw = math.radians(-40.0)")
code_lines.append("viewport.camera.pitch = math.radians(35.0)")
code_lines.append("viewport.update()")
code_lines.append("print('GROUND_FLOOR_BUILT_SUCCESS')")

full_script = "\n".join(code_lines)
target_path = Path(r"c:\Coding Projects\Digital Twin\scripts\ingetrazo_payload.py")
target_path.write_text(full_script, encoding="utf-8")
print(f"Generated payload with {len(code_lines)} lines ({len(full_script)} bytes).")


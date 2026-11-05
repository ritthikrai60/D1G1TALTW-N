import json
import math

with open(r"c:\Coding Projects\Digital Twin\scripts\extracted_geometry.json", "r", encoding="utf-8") as f:
    cad_data = json.load(f)

print("Current F0 stats:")
print("Cols:", len(cad_data["floors"]["00"]["columns"]))
print("Walls:", len(cad_data["floors"]["00"]["wall_segments"]))
print("Doors:", len(cad_data["floors"]["00"].get("doors", [])))


import json
import math

with open(r"c:\Coding Projects\Digital Twin\scripts\extracted_geometry.json", "r", encoding="utf-8") as f:
    data = json.load(f)

cols = data["floors"]["00"]["columns"]
print(f"Total columns in JSON for Floor 00: {len(cols)}")

# Let's sort columns by Y then X
cols_sorted = sorted(cols, key=lambda c: (round(c['y'], 1), round(c['x'], 1)))
for i, c in enumerate(cols_sorted):
    print(f"Col #{i+1:02d}: x={c['x']:6.2f}, y={c['y']:6.2f}, w={c.get('w', 0.5):.2f}, d={c.get('d', 0.5):.2f}")


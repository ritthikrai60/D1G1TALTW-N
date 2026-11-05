import json
import re

# Read columns and slab from generated_basement_updated_payload.py
with open('scripts/generated_basement_updated_payload.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract slab and 77 columns
cols_and_slab_code = text.split('# 3. CORE STAIR (')[0].strip()

# Now build the 3 True Authentic Stairs
stairs_code = """
# === 3. ST-1: PRIMARY FIRE EGRESS STAIR CORE (Layer P-2 (0.15)) ===
# Location: X in [6.1, 9.5], Y in [3.5, 6.2]
# West Flight: 5 steps climbing North from Z = 0.00m to Mid-Landing (Z = 0.875m)
for s in range(5):
    z = round(s * 0.175, 3)
    y_pos = round(5.05 + s * 0.25, 3)
    st = box((6.15, y_pos, 0.00), (1.50, 0.28, z + 0.175), name=f'ST1_West_Step_{s+1}', color=(0.82, 0.76, 0.70, 1.0))
    st.layer = 'Stairs'

# ST-1 Mid-Landing at North (Z = 0.875m)
st1_mid = box((6.15, 6.28, 0.00), (3.30, 1.25, 0.875), name='ST1_Mid_Landing', color=(0.82, 0.76, 0.70, 1.0))
st1_mid.layer = 'Stairs'

# ST-1 Center Divider Rail
st1_rail = box((7.65, 3.50, 0.00), (0.10, 2.75, 1.20), name='ST1_Center_Rail', color=(0.50, 0.52, 0.55, 1.0))
st1_rail.layer = 'Stairs'

# ST-1 East Flight: 10 steps climbing North to South (overhead to Floor 01, Z = 0.875m to 2.625m)
for s in range(10):
    z = round(0.875 + s * 0.175, 3)
    y_pos = round(6.00 - s * 0.25, 3)
    st = box((7.75, y_pos, 0.00), (1.50, 0.28, z + 0.175), name=f'ST1_East_Step_{s+1}', color=(0.82, 0.76, 0.70, 1.0))
    st.layer = 'Stairs'

# === 4. ST-2: CENTRAL OPEN STAIR NEAR LOCKERS (Layer A-stair) ===
# Location: X in [7.9, 10.6], Y in [-13.2, -9.0]
# Entrance flight: 4 steps stepping East from Z = 0.00m to Lower Landing (Z = 0.70m)
for s in range(4):
    z = round(s * 0.175, 3)
    x_pos = round(8.00 + s * 0.25, 3)
    st = box((x_pos, -13.15, 0.00), (0.28, 1.45, z + 0.175), name=f'ST2_Entrance_Step_{s+1}', color=(0.75, 0.78, 0.85, 1.0))
    st.layer = 'Stairs'

# ST-2 Lower Landing (Z = 0.70m)
st2_low = box((8.85, -13.15, 0.00), (1.50, 1.65, 0.70), name='ST2_Lower_Landing', color=(0.75, 0.78, 0.85, 1.0))
st2_low.layer = 'Stairs'

# ST-2 Main Flight: 10 steps climbing North from Z = 0.70m up to 2.45m
for s in range(10):
    z = round(0.70 + s * 0.175, 3)
    y_pos = round(-11.45 + s * 0.25, 3)
    st = box((8.90, y_pos, 0.00), (1.45, 0.28, z + 0.175), name=f'ST2_Main_Step_{s+1}', color=(0.75, 0.78, 0.85, 1.0))
    st.layer = 'Stairs'

# ST-2 Mid-Landing at North (Z = 2.45m)
st2_mid = box((8.90, -8.95, 0.00), (1.50, 1.20, 2.45), name='ST2_Mid_Landing', color=(0.75, 0.78, 0.85, 1.0))
st2_mid.layer = 'Stairs'

# === 5. ST-3: SOUTH OUTDOOR LANDSCAPE STAIR (Layer A-stair) ===
# Location: X in [4.1, 8.9], Y in [-21.2, -18.0]
# 16 angled parallel steps climbing East from Z = 0.00m up to +2.40m
for s in range(16):
    z = round((s + 1) * 0.15, 3)
    x_pos = round(4.15 + s * 0.30, 3)
    y_pos = round(-21.15 + s * 0.038, 3)
    st = box((x_pos, y_pos, 0.00), (0.33, 2.60, z), name=f'ST3_Landscape_Step_{s+1:02d}', color=(0.86, 0.82, 0.76, 1.0))
    st.layer = 'Stairs'

# Viewport update
viewport.camera.target = QVector3D(8.0, -4.0, 1.5)
viewport.camera.distance = 55.0
viewport.camera.yaw = -0.75
viewport.camera.pitch = 0.55
viewport.update()
print(f'Model built perfectly! Total groups: {len(groups)}')
"""

full_code = cols_and_slab_code + "\n\n" + stairs_code
with open('scripts/final_basement_model_script.py', 'w', encoding='utf-8') as f:
    f.write(full_code)

print("Final accurate basement model script saved! Total chars:", len(full_code))


import math

# Let's inspect the exact bounding polygons for Floor 00
# 1. South Core & Service Rooms:
#   South edge: (-16.5, -25.9) to (-5.8, -24.1)
#   East edge: (-5.8, -24.1) to (-9.4, -1.8)
#   North edge: (-9.4, -1.8) to (-20.8, -3.5)
#   West edge: (-20.8, -3.5) to (-18.8, -18.0) to (-16.5, -25.9)

# 2. North Utility & Structural Rooms:
#   South edge: (-29.9, 8.5) to (-9.4, 7.5)
#   East edge: (-9.4, 7.5) to (-9.4, 32.0)
#   North edge: (-9.4, 32.0) to (-35.5, 32.2)
#   West edge: (-35.5, 32.2) to (-29.9, 16.4) to (-29.9, 8.5)

# 3. Main Parking & Inner Parking Driveway:
#   Main stalls #13-#30 + driveway: (-45.0, -28.5) to (-16.5, -28.5) up to Y = -11.5
#   Middle stalls #1-#12 + driveway: (-44.5, -11.5) to (-20.8, -11.5) up to Y = +10.0
#   Inner court stalls #31-#43 + driveway: (-39.0, +10.0) to (-29.9, +10.0) up to Y = +29.5

print("Polygons defined cleanly")


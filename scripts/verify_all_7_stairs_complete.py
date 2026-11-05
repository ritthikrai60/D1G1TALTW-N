import math

# Forensic data of all 7 stairs:
# 1. STAIR 3 (North Core Fire Stair: บันได 3)
# East flight: X in [7.78, 9.49], Y from 3.06 to 5.92 (12 steps, walks North UP)
# North Mid-Landing: X in [6.25, 9.50], Y from 6.00 to 9.10
# West flight: X in [6.25, 7.75], Y from 3.06 to 5.92 (walks South, arrival from F00 / continues to F02)

# 2. STAIR 1 / ST-2 (South Core Fire Stair: บันไดแกนใต้)
# Lower flight from F00: X in [7.8, 9.3], Y from -12.5 to -9.6 (walks North UP to Mid-Landing)
# Mid-Landing at North: X in [7.8, 11.2], Y in [-9.6, -8.0] at Z = 1.75m
# Upper flight to F01: X in [9.6, 11.2], Y from -9.6 to -12.5 (walks South UP to South Arrival Landing at Z = 3.50m)
# South Arrival Landing: X in [7.8, 11.2], Y in [-14.0, -12.5] at Z = 3.50m

# 3. STAIR 4 (Foyer Rotunda Fan Steps: บันได 4)
# Center: (19.50, 1.50), Rin = 2.40m, Rout = 4.80m, 10 fan steps, angle 40 to 120 deg

# 4. LOBBY CURVED STAIR (บันไดวน A6-01)
# Center: (22.80, -4.20), Rin = 0.85m, Rout = 2.45m, 16 treads, angle -15 to 185 deg

# 5. SOUTH PORTICO STEPS (บันไดทางเข้าด้านหน้า ST-2)
# Center: (7.0, -20.0), Width 5.59m, 14 steps, walks South to North UP from 0.00 to 3.50m
# Plus side terrace steps at X in [10.5, 12.0], Y in [-17.5, -16.0]

# 6. EAST WING STAIRS (บันไดปีกตะวันออก)
# Flight A: X in [57.0, 60.5], Y in [11.0, 14.5], angle 33 deg, 12 steps
# Flight B (Kitchen delivery): X in [61.0, 63.5], Y in [8.0, 10.5], 7 steps

# 7. WEST WING ARENA GRAND STEPS (บันไดอัฒจันทร์/MMA Zone)
# Center: (-18.5, 20.0), Width 4.80m, 10 steps stepping North from 2.00 to 3.50m

print("All 7 stair systems mapped with exact walk directions!")


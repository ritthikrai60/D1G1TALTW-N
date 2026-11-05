import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import shapely
from shapely.geometry import Polygon, MultiPolygon, LineString, box
import shapely.ops
# No matplotlib


doc = load_pdf_doc()['document']
X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

l_col = next(x for x in doc['layers'] if x['name'] == 'A-col')
l_wall = next(x for x in doc['layers'] if x['name'] == 'A-wall')

# Let's inspect the wall lines and build exact polygons:
# 1. North boundary retaining wall:
# Outer: Y = 43.107 from X=0.077 to 10.727
# Inner: Y = 42.857 from X=0.727 to 10.076
# Wall polygon: [ (0.077, 43.107), (10.727, 43.107), (10.727, 42.857), (0.077, 42.857) ]
p_north = Polygon([(0.077, 42.857), (10.727, 42.857), (10.727, 43.107), (0.077, 43.107)])

# 2. Central dividing wall (runs N-S between NW room and NE room):
# X in [4.577, 4.827], Y in [27.607, 42.857]
p_center_div = Polygon([(4.577, 27.607), (4.827, 27.607), (4.827, 42.857), (4.577, 42.857)])

# 3. Intermediate E-W dividing wall:
# Y in [27.607, 27.857], X in [0.402, 10.402]
p_mid_ew = Polygon([(0.402, 27.607), (10.402, 27.607), (10.402, 27.857), (0.402, 27.857)])

# 4. East retaining wall (runs N-S along entire east edge from stall 12 up to north wall):
# X in [10.402, 10.652], Y in [18.851, 43.107]
p_east_retaining = Polygon([(10.402, 18.851), (10.652, 18.851), (10.652, 43.107), (10.402, 43.107)])

# 5. Outer West wall of North rooms:
# child 2: [(0.402, 27.532), (0.402, 42.632), (0.152, 42.632), (0.152, 27.532)]
p_west_north = Polygon([(0.152, 27.532), (0.402, 27.532), (0.402, 43.107), (0.152, 43.107)])

# 6. Dividing wall between Room 1 (lower south room) and Room 2 (middle room):
# Y in [23.382, 23.632], X in [0.152, 10.402]
p_room1_2_div = Polygon([(0.152, 23.382), (10.402, 23.382), (10.402, 23.632), (0.152, 23.632)])

# 7. South wall directly behind parking stalls 9-12 (angled):
# Inner: from (0.402, 19.918) to (10.402, 19.125)
# Outer: from (0.152, 19.683) to (10.652, 18.851)
p_south_curb = Polygon([
    (0.152, 19.683), (10.652, 18.851),
    (10.652, 19.125), (0.152, 19.918)
])

# 8. West wall of Room 1 (lower south room):
# X in [0.152, 0.402], Y in [19.683, 23.382]
p_west_room1 = Polygon([(0.152, 19.683), (0.402, 19.683), (0.402, 23.382), (0.152, 23.382)])

# 9. West wall of Room 2 (middle room) with OPEN DOORWAY (no doors!):
# Room 2 Y range is [23.632, 27.532].
# Doorway opening is at Y in [24.819, 26.42] (width 1.60m double portal).
# Wall segment 9A (south of doorway): Y in [23.632, 24.819], X in [0.152, 0.402]
p_west_room2_south = Polygon([(0.152, 23.632), (0.402, 23.632), (0.402, 24.819), (0.152, 24.819)])
# Wall segment 9B (north of doorway): Y in [26.42, 27.532], X in [0.152, 0.402]
p_west_room2_north = Polygon([(0.152, 26.42), (0.402, 26.42), (0.402, 27.532), (0.152, 27.532)])

north_room_walls = [
    p_north, p_center_div, p_mid_ew, p_east_retaining,
    p_west_north, p_room1_2_div, p_south_curb, p_west_room1,
    p_west_room2_south, p_west_room2_north
]

print(f"Total north room wall pieces: {len(north_room_walls)}")
union_north = shapely.ops.unary_union(north_room_walls)
print(f"Union geom type: {union_north.geom_type}, area: {union_north.area:.2f} m^2")

# Let's check overlap with columns in this zone
cols_in_zone = []
for lname in ['A-col', 'P-1']:
    l = doc['layers']
    target = next((x for x in l if x['name'] == lname), None)
    if not target: continue
    for i, c in enumerate(target['kind']['children']):
        for sp in extract_subpaths(c):
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) >= 4:
                try:
                    p = Polygon(pts)
                    if p.is_valid and 0.04 <= p.area <= 3.0:
                        xs = [pt[0] for pt in pts]
                        ys = [pt[1] for pt in pts]
                        if -1.0 <= min(xs) and max(xs) <= 12.0 and 18.0 <= min(ys) and max(ys) <= 44.0:
                            cols_in_zone.append(p)
                except: pass

print(f"Columns in north room zone: {len(cols_in_zone)}")
fused = shapely.ops.unary_union(north_room_walls + cols_in_zone)
print(f"Fused with columns geom type: {fused.geom_type}, area: {fused.area:.2f} m^2")

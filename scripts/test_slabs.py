import sys
sys.path.insert(0, '.')
from scripts.verify_extraction import curb_pts, poly_area, ensure_ccw

# Build Parking Slab polygon:
# North edge: (-24.0, 21.0) -> (-1.0, 21.0)
# East edge meeting core: (-1.0, 6.0) -> (-11.5, 6.0) -> (-11.5, -3.5) -> (3.71, -3.5) -> (3.709, -16.219)
# South curb: reversed curb_pts from (3.709, -16.219) to (-18.849, -15.533)
# West edge: (-18.849, -15.533) -> (-24.0, -0.35) -> (-24.0, 21.0)

# Check curb_pts order:
print("curb_pts[0]:", curb_pts[0], "curb_pts[-1]:", curb_pts[-1])
# curb_pts[0] is (-18.849, -15.533) and curb_pts[-1] is (3.709, -16.219)
curb_reversed = curb_pts[::-1] # from (3.71, -16.22) to (-18.85, -15.53)

parking_poly = [
    (-24.0, 21.0),
    (-1.0, 21.0),
    (-1.0, 6.0),
    (-11.5, 6.0),
    (-11.5, -3.5),
    (3.71, -3.5),
] + curb_reversed + [
    (-24.0, -0.35),
    (-24.0, 21.0)
]
parking_poly = ensure_ccw(parking_poly[:-1])
print(f"Parking slab polygon valid: len={len(parking_poly)}, area={abs(poly_area(parking_poly)):.1f} m2")

# Service Core Slab:
# Covers the core rooms:
# East side: (10.7, 9.5) -> (14.3, -12.8) -> (9.5, -13.8) -> (-1.0, -13.8) -> (-1.0, -3.5) -> (-11.5, -3.5) -> (-11.5, 6.0) -> (-1.0, 6.0) -> (-1.0, 9.5)
core_slab_poly = [
    (-1.0, 9.5),
    (10.7, 9.5),
    (14.3, -12.8),
    (9.5, -13.8),
    (-1.0, -13.8),
    (-1.0, -3.5),
    (-11.5, -3.5),
    (-11.5, 6.0),
    (-1.0, 6.0),
]
core_slab_poly = ensure_ccw(core_slab_poly)
print(f"Core slab polygon valid: len={len(core_slab_poly)}, area={abs(poly_area(core_slab_poly)):.1f} m2")


import sys
sys.path.insert(0, '.')
from scripts.verify_extraction import curb_pts, poly_area, ensure_ccw

# Core Slab Polygon:
# North wing: (-11.5, 1.2) -> (-11.5, 6.5) -> (-1.0, 6.5) -> (-1.0, 9.5) -> (10.7, 9.5)
# East edge: (10.7, 9.5) -> (14.3, -12.8) -> (9.5, -14.0)
# South edge: (9.5, -14.0) -> (-0.5, -14.0)
# West edge: (-0.5, -14.0) -> (-0.5, 1.2) -> (-11.5, 1.2)
core_slab_poly = [
    (-11.5, 1.2),
    (-11.5, 6.5),
    (-1.0, 6.5),
    (-1.0, 9.5),
    (10.7, 9.5),
    (14.3, -12.8),
    (9.5, -14.0),
    (-0.5, -14.0),
    (-0.5, 1.2),
]
core_slab_poly = ensure_ccw(core_slab_poly)
print(f"Refined Core Slab: area={abs(poly_area(core_slab_poly)):.1f} m2, pts={len(core_slab_poly)}")

# Parking & Driveway Slab Polygon:
curb_reversed = curb_pts[::-1]
parking_poly = [
    (-24.0, 21.0),
    (-1.0, 21.0),
    (-1.0, 9.5),
    (-1.0, 6.5),
    (-11.5, 6.5),
    (-11.5, 1.2),
    (-0.5, 1.2),
    (-0.5, -14.0),
    (3.71, -14.0),
] + curb_reversed + [
    (-24.0, -0.35),
]
parking_poly = ensure_ccw(parking_poly)
print(f"Refined Parking & Driveway Slab: area={abs(poly_area(parking_poly)):.1f} m2, pts={len(parking_poly)}")


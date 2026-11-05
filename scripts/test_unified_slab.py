import sys
sys.path.insert(0, '.')
from scripts.verify_extraction import curb_pts
from scripts.verify_all_77_cols import ensure_ccw, poly_area

# Outer boundary connecting:
# Northwest corner (-26.0, 44.0)
# Northeast corner (32.0, 44.0)
# East hillside expansion (66.0, 22.0) down to (66.0, 6.0) then to (14.0, -10.0)
# South stair & entrance (10.0, -22.0) to (2.0, -22.0)
# Southwest curb curve to (-26.0, -0.35)
# West edge up to (-26.0, 44.0)

curb_rev = curb_pts[::-1]

unified_basement_poly = [
    (-26.0, 44.0),
    (32.0, 44.0),
    (32.0, 22.0),
    (66.0, 22.0),
    (66.0, 6.0),
    (14.0, -10.0),
    (10.0, -14.0),
    (10.0, -22.0),
    (2.0, -22.0),
    (2.0, -14.0),
    (3.71, -14.0),
] + curb_rev + [
    (-26.0, -0.35),
    (-26.0, 44.0)
]

unified_basement_poly = ensure_ccw(unified_basement_poly[:-1])
print(f"Unified basement slab polygon: {len(unified_basement_poly)} vertices, area={poly_area(unified_basement_poly):.2f} m2")


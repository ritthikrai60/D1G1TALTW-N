import sys
sys.path.insert(0, '.')
from scripts.verify_all_77_cols import ensure_ccw, poly_area

slabs = {
    'Slab_Open_Parking': [
        (-24.0, 21.0), (-1.0, 21.0), (-1.0, 9.5), (-1.0, 6.5),
        (-11.5, 6.5), (-11.5, 1.2), (-0.5, 1.2), (-0.5, -14.0),
        (3.71, -14.0), (3.709, -16.219), (-18.849, -15.533), (-24.0, -0.35)
    ],
    'Slab_Service_Core': [
        (-11.5, 1.2), (-11.5, 6.5), (-1.0, 6.5), (-1.0, 9.5),
        (10.7, 9.5), (14.3, -12.8), (9.5, -14.0), (-0.5, -14.0), (-0.5, 1.2)
    ],
    'Slab_North_Wing': [
        (-16.0, 21.0), (0.5, 21.0), (0.5, 43.5), (-16.0, 43.5)
    ],
    'Slab_North_Parking': [
        (-25.0, 21.0), (-16.0, 21.0), (-16.0, 43.5), (-25.0, 43.5)
    ],
    'Slab_North_Terrace': [
        (0.5, 19.5), (32.0, 19.5), (32.0, 43.5), (0.5, 43.5)
    ],
    'Slab_East_Slope': [
        (14.0, -10.0), (66.0, 6.0), (66.0, 22.0), (32.0, 22.0), (14.0, 9.5)
    ],
}

print("=== VERIFYING ALL SLAB POLYGONS ===")
for name, poly in slabs.items():
    ccw_poly = ensure_ccw(poly)
    area = abs(poly_area(ccw_poly))
    print(f"  {name:20s}: area = {area:7.1f} m2, pts = {len(ccw_poly)}")


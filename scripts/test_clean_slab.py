import sys
sys.path.insert(0, '.')
from shapely.geometry import Polygon, Point, LineString

# Test clean line from (10.0, -22.0) to (68.0, 5.0)
cols = [(20.29, -10.73), (30.82, -8.58), (41.48, -3.87), (51.56, 0.91), (57.51, 4.09), (63.71, 7.95)]
for c in cols:
    y_line = -22.0 + (c[0] - 10.0) / 58.0 * 27.0
    status = "INSIDE" if c[1] > y_line else "OUTSIDE"
    print(f"Col at {c}: line y = {y_line:6.2f}, diff = {c[1]-y_line:5.2f}m -> {status}")


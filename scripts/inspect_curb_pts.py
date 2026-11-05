import sys
sys.path.insert(0, '.')
from scripts.verify_extraction import curb_pts

# Let's inspect curb_pts and south boundary
print("curb_pts[0] (south-west):", curb_pts[0])
print("curb_pts[-1] (south-east near entrance):", curb_pts[-1])
for i, pt in enumerate(curb_pts):
    if i % 5 == 0 or i == len(curb_pts)-1:
        print(f"  curb[{i:2d}]: ({pt[0]:.2f}, {pt[1]:.2f})")


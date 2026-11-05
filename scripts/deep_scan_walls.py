import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import load_pdf_doc, extract_subpaths
import shapely
from shapely.geometry import Polygon, MultiPolygon, LineString, Point
import shapely.ops
from PIL import Image, ImageDraw
import os

doc = load_pdf_doc()['document']
layers = {l['name']: l for l in doc['layers']}

X0 = 1000.0
Y0 = 1500.0
SCALE = 28.3464567

def to_m(pt):
    return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Let's inspect ALL layers that could contain walls:
# 'A-wall', 'WALL', 'P-1 (0.50)', 'P-2 (0.15)', 'P-4 (0.10)', 'P-3 (0.25)', 'P-4', 'P-2', 'P-3', 'P-5', 'เส้นบาง'

candidates = ['A-wall', 'WALL', 'P-1 (0.50)', 'P-2 (0.15)', 'P-4 (0.10)', 'P-3 (0.25)', 'P-4', 'P-2', 'P-3', 'P-5', 'WC-OUTL', 'WC-DET1']

print("=== DEEP FORENSIC SCAN OF ALL WALL CANDIDATES ===")
for cname in candidates:
    l = layers.get(cname)
    if not l: continue
    ch = l['kind'].get('children', [])
    print(f"Layer '{cname}': {len(ch)} children")

# Let's check where walls exist geographically across the whole site:
# North wing (Y > 20)
# South wing (Y < -10)
# West wing (X < -10)
# East wing (X > 20)
# Center core (-5 < X < 15, -10 < Y < 15)



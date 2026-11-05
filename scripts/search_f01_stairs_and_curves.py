import zlib, re, json
import sys
sys.path.insert(0, '.')
from scripts.inspect_paths import extract_subpaths
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box

with open(r'c:\Coding Projects\Digital Twin\01-First_Floor-Clean.pdf', 'rb') as f: data = f.read()
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
s1 = zlib.decompress(streams[1]).decode('utf-8')
meta = json.loads(s1)
doc = meta['document']

X0, Y0, SCALE = 1000.0, 1500.0, 28.3464567
def to_m(pt): return (round((pt[0] - X0) / SCALE, 3), round(-(pt[1] - Y0) / SCALE, 3))

# Search text in PDF for stair / ST / lobby / etc.
print("=== Text Search in Stream 1 ===")
text_matches = re.findall(r'(\bST[-\s]?\d+|\bSTAIR|\bUP\b|\bDN\b|\bLOBBY\b|FOYER|HALL)', s1, re.IGNORECASE)
print(f"Text tokens found: {set(text_matches)}")

# Check text objects in layers if any
for l in doc['layers']:
    for c in l['kind']['children']:
        # if there are text fields
        if 'text' in c or 'Text' in c:
            print(f"Layer {l['name']} has text: {c}")

# Let's inspect layers with arcs or curves or circles
# In SVG/vector paths, curves have control points (in/out handles)
curved_elements = []
for l in doc['layers']:
    for idx, c in enumerate(l['kind']['children']):
        for sp in extract_subpaths(c):
            # check if anchors have handles
            has_curve = False
            for pt in sp.get('points', []):
                # check if handle_in or handle_out differs from anchor
                pass
            # or if points > 10 in small radius
            pts = [to_m(p) for p in sp['anchors']]
            if len(pts) > 6:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                dx = max(xs) - min(xs)
                dy = max(ys) - min(ys)
                if 2.0 <= dx <= 15.0 and 2.0 <= dy <= 15.0:
                    curved_elements.append((l['name'], idx, len(pts), min(xs), max(xs), min(ys), max(ys)))

print(f"\nPotential circular/curved elements (candidates for spiral stair or rotunda): {len(curved_elements)}")
for item in curved_elements[:20]:
    print(f"  Layer {item[0]:15s} child {item[1]:3d}: {item[2]:2d} pts, X=[{item[3]:.2f}, {item[4]:.2f}], Y=[{item[5]:.2f}, {item[6]:.2f}]")


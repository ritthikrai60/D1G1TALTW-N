import sys
sys.path.insert(0, '.')
from scripts.inspect_stairs_deep import groups

north_items = groups.get('north_stair', [])
print(f"Total north items in A-stair: {len(north_items)}")
for it in north_items[:20]:
    print(f"  Item {it['idx']:3d}: pts={it['pts_len']}, w={it['w']:.2f}m, h={it['h']:.2f}m, at ({it['cx']:.1f}, {it['cy']:.1f}), m=({it['cx_m']:.2f}, {it['cy_m']:.2f})")


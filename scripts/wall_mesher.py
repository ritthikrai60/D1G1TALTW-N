import shapely
from shapely.geometry import Polygon
from shapely.ops import triangulate
import uuid

def polygon_with_holes_to_group(poly, z0, z1, name, layer_name, color=(0.92, 0.90, 0.86, 1.0)):
    faces = []
    edges = []
    
    # 1. Triangulate top and bottom faces
    triangles = [t for t in triangulate(poly) if poly.contains(t.centroid)]
    
    # Bottom faces (CW)
    for t in triangles:
        coords = list(t.exterior.coords)[:-1]
        v_bot = [[pt[0], pt[1], z0] for pt in reversed(coords)]
        faces.append({'vertices': v_bot, 'color': list(color)})
        
    # Top faces (CCW)
    for t in triangles:
        coords = list(t.exterior.coords)[:-1]
        v_top = [[pt[0], pt[1], z1] for pt in coords]
        faces.append({'vertices': v_top, 'color': list(color)})
        
    # 2. Side walls for exterior ring
    ext_coords = list(poly.exterior.coords)[:-1]
    n_ext = len(ext_coords)
    for i in range(n_ext):
        p1 = ext_coords[i]
        p2 = ext_coords[(i + 1) % n_ext]
        quad = [
            [p1[0], p1[1], z0],
            [p2[0], p2[1], z0],
            [p2[0], p2[1], z1],
            [p1[0], p1[1], z1]
        ]
        faces.append({'vertices': quad, 'color': list(color)})
        edges.append({'a': [p1[0], p1[1], z0], 'b': [p2[0], p2[1], z0]})
        edges.append({'a': [p1[0], p1[1], z1], 'b': [p2[0], p2[1], z1]})
        edges.append({'a': [p1[0], p1[1], z0], 'b': [p1[0], p1[1], z1]})
        
    # 3. Side walls for interior rings (holes)
    for interior in poly.interiors:
        int_coords = list(interior.coords)[:-1]
        n_int = len(int_coords)
        for i in range(n_int):
            p1 = int_coords[i]
            p2 = int_coords[(i + 1) % n_int]
            # hole normal faces inwards
            quad = [
                [p1[0], p1[1], z0],
                [p1[0], p1[1], z1],
                [p2[0], p2[1], z1],
                [p2[0], p2[1], z0]
            ]
            faces.append({'vertices': quad, 'color': list(color)})
            edges.append({'a': [p1[0], p1[1], z0], 'b': [p2[0], p2[1], z0]})
            edges.append({'a': [p1[0], p1[1], z1], 'b': [p2[0], p2[1], z1]})
            edges.append({'a': [p1[0], p1[1], z0], 'b': [p1[0], p1[1], z1]})
            
    return {
        'name': name,
        'layer': layer_name,
        'uid': uuid.uuid4().hex[:16],
        'faces': faces,
        'edges': edges
    }

print("Wall mesher defined.")


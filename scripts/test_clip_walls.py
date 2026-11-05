import math

def clip_walls_with_doors(walls, doors, door_margin=0.05):
    """
    Subdivide wall segments that pass through door openings so doorways remain open.
    """
    split_walls = []
    for w in walls:
        p1 = list(w["p1"])
        p2 = list(w["p2"])
        layer = w.get("layer", "")
        vx = p2[0] - p1[0]
        vy = p2[1] - p1[1]
        length = math.hypot(vx, vy)
        if length < 0.3:
            continue
        
        # Check intersections with any door
        cuts = []
        for d in doors:
            dx, dy = d["x"], d["y"]
            dw = d["width_m"] * 0.5 + door_margin
            # project d onto segment
            t = ((dx - p1[0]) * vx + (dy - p1[1]) * vy) / (length * length)
            proj_x = p1[0] + t * vx
            proj_y = p1[1] + t * vy
            dist = math.hypot(dx - proj_x, dy - proj_y)
            if dist < 0.35 and 0.0 < t < 1.0: # door intersects this wall
                # compute t_start and t_end
                t_start = max(0.0, t - dw / length)
                t_end = min(1.0, t + dw / length)
                if t_end > t_start:
                    cuts.append((t_start, t_end, d))
        
        if not cuts:
            split_walls.append({"p1": p1, "p2": p2, "layer": layer})
        else:
            # Sort cuts by t_start
            cuts.sort(key=lambda c: c[0])
            # Merge overlapping cuts
            merged_cuts = []
            for c in cuts:
                if not merged_cuts:
                    merged_cuts.append(c)
                else:
                    last_start, last_end, last_d = merged_cuts[-1]
                    if c[0] <= last_end:
                        merged_cuts[-1] = (last_start, max(last_end, c[1]), last_d)
                    else:
                        merged_cuts.append(c)
            
            curr_t = 0.0
            for c_start, c_end, d in merged_cuts:
                if c_start > curr_t + 0.15:
                    pt1 = [p1[0] + curr_t * vx, p1[1] + curr_t * vy]
                    pt2 = [p1[0] + c_start * vx, p1[1] + c_start * vy]
                    split_walls.append({"p1": pt1, "p2": pt2, "layer": layer})
                curr_t = c_end
            if curr_t < 1.0 - 0.15:
                pt1 = [p1[0] + curr_t * vx, p1[1] + curr_t * vy]
                pt2 = [p1[0] + 1.0 * vx, p1[1] + 1.0 * vy]
                split_walls.append({"p1": pt1, "p2": pt2, "layer": layer})
                
    return split_walls

print("Clip function ready")


def _normalize_winding(face_pts, sweep_vec):
    p0, p1, p2 = face_pts[0], face_pts[1], face_pts[2]
    v1 = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
    v2 = [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]]
    n = [
        v1[1]*v2[2] - v1[2]*v2[1],
        v1[2]*v2[0] - v1[0]*v2[2],
        v1[0]*v2[1] - v1[1]*v2[0]
    ]
    dot = n[0]*sweep_vec[0] + n[1]*sweep_vec[1] + n[2]*sweep_vec[2]
    
    # We can check for degeneracy!
    mag_n = (n[0]**2 + n[1]**2 + n[2]**2)**0.5
    mag_s = (sweep_vec[0]**2 + sweep_vec[1]**2 + sweep_vec[2]**2)**0.5
    if mag_n == 0 or mag_s == 0:
        return False
    if abs(dot) / (mag_n * mag_s) < 1e-4:
        return False # Orthogonal (degenerate)
        
    if dot < 0:
        face_pts.reverse()
    return True

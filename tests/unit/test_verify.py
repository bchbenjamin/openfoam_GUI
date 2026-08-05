def cross(v1, v2):
    """

    Args:
      v1: 
      v2: 

    Returns:

    """
    return [v1[1]*v2[2] - v1[2]*v2[1], v1[2]*v2[0] - v1[0]*v2[2], v1[0]*v2[1] - v1[1]*v2[0]]

pts_align = [[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [2.0, 0.0, 1.0], [1.0, 0.0, 1.0]] 
v1 = [pts_align[1][i] - pts_align[0][i] for i in range(3)]
v2 = [pts_align[2][i] - pts_align[1][i] for i in range(3)]
n1 = cross(v1, v2)
print("pts_align normal:", n1)

pts_oppose = list(reversed(pts_align))
v1 = [pts_oppose[1][i] - pts_oppose[0][i] for i in range(3)]
v2 = [pts_oppose[2][i] - pts_oppose[1][i] for i in range(3)]
n2 = cross(v1, v2)
print("pts_oppose normal:", n2)

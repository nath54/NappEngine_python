#
from math import sin, cos, atan, pi
#
from lib_nadisplay_rects import ND_Point


#
def calc_rad_agl_about_h_axis(x1: int, y1: int, x2: int, y2: int) -> float:
    #
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    #
    if x2 == x1:
        if y2 == y1:
            raise RuntimeError("Error: Cannot calculate an angle with two points that are equals")
        if y2 < y1:
            return 0
        if y2 > y1:
            return pi
    if x2 < x1:
        if y2 == y1:
            return pi * 3 / 2
        if y2 < y1:
            return 2 * pi - atan( dx / dy )
        if y2 > y1:
            return pi + atan( dx / dy )
    if x2 > x1:
        if y2 == y1:
            return pi / 2
        if y2 < y1:
            return atan( dx / dy )
        if y2 > y1:
            return pi - atan( dx / dy )
    #
    raise RuntimeError("Error: Code reached point that it shouldn't")


#
def calc_point_with_angle_and_distance_from_another_point(x1: int, y1: int, alpha: float, t: float) -> tuple[int, int]:
    #
    x2: int = int( x1 + t * cos(alpha) )
    y2: int = int( y1 + t * sin(alpha) )
    #
    return x2, y2


#
def convert_deg_to_rad(angle_in_deg: float) -> float:
    #
    return (angle_in_deg * pi) / 180.0




def earcut_triangulate_polygon(points: list[ND_Point]) -> list[tuple[ND_Point, ND_Point, ND_Point]]:
    #
    triangles: list[tuple[ND_Point, ND_Point, ND_Point]] = []
    remaining = points[:]
    #
    while len(remaining) > 3:
        ear_found = False
        for i in range(len(remaining)):
            prev, curr, next = remaining[i - 1], remaining[i], remaining[(i + 1) % len(remaining)]
            if earcut_is_ear(prev, curr, next, remaining):
                triangles.append((prev, curr, next))
                del remaining[i]
                ear_found = True
                break
        #
        if not ear_found:
            break  # If no ear is found, terminate early to avoid infinite loops
    #
    if len(remaining) == 3:
        triangles.append((remaining[0], remaining[1], remaining[2]))
    #
    return triangles

#
def earcut_is_ear(prev: ND_Point, curr: ND_Point, next: ND_Point, points: list[ND_Point]) -> bool:
    if not earcut_is_convex(prev, curr, next):
        return False
    for p in points:
        if p not in (prev, curr, next) and earcut_is_point_inside_triangle(p, prev, curr, next):
            return False
    return True

#
def earcut_is_convex(a: ND_Point, b: ND_Point, c: ND_Point) -> bool:
    cross_product = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
    return cross_product > 0

#
def earcut_is_point_inside_triangle(p: ND_Point, a: ND_Point, b: ND_Point, c: ND_Point) -> bool:
    def sign(p1: ND_Point, p2: ND_Point, p3: ND_Point):
        return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)

    d1, d2, d3 = sign(p, a, b), sign(p, b, c), sign(p, c, a)
    has_neg, has_pos = (d1 < 0) or (d2 < 0) or (d3 < 0), (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)

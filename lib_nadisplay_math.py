from math import sin, cos, atan, pi


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



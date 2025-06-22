"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Some utility classes for manipuling points, rects and base elements positions.

"""

#
from typing import Optional
#
from lib_nadisplay_point import ND_Point


#
class ND_Rect:
    #
    def __init__(self, x: int, y: int, w: int = 1, h: int = 1) -> None:
        #
        self.x: int = x
        self.y: int = y
        self.w: int = w
        self.h: int = h


    #
    def __hash__(self) -> int:
        return hash(f"{self.x}_{self.y}_{self.w}_{self.h}")


    #
    def __repr__(self) -> str:
        #
        return f"ND_Rect(x={self.x}, y={self.y}, w={self.w}, h={self.h})"


    #
    @property
    def left(self) -> int:
        #
        return self.x


    #
    @property
    def right(self) -> int:
        #
        return self.x + self.w


    #
    @property
    def top(self) -> int:
        #
        return self.y


    #
    @property
    def bottom(self) -> int:
        #
        return self.y + self.h


    #
    def intersects_with_other_rect(self, other: "ND_Rect") -> bool:
        #
        return (self.left < other.right and self.right > other.left and
                self.top < other.bottom and self.bottom > other.top)


    #
    def get_intersection_area_with_other_rect(self, other: "ND_Rect") -> Optional["ND_Rect"]:
        #
        if not self.intersects_with_other_rect(other):
            return None

        #
        x: int = max(self.left, other.left)
        y: int = max(self.top, other.top)
        w: int = min(self.right, other.right) - x
        h: int = min(self.bottom, other.bottom) - y

        #
        return ND_Rect(x, y, w, h)


    #
    def union(self, other: "ND_Rect") -> "ND_Rect":
        #
        x: int = min(self.left, other.left)
        y: int = min(self.top, other.top)
        w: int = max(self.right, other.right) - x
        h: int = max(self.bottom, other.bottom) - y

        #
        return ND_Rect(x, y, w, h)


    #
    @staticmethod
    def enclose_points(points: list[tuple[int, int] | ND_Point]) -> Optional["ND_Rect"]:
        #
        if not points:
            return None

        #
        def get_x(p: tuple[int, int] | ND_Point):
            return p[0] if isinstance(p, tuple) else p.x

        #
        def get_y(p: tuple[int, int] | ND_Point):
            return p[1] if isinstance(p, tuple) else p.y

        #
        x_min: int = get_x(min(points, key=get_x))
        y_min: int = get_y(min(points, key=get_y))
        x_max: int = get_x(max(points, key=get_x))
        y_max: int = get_y(max(points, key=get_y))

        #
        return ND_Rect(x_min, y_min, x_max - x_min, y_max - y_min)


    #
    def contains_point(self, point: ND_Point) -> bool:
        #
        return (self.left <= point.x < self.right and
                self.top <= point.y < self.bottom)


"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Some utility classes for base elements positions.

"""

#
from typing import Optional
#
from lib_nadisplay_rects import ND_Rect

# Define a small epsilon for floating point comparisons to handle precision issues
# Adjust based on expected scale of coordinates if needed
EPSILON: float = 1e-6


#
class ND_Position_Margins:
    """
    if is int, it is pixel value, else if is string, is "value_float%",
    where it indicates the repartition of available empty space between the element to share between his sides.
    """

    def __init__(
        self,
        margin: Optional[int | str] = None,
        margin_left: Optional[int | str] = None,
        margin_right: Optional[int | str] = None,
        margin_top: Optional[int | str] = None,
        margin_bottom: Optional[int | str] = None,
        #
        min_margin_left: int = 0,
        min_margin_right: int = 0,
        min_margin_top: int = 0,
        min_margin_bottom: int = 0,
        #
        width_stretch_ratio: float = 1.0,
        height_stretch_ratio: float = 1.0
    ) -> None:

        #
        self.margin: Optional[int | str] = margin
        self.margin_left: Optional[int | str] = margin_left
        self.margin_right: Optional[int | str] = margin_right
        self.margin_top: Optional[int | str] = margin_top
        self.margin_bottom: Optional[int | str] = margin_bottom
        #
        self.min_margin_left: int = min_margin_left
        self.min_margin_right: int = min_margin_right
        self.min_margin_top: int = min_margin_top
        self.min_margin_bottom: int = min_margin_bottom
        #
        self.width_stretch_ratio: float = width_stretch_ratio
        self.height_stretch_ratio: float = height_stretch_ratio


#
class ND_Position_Constraints:
    """
    If is int, it is pixel value, else if is string, it is "value_float%" where it indicates the percentage of the containers row or column size.
    If the min and max values are both specified and of the same value, it forces the size to be that value.
    """

    #
    def __init__(
        self,
        min_width: Optional[int] = None,
        max_width: Optional[int] = None,
        min_height: Optional[int] = None,
        max_height: Optional[int] = None,
    ) -> None:

        #
        self.min_width: Optional[int] = min_width
        self.max_width: Optional[int] = max_width
        self.min_height: Optional[int] = min_height
        self.max_height: Optional[int] = max_height


#
class ND_Position:
    #
    def __init__(self, x: int = 0, y: int = 0, w: int = -1, h: int = -1) -> None:
        """
        With or Height with negative value is like auto width and height.
        In a grid it will take the maximum grid size.
        If a min and max value are specified, and a maximum column/row size are specified to, it will try to adjust to the best while beeing clamped.
        If a min and max value are specified, and no other constraints, it will just sit in the middle of the min and max values.
        """
        #
        self._x: int = x
        self._y: int = y
        self._w: int = w
        self._h: int = h

    #
    @property
    def x(self) -> int:
        #
        return self._x

    #
    @x.setter
    def x(self, new_x: int) -> None:
        #
        self._x = new_x

    #
    @property
    def y(self) -> int:
        #
        return self._y

    #
    @y.setter
    def y(self, new_y: int) -> None:
        #
        self._y = new_y

    #
    @property
    def w(self) -> int:
        #
        return self._w

    #
    @w.setter
    def w(self, new_w: int) -> None:
        #
        self._w = new_w

    #
    @property
    def h(self) -> int:
        #
        return self._h

    #
    @h.setter
    def h(self, new_h: int) -> None:
        #
        self._h = new_h

    #
    @property
    def rect(self) -> ND_Rect:
        #
        return ND_Rect(self.x, self.y, self.w, self.h)

    #
    @property
    def visible(self) -> bool:
        #
        return True

    #
    def __repr__(self) -> str:
        return f"Position(x={self.x}, y={self.y}, w={self.w}, h={self.h})"

    #
    def set_x(self, new_x: int) -> None:
        self._x = new_x

    #
    def set_y(self, new_y: int) -> None:
        self._y = new_y

    #
    def set_w(self, new_w: int) -> None:
        self._w = new_w

    #
    def set_h(self, new_h: int) -> None:
        self._h = new_h

    #
    def get_min_width(self) -> int:
        #
        return self._w

    #
    def get_max_width(self) -> int:
        #
        return self._w

    #
    def get_min_height(self) -> int:
        #
        return self._h

    #
    def get_max_height(self) -> int:
        #
        return self._h

    #
    def get_margin_top(self, space_left: int = -1) -> int:
        #
        return 0

    #
    def get_margin_bottom(self, space_left: int = -1) -> int:
        #
        return 0

    #
    def get_margin_left(self, space_left: int = -1) -> int:
        #
        return 0

    #
    def get_margin_right(self, space_left: int = -1) -> int:
        #
        return 0

    #
    def get_width_stretch_ratio(self) -> float:
        #
        return 1

    #
    def get_height_stretch_ratio(self) -> float:
        #
        return 1



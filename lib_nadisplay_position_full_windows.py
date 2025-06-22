"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""

#
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window


#
class ND_Position_FullWindow(ND_Position):
    #
    def __init__(self, window: ND_Window) -> None:
        #
        super().__init__()
        #
        self.window = window

    #
    @property
    def x(self) -> int:
        return 0

    #
    @x.setter
    def x(self, new_x: int) -> None:
        # TODO
        pass

    #
    @property
    def y(self) -> int:
        return 0

    #
    @y.setter
    def y(self, new_y: int) -> None:
        # TODO
        pass

    #
    @property
    def w(self) -> int:
        return self.window.width

    #
    @w.setter
    def w(self, new_w: int) -> None:
        # TODO
        pass

    #
    @property
    def h(self) -> int:
        return self.window.height

    #
    @h.setter
    def h(self, new_h: int) -> None:
        # TODO
        pass


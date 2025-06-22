"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""


#
from typing import Optional
#
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window, ND_Elt
from lib_nadisplay_point_3d import ND_Point_3D



#
class ND_Elt_3D:

    #
    def __init__(self, origin: ND_Point_3D) -> None:
        #
        self.origin: ND_Point_3D = origin

    #
    def render(self) -> None:
        #
        pass


#
class ND_Space_3D(ND_Elt):

    #
    def __init__(self, window: ND_Window, elt_id: str, position: ND_Position, elts: Optional[list[ND_Elt_3D]] = None ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position)

        #
        self.elts: list[ND_Elt_3D] = elts if elts is not None else []

    #
    def render(self) -> None:
        # Will be rendered by a ND_Camera_3D
        pass


#
class ND_Camera_3D(ND_Elt):

    #
    def __init__(self, window: ND_Window, elt_id: str, position: ND_Position, space_3D: ND_Space_3D) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.space_3D: ND_Space_3D = space_3D

    #
    def render(self) -> None:
        # TODO
        return


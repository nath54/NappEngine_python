"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""


#
from typing import Optional, Any
#
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window, ND_Elt, ND_EventsHandler_Elts
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
    def __init__(
            self, window: ND_Window,
            elt_id: str,
            position: ND_Position,
            elts: Optional[list[ND_Elt_3D]] = None,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)

        #
        self.elts: list[ND_Elt_3D] = elts if elts is not None else []

    #
    def render(self) -> None:
        # Will be rendered by a ND_Elt_Camera_3D
        pass


#
class ND_Elt_Camera_3D(ND_Elt):

    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position:ND_Position,
            space_3D: ND_Space_3D,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)
        #
        self.space_3D: ND_Space_3D = space_3D

    #
    def render(self) -> None:
        # TODO
        return


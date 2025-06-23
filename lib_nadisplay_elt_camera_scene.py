"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""

#
from typing import Optional, Any
#
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window, ND_Scene, ND_Elt, ND_EventsHandler_Elts

#
class ND_Elt_CameraScene(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            scene_to_render: ND_Scene,
            zoom: float = 1.0,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)
        #
        self.scene_to_render: ND_Scene = scene_to_render
        self.zoom: float = zoom

    #
    def render(self) -> None:
        # TODO
        pass
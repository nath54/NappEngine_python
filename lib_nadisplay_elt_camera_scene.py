"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""


#
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window, ND_Scene, ND_Elt

#
class ND_Elt_CameraScene(ND_Elt):
    #
    def __init__(self, window: ND_Window, elt_id: str, position: ND_Position, scene_to_render: ND_Scene, zoom: float = 1.0) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.scene_to_render: ND_Scene = scene_to_render
        self.zoom: float = zoom

    #
    def render(self) -> None:
        # TODO
        pass
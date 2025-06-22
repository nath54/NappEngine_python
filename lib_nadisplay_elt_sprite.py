"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""


from typing import Callable, Optional
#
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window
from lib_nadisplay_transformation import ND_Transformation
from lib_nadisplay_val import ND_Val  # type: ignore
from lib_nadisplay_core import ND_MainApp, ND_Display, ND_EventsManager  # type: ignore
from lib_nadisplay_elt_text import ND_Elt_Text  # type: ignore
from lib_nadisplay_elt_clickable import ND_Elt_Clickable  # type: ignore
from lib_nadisplay_elt_rectangle import ND_Elt_Rectangle  # type: ignore
from lib_nadisplay_elt_text import ND_Elt_Text  # type: ignore
from lib_nadisplay_elt_text import ND_Elt_Text  # type: ignore



# ND_Elt_Sprite class implementation
class ND_Elt_Sprite(ND_Elt_Clickable):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            onclick: Optional[Callable[["ND_Elt_Clickable"], None]] = None,
            mouse_active: bool = True,
            base_texture: Optional[int | str] = None,
            hover_texture: Optional[int | str] = None,
            clicked_texture: Optional[int | str] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, onclick=onclick, active=mouse_active)
        self.base_texture: Optional[int | str] = base_texture
        self.hover_texture: Optional[int | str] = self.window.prepare_image_to_render(hover_texture) if isinstance(hover_texture, str) else hover_texture
        self.clicked_texture: Optional[int | str] = self.window.prepare_image_to_render(clicked_texture) if isinstance(clicked_texture, str) else clicked_texture
        #
        self.transformations = ND_Transformation()

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        #
        texture: Optional[int] = None

        # Getting the right colors along the state
        if self.state == "hover" and self.hover_texture is not None:
            if isinstance(self.hover_texture, str):
                self.hover_texture = self.window.prepare_image_to_render(self.hover_texture)
            #
            texture = self.hover_texture
        elif self.state == "clicked" and self.clicked_texture is not None:
            if isinstance(self.clicked_texture, str):
                self.clicked_texture = self.window.prepare_image_to_render(self.clicked_texture)
            #
            texture = self.clicked_texture
        #
        if texture is None:
            if isinstance(self.base_texture, str):
                self.base_texture = self.window.prepare_image_to_render(self.base_texture)
            #
            texture = self.base_texture

        # Drawing the background rect color or texture
        if texture is not None:
            # print(f"DEBUG | rendering texture id {texture} at x={self.x}, y={self.y}, w={self.w}, h={self.h}")
            self.window.render_prepared_texture(texture, self.x, self.y, self.w, self.h, self.transformations)

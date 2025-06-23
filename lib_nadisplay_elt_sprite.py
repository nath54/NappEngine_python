"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""


from typing import Optional, Any
#
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window, ND_Elt, ND_EventsHandler_Elts
from lib_nadisplay_transformation import ND_Transformation



# ND_Elt_Sprite class implementation
class ND_Elt_Sprite(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            base_texture: Optional[int | str] = None,
            hover_texture: Optional[int | str] = None,
            clicked_texture: Optional[int | str] = None,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)
        #
        self.base_texture: Optional[int] = self.window.prepare_image_to_render(base_texture) if isinstance(base_texture, str) else base_texture
        self.hover_texture: Optional[int] = self.window.prepare_image_to_render(hover_texture) if isinstance(hover_texture, str) else hover_texture
        self.clicked_texture: Optional[int] = self.window.prepare_image_to_render(clicked_texture) if isinstance(clicked_texture, str) else clicked_texture

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        #
        texture: Optional[int] = None

        #
        if self.elt_state == "hover" and self.hover_texture is not None:
            #
            texture = self.hover_texture
        #
        elif self.elt_state == "clicked" and self.clicked_texture is not None:
            #
            texture = self.clicked_texture
        #
        if texture is not None:
            #
            texture = self.base_texture

        #
        transformation: ND_Transformation = self.get_style_attribute_transformation(attribute_name="transformation")

        # Drawing the background rect color or texture
        if texture is not None:
            # print(f"DEBUG | rendering texture id {texture} at x={self.x}, y={self.y}, w={self.w}, h={self.h}")
            self.window.render_prepared_texture(texture_id=texture, x=self.x, y=self.y, width=self.w, height=self.h, transformations=transformation)

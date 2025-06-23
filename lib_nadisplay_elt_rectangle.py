"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""

#
from typing import Optional, Any
#
from lib_nadisplay_colors import ND_Color, cl
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window, ND_Elt, ND_EventsHandler_Elts
from lib_nadisplay_transformation import ND_Transformation



# ND_Elt_Rectangle class implementation
class ND_Elt_Rectangle(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        #
        x, y = self.x, self.y

        #
        bg_color: ND_Color = self.get_style_attribute_color(attribute_name="bg_color")
        border_color: ND_Color = self.get_style_attribute_color(attribute_name="border_color")
        border_size: int = self.get_style_attribute_int(attribute_name="border_size")
        border_radius: int = self.get_style_attribute_int(attribute_name="border_radius")
        bg_texture: Optional[int] = self.get_style_attribute_texture_id(attribute_name="bg_texture")
        #
        texture_transformations: ND_Transformation = self.get_style_attribute_transformation(attribute_name="transformation")

        # Drawing the background rect color or texture
        if bg_texture:
            self.window.render_prepared_texture(texture_id=bg_texture, x=x, y=y, width=self.w, height=self.h, transformations=texture_transformations)
        else:
            if border_size <= 0 and border_radius <= 0:
                self.window.draw_filled_rect(x=x, y=y, width=self.w, height=self.h, fill_color=bg_color)
            elif border_size:
                self.window.draw_rounded_rect(x=x, y=y, width=self.w, height=self.h, radius=border_radius, fill_color=bg_color, border_color=cl((0, 0, 0, 0)), border_size=border_size)
            else:
                self.window.draw_rounded_rect(x=x, y=y, width=self.w, height=self.h, radius=border_radius, fill_color=bg_color, border_color=border_color, border_size=border_size)

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
from lib_nadisplay_utils import get_font_size
from lib_nadisplay_core import ND_Window, ND_Elt, ND_EventsHandler_Elts
from lib_nadisplay_transformation import ND_Transformation



# ND_Elt_Button class implementation
class ND_Elt_Button(ND_Elt):

    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            text: str,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)
        #
        self.text: str = text
        #
        self.bases_text_sizes: dict[int, tuple[int, int]] = {}

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        #
        x, y = self.x, self.y

        #
        font_name: str = self.get_style_attribute_str(attribute_name="font_name")
        font_size: int = self.get_style_attribute_int(attribute_name="font_size")
        font_color: ND_Color = self.get_style_attribute_color(attribute_name="font_color")
        bg_color: ND_Color = self.get_style_attribute_color(attribute_name="bg_color")
        border_color: ND_Color = self.get_style_attribute_color(attribute_name="border_color")
        border_size: int = self.get_style_attribute_int(attribute_name="border_size")
        border_radius: int = self.get_style_attribute_int(attribute_name="border_radius")
        bg_texture: Optional[int] = self.get_style_attribute_texture_id(attribute_name="bg_texture")
        #
        texture_transformations: ND_Transformation = self.get_style_attribute_transformation(attribute_name="transformation")

        # Drawing the background rect color or texture
        #
        if bg_texture:
            #
            self.window.render_prepared_texture(bg_texture, x, y, self.w, self.h, transformations=texture_transformations)
        #
        else:
            #
            if border_size <= 0 and border_radius <= 0:
                #
                self.window.draw_filled_rect(x=x, y=y, width=self.w, height=self.h, fill_color=bg_color)
            #
            elif not border_size <= 0:
                #
                self.window.draw_rounded_rect(x=x, y=y, width=self.w, height=self.h, radius=border_radius, fill_color=bg_color, border_color=cl((255, 0, 0, 0)), border_size=border_size)
            #
            else:
                #
                self.window.draw_rounded_rect(x=x, y=y, width=self.w, height=self.h, radius=border_radius, fill_color=bg_color, border_color=border_color, border_size=border_size)

        #
        if font_size not in self.bases_text_sizes:
            #
            self.bases_text_sizes[font_size] = get_font_size(self.text, font_size, font_ratio=0.5)

        #
        base_text_w: int
        base_text_h: int
        #
        base_text_w, base_text_h = self.bases_text_sizes[font_size]

        #
        self.window.draw_text(
                txt=self.text,
                x=x + (self.w - base_text_w) // 2,
                y=y + (self.h - base_text_h) // 2,
                font_name=font_name,
                font_size=font_size,
                font_color=font_color
        )

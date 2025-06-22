"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""

#
from typing import Callable, Optional, Any
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
        self.font_name: Optional[str] = font_name
        self.font_size: int = font_size
        self.base_bg_color: ND_Color = base_bg_color if base_bg_color is not None else cl("gray")
        self.base_fg_color: ND_Color = base_fg_color if base_fg_color is not None else cl("black")
        self.base_bg_texture: Optional[int] = self.window.prepare_image_to_render(base_bg_texture) if isinstance(base_bg_texture, str) else base_bg_texture
        self.hover_bg_color: ND_Color = hover_bg_color if hover_bg_color is not None else cl("dark gray")
        self.hover_fg_color: ND_Color = hover_fg_color if hover_fg_color is not None else cl("black")
        self.hover_bg_texture: Optional[int] = self.window.prepare_image_to_render(hover_bg_texture) if isinstance(hover_bg_texture, str) else hover_bg_texture
        self.clicked_bg_color: ND_Color = clicked_bg_color if clicked_bg_color is not None else cl("very dark gray")
        self.clicked_fg_color: ND_Color = clicked_fg_color if clicked_fg_color is not None else cl("black")
        self.clicked_bg_texture: Optional[int] = self.window.prepare_image_to_render(clicked_bg_texture) if isinstance(clicked_bg_texture, str) else clicked_bg_texture
        #
        self.border: bool = border
        self.border_radius: int = border_radius
        #
        self.base_text_w: int = 0
        self.base_text_h: int = 0
        #
        self.base_text_w, self.base_text_h = get_font_size(self.text, self.font_size, font_ratio=0.5)
        #
        self.texture_transformations: ND_Transformation = texture_transformations

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        #
        x, y = self.x, self.y

        #
        bg_color: ND_Color
        fg_color: ND_Color
        bg_texture: Optional[int]

        # Getting the right colors along the state
        if self.state == "normal":
            bg_color, fg_color, bg_texture = self.base_bg_color, self.base_fg_color, self.base_bg_texture
        elif self.state == "hover":
            bg_color, fg_color, bg_texture = self.hover_bg_color, self.hover_fg_color, self.hover_bg_texture if self.hover_bg_texture is not None else self.base_bg_texture
        else:  # clicked
            bg_color, fg_color, bg_texture = self.clicked_bg_color, self.clicked_fg_color, self.clicked_bg_texture if self.clicked_bg_texture is not None else self.base_bg_texture

        # Drawing the background rect color or texture
        if bg_texture:
            self.window.render_prepared_texture(bg_texture, x, y, self.w, self.h, transformations=self.texture_transformations)
        else:
            if not self.border and self.border_radius <= 0:
                self.window.draw_filled_rect(x, y, self.w, self.h, bg_color)
            elif not self.border:
                self.window.draw_rounded_rect(x, y, self.w, self.h, self.border_radius, bg_color, cl((255, 0, 0, 0)))
            else:
                self.window.draw_rounded_rect(x, y, self.w, self.h, self.border_radius, bg_color, fg_color)

        #
        self.window.draw_text(
                txt=self.text,
                x=x + (self.w - self.base_text_w) // 2,
                y=y + (self.h - self.base_text_h) // 2,
                font_name=self.font_name,
                font_size=self.font_size,
                font_color=fg_color
        )

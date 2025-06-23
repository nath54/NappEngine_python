"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""


from typing import Any, Optional

from lib_nadisplay_colors import ND_Color
from lib_nadisplay_position import ND_Position
from lib_nadisplay_utils import get_font_size
from lib_nadisplay_core import ND_Window, ND_Elt, ND_EventsHandler_Elts



# ND_Elt_Text class implementation
class ND_Elt_Text(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            text: str,
            text_wrap: bool = False,
            text_h_align: str = "center",
            text_v_align: str = "center",
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)
        self.text: str = text
        #
        self.text_wrap: bool = text_wrap
        #
        self.text_h_align: str = text_h_align
        self.text_v_align: str = text_v_align
        #
        self.base_text_w: int = 0
        self.base_text_h: int = 0
        #
        self.bases_text_sizes: dict[int, tuple[int, int]] = {}

    #
    def get_value(self) -> Any:
        #
        return self.text

    #
    def set_value(self, new_value: Any) -> None:
        #
        self.text = str(new_value)

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        #
        font_name: str = self.get_style_attribute_str(attribute_name="font_name")
        font_size: int = self.get_style_attribute_int(attribute_name="font_size")
        font_color: ND_Color = self.get_style_attribute_color(attribute_name="font_color")

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
        x, y = self.x, self.y

        if self.w <= 0 or self.h <= 0:
            #
            # TODO: Taille indéterminée
            #
            pass
        else:
            #
            # TODO: Taille déterminée
            #
            if self.text_wrap:
                #
                # TODO: Calculer ce qui wrap ou pas
                #
                pass
            else:
                #
                if self.text_h_align == "center":
                    #
                    x=x + (self.w - base_text_w) // 2
                    #
                elif self.text_h_align == "right":
                    #
                    x=x + (self.w - base_text_w)
                    #
                #
                if self.text_v_align == "center":
                    #
                    y=y + (self.h - base_text_h) // 2
                    #
                elif self.text_v_align == "right":
                    #
                    y=y + (self.h - base_text_h)
                    #

        #
        self.window.draw_text(
                txt=self.text,
                x=x,
                y=y,
                font_name=font_name,
                font_size=font_size,
                font_color=font_color
        )
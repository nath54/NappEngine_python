"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""


from typing import Any, Optional

from lib_nadisplay_colors import ND_Color, cl
from lib_nadisplay_position import ND_Position
from lib_nadisplay_utils import get_font_size
from lib_nadisplay_core import ND_Window, ND_Elt



# ND_Elt_Text class implementation
class ND_Elt_Text(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            text: str,
            font_name: Optional[str] = None,
            font_size: int = 24,
            font_color: ND_Color = cl("gray"),
            text_wrap: bool = False,
            text_h_align: str = "center",
            text_v_align: str = "center"
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        self.text: str = text
        self.font_name: Optional[str] = font_name
        self.font_size: int = font_size
        self.font_color: ND_Color = font_color
        #
        self.text_wrap: bool = text_wrap
        #
        self.text_h_align: str = text_h_align
        self.text_v_align: str = text_v_align
        #
        self.base_text_w: int = 0
        self.base_text_h: int = 0
        #
        self.base_text_w, self.base_text_h = get_font_size(self.text, self.font_size, font_ratio=0.5)
        #

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
                    x=x + (self.w - self.base_text_w) // 2
                    #
                elif self.text_h_align == "right":
                    #
                    x=x + (self.w - self.base_text_w)
                    #
                #
                if self.text_v_align == "center":
                    #
                    y=y + (self.h - self.base_text_h) // 2
                    #
                elif self.text_v_align == "right":
                    #
                    y=y + (self.h - self.base_text_h)
                    #

        #
        self.window.draw_text(
                txt=self.text,
                x=x,
                y=y,
                font_name=self.font_name,
                font_size=self.font_size,
                font_color=self.font_color
        )
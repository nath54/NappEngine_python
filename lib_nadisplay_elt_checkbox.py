"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""

#
from typing import Any, Optional
#
import lib_nadisplay_events as nd_event
from lib_nadisplay_colors import cl, ND_Color
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window, ND_Elt, ND_EventsHandler_Elts
from lib_nadisplay_elt_button import ND_Elt_Button
from lib_nadisplay_utils import dict_sum



# ND_Elt_Checkbox
class ND_Elt_Checkbox(ND_Elt):
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            checked: bool = False,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)
        #
        self.checked: bool = checked
        #
        self.bt_checked: ND_Elt_Button = ND_Elt_Button(
            window=self.window,
            elt_id=f"{self.elt_id}_bt_checked",
            position=self.position,
            text="v",
            style_name=self.style_name,
            styles_override=dict_sum(self.styles_override, {
                "font_color_normal": cl("dark green"),
                "font_color_hover": cl("green"),
                "font_color_clicked": cl("black"),
                "font_color_deactivated": cl("black"),
                "border_color": cl("white"),
                "bg_color_normal": ND_Color(40, 40, 40),
                "bg_color_hover": ND_Color(100, 100, 100),
                "bg_color_clicked": cl("white"),
                "bg_color_deactivated": ND_Color(60, 60, 60),
                "border_color": cl("black"),
                "border_radius": 3,
                "border_size": 2
            }),
            events_handler=ND_EventsHandler_Elts( fn_on_click=self.on_bt_checked_pressed )
        )
        #
        self.bt_unchecked: ND_Elt_Button = ND_Elt_Button(
            window=self.window,
            elt_id=f"{self.elt_id}_bt_unchecked",
            position=self.position,
            text="x",
            style_name=self.style_name,
            styles_override=dict_sum(self.styles_override, {
                "font_color_normal": cl("dark red"),
                "font_color_hover": cl("red"),
                "font_color_clicked": cl("black"),
                "font_color_deactivated": cl("black"),
                "border_color": cl("white"),
                "bg_color_normal": ND_Color(40, 40, 40),
                "bg_color_hover": ND_Color(100, 100, 100),
                "bg_color_clicked": cl("white"),
                "bg_color_deactivated": ND_Color(60, 60, 60),
                "border_color": cl("black"),
                "border_radius": 3,
                "border_size": 2
            }),
            events_handler=ND_EventsHandler_Elts( fn_on_click=self.on_bt_unchecked_pressed )
        )

    #
    def get_value(self) -> Any:
        #
        return self.checked

    #
    def set_value(self, new_value: Any) -> None:
        #
        self.checked = bool(new_value)

    #
    def render(self) -> None:
        if self.checked:
            self.bt_checked.render()
        else:
            self.bt_unchecked.render()

    #
    def on_bt_checked_pressed(self, elt: ND_Elt)-> None:
        #
        self.checked = False
        #
        self.bt_checked.visible = False
        self.bt_unchecked.visible = True

    #
    def on_bt_unchecked_pressed(self, elt: ND_Elt) -> None:
        #
        self.checked = True
        #
        self.bt_checked.visible = True
        self.bt_unchecked.visible = False

    #
    def is_checked(self) -> bool:
        return self.checked

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if not self.visible:
            return
        #
        if self.checked:
            self.bt_checked.handle_event(event)
        else:
            self.bt_unchecked.handle_event(event)



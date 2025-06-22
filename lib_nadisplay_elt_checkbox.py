"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""

#
from typing import Callable, Any, Optional
#
import lib_nadisplay_events as nd_event
from lib_nadisplay_colors import cl
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window, ND_Elt
from lib_nadisplay_elt_clickable import ND_Elt_Clickable
from lib_nadisplay_elt_button import ND_Elt_Button


# ND_Elt_Checkbox
class ND_Elt_Checkbox(ND_Elt):
    def __init__(
        self,
        window: ND_Window,
        elt_id: str,
        position: ND_Position,
        checked: bool = False,
        on_pressed: Optional[Callable[["ND_Elt_Checkbox"], None]] = None
    ) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.on_pressed: Optional[Callable[["ND_Elt_Checkbox"], None]] = on_pressed
        #
        self.checked: bool = checked
        #
        self.bt_checked: ND_Elt_Button = ND_Elt_Button(
            window=self.window,
            elt_id=f"{self.elt_id}_bt_checked",
            position=self.position,
            onclick=self.on_bt_checked_pressed,
            text="v",
            base_fg_color=cl("dark green"),
            hover_fg_color=cl("green")
            # TODO: style
        )
        #
        self.bt_unchecked: ND_Elt_Button = ND_Elt_Button(
            window=self.window,
            elt_id=f"{self.elt_id}_bt_unchecked",
            position=self.position,
            onclick=self.on_bt_unchecked_pressed,
            text="x",
            base_fg_color=cl("dark red"),
            hover_fg_color=cl("red")
            # TODO: style
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
    def on_bt_checked_pressed(self, clickable: ND_Elt_Clickable) -> None:
        #
        self.checked = False
        #
        self.bt_checked.visible = False
        self.bt_unchecked.visible = True
        #
        if self.on_pressed is not None:
            self.on_pressed(self)

    #
    def on_bt_unchecked_pressed(self, clickable: ND_Elt_Clickable) -> None:
        #
        self.checked = True
        #
        self.bt_checked.visible = True
        self.bt_unchecked.visible = False
        #
        if self.on_pressed is not None:
            self.on_pressed(self)

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



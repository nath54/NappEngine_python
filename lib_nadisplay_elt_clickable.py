"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""


from typing import Callable, Optional


import lib_nadisplay_events as nd_event
from lib_nadisplay_point import ND_Point
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window, ND_Elt



# ND_Elt_Clickable class implementation
class ND_Elt_Clickable(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            onclick: Optional[Callable[["ND_Elt_Clickable"], None]] = None,
            active: bool = True,
            block_events_below: bool = True
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        self.onclick: Optional[Callable[[ND_Elt_Clickable], None]] = onclick
        self.state: str = "normal"  # Can be "normal", "hover", or "clicked"
        self.mouse_bt_down_on_hover: bool = False
        self.block_events_below: bool = block_events_below
        #
        self.active: bool = active

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if not self.visible:
            self.state = "normal"
            return
        #
        if not self.clickable:
            self.state = "normal"
            return
        #
        if not self.active:
            self.state = "normal"
            return
        #
        if isinstance(event, nd_event.ND_EventMouseMotion):
            #
            if self.position.rect.contains_point(ND_Point(event.x, event.y)):
                self.state = "hover"
            else:
                self.state = "normal"
        #
        elif isinstance(event, nd_event.ND_EventMouseButtonDown):
            if event.button_id == 1:
                if self.position.rect.contains_point(ND_Point(event.x, event.y)):
                    #
                    self.state = "clicked"
                    #
                    self.mouse_bt_down_on_hover = True
                else:
                    self.mouse_bt_down_on_hover = False
        #
        elif isinstance(event, nd_event.ND_EventMouseButtonUp):
            if event.button_id == 1:
                #
                self.state = "hover" if self.position.rect.contains_point(ND_Point(event.x, event.y)) else "normal"
                #
                if self.state == "hover" and self.mouse_bt_down_on_hover:
                    #
                    if self.block_events_below:
                        event.blocked = True
                    #
                    if self.onclick:
                        self.onclick(self)
            #
            self.mouse_bt_down_on_hover = False
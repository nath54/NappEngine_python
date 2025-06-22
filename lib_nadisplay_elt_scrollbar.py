"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""

#
from typing import Callable, Optional
#
import lib_nadisplay_events as nd_event
from lib_nadisplay_colors import ND_Color, cl
from lib_nadisplay_point import ND_Point
from lib_nadisplay_position import ND_Position
from lib_nadisplay_utils import clamp
from lib_nadisplay_core import ND_Window, ND_Elt



# ND_H_ScrollBar class implementation
class ND_H_ScrollBar(ND_Elt):
    #
    def __init__(
                    self,
                    window: ND_Window,
                    elt_id: str,
                    position: ND_Position,
                    content_width: int,
                    bg_cl: ND_Color = cl((10, 10, 10)),
                    fg_cl: ND_Color = cl("white"),
                    on_value_changed: Optional[Callable[["ND_H_ScrollBar", float], None]] = None
        ) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.on_value_changed: Optional[Callable[[ND_H_ScrollBar, float], None]] = on_value_changed
        #
        self.content_width: int = content_width
        self.scroll_position: float = 0
        self.dragging: bool = False
        self.prep_dragging: bool = False
        #
        self.bg_cl: ND_Color = bg_cl
        self.fg_cl: ND_Color = fg_cl

    #
    def get_scroll_ratio(self) -> float:
        #
        return self.scroll_position / float(self.content_width)

    #
    @property
    def thumb_width(self) -> int:
        return max(20, int(self.w * (self.w / self.content_width)))

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        # Draw background
        self.window.draw_filled_rect(self.x, self.y, self.w, self.h, self.bg_cl)
        #
        self.window.draw_unfilled_rect(self.x, self.y, self.w, self.h, self.fg_cl)

        # Draw thumb
        thumb_x = self.x + int(self.scroll_position * (self.w - self.thumb_width) / (self.content_width - self.w))
        self.window.draw_filled_rect(thumb_x, self.y, self.thumb_width, self.h, self.fg_cl)

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if isinstance(event, nd_event.ND_EventMouse):
            #
            if not self.position.rect.contains_point(ND_Point(event.x, event.y)):
                self.prep_dragging = False
                self.dragging = False
                return
            #
            if isinstance(event, nd_event.ND_EventMouseButtonDown):
                if event.button_id == 1:
                    self.prep_dragging = True
            #
            elif isinstance(event, nd_event.ND_EventMouseButtonUp):
                if event.button_id == 1:
                    if self.dragging:
                        self.dragging = False
                    else:
                        relative_x = event.x - self.x
                        self.scroll_position = max(0, min(self.content_width - self.w,
                                                    int(relative_x * self.content_width / self.w)))
                        #
                        if self.on_value_changed is not None:
                            self.on_value_changed(self, self.scroll_position)

            #
            elif isinstance(event, nd_event.ND_EventMouseMotion):
                if self.dragging or self.prep_dragging:
                    #
                    if self.prep_dragging:
                        self.dragging = True
                        self.prep_dragging = False
                    #
                    relative_x = event.x - self.x
                    self.scroll_position = max(0, min(self.content_width - self.w,
                                                    int(relative_x * self.content_width / self.w)))
                    #
                    if self.on_value_changed is not None:
                        self.on_value_changed(self, self.scroll_position)


# ND_V_ScrollBar class implementation
class ND_V_ScrollBar(ND_Elt):
    #
    def __init__(
                    self,
                    window: ND_Window,
                    elt_id: str,
                    position: ND_Position,
                    content_height: int,
                    fg_color: ND_Color = cl("white"),
                    bg_color: ND_Color = cl("dark gray"),
                    on_value_changed: Optional[Callable[["ND_V_ScrollBar", float], None]] = None
        ) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.on_value_changed: Optional[Callable[[ND_V_ScrollBar, float], None]] = on_value_changed
        #
        self.content_height = content_height
        self.scroll_position = 0
        self.dragging = False
        #
        self.fg_color: ND_Color = fg_color
        self.bg_color: ND_Color = bg_color

    #
    def get_scroll_ratio(self) -> float:
        #
        return self.scroll_position / float(self.content_height)

    @property
    def thumb_height(self) -> int:
        return clamp(int(self.w * (self.w / self.content_height)), 2, 20)

    #
    def render(self) -> None:
        if not self.visible:
            return

        # Draw background
        self.window.draw_filled_rect(self.x, self.y, self.w, self.h, self.bg_color)

        # Draw thumb
        thumb_y = self.y + int(self.scroll_position * (self.h - self.thumb_height) / (self.content_height))
        self.window.draw_filled_rect(self.x, thumb_y, self.w, self.thumb_height, self.fg_color)

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if isinstance(event, nd_event.ND_EventMouseButtonDown):
            if event.button_id == 1:
                if self.position.rect.contains_point(ND_Point(event.x, event.y)):
                    #
                    self.scroll_position = clamp(int(((event.y - self.y) / self.h) * self.content_height), 0, self.content_height)
                    #
                    if self.on_value_changed is not None:
                        self.on_value_changed(self, self.scroll_position)
                    #
                    event.blocked = True
                    #
                    self.dragging = True
                else:
                    self.dragging = False
        #
        elif isinstance(event, nd_event.ND_EventMouseButtonUp):
            if event.button_id == 1:
                self.dragging = False
        #
        elif isinstance(event, nd_event.ND_EventMouseMotion):
            if self.dragging:
                relative_y = event.y - self.y
                self.scroll_position = max(0, min(self.content_height - self.h,
                                                int(relative_y * self.content_height / self.h)))
                #
                if self.on_value_changed is not None:
                    self.on_value_changed(self, self.scroll_position)


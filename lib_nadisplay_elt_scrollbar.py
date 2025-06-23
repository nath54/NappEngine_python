"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""

#
from typing import Callable, Optional, Any
#
import lib_nadisplay_events as nd_event
from lib_nadisplay_colors import ND_Color
from lib_nadisplay_point import ND_Point
from lib_nadisplay_position import ND_Position
from lib_nadisplay_utils import clamp
from lib_nadisplay_core import ND_Window, ND_Elt, ND_EventsHandler_Elts



# ND_Elt_H_ScrollBar class implementation
class ND_Elt_H_ScrollBar(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            content_width: int,
            on_value_changed: Optional[Callable[["ND_Elt_H_ScrollBar", float], None]] = None,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)
        #
        self.on_value_changed: Optional[Callable[[ND_Elt_H_ScrollBar, float], None]] = on_value_changed
        #
        self.content_width: int = content_width
        self.scroll_position: float = 0
        self.dragging: bool = False
        self.prep_dragging: bool = False

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

        #
        bg_color: ND_Color = self.get_style_attribute_color(attribute_name="bg_color")
        fg_color: ND_Color = self.get_style_attribute_color(attribute_name="fg_color")

        # Draw background
        self.window.draw_filled_rect(self.x, self.y, self.w, self.h, bg_color)
        #
        self.window.draw_unfilled_rect(self.x, self.y, self.w, self.h, fg_color)

        # Draw thumb
        thumb_x = self.x + int(self.scroll_position * (self.w - self.thumb_width) / (self.content_width - self.w))
        self.window.draw_filled_rect(thumb_x, self.y, self.thumb_width, self.h, fg_color)

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


# ND_Elt_V_ScrollBar class implementation
class ND_Elt_V_ScrollBar(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            content_height: int,
            on_value_changed: Optional[Callable[["ND_Elt_V_ScrollBar", float], None]] = None,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)
        #
        self.on_value_changed: Optional[Callable[[ND_Elt_V_ScrollBar, float], None]] = on_value_changed
        #
        self.content_height = content_height
        self.scroll_position = 0
        self.dragging = False

    #
    def get_scroll_ratio(self) -> float:
        #
        return self.scroll_position / float(self.content_height)

    @property
    def thumb_height(self) -> int:
        return clamp(int(self.w * (self.w / self.content_height)), 2, 20)

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        #
        bg_color: ND_Color = self.get_style_attribute_color(attribute_name="bg_color")
        fg_color: ND_Color = self.get_style_attribute_color(attribute_name="fg_color")

        # Draw background
        self.window.draw_filled_rect(self.x, self.y, self.w, self.h, bg_color)

        # Draw thumb
        thumb_y = self.y + int(self.scroll_position * (self.h - self.thumb_height) / (self.content_height))
        self.window.draw_filled_rect(self.x, thumb_y, self.w, self.thumb_height, fg_color)

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


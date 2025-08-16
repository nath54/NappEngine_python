# lib_nadisplay_elt_scrollbar.py
"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:
This module provides implementations for horizontal and vertical scrollbar UI elements.
The scrollbars can be used to navigate through content that exceeds the visible area
of a container. They handle mouse events for dragging and position updates, and
provide callbacks for when the scroll position changes.
"""

#
### Import necessary modules and classes. ###
#
from typing import Callable, Optional, Any
import lib_nadisplay_events as nd_event
from lib_nadisplay_colors import ND_Color
from lib_nadisplay_point import ND_Point
from lib_nadisplay_position import ND_Position
from lib_nadisplay_utils import clamp
from lib_nadisplay_core import ND_Window, ND_Elt, ND_EventsHandler_Elts


#
### ND_Elt_H_ScrollBar class implementation. ###
#
class ND_Elt_H_ScrollBar(ND_Elt):

    """
    A horizontal scrollbar UI element that allows users to scroll through content
    that exceeds the visible width of a container.

    Attributes:
        on_value_changed (Callable): Callback function triggered when scroll position changes
        content_width (int): Total width of the content being scrolled
        scroll_position (float): Current scroll position
        dragging (bool): Flag indicating if the scrollbar thumb is being dragged
        prep_dragging (bool): Flag indicating if a drag operation is about to start
    """

    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            content_width: int,
            scroll_position: float = 0,
            on_value_changed: Optional[Callable[["ND_Elt_H_ScrollBar", float], None]] = None,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        """
        Initialize a horizontal scrollbar element.

        Args:
            window: The window this element belongs to
            elt_id: A unique identifier for this element
            position: The position and dimensions of this element
            content_width: The total width of the content being scrolled
            scroll_position: Initial scroll position (default: 0)
            on_value_changed: Callback function triggered when scroll position changes
            style_name: Name of the style to apply (default: "default")
            styles_override: Dictionary to override specific style attributes
            events_handler: Event handler for this element
        """

        #
        ### Call the parent class constructor to initialize base attributes. ###
        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)

        #
        ### Initialize callback function for scroll position changes. ###
        ### This is a function that will be called when the scroll position changes. ###
        #
        self.on_value_changed: Optional[Callable[[ND_Elt_H_ScrollBar, float], None]] = on_value_changed

        #
        ### Initialize the total width of the content being scrolled. ###
        ### This determines the maximum scrollable distance. ###
        #
        self.content_width: int = content_width

        #
        ### Initialize the current scroll position. ###
        ### This represents how far the content has been scrolled horizontally. ###
        #
        self.scroll_position: float = scroll_position

        #
        ### Initialize flag to track if the scrollbar thumb is being dragged. ###
        ### This is set to True when the user clicks and drags the thumb. ###
        #
        self.dragging: bool = False

        #
        ### Initialize flag to prepare for dragging. ###
        ### This is set to True when the user clicks on the thumb but hasn't moved the mouse yet. ###
        #
        self.prep_dragging: bool = False

    #
    def get_scroll_ratio(self) -> float:

        """
        Calculate and return the current scroll ratio.

        The scroll ratio is the current scroll position divided by the total content width,
        representing how far through the content the user has scrolled (0.0 to 1.0).

        Returns:
            float: The scroll ratio between 0.0 and 1.0
        """

        #
        ### Calculate the ratio by dividing current scroll position by total content width. ###
        #
        return clamp(self.scroll_position / float(self.content_width), 0, 1)

    #
    @property
    def thumb_width(self) -> int:

        """
        Calculate and return the width of the scrollbar thumb.

        The thumb width is proportional to the ratio of visible width to total content width,
        with a minimum width of 20 pixels to ensure it remains usable.

        Returns:
            int: The width of the scrollbar thumb in pixels
        """

        #
        ### Calculate thumb width based on the ratio of visible width to content width. ###
        ### Ensure minimum width of 20 pixels for usability and maximum widht of scrollbar size. ###
        #
        return min( self.w, max(20, int(self.w * (self.w / self.content_width))) )

    #
    def render(self) -> None:

        """
        Render the horizontal scrollbar on the window.

        This method draws the scrollbar background and thumb at the appropriate position
        based on the current scroll position. It only renders if the element is visible.
        """

        #
        ### Check if the element is visible; if not, skip rendering. ###
        #
        if not self.visible:
            #
            return

        #
        ### Get the background color from the style attributes. ###
        ### This will be used to fill the scrollbar background. ###
        #
        bg_color: ND_Color = self.get_style_attribute_color(attribute_name="bg_color")

        #
        ### Get the foreground color from the style attributes. ###
        ### This will be used for the scrollbar thumb and border. ###
        #
        fg_color: ND_Color = self.get_style_attribute_color(attribute_name="fg_color")

        #
        ### Draw the scrollbar background as a filled rectangle. ###
        ### This creates the track for the scrollbar thumb. ###
        #
        self.window.draw_filled_rect(self.x, self.y, self.w, self.h, bg_color)

        #
        ### Draw the scrollbar border as an unfilled rectangle. ###
        ### This creates the visual boundary of the scrollbar. ###
        #
        self.window.draw_unfilled_rect(self.x, self.y, self.w, self.h, fg_color)

        #
        ### Calculate the x-position of the thumb based on the current scroll position. ###
        ### The thumb position is proportional to the scroll position within the available space. ###
        #
        thumb_x: int = self.x + int(self.scroll_position * (self.w - self.thumb_width) / (self.content_width - self.w))

        #
        ### Draw the scrollbar thumb as a filled rectangle. ###
        ### This is the draggable part of the scrollbar. ###
        #
        self.window.draw_filled_rect(thumb_x, self.y, self.thumb_width, self.h, fg_color)

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:

        """
        Handle mouse events for the horizontal scrollbar.

        This method processes mouse button down, mouse button up, and mouse motion events
        to allow dragging the thumb and updating the scroll position accordingly.

        Args:
            event: The mouse event to handle
        """

        #
        ### Check if the event has been blocked by another element. ###
        ### If so, don't process this event. ###
        #
        if event.blocked:
            #
            return

        #
        ### Check if the event is a mouse event. ###
        #
        if isinstance(event, nd_event.ND_EventMouse):

            #
            ### Check if the mouse is outside the scrollbar area. ###
            ### If so, reset dragging states and return. ###
            #
            if not self.position.rect.contains_point(ND_Point(event.x, event.y)):

                #
                ### Reset the preparation flag for dragging. ###
                #
                self.prep_dragging = False

                #
                ### Reset the dragging flag. ###
                #
                self.dragging = False

                #
                return

            #
            ### Handle mouse button down events. ###
            #
            if isinstance(event, nd_event.ND_EventMouseButtonDown):

                #
                ### Check if the left mouse button was pressed. ###
                #
                if event.button_id == 1:

                    #
                    ### Set the preparation flag for dragging. ###
                    ### This indicates the user has clicked on the thumb. ###
                    #
                    self.prep_dragging = True

            #
            ### Handle mouse button up events. ###
            #
            elif isinstance(event, nd_event.ND_EventMouseButtonUp):

                #
                ### Check if the left mouse button was released. ###
                #
                if event.button_id == 1:

                    #
                    ### Check if we were dragging the thumb. ###
                    #
                    if self.dragging:

                        #
                        ### Stop dragging. ###
                        #
                        self.dragging = False

                    #
                    else:

                        #
                        ### Calculate the relative x-position within the scrollbar. ###
                        #
                        relative_x: int = event.x - self.x

                        #
                        ### Calculate the new scroll position based on where the user clicked. ###
                        ### This allows jumping to a specific position by clicking on the track. ###
                        #
                        self.scroll_position = max(0, min(self.content_width - self.w,
                                                    int(relative_x * self.content_width / self.w)))

                        #
                        ### Call the callback function if it exists. ###
                        #
                        if self.on_value_changed is not None:
                            self.on_value_changed(self, self.scroll_position)

            #
            ### Handle mouse motion events. ###
            #
            elif isinstance(event, nd_event.ND_EventMouseMotion):

                #
                ### Check if we are dragging or preparing to drag. ###
                #
                if self.dragging or self.prep_dragging:

                    #
                    ### If we were preparing to drag, start dragging now. ###
                    #
                    if self.prep_dragging:

                        #
                        ### Set dragging flag to True. ###
                        #
                        self.dragging = True

                        #
                        ### Reset preparation flag. ###
                        #
                        self.prep_dragging = False

                    #
                    ### Calculate the relative x-position within the scrollbar. ###
                    #
                    relative_x = event.x - self.x

                    #
                    ### Calculate the new scroll position based on mouse movement. ###
                    ### This updates the scroll position as the user drags the thumb. ###
                    #
                    self.scroll_position = max(0, min(self.content_width - self.w,
                                                    int(relative_x * self.content_width / self.w)))

                    #
                    ### Call the callback function if it exists. ###
                    #
                    if self.on_value_changed is not None:
                        #
                        self.on_value_changed(self, self.scroll_position)


#
### ND_Elt_V_ScrollBar class implementation. ###
#
class ND_Elt_V_ScrollBar(ND_Elt):

    """
    A vertical scrollbar UI element that allows users to scroll through content
    that exceeds the visible height of a container.

    Attributes:
        on_value_changed (Callable): Callback function triggered when scroll position changes
        content_height (int): Total height of the content being scrolled
        scroll_position (float): Current scroll position
        dragging (bool): Flag indicating if the scrollbar thumb is being dragged
    """

    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            content_height: int,
            scroll_position: float = 0,
            on_value_changed: Optional[Callable[["ND_Elt_V_ScrollBar", float], None]] = None,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        """
        Initialize a vertical scrollbar element.

        Args:
            window: The window this element belongs to
            elt_id: A unique identifier for this element
            position: The position and dimensions of this element
            content_height: The total height of the content being scrolled
            scroll_position: Initial scroll position (default: 0)
            on_value_changed: Callback function triggered when scroll position changes
            style_name: Name of the style to apply (default: "default")
            styles_override: Dictionary to override specific style attributes
            events_handler: Event handler for this element
        """

        #
        ### Call the parent class constructor to initialize base attributes. ###
        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)

        #
        ### Initialize callback function for scroll position changes. ###
        ### This is a function that will be called when the scroll position changes. ###
        #
        self.on_value_changed: Optional[Callable[[ND_Elt_V_ScrollBar, float], None]] = on_value_changed

        #
        ### Initialize the total height of the content being scrolled. ###
        ### This determines the maximum scrollable distance. ###
        #
        self.content_height: int = content_height

        #
        ### Initialize the current scroll position. ###
        ### This represents how far the content has been scrolled vertically. ###
        #
        self.scroll_position: float = scroll_position

        #
        ### Initialize flag to track if the scrollbar thumb is being dragged. ###
        ### This is set to True when the user clicks and drags the thumb. ###
        #
        self.dragging: bool = False

    #
    def get_scroll_ratio(self) -> float:

        """
        Calculate and return the current scroll ratio.

        The scroll ratio is the current scroll position divided by the total content height,
        representing how far through the content the user has scrolled (0.0 to 1.0).

        Returns:
            float: The scroll ratio between 0.0 and 1.0
        """

        #
        ### Calculate the ratio by dividing current scroll position by total content height. ###
        #
        return clamp(self.scroll_position / float(self.content_height), 0, 1)

    #
    @property
    def thumb_height(self) -> int:

        """
        Calculate and return the height of the scrollbar thumb.

        The thumb height is proportional to the ratio of visible height to total content height,
        clamped between 2 and 20 pixels to ensure it remains usable.

        Returns:
            int: The height of the scrollbar thumb in pixels
        """

        #
        ### Calculate thumb height based on the ratio of visible height to content height. ###
        ### Clamp the value between 2 and 20 pixels for usability. ###
        #
        return min( self.h, max(20, int(self.h * (self.h / self.content_height))) )

    #
    def render(self) -> None:

        """
        Render the vertical scrollbar on the window.

        This method draws the scrollbar background and thumb at the appropriate position
        based on the current scroll position. It only renders if the element is visible.
        """

        #
        ### Check if the element is visible; if not, skip rendering. ###
        #
        if not self.visible:
            #
            return

        #
        ### Get the background color from the style attributes. ###
        ### This will be used to fill the scrollbar background. ###
        #
        bg_color: ND_Color = self.get_style_attribute_color(attribute_name="bg_color")

        #
        ### Get the foreground color from the style attributes. ###
        ### This will be used for the scrollbar thumb. ###
        #
        fg_color: ND_Color = self.get_style_attribute_color(attribute_name="fg_color")

        #
        ### Draw the scrollbar background as a filled rectangle. ###
        ### This creates the track for the scrollbar thumb. ###
        #
        self.window.draw_filled_rect(self.x, self.y, self.w, self.h, bg_color)

        #
        ### Calculate the y-position of the thumb based on the current scroll position. ###
        ### The thumb position is proportional to the scroll position within the available space. ###
        #
        thumb_y = self.y + int(self.scroll_position * (self.h - self.thumb_height) / (self.content_height))

        #
        ### Draw the scrollbar thumb as a filled rectangle. ###
        ### This is the draggable part of the scrollbar. ###
        #
        self.window.draw_filled_rect(self.x, thumb_y, self.w, self.thumb_height, fg_color)

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:

        """
        Handle mouse events for the vertical scrollbar.

        This method processes mouse button down, mouse button up, and mouse motion events
        to allow dragging the thumb and updating the scroll position accordingly.

        Args:
            event: The mouse event to handle
        """

        #
        ### Check if the event has been blocked by another element. ###
        ### If so, don't process this event. ###
        #
        if event.blocked:
            #
            return

        #
        ### Handle mouse button down events. ###
        #
        if isinstance(event, nd_event.ND_EventMouseButtonDown):

            #
            ### Check if the left mouse button was pressed. ###
            #
            if event.button_id == 1:

                #
                ### Check if the mouse is within the scrollbar area. ###
                #
                if self.position.rect.contains_point(ND_Point(event.x, event.y)):

                    #
                    ### Calculate the new scroll position based on where the user clicked. ###
                    ### This allows jumping to a specific position by clicking on the track. ###
                    #
                    self.scroll_position = clamp(int(((event.y - self.y) / self.h) * self.content_height), 0, self.content_height)

                    #
                    ### Call the callback function if it exists. ###
                    #
                    if self.on_value_changed is not None:
                        #
                        self.on_value_changed(self, self.scroll_position)

                    #
                    ### Block the event to prevent other elements from processing it. ###
                    #
                    event.blocked = True

                    #
                    ### Set the dragging flag to True. ###
                    #
                    self.dragging = True

                #
                else:

                    #
                    ### If the mouse is outside the scrollbar, ensure dragging is False. ###
                    #
                    self.dragging = False

        #
        ### Handle mouse button up events. ###
        #
        elif isinstance(event, nd_event.ND_EventMouseButtonUp):

            #
            ### Check if the left mouse button was released. ###
            #
            if event.button_id == 1:

                #
                ### Stop dragging. ###
                #
                self.dragging = False

        #
        ### Handle mouse motion events. ###
        #
        elif isinstance(event, nd_event.ND_EventMouseMotion):

            #
            ### Check if we are dragging the thumb. ###
            #
            if self.dragging:

                #
                ### Calculate the relative y-position within the scrollbar. ###
                #
                relative_y: int = event.y - self.y

                #
                ### Calculate the new scroll position based on mouse movement. ###
                ### This updates the scroll position as the user drags the thumb. ###
                #
                self.scroll_position = max(0, min(self.content_height - self.h,
                                                int(relative_y * self.content_height / self.h)))

                #
                ### Call the callback function if it exists. ###
                #
                if self.on_value_changed is not None:
                    #
                    self.on_value_changed(self, self.scroll_position)

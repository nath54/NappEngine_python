"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""

#
from typing import Callable, Any, Optional
#
import lib_nadisplay_events as nd_event
from lib_nadisplay_colors import ND_Color, cl
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window, ND_Elt
from lib_nadisplay_elt_scrollbar import ND_Elt_H_ScrollBar




#
class ND_Elt_LineEdit(ND_Elt):
    def __init__(
        self,
        window: ND_Window,
        elt_id: str,
        position: ND_Position,
        text: str = "",
        place_holder: str = "",
        max_text_length: int = -1,
        mouse_active: bool = True,
        font_name: Optional[str] = None,
        font_size: int = 24,
        border_radius: int = 5,
        border: bool = True,
        base_bg_color: Optional[ND_Color] = None,
        base_fg_color: Optional[ND_Color] = None,
        hover_bg_color: Optional[ND_Color] = None,
        hover_fg_color: Optional[ND_Color] = None,
        clicked_bg_color: Optional[ND_Color] = None,
        clicked_fg_color: Optional[ND_Color] = None,
        characters_restrictions: Optional[set[str]] = None,
        password_mode: bool = False,
        on_line_edit_validated: Optional[Callable[["ND_Elt_LineEdit", str], None]] = None,
        on_line_edit_escaped: Optional[Callable[["ND_Elt_LineEdit"], None]] = None
    ) -> None:
        super().__init__(window=window, elt_id=elt_id, position=position)
        self.state: str = "normal"
        self.text: str = text
        self.place_holder: str = place_holder
        self.font_name: Optional[str] = font_name
        self.font_size: int = font_size
        self.base_bg_color: ND_Color = base_bg_color if base_bg_color else cl("gray")
        self.base_fg_color: ND_Color = base_fg_color if base_fg_color else cl("black")
        self.hover_bg_color: ND_Color = hover_bg_color if hover_bg_color else cl("dark gray")
        self.hover_fg_color: ND_Color = hover_fg_color if hover_fg_color else cl("black")
        self.clicked_bg_color: ND_Color = clicked_bg_color if clicked_bg_color else cl("very dark gray")
        self.clicked_fg_color: ND_Color = clicked_fg_color if clicked_fg_color else cl("black")
        self.border: bool = border
        self.border_radius: int = border_radius
        self.cursor: int = len(text)
        self.cursor_width: int = 2
        self.cursor_height: int = self.font_size
        self.focused: bool = False
        self.max_text_length: int = max_text_length
        self.characters_restrictions: Optional[set[str]] = characters_restrictions   # Do not accept others character that theses
        self.password_mode: bool = password_mode
        self.on_line_edit_validated: Optional[Callable[[ND_Elt_LineEdit, str], None]] = on_line_edit_validated
        self.on_line_edit_escaped: Optional[Callable[[ND_Elt_LineEdit], None]] = on_line_edit_escaped

        # Scrollbar-related
        self.scrollbar_height: int = 10
        self.full_text_width: int = 0
        self.scroll_offset: int = 0
        self.scrollbar: ND_Elt_H_ScrollBar = ND_Elt_H_ScrollBar(
            window = self.window,
            elt_id = f"scrollbar_{self.elt_id}",
            position = ND_Position(self.x, self.y + self.h - self.scrollbar_height, self.w, self.scrollbar_height),
            content_width = self.window.get_text_size_with_font(self.text, self.font_size, self.font_name).x
        )

    #
    def set_text(self, txt: str) -> None:
        #
        self.text = txt
        self.cursor = len(self.text)

    #
    def get_value(self) -> Any:
        #
        return self.text

    #
    def set_value(self, new_value: Any) -> None:
        #
        self.set_text(txt = str(new_value))

    #
    def render(self) -> None:
        if not self.visible:
            return

        # Determine background and text color based on the state
        bg_color = self.base_bg_color
        fg_color = self.base_fg_color
        if self.state == "hover":
            bg_color = self.hover_bg_color
            fg_color = self.hover_fg_color
        elif self.state == "clicked":
            bg_color = self.clicked_bg_color
            fg_color = self.clicked_fg_color

        # Draw the background rectangle
        if self.border:
            self.window.draw_rounded_rect(
                self.x, self.y, self.w, self.h, self.border_radius, bg_color, fg_color
            )
        else:
            self.window.draw_filled_rect(self.x, self.y, self.w, self.h, bg_color)

        # Determine the visible portion of the text
        render_text = self.text if self.text else self.place_holder
        text_color = fg_color if self.text else cl("light gray")

        self.full_text_width = self.window.get_text_size_with_font(render_text, self.font_size, self.font_name).x

        #
        if self.scrollbar.scroll_position > 0:
            size_hidden: int
            count_hidden: int
            size_hidden, count_hidden = self.window.get_count_of_renderable_chars_fitting_given_width(txt=render_text, given_width=int(self.scrollbar.scroll_position), font_name=self.font_name, font_size=self.font_size)
            #
            if count_hidden > 0:
                render_text = render_text[count_hidden:]
                self.scroll_offset = int(self.scrollbar.scroll_position) - size_hidden
        else:
            self.scroll_offset = 0

        visible_text = render_text

        visible_text_width: int = self.full_text_width
        if self.full_text_width > self.w:
            while visible_text_width > self.w:
                visible_text = visible_text[1:]
                visible_text_width = self.window.get_text_size_with_font(visible_text, self.font_size, self.font_name).x

        # TODO: correct the text that is displayed and visible


        # Render the text
        self.window.draw_text(
            txt=visible_text,
            x=self.x + 5 - self.scroll_offset,
            y=self.y + (self.h - self.cursor_height) // 2,
            font_size=self.font_size,
            font_color=text_color,
            font_name=self.font_name,
        )

        # Render the cursor if focused
        if self.focused and len(self.text) >= self.cursor:

            txt_before_cursor_width: int = self.window.get_text_size_with_font(self.text[: self.cursor], self.font_size, self.font_name).x

            cursor_x = self.x + 5 + txt_before_cursor_width - self.scroll_offset
            self.window.draw_filled_rect(cursor_x, self.y + 5, self.cursor_width, self.cursor_height, fg_color)

        # Render horizontal scrollbar if necessary
        if self.full_text_width > self.w:
            self.scrollbar.render()

    #
    def write(self, char: str) -> None:
        #
        if self.max_text_length > 0 and len(self.text) + len(char) > self.max_text_length:
            return
        #
        self.text = self.text[: self.cursor] + char + self.text[self.cursor :]
        self.cursor += len(char)
        #
        self.full_text_width = self.window.get_text_size_with_font(self.text, self.font_size, self.font_name).x
        self.scrollbar.content_width = self.full_text_width

    #
    def print_debug_infos(self) -> None:
        #
        print(f"\nDEBUG | line_edit={self.elt_id} | visible={self.visible} | focused={self.focused} | text={self.text} | cursor={self.cursor} | full_text_width={self.full_text_width} | scroll_position={self.scrollbar.scroll_position}\n")

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if isinstance(event, nd_event.ND_EventKeyDown) and event.key == "F3":
            self.print_debug_infos()
        #
        if not self.visible:
            return
        #
        if isinstance(event, nd_event.ND_EventMouse):
            if event.x >= self.x and event.x <= self.x + self.w and event.y >= self.y and event.y <= self.y + self.h:
                if isinstance(event, nd_event.ND_EventMouseButtonDown):
                    if self.state == "clicked":
                        # TODO: move the cursor to the closest place possible of the click
                        pass
                    else:
                        self.state = "clicked"
                        self.focused = True
                elif isinstance(event, nd_event.ND_EventMouseMotion):
                    self.state = "hover"
            elif isinstance(event, nd_event.ND_EventMouseButtonDown):
                self.state = "normal"
                self.focused = False
                #
                if self.on_line_edit_escaped is not None:
                    self.on_line_edit_escaped(self)
            else:
                self.state = "normal"

            # Delegate scrollbar events
            if self.full_text_width > self.w:
                self.scrollbar.handle_event(event)
                self.scroll_offset = int(self.scrollbar.get_scroll_ratio() * (self.full_text_width - self.w))

        elif isinstance(event, nd_event.ND_EventKeyDown) and self.focused:
            #
            shift_pressed: bool = self.window.main_app.events_manager.is_shift_pressed()
            #
            # TODO: complete with all the keys, for instance the numpad keys, etc...
            if event.key == "escape":
                self.state = "normal"
                self.focused = False
                #
                if self.on_line_edit_escaped is not None:
                    self.on_line_edit_escaped(self)
            elif event.key == "return":
                self.state = "normal"
                self.focused = False
                #
                if self.on_line_edit_validated is not None:
                    self.on_line_edit_validated(self, self.text)
            #
            elif event.key == "backspace" and self.cursor > 0:
                self.text = self.text[: self.cursor - 1] + self.text[self.cursor :]
                self.cursor -= 1
                self.full_text_width = self.window.get_text_size_with_font(self.text, self.font_size, self.font_name).x
                self.scrollbar.content_width = self.full_text_width
            #
            elif event.key == "left arrow" and self.cursor > 0:
                self.cursor -= 1
            #
            elif event.key == "right arrow" and self.cursor < len(self.text):
                self.cursor += 1
                text_width = self.window.get_text_size_with_font(self.text[:self.cursor], self.font_size, self.font_name).x
                if text_width - self.scroll_offset > self.w:
                    self.scroll_offset = text_width - self.w
            #
            elif len(event.key) == 1:
                if shift_pressed:
                    self.write(event.key.upper())
                else:
                    self.write(event.key)
            #
            elif event.key == "espace":
                self.write(" ")
            #
            elif event.key == "semicolon":
                if shift_pressed:
                    self.write(".")
                else:
                    self.write(",")

            # Update scrollbar position
            if self.full_text_width > self.w:
                self.scrollbar.scroll_position = self.scroll_offset / (self.full_text_width - self.w)
            #
            # print(f"DEBUG | event = {event}")
            # self.print_debug_infos()

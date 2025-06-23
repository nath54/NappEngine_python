"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""

#
from typing import Callable, Any, Optional
#
import lib_nadisplay_events as nd_event
from lib_nadisplay_position import ND_Position
from lib_nadisplay_utils import clamp
from lib_nadisplay_core import ND_Window, ND_Elt, ND_EventsHandler_Elts
from lib_nadisplay_elt_button import ND_Elt_Button
from lib_nadisplay_elt_line_edit import ND_Elt_LineEdit
from lib_nadisplay_elt_container import ND_Elt_Container, ND_Position_Container
from lib_nadisplay_utils import dict_sum



# ND_Elt_NumberInput
class ND_Elt_NumberInput(ND_Elt):
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            value: float = 0,
            min_value: float = 0,
            max_value: float = 100,
            step: float = 1,
            digits_after_comma: int = 0,
            on_new_value_validated: Optional[Callable[["ND_Elt_NumberInput", float], None]] = None,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)
        #
        self.on_new_value_validated: Optional[Callable[["ND_Elt_NumberInput", float], None]] = on_new_value_validated
        #
        self.min_value: float = min_value
        self.max_value: float = max_value
        self.step: float = step
        self.digits_after_comma: int = digits_after_comma
        if self.digits_after_comma > 0:
            self.value = round(clamp(value, self.min_value, self.max_value), self.digits_after_comma)
        else:
            self.value = int(clamp(value, self.min_value, self.max_value))
        #
        self.main_row_container: ND_Elt_Container = ND_Elt_Container(
            window=self.window,
            elt_id=f"{self.elt_id}_main_row_container",
            position=self.position,
            element_alignment="row"
        )
        #
        self.line_edit: ND_Elt_LineEdit = ND_Elt_LineEdit(
            window=self.window,
            elt_id=f"{self.elt_id}_line_edit",
            position=ND_Position_Container(w="80%", h="100%", container=self.main_row_container),
            text=str(self.value),
            place_holder="value",
            on_line_edit_escaped=self.on_line_edit_escaped,
            on_line_edit_validated=self.on_line_edit_validated,
            style_name=style_name,
            styles_override=dict_sum(styles_override, {
                "font_name": "FreeSans",
                "font_size": 24
            }),
            events_handler=events_handler
        )
        #
        self.main_row_container.add_element(self.line_edit)
        #
        self.col_bts_container: ND_Elt_Container = ND_Elt_Container(
            window=self.window,
            elt_id=f"{self.elt_id}_col_bts_container",
            position=ND_Position_Container(w="20%", h="100%", container=self.main_row_container)
        )
        self.main_row_container.add_element(self.col_bts_container)
        #
        self.bt_up: ND_Elt_Button = ND_Elt_Button(
            window=self.window,
            elt_id=f"{self.elt_id}_bt_up",
            position=ND_Position_Container(w="100%", h="50%", container=self.col_bts_container),
            text="^",
            style_name=style_name,
            styles_override=dict_sum(styles_override, {
                "font_name": "FreeSans",
                "font_size": 12
            }),
            events_handler=ND_EventsHandler_Elts( fn_on_click=self.on_bt_up_pressed )
        )
        self.col_bts_container.add_element(self.bt_up)
        #
        self.bt_down: ND_Elt_Button = ND_Elt_Button(
            window=self.window,
            elt_id=f"{self.elt_id}_bt_down",
            position=ND_Position_Container(w="100%", h="50%", container=self.col_bts_container),
            text="v",
            style_name=style_name,
            styles_override=dict_sum(styles_override, {
                "font_name": "FreeSans",
                "font_size": 12
            }),
            events_handler=ND_EventsHandler_Elts( fn_on_click=self.on_bt_down_pressed )
        )
        self.col_bts_container.add_element(self.bt_down)


    #
    def get_value(self) -> Any:
        #
        return self.value

    #
    def set_value(self, new_value: Any) -> None:
        #
        self.value = int(new_value)

    #
    def update_layout(self) -> None:
        self.main_row_container.update_layout()

    #
    def render(self) -> None:
        #
        if not self.visible:
            return
        #
        self.main_row_container.render()
        #

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        self.line_edit.handle_event(event)
        self.bt_up.handle_event(event)
        self.bt_down.handle_event(event)

    #
    def on_bt_up_pressed(self, elt: ND_Elt) -> None:
        #
        new_value: float = self.value + self.step
        #
        if self.digits_after_comma > 0:
            self.value = round(clamp(new_value, self.min_value, self.max_value), self.digits_after_comma)
        else:
            self.value = int(clamp(new_value, self.min_value, self.max_value))
        #
        self.line_edit.set_text(str(self.value))

    #
    def on_bt_down_pressed(self, elt: ND_Elt) -> None:
        #
        new_value: float = self.value - self.step
        #
        if self.digits_after_comma > 0:
            self.value = round(clamp(new_value, self.min_value, self.max_value), self.digits_after_comma)
        else:
            self.value = int(clamp(new_value, self.min_value, self.max_value))
        #
        self.line_edit.set_text(str(self.value))

    #
    def on_line_edit_validated(self, line_edit: ND_Elt_LineEdit, value: str) -> None:
        #
        try:
            new_value: float = float(self.line_edit.text)
            #
            if self.digits_after_comma > 0:
                self.value = round(clamp(new_value, self.min_value, self.max_value), self.digits_after_comma)
            else:
                self.value = int(clamp(new_value, self.min_value, self.max_value))
        except Exception as _:
            pass
        finally:
            self.line_edit.set_text(str(self.value))
            #
            if self.on_new_value_validated is not None:
                #
                self.on_new_value_validated(self, self.value)

    #
    def on_line_edit_escaped(self, line_edit: ND_Elt_LineEdit) -> None:
        #
        value: str = self.line_edit.text
        #
        self.on_line_edit_validated(line_edit, value)
        #
        # self.line_edit.set_text(str(self.value))


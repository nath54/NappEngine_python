"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""


from typing import Callable, Any, Optional
#
import lib_nadisplay_events as nd_event
from lib_nadisplay_point import ND_Point
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window, ND_Elt
from lib_nadisplay_elt_clickable import ND_Elt_Clickable
from lib_nadisplay_elt_button import ND_Button
from lib_nadisplay_elt_container import ND_Container, ND_Position_Container



# ND_SelectOptions
class ND_SelectOptions(ND_Elt):
    def __init__(
        self,
        window: ND_Window,
        elt_id: str,
        position: ND_Position,
        value: str,
        options: set[str],
        option_list_buttons_height: int = 300,
        on_value_selected: Optional[Callable[["ND_SelectOptions", str], None]] = None,
        font_size: int = 24,
        font_name: Optional[str] = None
    ) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.font_name: Optional[str] = font_name
        self.font_size: int = font_size
        #
        self.on_value_selected: Optional[Callable[[ND_SelectOptions, str], None]] = on_value_selected
        #
        self.value: str = value
        self.options: set[str] = options
        #
        self.options_bts: dict[str, ND_Button] = {}
        #
        self.option_list_buttons_height: int = option_list_buttons_height
        #
        self.state: str = "base"  # "base" or "selection"
        #
        # 1st side: the main button to show which element is selected, and if clicked, hide itself and show the 2nd part of it
        #
        self.main_button: ND_Button = ND_Button(
            window=self.window,
            elt_id=f"{self.elt_id}_main_button",
            position=self.position,
            text=self.value,
            onclick=self.on_main_button_clicked,
            font_name=font_name,
            font_size=font_size
        )
        #
        # 2nd side: the buttons list to select a new option / see all the available options
        #
        self.bts_options_container: ND_Container = ND_Container(
            window=self.window,
            elt_id=f"{self.elt_id}_bts_options_container",
            position=ND_Position(x=self.x, y=self.y, w=self.w, h=self.option_list_buttons_height),
            element_alignment="col",
            scroll_h=True,
            overflow_hidden=True
        )
        self.bts_options_container.visible = False
        #
        option: str
        for option in self.options:
            self.options_bts[option] = ND_Button(
                window=self.window,
                elt_id=f"{self.elt_id}_bt_option_{option}",
                position=ND_Position_Container(w=self.w, h=self.h, container=self.bts_options_container),
                text=option,
                onclick=lambda x, option=option: self.on_option_button_clicked(option), # type: ignore
                font_name=self.font_name,
                font_size=self.font_size
            )
            self.bts_options_container.add_element(self.options_bts[option])

    #
    def get_value(self) -> Any:
        #
        return self.value

    #
    def set_value(self, new_value: Any) -> None:
        #
        if new_value in self.options:
            #
            self.value = new_value

    #
    def render(self) -> None:
        #
        if self.state == "base":
            self.main_button.render()
        else:
            self.bts_options_container.render()

    #
    def update_layout(self) -> None:
        #
        self.bts_options_container.position = ND_Position(x=self.x, y=self.y, w=self.w, h=self.option_list_buttons_height)
        #
        self.bts_options_container.update_layout()

    #
    def add_option(self, option_value: str) -> None:
        #
        if option_value in self.options:
            return
        #
        self.options.add(option_value)

        #
        self.options_bts[option_value] = ND_Button(
            window=self.window,
            elt_id=f"{self.elt_id}_bt_option_{option_value}",
            position=ND_Position_Container(w=self.w, h=self.h, container=self.bts_options_container),
            text=option_value,
            onclick=lambda x, option=option_value: self.on_option_button_clicked(option), # type: ignore
            font_name=self.font_name,
            font_size=self.font_size
        )
        self.bts_options_container.add_element(self.options_bts[option_value])

        #
        self.update_layout()

    #
    def remove_option(self, option_value: str, new_value: Optional[str] = None) -> None:
        #
        if option_value not in self.options:
            return
        #
        if len(self.options) == 1:  # On ne veut pas ne plus avoir d'options possibles
            return
        #
        self.bts_options_container.remove_element(self.options_bts[option_value])
        #
        del self.options_bts[option_value]
        self.options.remove(option_value)
        #
        if self.value == option_value:
            #
            if new_value is not None and new_value in self.options:
                self.value = new_value
            #
            else:
                #
                self.value = next(iter(self.options))
            #
            self.main_button.text = self.value
        #
        self.update_layout()

    #
    def update_options(self, new_options: set[str], new_value: Optional[str] = None) -> None:
        #
        if len(new_options) == 0:
            return
        #
        for bt in self.options_bts.values():
            self.bts_options_container.remove_element(bt)
        #
        self.options_bts = {}
        #
        self.options = new_options
        #
        option: str
        for option in self.options:
            self.options_bts[option] = ND_Button(
                window=self.window,
                elt_id=f"{self.elt_id}_bt_option_{option}",
                position=ND_Position_Container(w=self.w, h=self.h, container=self.bts_options_container),
                text=option,
                onclick=lambda x, option=option: self.on_option_button_clicked(option), # type: ignore
                font_name=self.font_name,
                font_size=self.font_size
            )
            self.bts_options_container.add_element(self.options_bts[option])

        #
        if self.value not in self.options:
            #
            if new_value is not None and new_value in self.options:
                self.value = new_value
            #
            else:
                #
                self.value = next(iter(self.options))
            #
            self.main_button.text = self.value
        #
        self.update_layout()

    #
    def set_state_base(self) -> None:
        #
        self.state = "base"
        self.bts_options_container.visible = False
        self.main_button.visible = True

    #
    def set_state_selection(self) -> None:
        #
        self.state = "selection"
        #
        self.bts_options_container.visible = True
        self.main_button.visible = False

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if self.state == "base":
            self.main_button.handle_event(event)
        else:
            self.bts_options_container.handle_event(event)
            #
            if isinstance(event, nd_event.ND_EventMouseButtonDown):
                if not self.bts_options_container.position.rect.contains_point(ND_Point(event.x, event.y)):
                    self.set_state_base()

    #
    def on_main_button_clicked(self, clickable: ND_Elt_Clickable) -> None:
        #
        self.set_state_selection()

    #
    def on_option_button_clicked(self, new_option: str) -> None:
        #
        self.value = new_option
        self.main_button.text = self.value
        #
        self.set_state_base()
        #
        if self.on_value_selected is not None:
            self.on_value_selected(self, self.value)

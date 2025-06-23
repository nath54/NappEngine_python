"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""


from typing import Optional, Any

import lib_nadisplay_events as nd_event
from lib_nadisplay_point import ND_Point
from lib_nadisplay_position import ND_Position, ND_Position_Constraints, ND_Position_Margins
from lib_nadisplay_utils import clamp, get_percentage_from_str
from lib_nadisplay_core import ND_Window, ND_Elt, ND_EventsHandler_Elts
from lib_nadisplay_elt_scrollbar import ND_Elt_H_ScrollBar, ND_Elt_V_ScrollBar



# ND_Elt_Container class implementation
class ND_Elt_Container(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            overflow_hidden: bool = True,
            scroll_w: bool = False,
            scroll_h: bool = False,
            element_alignment: str = "row_wrap",
            element_alignment_kargs: dict[str, int | float | str | bool] = {},
            inverse_z_order: bool = False,
            min_space_width_containing_elements: int = 0,
            min_space_height_containing_elements: int = 0,
            scrollbar_w_height: int = 20,
            scrollbar_h_width: int = 20,
            scroll_speed_w: int = 4,
            scroll_speed_h: int = 4,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)

        # If the elements overflows are hidden or not (only used in the render() function)
        self.overflow_hidden: bool = overflow_hidden

        # If the container is a scrollable container in theses directions
        self.scroll_w: bool = scroll_w
        self.scroll_h: bool = scroll_h

        #
        self.scroll_speed_w: int = scroll_speed_w
        self.scroll_speed_h: int = scroll_speed_h

        #
        self.scroll_x: float = 0
        self.scroll_y: float = 0
        self.last_scroll_x: float = 0
        self.last_scroll_y: float = 0

        # The current scroll value
        self.scroll: ND_Point = ND_Point(0, 0)

        # If the elements are aligned in a row, a column, a row with wrap, a column with wrap or a grid
        self.element_alignment: str = element_alignment
        self.element_alignment_kargs: dict[str, int | float | str | bool] = element_alignment_kargs
        self.inverse_z_order: bool = inverse_z_order

        # List of contained elements
        self.elements: list[ND_Elt] = []
        #
        self.elements_by_id: dict[str, ND_Elt] = {}

        # Elements that represents the scrollbar if there is one
        self.w_scrollbar: Optional[ND_Elt_H_ScrollBar] = None
        self.h_scrollbar: Optional[ND_Elt_V_ScrollBar] = None

        #
        self.scrollbar_w_height: int = scrollbar_w_height
        self.scrollbar_h_width: int = scrollbar_h_width

        # Representing the total contained content width and height
        self.content_width: int = 0
        self.content_height: int = 0

        # To help giving contained element space.
        self.min_space_width_containing_elements: int = min_space_width_containing_elements
        self.min_space_height_containing_elements: int = min_space_height_containing_elements

    #
    def get_element_recursively_from_subchild(self, elt_id: str) -> Optional[ND_Elt]:
        #
        if elt_id in self.elements_by_id:
            return self.elements_by_id[elt_id]
        #
        r: Optional[ND_Elt]
        #
        for elt in self.elements_by_id.values():
            #
            r = elt.get_element_recursively_from_subchild(elt_id=elt_id)
            #
            if r is not None:
                #
                return r
        #
        return None

    #
    def update_scroll_layout(self) -> None:
        #
        self.scroll_x = -self.w_scrollbar.scroll_position if self.w_scrollbar else 0
        self.scroll_y = -self.h_scrollbar.scroll_position if self.h_scrollbar else 0
        #
        self.update_layout()
        #
        return
        # #
        # scroll_dx: int = int(self.last_scroll_x - self.scroll_x)
        # scroll_dy: int = int(self.last_scroll_y - self.scroll_y)
        # #
        # elt: ND_Elt
        # for elt in self.elements:
        #     #
        #     elt.position.x += scroll_dx
        #     elt.position.y += scroll_dy
        #     #
        #     if hasattr(elt, "update_scroll_layout"):
        #         elt.update_scroll_layout()
        # #
        # self.last_scroll_x = self.scroll_x
        # self.last_scroll_y = self.scroll_y

    #
    def add_element(self, element: ND_Elt) -> None:
        #
        if element.elt_id in self.elements_by_id:
            raise IndexError(f"Error: Trying to add an element with id {element.elt_id} in container {self.elt_id}, but there was already an element with the same id in there!")
        #
        self.elements.append(element)
        self.elements_by_id[element.elt_id] = element
        #
        self.update_layout()
        #
        if hasattr(element, "update_layout"):
            element.update_layout()

    #
    def remove_element(self, element: ND_Elt) -> None:
        #
        if element.elt_id not in self.elements_by_id:
            raise IndexError(f"Error: Trying to remove an element with id {element.elt_id} in container {self.elt_id}, but there aren't such elements in there !")
        #
        self.elements.remove(element)
        del self.elements_by_id[element.elt_id]
        #
        self.update_layout()

    #
    def remove_element_from_elt_id(self, elt_id: str) -> None:
        #
        if elt_id not in self.elements_by_id:
            raise IndexError(f"Error: Trying to remove an element with id {elt_id} in container {self.elt_id}, but there aren't such elements in there !")
        #
        element: ND_Elt = self.elements_by_id[elt_id]
        #
        self.elements.remove(element)
        del self.elements_by_id[element.elt_id]
        #
        self.update_layout()

    #
    def update_layout(self) -> None:
        #
        if self.element_alignment == "row_wrap":
            self._layout_row_wrap()
        elif self.element_alignment == "col_wrap":
            self._layout_column_wrap()
        elif self.element_alignment == "grid":
            self._layout_grid()
        elif self.element_alignment == "col":
            self._layout_column()
        else:  #  self.element_alignment == "row"
            self._layout_row()

        #
        for elt in self.elements:
            if hasattr(elt, "update_layout"):
                elt.update_layout()

        #
        if self.scroll_w:
            #
            if self.content_width > self.w:
                #
                if not self.w_scrollbar:
                    self.w_scrollbar = ND_Elt_H_ScrollBar(
                                                        window=self.window,
                                                        elt_id=f"{self.elt_id}_wscroll",
                                                        position=ND_Position(self.x, self.y + self.h - self.scrollbar_w_height, self.w, self.scrollbar_w_height),
                                                        content_width=self.content_width,
                                                        on_value_changed=lambda _elt, _value: self.update_scroll_layout()
                    )
                #
                else:
                    self.w_scrollbar.content_width = self.content_width
                    self.w_scrollbar.position.set_x(self.x)
                    self.w_scrollbar.position.set_y(self.y + self.h - self.scrollbar_w_height)
                    self.w_scrollbar.position.set_w(self.w)
                    self.w_scrollbar.position.set_h(self.scrollbar_w_height)
            #
            elif self.w_scrollbar:
                #
                del(self.w_scrollbar)
                self.w_scrollbar = None

        #
        if self.scroll_h:
            #
            if self.content_height > self.h:
                #
                if not self.h_scrollbar:
                    self.h_scrollbar = ND_Elt_V_ScrollBar(
                                                        window=self.window,
                                                        elt_id=f"{self.elt_id}_hscroll",
                                                        position=ND_Position(self.x + self.w - self.scrollbar_h_width, self.y, self.scrollbar_h_width, self.h),
                                                        content_height=self.content_height,
                                                        on_value_changed=lambda _elt, _value: self.update_scroll_layout()
                    )
                #
                else:
                    self.h_scrollbar.content_height = self.content_height
                    self.h_scrollbar.position.set_x(self.x + self.w - self.scrollbar_h_width)
                    self.h_scrollbar.position.set_y(self.y)
                    self.h_scrollbar.position.set_w(self.scrollbar_h_width)
                    self.h_scrollbar.position.set_h(self.h)
            #
            elif self.h_scrollbar:
                #
                del(self.h_scrollbar)
                self.h_scrollbar = None

    #
    def _layout_row_wrap(self) -> None:
        # Initialize row tracking variables
        rows_height: list[int] = [0]
        rows_width: list[int] = [0]
        rows_left_width_total_weight: list[float] = [0]
        rows: list[list[ND_Elt]] = [ [] ]

        #
        crt_x: int = 0
        max_x: int = self.w

        # First pass
        for elt in self.elements:
            #
            elt_w: int = max(elt.w, self.min_space_width_containing_elements) + elt.get_margin_left() + elt.get_margin_right()
            elt_h: int = max(elt.h, self.min_space_height_containing_elements) + elt.get_margin_top() + elt.get_margin_bottom()
            elt_stretch_ratio: float = elt.get_width_stretch_ratio()

            # Si ca dépasse, on crée une nouvelle ligne
            if rows_width[-1] + elt_w >= max_x:
                #
                rows_height.append(elt_h)
                rows_width.append(elt_w)
                rows_left_width_total_weight.append(elt_stretch_ratio)
                rows.append([elt])
                #
                continue

            # Sinon, on ajoute à la ligne actuelle
            #
            rows_height[-1] = max( rows_height[-1], elt_h )
            rows_width[-1] = rows_width[-1] + elt_w
            rows_left_width_total_weight[-1] += elt_stretch_ratio
            rows[-1].append( elt )

        #
        self.content_height = sum(rows_height)
        self.content_width = max(rows_width)
        #
        self.last_scroll_y = self.scroll_y
        self.last_scroll_x = self.scroll_x
        crt_y: int = self.y + int(self.scroll_y)
        space_left: int = 0

        # Second pass
        for i_row in range(len(rows)):
            #
            crt_x = self.x + int(self.scroll_x)
            space_left = self.w - rows_width[i_row]
            #
            for elt in rows[i_row]:
                #
                margin_left: int = 0
                margin_right: int = 0
                margin_top: int = 0
                elt_space_left: int = 0
                #
                if isinstance(elt.position, ND_Position_Container):
                    #
                    elt_stretch_ratio = elt.position.get_width_stretch_ratio()
                    #
                    if elt_stretch_ratio > 0:
                        # We can assume that if elt_stretch_ratio is > 0, the rows_left_width_total_weight[i_row] is > 0
                        elt_space_left = int( float(space_left) * (elt_stretch_ratio / rows_left_width_total_weight[i_row] ) )
                    #
                    margin_left = elt.get_margin_left(elt_space_left)
                    margin_right = elt.get_margin_right(elt_space_left)
                    margin_top = elt.get_margin_top(rows_height[i_row] - elt.h)
                #
                elt.position.set_x(crt_x + margin_left)
                crt_x += elt.w + margin_left + margin_right
                elt.position.set_y(crt_y + margin_top)
            #
            crt_y += rows_height[i_row]

    #
    def _layout_row(self) -> None:

        # Initialize row tracking variables
        row_width: int = 0
        row_left_width_total_weight: float = 0

        #
        crt_x: int = 0

        # First pass
        for elt in self.elements:
            #
            elt_w: int = max(elt.w, self.min_space_width_containing_elements) + elt.get_margin_left() + elt.get_margin_right()
            elt_stretch_ratio: float = elt.get_width_stretch_ratio()

            # On ajoute à la ligne actuelle
            row_width = row_width + elt_w
            row_left_width_total_weight += elt_stretch_ratio

        ##
        self.content_width = row_width
        #
        if isinstance(self.position, ND_Position_Container) and self.position.is_w_auto():
            #
            self.position.set_w(new_w=self.content_width)
            # self.position._w = self.content_width
        #
        self.last_scroll_y = self.scroll_y
        crt_y: int = self.y + int(self.scroll_y)
        space_left: int = 0

        # Second pass
        #
        self.content_height = 0
        #
        self.last_scroll_x = self.scroll_x
        crt_x = self.x + int(self.scroll_x)
        space_left = self.w - row_width
        #
        for elt in self.elements:
            #
            margin_left: int = 0
            margin_right: int = 0
            margin_top: int = 0
            margin_bottom: int = 0
            elt_space_left: int = 0
            #
            if isinstance(elt.position, ND_Position_Container):
                #
                elt_stretch_ratio = elt.position.get_width_stretch_ratio()
                #
                if elt_stretch_ratio > 0:
                    # We can assume that if elt_stretch_ratio is > 0, the rows_left_width_total_weight[i_row] is > 0
                    elt_space_left = int( float(space_left) * (elt_stretch_ratio / row_left_width_total_weight ) )
                #
                margin_left = elt.get_margin_left(elt_space_left)
                margin_right = elt.get_margin_right(elt_space_left)
                margin_top = elt.get_margin_top(self.h - elt.h)
                margin_bottom = elt.get_margin_bottom(self.h - elt.h)
            #
            elt.position.set_x(crt_x + margin_left)
            crt_x += elt.w + margin_left + margin_right
            elt.position.set_y(crt_y + margin_top)
            #
            if margin_top + elt.h + margin_bottom > self.content_height:
                self.content_height = margin_top + elt.h + margin_bottom

    #
    def _layout_column_wrap(self) -> None:

        # Initialize col tracking variables
        cols_height: list[int] = [0]
        cols_width: list[int] = [0]
        cols_left_height_total_weight: list[float] = [0]
        cols: list[list[ND_Elt]] = [ [] ]

        #
        crt_y: int = 0
        max_y: int = self.h

        # First pass
        for elt in self.elements:
            #
            elt_w: int = max(elt.w, self.min_space_width_containing_elements) + elt.get_margin_left() + elt.get_margin_right()
            elt_h: int = max(elt.h, self.min_space_height_containing_elements) + elt.get_margin_top() + elt.get_margin_bottom()
            elt_stretch_ratio: float = elt.get_height_stretch_ratio()

            # Si ca dépasse, on crée une nouvelle ligne
            if cols_height[-1] + elt_h > max_y:
                #
                cols_height.append(elt_h)
                cols_width.append(elt_w)
                cols_left_height_total_weight.append(elt_stretch_ratio)
                cols.append([elt])
                #
                continue

            # Sinon, on ajoute à la ligne actuelle
            #
            cols_width[-1] = max( cols_width[-1], elt_w )
            cols_height[-1] = cols_height[-1] + elt_h
            cols_left_height_total_weight[-1] += elt_stretch_ratio
            cols[-1].append( elt )

        #
        self.content_height = max(cols_height)
        self.content_width = sum(cols_width)
        #
        self.last_scroll_x = self.scroll_x
        self.last_scroll_y = self.scroll_y
        crt_x: int = self.x + int(self.scroll_x)
        space_left: int = 0

        # Second pass
        for i_col in range(len(cols)):
            #
            crt_y = self.y + int(self.scroll_y)
            space_left = self.h - cols_height[i_col]
            #
            for elt in cols[i_col]:
                #
                margin_top: int = 0
                margin_bottom: int = 0
                margin_left: int = 0
                elt_space_left: int = 0
                #
                if isinstance(elt.position, ND_Position_Container):
                    #
                    elt_stretch_ratio = elt.position.get_width_stretch_ratio()
                    #
                    if elt_stretch_ratio > 0:
                        # We can assume that if elt_stretch_ratio is > 0, the cols_left_height_total_weight[i_col] is > 0
                        elt_space_left = int( float(space_left) * (elt_stretch_ratio / cols_left_height_total_weight[i_col] ) )
                    #
                    margin_top = elt.get_margin_top(elt_space_left)
                    margin_bottom = elt.get_margin_bottom(elt_space_left)
                    margin_left = elt.get_margin_top(cols_width[i_col] - elt.w)
                #
                elt.position.set_x(crt_x + margin_left)
                elt.position.set_y(crt_y + margin_top)
                crt_y += elt.h + margin_top + margin_bottom
            #
            crt_x += cols_width[i_col]

    #
    def _layout_column(self) -> None:

        # Initialize col tracking variables
        col_height: int = 0
        col_left_height_total_weight: float = 0

        #
        crt_y: int = 0

        # First pass
        for elt in self.elements:
            #
            elt_h: int = max(elt.h, self.min_space_height_containing_elements) + elt.get_margin_top() + elt.get_margin_bottom()
            elt_stretch_ratio: float = elt.get_height_stretch_ratio()

            # Sinon, on ajoute à la ligne actuelle
            #
            col_height = col_height + elt_h
            col_left_height_total_weight += elt_stretch_ratio

        #
        self.last_scroll_x = self.scroll_x
        crt_x: int = self.x + int(self.scroll_x)
        space_left: int = 0


        ##
        self.content_height = col_height
        #
        if isinstance(self.position, ND_Position_Container) and self.position.is_h_auto():
            #
            self.position.set_h(new_h=col_height)
            # self.position._h = col_height

        # Second pass
        #
        self.content_width = 0
        #
        self.last_scroll_y = self.scroll_y
        crt_y = self.y + int(self.scroll_y)
        space_left = self.h - col_height
        #
        for elt in self.elements:
            #
            margin_top: int = 0
            margin_bottom: int = 0
            margin_left: int = 0
            margin_right: int = 0
            elt_space_left: int = 0
            #
            if isinstance(elt.position, ND_Position_Container):
                #
                elt_stretch_ratio = elt.position.get_width_stretch_ratio()
                #
                if elt_stretch_ratio > 0 and col_left_height_total_weight > 0:
                    # We can assume that if elt_stretch_ratio is > 0, the col_left_height_total_weight is > 0
                    elt_space_left = int( float(space_left) * (elt_stretch_ratio / col_left_height_total_weight ) )
                #
                margin_top = elt.get_margin_top(elt_space_left)
                margin_bottom = elt.get_margin_bottom(elt_space_left)
                margin_left = elt.get_margin_left(self.w - elt.w)
                margin_right = elt.get_margin_right(self.w - elt.w)
            #
            elt.position.set_x(crt_x + margin_left)
            elt.position.set_y(crt_y + margin_top)
            crt_y += elt.h + margin_top + margin_bottom
            #
            if margin_left + elt.w + margin_right > self.content_width:
                self.content_width = margin_left + elt.w + margin_right
        #
        self.content_height = crt_y

    #
    def _layout_grid(self):
        #
        cols: int = int( self.element_alignment_kargs.get("cols", 3) )
        row_spacing: int = int( self.element_alignment_kargs.get("row_spacing", 5) )
        col_spacing: int = int( self.element_alignment_kargs.get("col_spacing", 5) )
        #
        max_width: int = (self.w - (cols - 1) * col_spacing) // cols
        #
        x: int = 0
        y: int = 0
        #
        row_height: int = 0

        #
        self.last_scroll_x = self.scroll_x
        self.last_scroll_y = self.scroll_y

        #
        for i, element in enumerate(self.elements):
            #
            # element.position._w = min(element.w, max_width)
            element.position.set_w(new_w=min(element.w, max_width))
            #
            if i % cols == 0 and i != 0:
                x = 0
                y += row_height + row_spacing
                row_height = 0
            #
            element.position.set_x(new_x=self.x + int(self.scroll_x) + x)
            element.position.set_y(new_y=self.y + int(self.scroll_y) + y)
            # element._x = self.x + int(self.scroll_x) + x
            # element._y = self.y + int(self.scroll_y) + y
            #
            x += element.w + col_spacing
            # x += element.tx + col_spacing
            #
            row_height = max(row_height, element.h)
            # row_height = max(row_height, element.ty)

        self.content_width = self.w
        self.content_height = y + row_height

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        #
        if self.overflow_hidden:
            self.window.enable_area_drawing_constraints(self.x, self.y, self.w, self.h)

        # Render each element with the scrollbar offsets applied
        elt: ND_Elt
        rendering_order = range(len(self.elements))
        #
        if self.inverse_z_order:
            rendering_order = rendering_order[::-1]
        #
        for i in rendering_order:
            #
            elt = self.elements[i]

            #
            elt.render()


        # Remove clipping
        if self.overflow_hidden:
            self.window.disable_area_drawing_constraints()

        # Render scrollbars
        if self.w_scrollbar:
            self.w_scrollbar.render()
        if self.h_scrollbar:
            self.h_scrollbar.render()

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if self.w_scrollbar:
            self.w_scrollbar.handle_event(event)
        if self.h_scrollbar:
            self.h_scrollbar.handle_event(event)

        # Mouse scroll events
        if isinstance(event, nd_event.ND_EventMouseWheelScrolled):
            #
            update_scroll: bool = False
            #
            if self.h_scrollbar is not None:
                #
                self.h_scrollbar.scroll_position = clamp(self.h_scrollbar.scroll_position + event.scroll_y * self.scroll_speed_h, 0, self.h_scrollbar.content_height)
                #
                update_scroll = True
            #
            if self.w_scrollbar is not None:
                #
                self.w_scrollbar.scroll_position = clamp(self.w_scrollbar.scroll_position + event.scroll_x * self.scroll_speed_w, 0, self.w_scrollbar.content_width)
                #
                update_scroll = True
            #
            if update_scroll:
                self.update_scroll_layout()


        # Propagate events to child elements
        elt_order = range(len(self.elements))
        #
        if not self.inverse_z_order:
            elt_order = elt_order[::-1]
        #
        for i in elt_order:
            #
            element = self.elements[i]
            if hasattr(element, 'handle_event'):
                element.handle_event(event)



#
class ND_Position_Container(ND_Position):
    #
    def __init__(
                    self,
                    w: int | str,
                    h: int | str,
                    container: ND_Elt_Container,
                    position_constraints: Optional[ND_Position_Constraints] = None,
                    position_margins: Optional[ND_Position_Margins] = None
    ) -> None:

        #
        self.w_str: Optional[str] = None
        self.h_str: Optional[str] = None

        #
        if isinstance(w, str):
            self.w_str = w
            w = -1

        #
        if isinstance(h, str):
            self.h_str = h
            h = -1

        #
        if self.w_str == "square" and self.h_str == "square":
            raise UserWarning("Error: width and height cannot have attribute 'square' !!!")

        #
        super().__init__(0, 0, w, h)

        #
        self.container: ND_Elt_Container = container
        #
        self.positions_constraints: Optional[ND_Position_Constraints] = position_constraints
        self.position_margins: Optional[ND_Position_Margins] = position_margins

    #
    def is_w_auto(self) -> bool:
        return self.w_str == "auto"

    #
    def is_h_auto(self) -> bool:
        return self.h_str == "auto"

    #
    @property
    def w(self) -> int:
        #
        if self.w_str is None:
            return self._w
        #
        elif self.w_str == "auto":
            return max(self._w, 0)
        #
        elif self.w_str == "square":
            return self.h
        #
        w: float = get_percentage_from_str(self.w_str) / 100.0
        #
        width: int = int(w * self.container.w)
        #
        if self.positions_constraints:
            #
            if self.positions_constraints.min_width and width < self.positions_constraints.min_width:
                width = self.positions_constraints.min_width
            #
            if self.positions_constraints.max_width and width > self.positions_constraints.max_width:
                width = self.positions_constraints.max_width
        #
        return width

    #
    @w.setter
    def w(self, new_w: int) -> None:
        # TODO
        pass

    #
    @property
    def h(self) -> int:
        #
        if self.h_str is None:
            return self._h
        #
        elif self.h_str == "auto":
            return max(self._h, 0)
        #
        elif self.h_str == "square":
            return self.w
        #
        h: float = get_percentage_from_str(self.h_str) / 100.0
        #
        height: int = int(h * self.container.h)
        #
        if self.positions_constraints:
            #
            if self.positions_constraints.min_height and height < self.positions_constraints.min_height:
                height = self.positions_constraints.min_height
            #
            if self.positions_constraints.max_height and height > self.positions_constraints.max_height:
                height = self.positions_constraints.max_height
        #
        return height

    #
    @h.setter
    def h(self, new_h: int) -> None:
        # TODO
        pass

    #
    @property
    def visible(self) -> bool:
        return self.container.visible

    #
    def get_margin_left(self, space_left: int = -1) -> int:
        #
        if self.position_margins is None:
            return 0

        #
        mleft: Optional[int | str] = self.position_margins.margin_left
        if mleft is None:
            mleft = self.position_margins.margin
        #
        if mleft is None:
            mleft = self.position_margins.min_margin_left

        #
        pleft: float = 0.0

        #
        if isinstance(mleft, int):
            if not isinstance(self.position_margins.margin_right, str):
                return mleft
            #
            pleft = (100.0 - get_percentage_from_str(self.position_margins.margin_right)) / 100.0
        else:
            pleft = get_percentage_from_str(mleft) / 100.0

        #
        return max(
                    self.position_margins.min_margin_left,
                    int( space_left * pleft )
        )

    #
    def get_margin_right(self, space_left: int = -1) -> int:
        #
        if self.position_margins is None:
            return 0

        #
        mval: Optional[int | str] = self.position_margins.margin_right
        if mval is None:
            mval = self.position_margins.margin
        #
        if mval is None:
            mval = self.position_margins.min_margin_right

        #
        pval: float = 0.0

        #
        if isinstance(mval, int):
            if not isinstance(self.position_margins.margin_left, str):
                return mval
            #
            pval = (100.0 - get_percentage_from_str(self.position_margins.margin_left)) / 100.0
        else:
            pval = get_percentage_from_str(mval) / 100.0

        #
        return max(
                    self.position_margins.min_margin_right,
                    int( space_left * pval )
        )

    #
    def get_margin_top(self, space_left: int = -1) -> int:
        #
        if self.position_margins is None:
            return 0

        #
        mval: Optional[int | str] = self.position_margins.margin_top
        if mval is None:
            mval = self.position_margins.margin
        #
        if mval is None:
            mval = self.position_margins.min_margin_top

        #
        pval: float = 0.0

        #
        if isinstance(mval, int):
            if not isinstance(self.position_margins.margin_bottom, str):
                return mval
            #
            pval = (100.0 - get_percentage_from_str(self.position_margins.margin_bottom)) / 100.0
        else:
            pval = get_percentage_from_str(mval) / 100.0

        #
        return max(
                    self.position_margins.min_margin_top,
                    int( space_left * pval )
        )

    #
    def get_margin_bottom(self, space_left: int = -1) -> int:
        #
        if self.position_margins is None:
            return 0

        #
        mval: Optional[int | str] = self.position_margins.margin_bottom
        if mval is None:
            mval = self.position_margins.margin
        #
        if mval is None:
            mval = self.position_margins.min_margin_bottom

        #
        pval: float = 0.0

        #
        if isinstance(mval, int):
            if not isinstance(self.position_margins.margin_top, str):
                return mval
            #
            pval = (100.0 - get_percentage_from_str(self.position_margins.margin_top)) / 100.0
        else:
            pval = get_percentage_from_str(mval) / 100.0

        #
        return max(
                    self.position_margins.min_margin_bottom,
                    int( space_left * pval )
        )

    #
    def get_width_stretch_ratio(self) -> float:
        #
        if self.position_margins is None:
            return 0.0
        #
        if isinstance(self.position_margins.margin_left, str) or isinstance(self.position_margins.margin_right, str):
            return self.position_margins.width_stretch_ratio
        #
        return 0.0

    #
    def get_height_stretch_ratio(self) -> float:
        #
        if self.position_margins is None:
            return 0.0
        #
        if isinstance(self.position_margins.margin_top, str) or isinstance(self.position_margins.margin_bottom, str):
            return self.position_margins.height_stretch_ratio
        #
        return 0.0



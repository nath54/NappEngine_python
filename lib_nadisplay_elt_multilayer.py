"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""

#
from typing import Optional
#
import lib_nadisplay_events as nd_event
from lib_nadisplay_position import ND_Position, ND_Position_Constraints, ND_Position_Margins
from lib_nadisplay_utils import get_percentage_from_str
from lib_nadisplay_core import ND_Window, ND_Elt





# ND_Elt_MultiLayer class implementation
class ND_Elt_MultiLayer(ND_Elt):
    #
    def __init__(
                    self,
                    window: ND_Window,
                    elt_id: str,
                    position: ND_Position,
                    elements_layers: dict[int, ND_Elt] = {}
    ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position)


        # list of elements sorted by render importance with layers (ascending order)
        self.elements_layers: dict[int, ND_Elt] = elements_layers
        self.elements_by_id: dict[str, ND_Elt] = {}

        #
        layer: int
        elt: ND_Elt
        #
        for layer in self.elements_layers:
            #
            elt = self.elements_layers[layer]
            element_id = elt.elt_id
            #
            if element_id in self.elements_by_id:
                raise UserWarning(f"Error: at least two elements have the same id: {element_id}!")
            #
            self.elements_by_id[element_id] = elt
            #
            self.update_layout_of_element(elt)
        #
        self.layers_keys: list[int] = sorted(list(self.elements_layers.keys()))

    #
    def get_element_recursively_from_subchild(self, elt_id: str) -> Optional[ND_Elt]:
        #
        if elt_id in self.elements_by_id:
            return self.elements_by_id[elt_id]
        #
        r: Optional[ND_Elt] = None
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
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        for elt in self.elements_by_id.values():

            #
            if hasattr(elt, "handle_event"):
                elt.handle_event(event)

        # TODO: gérer les évenenements en fonctions de si un layer du dessus bloque les évenements en dessous

        # #
        # layer: int
        # for layer in self.layers_keys[::-1]:

        #     elt_list: list[str] = self.collisions_layers[layer].get_colliding_ids( (event.button.x, event.button.y) )

        #     for elt_id in elt_list:
        #         self.elements_by_id[elt_id].handle_event(event)

        #     if len(elt_list) > 0:
        #         return

    #
    def update_layout_of_element(self, elt: ND_Elt) -> None:
        #
        ew: int = elt.w
        eh: int = elt.h
        emt: int = elt.get_margin_top(self.h - eh)
        eml: int = elt.get_margin_left(self.w - ew)
        #
        enx: int = self.x + eml
        eny: int = self.y + emt
        #
        elt.position.set_x(enx)
        elt.position.set_y(eny)
        #
        if hasattr(elt, "update_layout"):
            elt.update_layout()

    #
    def update_layout(self) -> None:
        #
        for elt in self.elements_by_id.values():
            #
            self.update_layout_of_element(elt)

    #
    def insert_to_layers_keys(self, layer_key: int) -> None:

        if ( len(self.layers_keys) == 0 ) or ( layer_key > self.layers_keys[-1] ):
            self.layers_keys.append(layer_key)
            return

        # Insertion inside a sorted list by ascendant
        i: int
        k: int
        for i, k in enumerate(self.layers_keys):
            if k > layer_key:
                self.layers_keys.insert(i, layer_key)
                return

    #
    def add_element(self, layer_id: int, elt: ND_Elt) -> None:
        #
        elt_id: str = elt.elt_id

        #
        if elt_id in self.elements_by_id:
            raise UserWarning(f"Error: at least two elements in the multi-layer {self.elt_id} have the same id: {elt_id}!")

        #
        if layer_id not in self.elements_layers:
            self.elements_layers[layer_id] = elt
            self.elements_by_id[elt.elt_id] = elt
            self.insert_to_layers_keys(layer_id)
            #
            self.update_layout_of_element(elt)
        #
        else:
            raise UserWarning(f"Error: trying to insert an element to multi-layer {self.elt_id} on the same layer than another element!")

    #
    def render(self) -> None:
        #
        layer_key: int
        for layer_key in self.layers_keys:
            #
            element: ND_Elt = self.elements_layers[layer_key]
            #
            element.render()




#
class ND_Position_MultiLayer(ND_Position):
    #
    def __init__(
                    self,
                    multilayer: ND_Elt_MultiLayer,
                    w: int | str = -1,
                    h: int | str = -1,
                    position_constraints: Optional[ND_Position_Constraints] = None,
                    position_margins: Optional[ND_Position_Margins] = None
    ) -> None:

        #
        self.w_str: Optional[str] = None
        self.h_str: Optional[str] = None

        #
        w_int: int = -1
        h_int: int = -1

        if isinstance(w, str):
            self.w_str = w
            w_int = -1
        #
        else:
            #
            w_int = int(w)

        #
        if isinstance(h, str):
            self.h_str = h
            h_int = -1
        #
        else:
            #
            h_int = int(h)

        #
        super().__init__(0, 0, w_int, h_int)

        #
        self.multilayer: ND_Elt_MultiLayer = multilayer
        #
        self.positions_constraints: Optional[ND_Position_Constraints] = position_constraints
        self.position_margins: Optional[ND_Position_Margins] = position_margins

    #
    @property
    def w(self) -> int:
        #
        if self.w_str is None:
            if self._w <= 0:
                return self.multilayer.w
            #
            return self._w
        #
        w: float = get_percentage_from_str(self.w_str) / 100.0
        #
        return int(w * self.multilayer.w)

    #
    @w.setter
    def w(self, new_value: int) -> None:  # type: ignore
        # TODO
        pass

    #
    @property
    def h(self) -> int:
        #
        if self.h_str is None:
            if self._h <= 0:
                return self.multilayer.h
            #
            return self._h
        #
        h: float = get_percentage_from_str(self.h_str) / 100.0
        #
        return int(h * self.multilayer.h)

    #
    @h.setter
    def h(self, new_value: int) -> None:  # type: ignore
        # TODO
        pass

    #
    @property
    def visible(self) -> bool:
        return self.multilayer.visible

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


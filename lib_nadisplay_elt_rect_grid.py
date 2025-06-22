"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""


from typing import Callable, Any, Optional
#
import math
import random
#
import numpy as np
#
from lib_nadisplay_colors import ND_Color
from lib_nadisplay_point import ND_Point
from lib_nadisplay_rects import ND_Rect
from lib_nadisplay_position import ND_Position
from lib_nadisplay_utils import clamp
from lib_nadisplay_core import ND_Window, ND_Elt
from lib_nadisplay_transformation import ND_Transformation




#
class ND_CameraGrid(ND_Elt):
    #
    def __init__(self, window: ND_Window, elt_id: str, position: ND_Position, grids_to_render: list["ND_RectGrid"], zoom_x: float = 1.0, zoom_y: float = 1.0) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.grids_to_render: list[ND_RectGrid] = grids_to_render
        #
        self.origin: ND_Point = ND_Point(0, 0)
        self.zoom_x: float = zoom_x
        self.zoom_y: float = zoom_y
        #
        self.min_zoom: float = 0.1
        self.max_zoom: float = 100
        #
        self.grid_lines_width: int = 0
        self.grid_lines_color: ND_Color = ND_Color(255, 255, 255)
        grid_to_render: ND_RectGrid
        for grid_to_render in self.grids_to_render:
            if grid_to_render.grid_lines_width > self.grid_lines_width:
                self.grid_lines_width = grid_to_render.grid_lines_width
                self.grid_lines_color = grid_to_render.grid_lines_color

    #
    def render(self) -> None:
        #
        if len(self.grids_to_render) == 0:  # If no grids to render
            return
        #
        zx: float = clamp(self.zoom_x, self.min_zoom, self.max_zoom)
        zy: float = clamp(self.zoom_y, self.min_zoom, self.max_zoom)
        #
        self.window.enable_area_drawing_constraints(self.x, self.y, self.w, self.h)
        #
        gtx: int = int(zx * self.grids_to_render[0].grid_tx)
        gty: int = int(zy * self.grids_to_render[0].grid_ty)
        #
        lines_width: int = 0
        if self.grid_lines_width > 0:
            lines_width = max( 1, round( max(zx, zy) * self.grid_lines_width ) )
        #
        deb_x: int = self.origin.x # math.ceil( self.origin.x / (gtx + lines_width) )
        deb_y: int = self.origin.y # math.ceil( self.origin.y / (gty + lines_width) )
        fin_x: int = self.origin.x + math.ceil( (self.w) / (gtx) ) + 1
        fin_y: int = self.origin.y + math.ceil( (self.h) / (gty) ) + 1

        # Dessin des lignes
        cx: int
        cy: int
        dcx: int
        dcy: int
        for cx in range(deb_x, fin_x + 1):
            #
            dcx = self.x + int((cx-deb_x) * gtx)

            # Dessin ligne
            self.window.draw_thick_line(
                                            x1=dcx, x2=dcx, y1=self.y, y2=self.y+self.h,
                                            color=self.grid_lines_color,
                                            line_thickness=lines_width
            )

        #
        for cy in range(deb_y, fin_y + 1):
            #
            dcy = self.y + int((cy-deb_y) * gty)

            # Dessin Ligne
            self.window.draw_thick_line(
                                            x1=self.x, x2=self.x+self.w, y1=dcy, y2=dcy,
                                            color=self.grid_lines_color,
                                            line_thickness=lines_width
            )

        #
        grid_to_render: ND_RectGrid
        for grid_to_render in self.grids_to_render:

            # Dessin des éléments
            for cx in range(deb_x, fin_x + 1):
                #
                dcx = self.x + int((cx-deb_x) * gtx)
                #
                for cy in range(deb_y, fin_y + 1):
                    #
                    dcy = self.y + int((cy-deb_y) * gty)
                    #
                    elt: Optional[ND_Elt] = grid_to_render.get_element_at_grid_case(ND_Point(cx, cy))
                    #
                    if elt is None:
                        continue
                    #
                    old_position: ND_Position = elt.position
                    #
                    old_transformations: ND_Transformation = elt.transformations
                    #
                    if ND_Point(cx, cy) in grid_to_render.grid_transformations:
                        elt.transformations = elt.transformations + grid_to_render.grid_transformations[ND_Point(cx, cy)]
                    #
                    elt.position = ND_Position(dcx, dcy, int(gtx), int(gty))
                    #
                    elt.render()
                    #
                    elt.position = old_position
                    #
                    elt.transformations = old_transformations
                    #

        #
        self.window.disable_area_drawing_constraints()
        #

    #
    def move_camera_to_grid_area(self, grid_area: ND_Rect, force_square_tiles: bool = True) -> None:
        #
        if not self.grids_to_render:
            return
        #
        self.origin.x = grid_area.x - 1
        self.origin.y = grid_area.y - 1
        #
        self.zoom_x = float(self.w) / float((grid_area.w+3) * (self.grids_to_render[0].grid_tx+self.grid_lines_width))
        self.zoom_y = float(self.h) / float((grid_area.h+3) * (self.grids_to_render[0].grid_ty+self.grid_lines_width))
        #
        if force_square_tiles:
            mz: float = min(self.zoom_x, self.zoom_y)
            self.zoom_x = mz
            self.zoom_y = mz


#
class ND_RectGrid(ND_Elt):
    #
    def __init__(self, window: ND_Window, elt_id: str, position: ND_Position, grid_tx: int, grid_ty: int, grid_lines_width: int = 0, grid_lines_color: ND_Color = ND_Color(0, 0, 0)) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.default_element_grid_id: int = -1  # elt_grid_id < 0 => is None, Nothing is displayed
        #
        self.grid_tx: int = grid_tx
        self.grid_ty: int = grid_ty
        #
        self.grid_lines_width: int = grid_lines_width
        self.grid_lines_color: ND_Color = grid_lines_color
        #
        self.grid_elements_by_id: dict[int, ND_Elt] = {}
        self.grid_positions_by_id: dict[int, set[ND_Point]] = {}
        self.elements_to_grid_id: dict[ND_Elt, int] = {}  # hash = object's pointer / (general/memory) id
        #
        self.next_available_id: int = 0
        #
        self.grid: dict[ND_Point, int] = {}  # dict key = (ND_Point=hash(f"{x}_{y}")) -> elt_grid_id
        self.grid_transformations: dict[ND_Point, ND_Transformation] = {}

    # Supprime tout, grille, éléments, ...
    def clean(self) -> None:
        #
        self.default_elt_grid_id = -1
        #
        self.grid_elements_by_id = {}
        self.grid_positions_by_id = {}
        self.elements_to_grid_id = {}
        #
        self.next_available_id = 0
        #
        self.grid = {}

    #
    def _set_grid_position(self, position: ND_Point, elt_grid_id: int = -1) -> None:
        #
        if elt_grid_id >= 0:
            self.grid[position] = elt_grid_id
            self.grid_positions_by_id[elt_grid_id].add(position)  # On ajoute la position de l'élement
        #
        elif position in self.grid:
            #
            old_elt_grid_id: int = self.grid[position]
            if old_elt_grid_id in self.grid_positions_by_id:  # On supprime la position de l'ancien element
                #
                if position in self.grid_positions_by_id[old_elt_grid_id]:
                    self.grid_positions_by_id[old_elt_grid_id].remove(position)
            #
            del self.grid[position]

    #
    def add_element_to_grid(self, element: ND_Elt, position: ND_Point | list[ND_Point]) -> int:
        #
        if element not in self.elements_to_grid_id:
            self.elements_to_grid_id[element] = self.next_available_id
            self.grid_elements_by_id[self.next_available_id] = element
            self.grid_positions_by_id[self.next_available_id] = set()
            self.next_available_id += 1
        #
        elt_grid_id = self.elements_to_grid_id[element]
        #
        self.add_element_position(elt_grid_id, position)
        #
        return elt_grid_id

    #
    def add_element_position(self, elt_id: int, position: ND_Point | list[ND_Point]) -> None:
        #
        if isinstance(position, list):  # liste de points
            #
            for pos in position:
                self._set_grid_position(pos, elt_id)
        #
        else:  # Point unique
            self._set_grid_position(position, elt_id)

    #
    def set_transformations_to_position(self, position: ND_Point, transformations: Optional[ND_Transformation]) -> None:
        #
        if transformations is None:
            if position in self.grid_transformations:
                del self.grid_transformations[position]
            return
        #
        self.grid_transformations[position] = transformations

    #
    def remove_element_of_grid(self, element: ND_Elt) -> None:
        #
        if element not in self.elements_to_grid_id:
            return
        #
        elt_id: int = self.elements_to_grid_id[element]

        # On va supprimer toutes les cases de la grille où l'élément était
        position: ND_Point
        for position in self.grid_positions_by_id[elt_id]:
            #
            self._set_grid_position(position, -1)

        # Si l'élément était l'élément par défaut
        if self.default_elt_grid_id == elt_id:
            #
            self.default_elt_grid_id = -1

        #
        del self.grid_positions_by_id[elt_id]
        del self.grid_elements_by_id[elt_id]
        del self.elements_to_grid_id[element]

    #
    def remove_at_position(self, pos: ND_Point) -> None:
        #
        if pos not in self.grid:
            return
        #
        elt_id: int = self.grid[pos]

        #
        if elt_id < 0:
            return

        # On supprimer la position de l'élément
        self.grid_positions_by_id[elt_id].remove(pos)
        self._set_grid_position(pos, -1)

    #
    def get_element_at_grid_case(self, case: ND_Point) -> Optional[ND_Elt]:
        #
        if case not in self.grid:
            return None
        #
        grid_elt_id: int = self.grid[case]
        #
        if grid_elt_id not in self.grid_elements_by_id:
            return None
        #
        return self.grid_elements_by_id[grid_elt_id]

    #
    def get_element_id_at_grid_case(self, case: ND_Point) -> Optional[int]:
        #
        if case not in self.grid:
            return None
        #
        return self.grid[case]

    #
    def get_empty_case_in_range(self, x_min: int, x_max: int, y_min: int, y_max: int) -> Optional[ND_Point]:
        #
        if x_min > x_max or y_min > y_max:
            #
            return None
        #
        dx: int = x_max - x_min
        dy: int = y_max - y_min
        r: int = int(math.sqrt(dx**2 + dy**2))

        # randoms
        xx: int
        yy: int
        p: ND_Point
        for _ in range(0, r):
            #
            xx = random.randint(x_min, x_max)
            yy = random.randint(y_min, y_max)
            p = ND_Point(xx, yy)
            #
            if p not in self.grid:
                return p

        # Brute si le random n'a rien trouvé
        for xx in range(x_min, x_max+1):
            for yy in range(y_min, y_max+1):
                #
                p = ND_Point(xx, yy)
                #
                if p not in self.grid:
                    return p

        #
        return None

    #
    def render(self) -> None:
        # Do nothing here, because it is a camera that have to render
        return

    #
    def export_chunk_of_grid_to_numpy(self, x_0: int, y_0: int, x_1: int, y_1: int, fn_elt_to_value: Callable[[Optional[ND_Elt], Optional[int]], int | float], np_type: type = np.float32) -> np.ndarray[Any, Any]:
        #
        dtx: int = x_1 - x_0
        dty: int = y_1 - y_0
        #
        grid: np.ndarray[Any, Any] = np.zeros((dtx, dty), dtype=np_type)
        #
        for dx in range(dtx):
            for dy in range(dty):
                #
                case_point: ND_Point = ND_Point(x_0 + dx, y_0 + dy)
                #
                elt: Optional[ND_Elt] = self.get_element_at_grid_case(case_point)
                elt_id: Optional[int] = self.get_element_id_at_grid_case(case_point)
                #
                grid[dx, dy] = fn_elt_to_value(elt, elt_id)
        #
        return grid


#
class ND_Position_RectGrid(ND_Position):
    #
    def __init__(self, rect_grid: ND_RectGrid) -> None:
        #
        super().__init__()
        #
        self.rect_grid: ND_RectGrid = rect_grid
        #

    #
    @property
    def w(self) -> int:
        return self.rect_grid.grid_tx

    #
    @w.setter
    def w(self, new_w: int) -> None:
        # TODO
        pass

    #
    @property
    def h(self) -> int:
        return self.rect_grid.grid_ty

    #
    @h.setter
    def h(self, new_h: int) -> None:
        # TODO
        pass

    #
    def current_grid_case(self, case: ND_Point) -> None:
        self._x = case.x
        self._y = case.y

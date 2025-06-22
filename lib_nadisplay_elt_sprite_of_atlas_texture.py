"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""


from typing import Optional
#
from lib_nadisplay_point import ND_Point
from lib_nadisplay_position import ND_Position
from lib_nadisplay_utils import clamp
from lib_nadisplay_core import ND_Window, ND_Elt
from lib_nadisplay_transformation import ND_Transformation



#
class ND_AtlasTexture:
    #
    def __init__(self, window: ND_Window, texture_atlas_path: str, tiles_size: ND_Point = ND_Point(32, 32)) -> None:
        #
        self.window: ND_Window = window
        #
        self.texture_atlas_path: str = texture_atlas_path
        #
        self.texture_atlas: Optional[int] = None
        #
        self.tiles_size: ND_Point = tiles_size
        self.texture_dim: ND_Point = ND_Point(-1, -1)

    #
    def render_texture_at_position(self,
                                    at_win_x: int, at_win_y: int, at_win_w: int, at_win_h: int,
                                    tile_x: int, tile_y: int, nb_tiles_w: int = 1, nb_tiles_h: int = 1,
                                    transformations: ND_Transformation = ND_Transformation()
        ) -> None:

        #
        if self.texture_atlas is None:
            #
            self.texture_atlas = self.window.prepare_image_to_render(self.texture_atlas_path)
            self.texture_dim = self.window.get_prepared_texture_size(self.texture_atlas)

        #
        src_x: int = self.tiles_size.x * tile_x
        src_y: int = self.tiles_size.y * tile_y
        src_w: int = self.tiles_size.x * nb_tiles_w
        src_h: int = self.tiles_size.y * nb_tiles_h

        #
        src_x = clamp(src_x, 0, self.texture_dim.x)
        src_y = clamp(src_y, 0, self.texture_dim.y)
        src_w = clamp(src_w, 0, self.texture_dim.x-src_x)
        src_h = clamp(src_h, 0, self.texture_dim.y-src_y)

        #
        self.window.render_part_of_prepared_texture(
                self.texture_atlas,
                at_win_x, at_win_y, at_win_w, at_win_h,
                src_x, src_y, src_w, src_h,
                transformations
        )


#
class ND_Elt_Sprite_of_AtlasTexture(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            atlas_texture: ND_AtlasTexture,
            tile_x: int,
            tile_y: int,
            nb_tiles_x: int = 1,
            nb_tiles_y: int = 1
        ) -> None:
        #
        super().__init__(window, elt_id, position)
        #
        self.atlas_texture: ND_AtlasTexture = atlas_texture
        #
        self.tile_x: int = tile_x
        self.tile_y: int = tile_y
        self.nb_tiles_x: int = nb_tiles_x
        self.nb_tiles_y: int = nb_tiles_y
        #
        self.transformations = ND_Transformation()

    #
    def render(self) -> None:
        #
        self.atlas_texture.render_texture_at_position(
                self.x, self.y, self.w, self.h,
                self.tile_x, self.tile_y, self.nb_tiles_x, self.nb_tiles_y,
                self.transformations
        )

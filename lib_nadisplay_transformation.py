"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Some utility functions for manipulating colors, and a database of common color names and their associated RGB codes.

"""

#
from typing import Optional
#
from lib_nadisplay_colors import ND_Color


#
class ND_Transformation:

    def __init__(
        self,
        color_modulation: Optional[ND_Color] = None,
        rotation: Optional[float] = None,
        flip_x: bool = False,
        flip_y: bool = False
    ) -> None:
        #
        self.color_modulation: Optional[ND_Color] = color_modulation
        self.rotation: Optional[float] = rotation % 360 if rotation is not None else None
        self.flip_x: bool = flip_x
        self.flip_y: bool = flip_y

    def __add__(self, t: 'ND_Transformation') -> 'ND_Transformation':
        #
        nt: ND_Transformation = ND_Transformation()
        #
        if self.color_modulation is not None:
            #
            if t.color_modulation is not None:
                #
                nt.color_modulation = self.color_modulation + t.color_modulation
            #
            else:
                nt.color_modulation = self.color_modulation
        #
        else:
            nt.color_modulation = t.color_modulation

        #
        if self.rotation is not None:
            #
            if t.rotation is not None:
                #
                nt.rotation = (self.rotation + t.rotation) % 360
            #
            else:
                nt.rotation = self.rotation
        #
        else:
            nt.rotation = t.rotation

        #
        nt.flip_x = (self.flip_x and not t.flip_x) or (t.flip_x and not self.flip_x)
        nt.flip_y = (self.flip_y and not t.flip_y) or (t.flip_y and not self.flip_y)

        #
        return nt

    #
    def __repr__(self) -> str:
        #
        return f"Transformations(color_modulation={self.color_modulation}, rotation={self.rotation}, flip_x={self.flip_x}, flip_y={self.flip_y})"

"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Some utility classes for manipuling points.

"""

#
from typing import Any
#
from math import sqrt
import numpy as np


#
class ND_Point:
    #
    def __init__(self, x: int, y: int) -> None:
        #
        self.x: int = x
        self.y: int = y


    #
    def __hash__(self) -> int:
        return hash(f"{self.x}_{self.y}")


    #
    def __repr__(self) -> str:
        #
        return f"ND_Point(x={self.x}, y={self.y})"


    #
    def __eq__(self, other: object) -> bool:
        #
        if not isinstance(other, ND_Point):
            return NotImplemented
        #
        return self.x == other.x and self.y == other.y


    #
    def __add__(self, other: 'ND_Point') -> 'ND_Point':
        #
        return ND_Point(self.x + other.x, self.y + other.y)


    #
    def __sub__(self, other: 'ND_Point') -> 'ND_Point':
        #
        return ND_Point(self.x - other.x, self.y - other.y)


    #
    def __neg__(self) -> 'ND_Point':
        return ND_Point(-self.x, -self.y)


    #
    def distance_to(self, other: 'ND_Point') -> float:
        #
        return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


    #
    def np_normalize(self) -> np.ndarray[Any, Any]:
        #
        norm: float = self.x + self.y
        return np.array([self.x / norm, self.y / norm])


    #
    @staticmethod
    def from_tuple(t: tuple[int, int]) -> 'ND_Point':
        #
        return ND_Point(t[0], t[1])


    #
    def to_tuple(self) -> tuple[int, int]:
        #
        return (self.x, self.y)

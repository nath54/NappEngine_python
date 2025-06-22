"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""


#
class ND_Val(int):
    #
    def __init__(self, value: int = 0, relative_from: int = -1) -> None:
        #
        self.value: int = value
        self.relative_from: int = -1

    #
    def get_value(self, relative_to: int = -1) -> int:
        #
        if relative_to == -1 or self.relative_from == -1:
            return self.value
        #
        return int(float(float(self.value) / float(self.relative_from)) * float(relative_to))

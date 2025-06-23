"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""

#
###
#
from typing import Any, Optional


#
def clamp(value: Any, mini: Any, maxi: Any) -> Any:
    if value < mini:
        return mini
    elif value > maxi:
        return maxi
    return value


#
def get_percentage_from_str(t: str) -> float:
    #
    t = t.strip()
    #
    if not t.endswith("%"):
        return 0
    #
    try:
        v: float = float(t[:-1])
        return v
    except Exception as _:
        return 0


#
def get_font_size(txt: str, font_size: int, font_ratio: float = 3.0 / 4.0) -> tuple[int, int]:
    return (len(txt) * int(float(font_size) * font_ratio), font_size)



#
def dict_sum(dict_a: Optional[dict[str, Any]], dict_b: Optional[dict[str, Any]]) -> dict[str, Any]:
    #
    res: dict[str, Any] = {}
    #
    if dict_a is not None:
        #
        for k, v in dict_a.items():
            #
            res[k] = v
    #
    if dict_b is not None:
        #
        for k, v in dict_b.items():
            #
            res[k] = v
    #
    return res


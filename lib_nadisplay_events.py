"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Bases abstract unified classes for events.

"""


#
class ND_Event:

    def __init__(self) -> None:
        #
        self.blocked: bool = False


#
class ND_EventQuit(ND_Event):

    def __init__(self) -> None:
        #
        super().__init__()


#
class ND_EventKeyboard(ND_Event):

    def __init__(self, keyboard_id: int = 0, key: str = "") -> None:
        #
        super().__init__()
        #
        self.keyboard_id: int = keyboard_id
        self.key: str = key


#
class ND_EventKeyDown(ND_EventKeyboard):

    def __init__(self, keyboard_id: int = 0, key: str = "") -> None:
        #
        super().__init__(keyboard_id=keyboard_id, key=key)


#
class ND_EventKeyUp(ND_EventKeyboard):

    def __init__(self, keyboard_id: int = 0, key: str = "") -> None:
        #
        super().__init__(keyboard_id=keyboard_id, key=key)


#
class ND_EventMouse(ND_Event):

    def __init__(self, mouse_id: int = 0, x: int = 0, y: int = 0) -> None:
        #
        super().__init__()
        #
        self.mouse_id: int = mouse_id
        self.x: int = x
        self.y: int = y


#
class ND_EventMouseButtonDown(ND_EventMouse):

    def __init__(self, mouse_id: int = 0, x: int = 0, y: int = 0, button_id: int = 0) -> None:
        #
        super().__init__(mouse_id=mouse_id, x=x, y=y)
        #
        self.button_id: int = button_id


#
class ND_EventMouseButtonUp(ND_EventMouse):

    def __init__(self, mouse_id: int = 0, x: int = 0, y: int = 0, button_id: int = 0) -> None:
        #
        super().__init__(mouse_id=mouse_id, x=x, y=y)
        #
        self.button_id: int = button_id


#
class ND_EventMouseMotion(ND_EventMouse):

    def __init__(self, mouse_id: int = 0, x: int = 0, y: int = 0, rel_x: int = 0, rel_y: int = 0) -> None:
        #
        super().__init__(mouse_id=mouse_id, x=x, y=y)
        #
        self.rel_x: int = rel_x
        self.rel_y: int = rel_y


#
class ND_EventMouseWheelScrolled(ND_EventMouse):

    def __init__(self, mouse_id: int = 0, x: int = 0, y: int = 0, scroll_x: int = 0, scroll_y: int = 0) -> None:
        #
        super().__init__(mouse_id=mouse_id, x=x, y=y)
        #
        self.scroll_x: int = scroll_x
        self.scroll_y: int = scroll_y


#
class ND_EventWindow(ND_Event):

    def __init__(self, window_id: int = 0) -> None:
        #
        super().__init__()
        #
        self.window_id: int = window_id


#
class ND_EventWindowMoved(ND_EventWindow):

    def __init__(self, window_id: int = 0, x: int = 0, y: int = 0) -> None:
        #
        super().__init__(window_id=window_id)
        #
        self.x: int = x
        self.y: int = y


#
class ND_EventWindowResized(ND_EventWindow):

    def __init__(self, window_id: int = 0, w: int = 0, h: int = 0) -> None:
        #
        super().__init__(window_id=window_id)
        #
        self.w: int = w
        self.h: int = h


#
class ND_EventWindowHidden(ND_EventWindow):

    def __init__(self, window_id: int = 0) -> None:
        #
        super().__init__(window_id=window_id)


#
class ND_EventWindowShown(ND_EventWindow):

    def __init__(self, window_id: int = 0) -> None:
        #
        super().__init__(window_id=window_id)


#
class ND_EventWindowFocusGained(ND_EventWindow):

    def __init__(self, window_id: int = 0) -> None:
        #
        super().__init__(window_id=window_id)


#
class ND_EventWindowFocusLost(ND_EventWindow):

    def __init__(self, window_id: int = 0) -> None:
        #
        super().__init__(window_id=window_id)


#
class ND_EventWindowClose(ND_EventWindow):

    def __init__(self, window_id: int = 0) -> None:
        #
        super().__init__(window_id=window_id)


#
class ND_EventEmpty(ND_Event):

    def __init__(self) -> None:
        #
        super().__init__()

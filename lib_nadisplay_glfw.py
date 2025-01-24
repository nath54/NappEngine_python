"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Some utilitary functions for GLFW backend for lib_nadisplay.

"""

import glfw  # type: ignore
from typing import Optional
from queue import Queue
from lib_nadisplay_rects import ND_Point
import lib_nadisplay_events as nd_event
from lib_nadisplay import ND_EventsManager, ND_MainApp, ND_Window, ND_Display



#
def get_display_info() -> Optional[glfw._GLFWvidmode]:
    # Initialize GLFW
    if not glfw.init():
        return None

    # Get the primary monitor
    monitor = glfw.get_primary_monitor()
    if not monitor:
        glfw.terminate()
        return None

    # Get video mode of the primary monitor
    video_mode = glfw.get_video_mode(monitor)
    if not video_mode:
        glfw.terminate()
        return None

    #
    return video_mode


#
class ND_Window_GLFW(ND_Window):
    #
    def __init__(
            self,
            display: ND_Display,
            window_id: int,
            init_state: Optional[str] = None,
            title: str = "App",
            fullscreen: bool = False
        ):

        #
        super().__init__(display=display, window_id=window_id, init_state=init_state)
        #
        self.glw_window: glfw._GLFWwindow = None


#
class ND_EventsManager_GLFW(ND_EventsManager):
    #
    def __init__(self, main_app: ND_MainApp) -> None:
        super().__init__(main_app)
        self.key_pressed: set[int | str] = set()
        self.events_waiting_to_poll: Queue[nd_event.ND_Event] = Queue()
        self.windows: list[ND_Window_GLFW] = []

    #
    def register_window_callback(self, nd_window: ND_Window_GLFW) -> None:
        if self.main_app.display is None or not self.main_app.display.initialized:
            return

        #
        self.windows.append(nd_window)

        # Register callbacks
        #
        glfw.set_key_callback(nd_window.glw_window,
            # window: glfw._GLFWwindow, key: int, scancode: int, action: int, mods: int
            lambda window, key, scancode, action, mods, nd_window=nd_window: self.key_callback(window, key, scancode, action, mods, nd_window)
        )
        #
        glfw.set_mouse_button_callback(nd_window.glw_window,
            # window: glfw._GLFWwindow, button: int, action: int, mods: int
            lambda window, button, action, mods, nd_window=nd_window: self.mouse_button_callback(window, button, action, mods, nd_window)
        )
        #
        glfw.set_cursor_pos_callback(nd_window.glw_window,
            # window: glfw._GLFWwindow, x: float, y: float
            lambda window, x, y, nd_window=nd_window: self.cursor_position_callback(window, x, y, nd_window)
        )
        #
        glfw.set_scroll_callback(nd_window.glw_window,
            # window: glfw._GLFWwindow, xoffset: float, yoffset: float
            lambda window, xoffset, yoffset, nd_window=nd_window: self.scroll_callback(window, xoffset, yoffset, nd_window)
        )
        #
        glfw.set_window_size_callback(nd_window.glw_window,
            # window: glfw._GLFWwindow, width: int, height: int
            lambda window, width, height, nd_window=nd_window: self.window_size_callback
        )
        #
        glfw.set_window_close_callback(nd_window.glw_window,
            # window: glfw._GLFWwindow
            lambda window, nd_window=nd_window: self.window_close_callback(window, nd_window)
        )
        #
        glfw.set_window_focus_callback(nd_window.glw_window,
            # window: glfw._GLFWwindow, focused: int
            lambda window, focused, nd_window=nd_window: self.window_focus_callback(window, focused, nd_window)
        )

    #
    def poll_next_event(self) -> Optional[nd_event.ND_Event]:
        #
        if self.main_app.display is None or not self.main_app.display.initialized:
            return None

        #
        try:
            ev: Optional[nd_event.ND_Event] = self.events_waiting_to_poll.get_nowait()
            #
            if ev is not None:
                print(f"DEBUG | event : {ev}")
            #
            return ev
        #
        except Exception as _:
            return None

    #
    def get_mouse_position(self) -> ND_Point:
        #
        if self.main_app.display is None or not self.main_app.display.initialized:
            return ND_Point(-1, -1)

        #
        if not self.windows:
            return ND_Point(-1, -1)

        #
        window: ND_Window_GLFW = self.windows[-1]
        #
        x, y = glfw.get_cursor_pos(window.glw_window)
        #
        return ND_Point(int(x), int(y))

    #
    def get_global_mouse_position(self) -> ND_Point:
        # GLFW does not provide global mouse position; stub implementation
        return self.get_mouse_position()

    # Event callback implementations
    def key_callback(self, window: glfw._GLFWwindow, key: int, scancode: int, action: int, mods: int, nd_window: ND_Window_GLFW) -> None:
        #
        if action == glfw.PRESS:
            self.events_waiting_to_poll.put(nd_event.ND_EventKeyDown(keyboard_id=key, key=chr(key)))
        elif action == glfw.RELEASE:
            self.events_waiting_to_poll.put(nd_event.ND_EventKeyUp(keyboard_id=key, key=chr(key)))

    #
    def mouse_button_callback(self, window: glfw._GLFWwindow, button: int, action: int, mods: int, nd_window: ND_Window_GLFW) -> None:
        #
        x, y = glfw.get_cursor_pos(window)
        if action == glfw.PRESS:
            self.events_waiting_to_poll.put(nd_event.ND_EventMouseButtonDown(mouse_id=0, x=int(x), y=int(y), button_id=button))
        elif action == glfw.RELEASE:
            self.events_waiting_to_poll.put(nd_event.ND_EventMouseButtonUp(mouse_id=0, x=int(x), y=int(y), button_id=button))

    #
    def cursor_position_callback(self, window: glfw._GLFWwindow, x: float, y: float, nd_window: ND_Window_GLFW) -> None:
        #
        self.events_waiting_to_poll.put(nd_event.ND_EventMouseMotion(mouse_id=0, x=int(x), y=int(y), rel_x=0, rel_y=0))

    #
    def scroll_callback(self, window: glfw._GLFWwindow, xoffset: float, yoffset: float, nd_window: ND_Window_GLFW) -> None:
        #
        self.events_waiting_to_poll.put(nd_event.ND_EventMouseWheelScrolled(mouse_id=0, x=0, y=0, scroll_x=int(xoffset), scroll_y=int(yoffset)))

    #
    def window_size_callback(self, window: glfw._GLFWwindow, width: int, height: int, nd_window: ND_Window_GLFW) -> None:
        #
        self.events_waiting_to_poll.put(nd_event.ND_EventWindowResized(window_id=nd_window.window_id, w=width, h=height))

    #
    def window_close_callback(self, window: glfw._GLFWwindow, nd_window: ND_Window_GLFW) -> None:
        #
        self.events_waiting_to_poll.put(nd_event.ND_EventWindowClose(window_id=nd_window.window_id))

    #
    def window_focus_callback(self, window: glfw._GLFWwindow, focused: int, nd_window: ND_Window_GLFW) -> None:
        #
        if focused:
            self.events_waiting_to_poll.put(nd_event.ND_EventWindowFocusGained(window_id=nd_window.window_id))
        else:
            self.events_waiting_to_poll.put(nd_event.ND_EventWindowFocusLost(window_id=nd_window.window_id))

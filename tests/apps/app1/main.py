import sys
sys.path.insert(0, "../../../")

from typing import Optional

import lib_nadisplay as nd

# from lib_nadisplay_sdl_sdlgfx import ND_Display_SDL_SDLGFX as DisplayClass, ND_Window_SDL_SDLGFX as WindowClass
from lib_nadisplay_sdl_opengl3 import ND_Display_SDL_OPENGL as DisplayClass, ND_Window_SDL_OPENGL as WindowClass  # Not working at all
# from lib_nadisplay_glfw_opengl3 import ND_Display_GLFW_OPENGL as DisplayClass, ND_Window_GLFW_OPENGL as WindowClass  # Not working at all
# from lib_nadisplay_glfw_vulkan import ND_Display_GLFW_VULKAN as DisplayClass, ND_Window_GLFW_VULKAN as WindowClass  # Not working at all
from lib_nadisplay_sdl import ND_EventsManager_SDL as EventsManagerClass
# from lib_nadisplay_glfw import ND_EventsManager_GLFW as EventsManagerClass  # Not working at all
# from lib_nadisplay_pygame import ND_Display_Pygame as DisplayClass, ND_Window_Pygame as WindowClass, ND_EventsManager_Pygame as EventsManagerClass  # Working a little

#
from scene_main_menu import create_main_menu_scene
from scene_tests_menu import create_tests_menu_scene

#
MAIN_WINDOW_ID: int = 0

#
if __name__ == "__main__":

    #
    app = nd.ND_MainApp(
                DisplayClass=DisplayClass,
                WindowClass=WindowClass,
                EventsManagerClass=EventsManagerClass,
                global_vars_to_save=[],
                path_to_global_vars_save_file=""
        )

    #
    if app.display is None:
        exit(1)

    #
    win_id: int = app.display.create_window({
        "title": "LibNadisplay App test 1",
        "size": (1080, 700),
        "window_id": MAIN_WINDOW_ID,
        "init_state": "main_menu"
    }, True)

    #
    win: Optional[nd.ND_Window] = app.display.get_window(win_id)

    #
    if win is None:
        exit(1)

    #
    create_main_menu_scene(win)
    create_tests_menu_scene(win)

    #
    app.run()

import sys
sys.path.insert(0, "../../../")

import lib_nadisplay as nd

from lib_nadisplay_sdl_sdlgfx import ND_Display_SDL_SDLGFX as DisplayClass, ND_Window_SDL_SDLGFX as WindowClass
# from lib_nadisplay_sdl_opengl import ND_Display_SDL_OPENGL as DisplayClass, ND_Window_SDL_OPENGL as WindowClass  # Not working at all
# from lib_nadisplay_glfw_opengl import ND_Display_GLFW_OPENGL as DisplayClass, ND_Window_GLFW_OPENGL as WindowClass  # Not working at all
# from lib_nadisplay_glfw_vulkan import ND_Display_GLFW_VULKAN as DisplayClass, ND_Window_GLFW_VULKAN as WindowClass  # Not working at all
from lib_nadisplay_sdl import ND_EventsManager_SDL as EventsManagerClass
# from lib_nadisplay_glfw import ND_EventsManager_GLFW as EventsManagerClass  # Not working at all
# from lib_nadisplay_pygame import ND_Display_Pygame as DisplayClass, ND_Window_Pygame as WindowClass, ND_EventsManager_Pygame as EventsManagerClass  # Working a little



if __name__ == "__main__":

    app = nd.ND_MainApp(
                DisplayClass=DisplayClass,
                WindowClass=WindowClass,
                EventsManagerClass=EventsManagerClass,
                global_vars_to_save=[],
                path_to_global_vars_save_file=""
        )

    app.run()
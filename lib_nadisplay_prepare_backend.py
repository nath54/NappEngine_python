"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""


#
def prepare_backend(backend: str = "sdl2_sdlgfx"):

    #
    if backend == "sdl2_sdlgfx":
        #
        from lib_nadisplay_backend_sdl2_sdlgfx import ND_Display_SDL2_SDLGFX as DisplayClass, ND_Window_SDL2_SDLGFX as WindowClass     # type: ignore
        from lib_nadisplay_backend_sdl2 import ND_EventsManager_SDL as EventsManagerClass     # type: ignore

    #
    elif backend == "sdl2_opengl":
        #
        from lib_nadisplay_backend_sdl2_opengl import ND_Display_SDL2_OPENGL as DisplayClass, ND_Window_SDL2_OPENGL as WindowClass     # type: ignore
        from lib_nadisplay_backend_sdl2 import ND_EventsManager_SDL as EventsManagerClass     # type: ignore

    #
    elif backend == "glfw_opengl":
        #
        from lib_nadisplay_backend_glfw_opengl import ND_Display_GLFW_OPENGL as DisplayClass, ND_Window_GLFW_OPENGL as WindowClass     # type: ignore
        from lib_nadisplay_backend_glfw import ND_EventsManager_GLFW as EventsManagerClass     # type: ignore

    #
    elif backend == "glfw_vulkan":
        #
        from lib_nadisplay_backend_glfw_vulkan import ND_Display_GLFW_VULKAN as DisplayClass, ND_Window_GLFW_VULKAN as WindowClass     # type: ignore
        from lib_nadisplay_backend_glfw import ND_EventsManager_GLFW as EventsManagerClass     # type: ignore

    #
    elif backend == "pygame":
        #
        from lib_nadisplay_backend_pygame import ND_Display_Pygame as DisplayClass, ND_Window_Pygame as WindowClass, ND_EventsManager_Pygame as EventsManagerClass     # type: ignore

    #
    else:
        #
        raise UserWarning(f"Unsupportend backend : `{backend}`.\n\nList of supported backends :\n\t- `sdl2_sdlgfx`\n\t- `sdl2_opengl`\n\t- `glfw_opengl`\n\t- `glfw_vulkan`\n\t- `pygame`\n")

    #
    return DisplayClass, WindowClass, EventsManagerClass


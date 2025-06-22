# type: ignore

"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

SDL + OPENGL backend for lib_nadisplay.

"""

# Import necessary modules for type hints and threading
from typing import Optional, Any, Callable, cast, Type
from threading import Lock

# Import operating system utilities
import os

# Import NumPy for numerical operations
import numpy as np  # type: ignore

# Import SDL3 libraries for graphics rendering and font handling
import sdl3  # type: ignore
# import sdl3.video  # type: ignore
# import sdl3.sdlttf as sdlttf  # type: ignore
# import sdl3.sdlimage as sdlimage  # type: ignore

# To optimize speed in production, OpenGL error checking and logging can be disabled
# import OpenGL
# OpenGL.ERROR_CHECKING = False
# OpenGL.ERROR_LOGGING = False

# Import OpenGL functionalities for rendering
import OpenGL.GL as gl  # type: ignore
from OpenGL.GL import shaders

# Optionally, GLUT can be used for window management and other utilities
# from OpenGL.GLUT import glutInit, glutCreateWindow, glutInitDisplayMode, GLUT_RGB, glutInitWindowSize

# Import ctypes for low-level operations
import ctypes
# Import FreeType for font loading and rendering
import freetype  # type: ignore
# Import GLM for mathematical operations (e.g., vectors, matrices)
import glm

# Import lib_nadisplay functions
from lib_nadisplay_colors import ND_Color
from lib_nadisplay_transformation import ND_Transformation
from lib_nadisplay_rects import ND_Rect, ND_Point
from lib_nadisplay_core import ND_MainApp, ND_Display, ND_Window, ND_Scene
from lib_nadisplay_SDL3 import to_sdl_color, get_display_info
from lib_nadisplay_backend_opengl import create_and_validate_gl_shader_program
from lib_font_renderer_opengl import FontRenderer

#
BASE_PATH: str = "../../../"

# Vertex shader source code for basic rendering
with open(f"{BASE_PATH}gl_shaders/basic_rendering_vertex.vert", "r", encoding="utf-8") as f:
    VERTEX_SHADER_SRC: str = f.read()

# Fragment shader source code for basic rendering
with open(f"{BASE_PATH}gl_shaders/basic_rendering_fragment.frag", "r", encoding="utf-8") as f:
    FRAGMENT_SHADER_SRC: str = f.read()

# Vertex shader for rendering with textures
with open(f"{BASE_PATH}gl_shaders/texture_rendering_vertex.vert", "r", encoding="utf-8") as f:
    VERTEX_SHADER_TEXTURES_SRC: str = f.read()

# Fragment shader for rendering with textures
with open(f"{BASE_PATH}gl_shaders/texture_rendering_fragment.frag", "r", encoding="utf-8") as f:
    FRAGMENT_SHADER_TEXTURES_SRC: str = f.read()


# Log information about the current OpenGL context
def log_opengl_context_info():
    vendor = gl.glGetString(gl.GL_VENDOR)  # Get GPU vendor
    renderer = gl.glGetString(gl.GL_RENDERER)  # Get GPU renderer
    version = gl.glGetString(gl.GL_VERSION)  # Get OpenGL version
    glsl_version = gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)  # Get GLSL version

    print(f"OpenGL Vendor: {vendor}")
    print(f"OpenGL Renderer: {renderer}")
    print(f"OpenGL Version: {version}")
    print(f"GLSL Version: {glsl_version}")

    error = gl.glGetError()  # Check for OpenGL errors
    if error != gl.GL_NO_ERROR:
        print(f"OpenGL Error: {error}")


# Log detailed attributes of the OpenGL context
def log_opengl_context_attributes():
    major_version = gl.glGetIntegerv(gl.GL_MAJOR_VERSION)  # OpenGL major version
    minor_version = gl.glGetIntegerv(gl.GL_MINOR_VERSION)  # OpenGL minor version
    context_flags = gl.glGetIntegerv(gl.GL_CONTEXT_FLAGS)  # Context flags
    context_profile_mask = gl.glGetIntegerv(gl.GL_CONTEXT_PROFILE_MASK)  # Profile mask

    print(f"OpenGL Major Version: {major_version}")
    print(f"OpenGL Minor Version: {minor_version}")
    print(f"OpenGL Context Flags: {context_flags}")
    print(f"OpenGL Context Profile Mask: {context_profile_mask}")

    error = gl.glGetError()  # Check for OpenGL errors
    if error != gl.GL_NO_ERROR:
        print(f"OpenGL Error: {error}")


#
class ND_Display_SDL3_OPENGL(ND_Display):
    #
    def __init__(self, main_app: ND_MainApp, WindowClass: Type[ND_Window]) -> None:
        #
        super().__init__(main_app=main_app, WindowClass=WindowClass)
        #
        self.main_not_threading: bool = True
        self.events_thread_in_main_thread: bool = True
        self.display_thread_in_main_thread: bool = True
        #
        self.ttf_fonts: dict[str, FontRenderer] = {}
        #

    #
    def get_time_msec(self) -> float:
        return sdl3.SDL_GetTicks()

    #
    def wait_time_msec(self, delay_in_msec: float) -> None:
        sdl3.SDL_Delay(int(delay_in_msec))

    #
    def init_display(self) -> None:

        # Initialize sdl3 and TTF
        sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO)
        # sdlttf.TTF_Init()

        # Request an OpenGL 3.3 context
        sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
        sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_MINOR_VERSION, 3)
        sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_PROFILE_MASK, sdl3.SDL_GL_CONTEXT_PROFILE_CORE)
        sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_DOUBLEBUFFER, 1)
        sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_DEPTH_SIZE, 24)

        # Load system fonts
        self.load_system_fonts()

        #
        self.initialized = True
        print("Display initialized successfully.")

    #
    def destroy_display(self) -> None:

        # Cleanup

        #
        w: Optional[ND_Window] = None
        #
        for w in self.windows.values():
            #
            if not w:
                continue
            #
            w.destroy_window()

        #
        # sdlttf.TTF_Quit()
        sdl3.SDL_Quit()

    #
    def get_font(self, font: str, font_size: int, window: "ND_Window_SDL3_OPENGL") -> Optional[FontRenderer]: # type: ignore
        #
        if not self.initialized:
            return None

        #
        if font not in self.ttf_fonts:

            #
            if font not in self.font_names:
                return None

            #
            font_path: str = self.font_names[font]
            #
            if not (font_path.endswith(".ttf") or font_path.endswith(".otf")) or not os.path.exists(font_path):
                return None
            #
            self.ttf_fonts[font] = FontRenderer(font_path, window)
        #
        return self.ttf_fonts[font]

    #
    def get_focused_window_id(self) -> int:
        #
        if not self.initialized:
            return -1

        # Get the focused window
        focused_window: Optional[object] = sdl3.SDL_GetKeyboardFocus()

        # Check if a window is focused
        if focused_window is not None:
            # Get the window ID
            window_id: int = sdl3.SDL_GetWindowID(focused_window)
            return window_id
        else:
            return -1  # Indicate that no window is focused

    #
    def create_window(self, window_params: dict[str, Any], error_if_win_id_not_available: bool = False) -> int:
        #
        win_id: int = -1
        if "window_id" in window_params:
            win_id = window_params["window_id"]
        #
        with self.thread_create_window:
            #
            if len(self.windows) == 0:
                self.main_app.start_events_thread()
            #
            if win_id == -1:
                win_id = len(self.windows)
                #
            elif win_id in self.windows and error_if_win_id_not_available:
                raise UserWarning(f"Window id {win_id} isn't available!")
            #
            while win_id in self.windows:
                win_id += 1
            #
            window_params["window_id"] = win_id
            #
            self.windows[win_id] = self.WindowClass(self, **window_params)

        #
        return win_id

    #
    def destroy_window(self, win_id: int) -> None:
        #
        with self.thread_create_window:
            #
            if win_id not in self.windows:
                return
            #
            if self.windows[win_id] is not None:
                #
                win: ND_Window = cast(ND_Window, self.windows[win_id])
                #
                win.destroy_window()
            #
            del(self.windows[win_id])


#
class ND_Window_SDL3_OPENGL(ND_Window):
    #
    def __init__(
            self,
            display: ND_Display,
            window_id: int,
            size: tuple[int, int] | str,
            title: str = "Pygame App",
            fullscreen: bool = False,
            init_state: Optional[str] = None
        ):

        #
        super().__init__(display=display, window_id=window_id, init_state=init_state)

        #
        if isinstance(size, str):
            #
            infos: Optional[sdl3.SDL_DisplayMode] = get_display_info()
            #
            if infos is not None:
                #
                screen_width: int = infos.w
                screen_height: int = infos.h
                #
                if size == "max":
                    self.width = screen_width
                    self.height = screen_height
                elif size == "max/1.5":
                    self.width = int(float(screen_width) / 1.5)
                    self.height = int(float(screen_height) / 1.5)
        #
        elif isinstance(size, tuple):
            self.width = size[0]
            self.height = size[1]

        #
        self.sdl_window: sdl3.SDL_Window = sdl3.SDL_CreateWindow(
                                    title.encode('utf-8'),
                                    self.width,
                                    self.height,
                                    sdl3.SDL_WINDOW_OPENGL
        )
        #
        if not self.sdl_window:
            raise UserWarning("Window creation failed:", sdl3.SDL_GetError())
        print("sdl3 window created successfully.")

        #
        x_c, y_c, w_c, h_c = ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0)
        sdl3.SDL_GetWindowPosition(self.sdl_window, ctypes.byref(x_c), ctypes.byref(y_c))
        sdl3.SDL_GetWindowSize(self.sdl_window, ctypes.byref(w_c), ctypes.byref(h_c))
        #
        self.x, self.y, self.width, self.height = x_c.value, y_c.value, w_c.value, h_c.value
        #
        self.rect = ND_Rect(self.x, self.y, self.width, self.height)

        #
        sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
        sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_MINOR_VERSION, 3)
        sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_PROFILE_MASK, sdl3.SDL_GL_CONTEXT_PROFILE_CORE)
        self.gl_context: Optional[sdl3.SDL_GL_Context] = sdl3.SDL_GL_CreateContext(self.sdl_window)
        #
        if not self.gl_context:
            raise UserWarning("OpenGL context creation failed:", sdl3.SDL_GetError())
        print("OpenGL context created successfully.")
        #
        # Make the context current
        if sdl3.SDL_GL_MakeCurrent(self.sdl_window, self.gl_context) != 0:
            raise UserWarning("Failed to make OpenGL context current:", sdl3.SDL_GetError())
        print("OpenGL context made current.")
        #
        sdl3.SDL_GL_SetSwapInterval(1)  # Enable vsync
        gl.glDisable(gl.GL_DEPTH_TEST)  # Disable depth test
        gl.glDisable(gl.GL_CULL_FACE)   #

        if self.gl_context is None:
            raise UserWarning(f"ERROR: GL context is invalid : {self.gl_context} !!!")

        # sdl_or_glfw_window_id is int and has been initialized to -1 in parent class
        self.sdl_or_glfw_window_id = sdl3.SDL_GetWindowID(self.sdl_window)

        #
        self.next_texture_id: int = 0
        self.textures_dimensions: dict[int, tuple[int, int]] = {}
        self.gl_textures: dict[int, int] = {}
        self.sdl_textures_surfaces: dict[int, object] = {}
        self.mutex_sdl_textures: Lock = Lock()
        #
        self.prepared_font_textures: dict[str, int] = {}
        #


        # Compile shaders and create a program
        self.shader_program: int = create_and_validate_gl_shader_program(
                                    VERTEX_SHADER_SRC, FRAGMENT_SHADER_SRC)
        if self.shader_program <= 0:
            raise UserWarning("Failed to create shader program.")
        print("Shader program created successfully.")

        # Compile shaders and create a program for textures
        self.shader_program_textures: int = create_and_validate_gl_shader_program(
                                            VERTEX_SHADER_TEXTURES_SRC, FRAGMENT_SHADER_TEXTURES_SRC)
        if self.shader_program_textures <= 0:
            raise UserWarning("Failed to create texture shader program.")
        print("Shader program created successfully.")


    #
    def _ensure_shaderProgram_base(self) -> None:
        #
        gl.glUseProgram(self.shader_program)

    #
    def _ensure_shaderProgram_textures(self) -> None:
        #
        gl.glUseProgram(self.shader_program_textures)

    #
    def _ensure_context(self) -> None:
        """Ensure the OpenGL context is current."""
        if not self.gl_context:
            print("No OpenGL context available.")
            raise RuntimeError("No valid OpenGL context.")
        if sdl3.SDL_GL_MakeCurrent(self.sdl_window, self.gl_context) != 0:
            print("Failed to make OpenGL context current:", sdl3.SDL_GetError())
            raise RuntimeError("Failed to make OpenGL context current.")
        if gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM) == 0:
            raise RuntimeError("No current OpenGL program bound.")
        print("\nOpenGL context is current.\n")
        #
        log_opengl_context_info()
        log_opengl_context_attributes()

    #
    def destroy_window(self) -> None:
        #
        for texture_id in self.gl_textures:
            #
            self.destroy_prepared_texture(texture_id)

        #
        sdl3.SDL_GL_DeleteContext(self.gl_context)
        sdl3.SDL_DestroyWindow(self.sdl_window)

    #
    def add_display_state(self, state: str, state_display_function: Callable, erase_if_state_already_exists: bool = False) -> None:
        #
        if (state not in self.display_states) or (state in self.display_states and erase_if_state_already_exists):
            self.display_states[state] = state_display_function

    #
    def remove_display_state(self, state: str) -> None:
        #
        if state in self.display_states:
            del self.display_states[state]

    #
    def set_title(self, new_title: str) -> None:
        #
        if not self.display.initialized:
            return

        #
        sdl3.SDL_SetWindowTitle(self.sdl_window, new_title.encode('utf-8'))

    #
    def set_position(self, new_x: int, new_y: int) -> None:
        #
        if not self.display.initialized:
            return

        #
        sdl3.SDL_SetWindowPosition(self.sdl_window, new_x, new_y)

    #
    def set_size(self, new_width: int, new_height: int) -> None:
        #
        if not self.display.initialized:
            return

        #
        sdl3.SDL_SetWindowSize(self.sdl_window, new_width, new_height)

    #
    def set_fullscreen(self, mode: int) -> None:
        """
        Set window fullscreen state:

        modes:
            - 0 = WINDOWED_MODE
            - 1 = BORDERLESS_FULLSCREEN
            - 2 = FULLSCREEN

        Args:
            mode (int): 0, 1, or 2 (see above)
        """

        #
        if not self.display.initialized:
            return

        if mode == 0:
            sdl3.SDL_SetWindowFullscreen(self.sdl_window, 0)
        elif mode == 1:
            sdl3.SDL_SetWindowFullscreen(self.sdl_window, sdl3.SDL_WINDOW_FULLSCREEN_DESKTOP)
        elif mode == 2:
            sdl3.SDL_SetWindowFullscreen(self.sdl_window, sdl3.SDL_WINDOW_FULLSCREEN)

    #
    def blit_texture(self, texture_id: int, dst_rect: ND_Rect) -> None:
        """
        Renders a texture using OpenGL shaders.
        """
        if texture_id not in self.gl_textures:
            print("Texture ID not found.")
            return

        #
        self._ensure_shaderProgram_textures()
        self._ensure_context()

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.gl_textures[texture_id])

        vertices = np.array([
            # Position       # Texture Coords
            dst_rect.x, dst_rect.y, 0.0, 1.0,  # Top-left corner
            dst_rect.x + dst_rect.w, dst_rect.y, 1.0, 1.0,  # Top-right corner
            dst_rect.x + dst_rect.w, dst_rect.y + dst_rect.h, 1.0, 0.0,  # Bottom-right corner
            dst_rect.x, dst_rect.y + dst_rect.h, 0.0, 0.0   # Bottom-left corner
        ], dtype=np.float32)

        vao = gl.glGenVertexArrays(1)
        vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        # Position attribute
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 4 * vertices.itemsize, None)
        gl.glEnableVertexAttribArray(0)

        # Texture coordinate attribute
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 4 * vertices.itemsize, ctypes.c_void_p(2 * vertices.itemsize))
        gl.glEnableVertexAttribArray(1)

        gl.glUseProgram(self.shader_program_textures)
        gl.glDrawArrays(gl.GL_TRIANGLE_FAN, 0, 4)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        gl.glDeleteBuffers(1, [vbo])
        gl.glDeleteVertexArrays(1, [vao])

    #
    def prepare_text_to_render(self, text: str, color: ND_Color, font_size: int, font_name: Optional[str] = None) -> int:

        return -1

        #
        if not self.display.initialized:
            return -1

        #
        self._ensure_shaderProgram_textures()

        #
        if font_name is None:
            font_name = self.display.default_font

        # Get font
        font: Optional[sdlttf.TTF_OpenFont] = self.display.get_font(font_name, font_size, self)  # type: ignore

        # Do nothing if not font got
        if font is None:
            return -1

        #
        color_sdl: sdl3.SDL_Color = to_sdl_color(color)

        # Create rendered text surface
        surface = sdlttf.TTF_RenderText_Blended(font, text.encode('utf-8'), color_sdl)

        # Convert the SDL surface into an OpenGL texture
        texture_id: int = self._create_opengl_texture_from_surface(surface)

        #
        return texture_id

    #
    def prepare_image_to_render(self, img_path: str) -> int:

        return -1

        #
        if not self.display.initialized:
            return -1

        #
        self._ensure_shaderProgram_textures()

        # Chargement de l'image
        image_surface = sdlimage.IMG_Load(img_path.encode('utf-8'))

        # Si l'image n'a pas bien été chargée, erreur est abandon
        if not image_surface:
            print(f"Failed to load image: {img_path}")
            return -1

        # Convert the SDL surface into an OpenGL texture
        texture_id: int = self._create_opengl_texture_from_surface(image_surface)

        #
        return texture_id

    #
    def render_prepared_texture(self, texture_id: int, x: int, y: int, width: int, height, transformations: ND_Transformation = ND_Transformation()) -> None:

        #
        if not self.display.initialized:
            return

        #
        if texture_id not in self.gl_textures:
            return

        #
        self._ensure_shaderProgram_textures()

        #
        self.blit_texture(texture_id, ND_Rect(x, y, width, height))

    #
    def get_prepared_texture_size(self, texture_id: int) -> ND_Point:
        #
        self._ensure_shaderProgram_textures()
        #
        if texture_id not in self.textures_dimensions:
            return ND_Point(0, 0)
        #
        return ND_Point(*self.textures_dimensions[texture_id])

    #
    def destroy_prepared_texture(self, texture_id: int) -> None:
        #
        self._ensure_shaderProgram_textures()
        #
        with self.mutex_sdl_textures:
            if texture_id in self.gl_textures:
                gl.glDeleteTextures(1, [self.gl_textures[texture_id]])
                sdl3.SDL_FreeSurface(self.sdl_textures_surfaces[texture_id])
                del self.sdl_textures_surfaces[texture_id]
                del self.gl_textures[texture_id]

    #
    def _create_opengl_texture_from_surface(self, surface: sdl3.SDL_Surface) -> int:
        """
        Converts an SDL_Surface to an OpenGL texture and returns the texture ID.
        """

        #
        if not self.display.initialized:
            return -1

        #
        self._ensure_shaderProgram_textures()

        # Ensure SDL_Surface is valid
        if not surface or not surface.contents:
            print("Invalid SDL_Surface provided.")
            return -1

        #
        self._ensure_context()

        width, height = surface.contents.w, surface.contents.h

        # Generate an OpenGL texture ID
        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)

        # Upload pixel data to OpenGL
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0,
            gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, ctypes.c_void_p(surface.contents.pixels)
        )

        # Set texture parameters
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

        # Unbind the texture and return the ID
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        return texture_id

    #
    def draw_text(self, txt: str, x: int, y: int, font_size: int, font_color: ND_Color, font_name: Optional[str] = None) -> None:
        #
        if not self.display.initialized:
            return

        #
        self._ensure_shaderProgram_textures()

        #
        if font_name is None:
            font_name = self.display.default_font

        #
        font_renderer: Optional[FontRenderer] = cast(Optional[FontRenderer], self.display.get_font(font_name, font_size, self))  # type: ignore

        #
        if font_renderer is None:
            return

        #
        self._ensure_context()

        # No texture cache, calcul it each time

        font_renderer.render_text(txt, x, y, font_size, font_color)

    #
    def draw_pixel(self, x: int, y: int, color: ND_Color) -> None:
        """
        Draw a single pixel on the screen at (x, y).
        """
        if not self.display.initialized:
            print("Display not initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        gl.glUseProgram(self.shader_program)
        gl.glPointSize(1)

        # Set color uniform
        gl.glUniform4f(gl.glGetUniformLocation(self.shader_program, "color"), *color.to_float_tuple())

        vertices = np.array([x, y], dtype=np.float32)

        vao = gl.glGenVertexArrays(1)
        vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 2 * vertices.itemsize, None)
        gl.glEnableVertexAttribArray(0)

        gl.glDrawArrays(gl.GL_POINTS, 0, 1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

        gl.glDeleteBuffers(1, [vbo])
        gl.glDeleteVertexArrays(1, [vao])

    #
    def draw_hline(self, x1: int, x2: int, y: int, color: ND_Color) -> None:
        """
        Draw a horizontal line between (x1, y) and (x2, y).
        """
        if not self.display.initialized:
            print("Display not initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        gl.glUseProgram(self.shader_program)

        # Set color uniform
        gl.glUniform4f(gl.glGetUniformLocation(self.shader_program, "color"), *color.to_float_tuple())

        vertices = np.array([
            x1, y,  # Start point
            x2, y   # End point
        ], dtype=np.float32)

        vao = gl.glGenVertexArrays(1)
        vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 2 * vertices.itemsize, None)
        gl.glEnableVertexAttribArray(0)

        gl.glDrawArrays(gl.GL_LINES, 0, 2)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

        gl.glDeleteBuffers(1, [vbo])
        gl.glDeleteVertexArrays(1, [vao])

    #
    def draw_vline(self, x: int, y1: int, y2: int, color: ND_Color) -> None:
        """
        Draw a vertical line between (x, y1) and (x, y2).
        """
        if not self.display.initialized:
            print("Display not initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        gl.glUseProgram(self.shader_program)

        # Set color uniform
        gl.glUniform4f(gl.glGetUniformLocation(self.shader_program, "color"), *color.to_float_tuple())

        vertices = np.array([
            x, y1,  # Start point
            x, y2   # End point
        ], dtype=np.float32)

        vao = gl.glGenVertexArrays(1)
        vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 2 * vertices.itemsize, None)
        gl.glEnableVertexAttribArray(0)

        gl.glDrawArrays(gl.GL_LINES, 0, 2)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

        gl.glDeleteBuffers(1, [vbo])
        gl.glDeleteVertexArrays(1, [vao])

    #
    def draw_line(self, x1: int, x2: int, y1: int, y2: int, color: ND_Color) -> None:
        """
        Draw a straight line between (x1, y1) and (x2, y2).
        """
        if not self.display.initialized:
            print("Display not initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        gl.glUseProgram(self.shader_program)

        # Set color uniform
        gl.glUniform4f(gl.glGetUniformLocation(self.shader_program, "color"), *color.to_float_tuple())

        vertices = np.array([
            x1, y1,  # Start point
            x2, y2   # End point
        ], dtype=np.float32)

        vao = gl.glGenVertexArrays(1)
        vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 2 * vertices.itemsize, None)
        gl.glEnableVertexAttribArray(0)

        gl.glDrawArrays(gl.GL_LINES, 0, 2)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

        gl.glDeleteBuffers(1, [vbo])
        gl.glDeleteVertexArrays(1, [vao])

    #
    def draw_thick_line(self, x1: int, x2: int, y1: int, y2: int, line_thickness: int, color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        # TODO

    #
    def draw_rounded_rect(self, x: int, y: int, width: int, height: int, radius: int, fill_color: ND_Color, border_color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        self.draw_filled_rect(x, y, width, height, fill_color)

        #
        # TODO

    #
    def draw_unfilled_rect(self, x: int, y: int, width: int, height: int, outline_color: ND_Color) -> None:
        #
        if not self.display.initialized:
            return

        #
        if self.shader_program <= 0:
            print(f"Error: shader program hasn't been initialized (={self.shader_program}).")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        gl.glUseProgram(self.shader_program)
        gl.glUniform4f(gl.glGetUniformLocation(self.shader_program, "color"), *outline_color.to_float_tuple())

        vertices = np.array([
            x, y,  # Bottom-left
            x + width, y,  # Bottom-right
            x + width, y + height,  # Top-right
            x, y + height,  # Top-left
            x, y  # Back to bottom-left
        ], dtype=np.float32)

        vao = gl.glGenVertexArrays(1)
        vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glEnableVertexAttribArray(0)

        gl.glDrawArrays(gl.GL_LINE_LOOP, 0, 5)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)
        gl.glDeleteBuffers(1, [vbo])
        gl.glDeleteVertexArrays(1, [vao])

    #
    def draw_filled_rect(self, x: int, y: int, width: int, height: int, fill_color: ND_Color) -> None:
        #
        if not self.display.initialized:
            return

        #
        if self.shader_program <= 0:
            print(f"Error: shader program hasn't been initialized (={self.shader_program}).")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()


        gl.glUseProgram(self.shader_program)
        gl.glUniform4f(gl.glGetUniformLocation(self.shader_program, "color"), *fill_color.to_float_tuple())

        vertices = np.array([
            x, y,  # Bottom-left
            x + width, y,  # Bottom-right
            x + width, y + height,  # Top-right
            x, y + height  # Top-left
        ], dtype=np.float32)

        vao = gl.glGenVertexArrays(1)
        vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glEnableVertexAttribArray(0)

        gl.glDrawArrays(gl.GL_QUADS, 0, 4)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)
        gl.glDeleteBuffers(1, [vbo])
        gl.glDeleteVertexArrays(1, [vao])

    #
    def draw_unfilled_circle(self, x: int, y: int, radius: int, outline_color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        # TODO

    #
    def draw_filled_circle(self, x: int, y: int, radius: int, fill_color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        # TODO

    #
    def draw_unfilled_ellipse(self, x: int, y: int, rx: int, ry: int, outline_color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        # TODO

    #
    def draw_filled_ellipse(self, x: int, y: int, rx: int, ry: int, fill_color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        # TODO

    #
    def draw_arc(self, x: int, y: int, radius: float, angle_start: float, angle_end: float, color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        # TODO

    #
    def draw_unfilled_pie(self, x: int, y: int, radius: float, angle_start: float, angle_end: float, outline_color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        # TODO

    #
    def draw_filled_pie(self, x: int, y: int, radius: float, angle_start: float, angle_end: float, fill_color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        # TODO

    #
    def draw_unfilled_triangle(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, outline_color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        # TODO

    #
    def draw_filled_triangle(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, filled_color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        # TODO

    #
    def draw_unfilled_polygon(self, x_coords: list[int], y_coords: list[int], outline_color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        if len(x_coords) != len(y_coords) or len(x_coords) < 3:
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        # TODO

    #
    def draw_filled_polygon(self, x_coords: list[int], y_coords: list[int], fill_color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        if len(x_coords) != len(y_coords) or len(x_coords) < 3:
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        # TODO

    #
    def draw_textured_polygon(self, x_coords: list[int], y_coords: list[int], texture_id: int, texture_dx: int = 0, texture_dy: int = 0) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program_textures <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        if texture_id not in self.gl_textures:
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        # TODO

    #
    def draw_bezier_curve(self, x_coords: list[int], y_coords: list[int], line_color: ND_Color, nb_interpolations: int = 3) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        if len(x_coords) != 4 or len(y_coords) != 4:
            raise ValueError("Bezier curve requires exactly 4 control points.")

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        # TODO

    #
    def apply_area_drawing_constraint(self, x: int, y: int, w: int, h: int) -> None:

        #
        # TODO
        pass

    #
    def enable_area_drawing_constraints(self, x: int, y: int, width: int, height: int) -> None:
        #
        self.push_to_clip_rect_stack(x, y, width, height)
        #
        if not self.display.initialized:
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()
        #
        self.apply_area_drawing_constraint(x, y, width, height)

    #
    def disable_area_drawing_constraints(self) -> None:
        #
        self.remove_top_of_clip_rect_stack()
        #
        if not self.display.initialized:
            return

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()
        #
        new_clip_rect: Optional[ND_Rect] = self.get_top_of_clip_rect_stack()
        #
        if new_clip_rect is None:
            #
            gl.glDisable(gl.GL_SCISSOR_TEST)
        else:
            #
            self.apply_area_drawing_constraint(new_clip_rect.x, new_clip_rect.y, new_clip_rect.w, new_clip_rect.h)

    #
    def update_display(self) -> None:

        #
        if not self.display.initialized:
            return

        #
        sdl3.SDL_GL_MakeCurrent(self.sdl_window, self.gl_context)
        gl.glViewport(0, 0, self.width, self.height)

        #
        if self.state is not None and self.state in self.display_states:
            #
            if self.display_states[self.state] is not None:
                #
                display_fn: Callable[[ND_Window], None] = cast(Callable[[ND_Window], None], self.display_states[self.state])
                display_fn(self)

        #
        scene: ND_Scene
        for scene in self.scenes.values():
            scene.render()

        #
        sdl3.SDL_GL_SwapWindow(self.sdl_window)


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

#
from math import pi, cos, sin

# Import NumPy for numerical operations
import numpy as np  # type: ignore

# Import SDL2 libraries for graphics rendering and font handling
import sdl2  # type: ignore
import sdl2.video  # type: ignore
import sdl2.sdlttf as sdlttf  # type: ignore
import sdl2.sdlimage as sdlimage  # type: ignore

# To optimize speed in production, OpenGL error checking and logging can be disabled
# import OpenGL
# OpenGL.ERROR_CHECKING = False
# OpenGL.ERROR_LOGGING = False

# Import OpenGL functionalities for rendering
import OpenGL.GL as gl  # type: ignore

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
from lib_nadisplay_colors import ND_Transformations
from lib_nadisplay_rects import ND_Rect, ND_Point
from lib_nadisplay import ND_MainApp, ND_Display, ND_Window, ND_Scene
from lib_nadisplay_sdl import to_sdl_color, get_display_info
from lib_nadisplay_opengl import create_and_validate_gl_shader_program, compile_shaders
from lib_nadisplay_math import calc_rad_agl_about_h_axis, calc_point_with_angle_and_distance_from_another_point, convert_deg_to_rad, earcut_triangulate_polygon

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


class FontRenderer:
    def __init__(self, font_path: str, window: "ND_Window_SDL_OPENGL") -> None:
        self.window: ND_Window_SDL_OPENGL = window  # Reference to the window object
        self.shader_program: int = 0  # OpenGL shader program
        self.shader_projection: int = 0  # OpenGL shader projection matrix
        self.projection = glm.ortho(0, self.window.width, self.window.height, 0, -100000, 100000)  # Default projection
        self.characters: dict = {}  # Dictionary to store font character data
        self.vao: int = 0  # Vertex Array Object ID
        self.vbo: int = 0  # Vertex Buffer Object ID

        # Ensure context is current on this thread
        self.window._ensure_context()

        self.init_shader()  # Initialize shaders
        self.load_font(font_path)  # Load font

    #
    def _get_rendering_buffer(self, xpos: float, ypos: float, w: float, h: float, zfix: float = 0.0) -> np.ndarray:
        """
        Generate the vertex data for rendering a textured quad.

        :param xpos: X position of the bottom-left corner of the quad.
        :param ypos: Y position of the bottom-left corner of the quad.
        :param w: Width of the quad.
        :param h: Height of the quad.
        :param zfix: Z position fix (usually 0.0).
        :return: A NumPy array representing the vertices of the quad.
        """
        return np.asarray([
            xpos,     ypos - h, 0, 0,  # Bottom-left vertex
            xpos,     ypos,     0, 1,  # Top-left vertex
            xpos + w, ypos,     1, 1,  # Top-right vertex
            xpos,     ypos - h, 0, 0,  # Bottom-left vertex again
            xpos + w, ypos,     1, 1,  # Top-right vertex
            xpos + w, ypos - h, 1, 0   # Bottom-right vertex
        ], np.float32)

    def init_shader(self) -> None:

        # Ensure OpenGL context is active before any OpenGL calls
        self.window._ensure_context()

        # Vertex shader source code for font rendering
        with open(f"{BASE_PATH}gl_shaders/font_rendering_vertex.vert", "r", encoding="utf-8") as f:
            vertex_shader_source: str = f.read()

        # Fragment shader source code for font rendering
        with open(f"{BASE_PATH}gl_shaders/font_rendering_fragment.frag", "r", encoding="utf-8") as f:
            fragment_shader_source: str = f.read()

        # Create the shader program
        self.shader_program = compile_shaders(vertex_shader_source, fragment_shader_source)
        gl.glUseProgram(self.shader_program)

        # Set up the projection matrix
        self.shader_projection = gl.glGetUniformLocation(self.shader_program, "projection")
        gl.glUniformMatrix4fv(self.shader_projection, 1, gl.GL_FALSE, glm.value_ptr(self.projection))

        # Disable byte-alignment restriction for texture
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)

    def load_font(self, font_path: str) -> None:
        # Use program
        gl.glUseProgram(self.shader_program)

        # Ensure OpenGL context is active
        self.window._ensure_context()
        self.window.verify_context()

        # Disable byte-alignment restriction for texture
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)

        # Enable blending for transparency
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # Load font using FreeType
        face = freetype.Face(font_path)  # Load font face
        face.set_char_size(48 * 64)  # Set character size

        # Load ASCII characters (0-127)
        for c in range(128):
            # Load character glyph
            face.load_char(chr(c))
            glyph = face.glyph

            # Create texture for the glyph bitmap
            texture_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D, 0, gl.GL_RED,
                glyph.bitmap.width, glyph.bitmap.rows,
                0, gl.GL_RED, gl.GL_UNSIGNED_BYTE, glyph.bitmap.buffer
            )

            # Set texture parameters
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

            # Store character data
            self.characters[chr(c)] = {
                'texture_id': texture_id,
                'size': (glyph.bitmap.width, glyph.bitmap.rows),
                'bearing': (glyph.bitmap_left, glyph.bitmap_top),
                'advance': glyph.advance.x
            }

        # Unbind texture
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        # Create VAO and VBO for rendering
        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, 6 * 4 * 4, None, gl.GL_DYNAMIC_DRAW)
        gl.glEnableVertexAttribArray(0)

        print("Calling glVertexAttribPointer")
        gl.glVertexAttribPointer(0, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

    def render_text(self, text: str, x: int, y: int, scale: float, color: ND_Color) -> None:

        # Ensure OpenGL context is active
        self.window._ensure_context()

        # Use program
        gl.glUseProgram(self.shader_program)

        #
        scale /= 50

        # Set text color
        gl.glUniform3f(
            gl.glGetUniformLocation(self.shader_program, "textColor"),
            color.r / 255, color.g / 255, color.b / 255
        )
        gl.glActiveTexture(gl.GL_TEXTURE0)

        # Disable depth to render the text correctly
        gl.glDisable(gl.GL_DEPTH_TEST)

        # Enable blending for transparency
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # Iterate over characters in the text
        for char in text:
            # Only ASCII characters are supported
            if char not in self.characters:
                continue

            # Get the character font glyph
            ch = self.characters[char]

            # Calculate position and size for the character
            xpos = x + ch['bearing'][0] * scale
            ypos = y + 40 * scale + (ch['size'][1] - ch['bearing'][1]) * scale
            w = ch['size'][0] * scale
            h = ch['size'][1] * scale

            # Convert screen coordinates to NDC
            xpos_ndc, ypos_ndc = self.window.screen_to_ndc(xpos, ypos)
            w_ndc, h_ndc = self.window.screen_to_ndc(w, h)

            # Bind the VAO
            gl.glBindVertexArray(self.vao)

            # Define vertex data for the character
            vertices = self._get_rendering_buffer(xpos, ypos, w, h)

            # Render the glyph texture over a quad
            gl.glBindTexture(gl.GL_TEXTURE_2D, ch['texture_id'])

            # Update the VBO with new vertex data
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, 6 * 4 * 4, None, gl.GL_DYNAMIC_DRAW)

            gl.glEnableVertexAttribArray(0)
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

            # Render the character as triangles
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)

            # Advance the cursor to the next position (in pixels)
            x += (ch['advance'] >> 6) * scale  # Advance is in 1/64th pixels

        # Unbind VAO and texture
        gl.glBindVertexArray(0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)


#
class ND_Display_SDL_OPENGL(ND_Display):
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
        return sdl2.SDL_GetTicks()

    #
    def wait_time_msec(self, delay_in_msec: float) -> None:
        sdl2.SDL_Delay(int(delay_in_msec))

    #
    def init_display(self) -> None:

        # Initialize SDL2 and TTF
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        sdlttf.TTF_Init()

        # Request an OpenGL 3.3 context
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 3)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_PROFILE_MASK, sdl2.SDL_GL_CONTEXT_PROFILE_CORE)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_DOUBLEBUFFER, 1)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_DEPTH_SIZE, 24)

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
        sdlttf.TTF_Quit()
        sdl2.SDL_Quit()

    #
    def get_font(self, font: str, font_size: int, window: "ND_Window_SDL_OPENGL") -> Optional[FontRenderer]: # type: ignore
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
        focused_window: Optional[object] = sdl2.SDL_GetKeyboardFocus()

        # Check if a window is focused
        if focused_window is not None:
            # Get the window ID
            window_id: int = sdl2.SDL_GetWindowID(focused_window)
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
class ND_Window_SDL_OPENGL(ND_Window):
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
            infos: Optional[sdl2.SDL_DisplayMode] = get_display_info()
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
        self.sdl_window: sdl2.SDL_Window = sdl2.SDL_CreateWindow(
                                    title.encode('utf-8'),
                                    sdl2.SDL_WINDOWPOS_CENTERED,
                                    sdl2.SDL_WINDOWPOS_CENTERED,
                                    self.width,
                                    self.height,
                                    sdl2.SDL_WINDOW_OPENGL
        )
        #
        if not self.sdl_window:
            raise UserWarning("Window creation failed:", sdl2.SDL_GetError())
        print("SDL2 window created successfully.")

        #
        x_c, y_c, w_c, h_c = ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0)
        sdl2.SDL_GetWindowPosition(self.sdl_window, ctypes.byref(x_c), ctypes.byref(y_c))
        sdl2.SDL_GetWindowSize(self.sdl_window, ctypes.byref(w_c), ctypes.byref(h_c))
        #
        self.x, self.y, self.width, self.height = x_c.value, y_c.value, w_c.value, h_c.value
        #
        self.rect = ND_Rect(self.x, self.y, self.width, self.height)

        #
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 3)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_PROFILE_MASK, sdl2.SDL_GL_CONTEXT_PROFILE_CORE)
        self.gl_context: Optional[sdl2.SDL_GL_Context] = sdl2.SDL_GL_CreateContext(self.sdl_window)
        #
        if not self.gl_context:
            raise UserWarning("OpenGL context creation failed:", sdl2.SDL_GetError())
        print("OpenGL context created successfully.")
        #
        # Make the context current
        if sdl2.SDL_GL_MakeCurrent(self.sdl_window, self.gl_context) != 0:
            raise UserWarning("Failed to make OpenGL context current:", sdl2.SDL_GetError())
        print("OpenGL context made current.")
        #
        sdl2.SDL_GL_SetSwapInterval(1)  # Enable vsync
        gl.glDisable(gl.GL_DEPTH_TEST)  # Disable depth test
        gl.glDisable(gl.GL_CULL_FACE)   #

        if self.gl_context is None:
            raise UserWarning(f"ERROR: GL context is invalid : {self.gl_context} !!!")

        # sdl_or_glfw_window_id is int and has been initialized to -1 in parent class
        self.sdl_or_glfw_window_id = sdl2.SDL_GetWindowID(self.sdl_window)

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
        log_opengl_context_info()
        log_opengl_context_attributes()


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
        if sdl2.SDL_GL_MakeCurrent(self.sdl_window, self.gl_context) != 0:
            print("Failed to make OpenGL context current:", sdl2.SDL_GetError())
            raise RuntimeError("Failed to make OpenGL context current.")
        if gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM) == 0:
            raise RuntimeError("No current OpenGL program bound.")
        #
        print("\nOpenGL context is current.\n\nCURRENT CONTEXT INFORMATIONS :\n\n")
        #
        log_opengl_context_info()
        log_opengl_context_attributes()

    def verify_context(self):
        #
        current_context = sdl2.SDL_GL_GetCurrentContext()
        if not current_context:
            raise RuntimeError("No current OpenGL context detected.")
        elif current_context != self.gl_context:
            print("Warning: Current context differs from window's context.")
        else:
            print("Context verified successfully.")

    #
    def destroy_window(self) -> None:
        #
        for texture_id in self.gl_textures:
            #
            self.destroy_prepared_texture(texture_id)

        #
        sdl2.SDL_GL_DeleteContext(self.gl_context)
        sdl2.SDL_DestroyWindow(self.sdl_window)

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
        sdl2.SDL_SetWindowTitle(self.sdl_window, new_title.encode('utf-8'))

    #
    def set_position(self, new_x: int, new_y: int) -> None:
        #
        if not self.display.initialized:
            return

        #
        sdl2.SDL_SetWindowPosition(self.sdl_window, new_x, new_y)

    #
    def set_size(self, new_width: int, new_height: int) -> None:
        #
        log_opengl_context_attributes()
        if not self.display.initialized:
            return

        #
        sdl2.SDL_SetWindowSize(self.sdl_window, new_width, new_height)

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
            sdl2.SDL_SetWindowFullscreen(self.sdl_window, 0)
        elif mode == 1:
            sdl2.SDL_SetWindowFullscreen(self.sdl_window, sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
        elif mode == 2:
            sdl2.SDL_SetWindowFullscreen(self.sdl_window, sdl2.SDL_WINDOW_FULLSCREEN)


    #
    def screen_to_ndc(self, x_screen: int, y_screen: int, viewport_origin: tuple[int, int]=(0, 0), invert_y: bool=True) -> tuple[float, float]:
        """
        Converts screen space coordinates (x_screen, y_screen) to OpenGL NDC coordinates.

        Parameters:
            x_screen (float): X coordinate in screen space.
            y_screen (float): Y coordinate in screen space.
            viewport_origin (tuple): The bottom-left corner of the viewport (default is (0, 0)).
            invert_y (bool): If True, assumes screen space has a top-left origin and inverts the Y axis.

            self.width (int): Width of the viewport in pixels.
            self.height (int): Height of the viewport in pixels.

        Returns:
            tuple: (x_ndc, y_ndc) coordinates in NDC space.
        """
        x_vp: int = viewport_origin[0]
        y_vp: int = viewport_origin[1]

        # Adjust for the viewport origin
        x_screen_adj: int = x_screen - x_vp
        y_screen_adj: int = y_screen - y_vp

        # Handle inverted Y-axis
        if invert_y:
            y_screen_adj = self.height - y_screen_adj

        # Convert to NDC
        x_ndc: float = 2 * (x_screen_adj / self.width) - 1
        y_ndc: float = 2 * (y_screen_adj / self.height) - 1

        return x_ndc, y_ndc

    #
    def ndc_to_screen(self, x_ndc: float, y_ndc: float, viewport_origin: tuple[int, int]=(0, 0), invert_y: bool=True) -> tuple[int, int]:
        """
        Converts OpenGL NDC coordinates (x_ndc, y_ndc) to screen space coordinates.

        Parameters:
            x_ndc (float): X coordinate in NDC space.
            y_ndc (float): Y coordinate in NDC space.
            viewport_origin (tuple): The bottom-left corner of the viewport (default is (0, 0)).
            invert_y (bool): If True, assumes screen space has a top-left origin and inverts the Y axis.

            self.width (int): Width of the viewport in pixels.
            self.height (int): Height of the viewport in pixels.

        Returns:
            tuple: (x_screen, y_screen) coordinates in screen space.
        """
        x_vp: int = viewport_origin[0]
        y_vp: int = viewport_origin[1]

        # Convert from NDC to screen coordinates
        x_screen: int = int( ((x_ndc + 1) / 2) * self.width + x_vp )
        y_screen: int = int( ((y_ndc + 1) / 2) * self.height + y_vp )

        # Handle inverted Y-axis
        if invert_y:
            y_screen = self.height - (y_screen - y_vp)

        return x_screen, y_screen

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
        color_sdl: sdl2.SDL_Color = to_sdl_color(color)

        # Create rendered text surface
        surface = sdlttf.TTF_RenderText_Blended(font, text.encode('utf-8'), color_sdl)

        # Convert the SDL surface into an OpenGL texture
        texture_id: int = self._create_opengl_texture_from_surface(surface)

        #
        return texture_id

    #
    def prepare_image_to_render(self, img_path: str) -> int:

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
    def render_prepared_texture(self, texture_id: int, x: int, y: int, width: int, height, transformations: ND_Transformations = ND_Transformations()) -> None:

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
                sdl2.SDL_FreeSurface(self.sdl_textures_surfaces[texture_id])
                del self.sdl_textures_surfaces[texture_id]
                del self.gl_textures[texture_id]

    #
    def _create_opengl_texture_from_surface(self, surface: sdl2.SDL_Surface) -> int:
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
    def _render_lines(self, points: list[ ND_Point ], color: ND_Color) -> None:
        #
        if not self.display.initialized:
            return
        #
        N: int = len(points)
        #
        gl.glUniform4f(gl.glGetUniformLocation(self.shader_program, "color"), *color.to_float_tuple())
        #
        vertices_pts: list[tuple[float, float]]=[(0, 0)] * N
        #
        x: float
        y: float
        for i in range(N):
            #
            x, y = self.screen_to_ndc(points[i].x, points[i].y)
            #
            vertices_pts[i] = (x, y)
        #
        vertices = np.array(vertices_pts, dtype=np.float32)

        #
        vao = gl.glGenVertexArrays(1)
        vbo = gl.glGenBuffers(1)

        #
        gl.glBindVertexArray(vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glEnableVertexAttribArray(0)

        #
        gl.glDrawArrays(gl.GL_LINE_STRIP, 0, N)

        #
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)
        gl.glDeleteBuffers(1, [vbo])
        gl.glDeleteVertexArrays(1, [vao])

    #
    def _render_uniform_colored_triangles(self, triangles: list[ tuple[ ND_Point, ND_Point, ND_Point ] ], color: ND_Color) -> None:
        #
        if not self.display.initialized:
            return
        #
        N: int = len(triangles)

        #
        self._ensure_shaderProgram_base()
        self._ensure_context()

        #
        gl.glUseProgram(self.shader_program)
        gl.glUniform4f(gl.glGetUniformLocation(self.shader_program, "color"), *color.to_float_tuple())

        #
        vertices_pts: list[tuple[float, float]] = [(0, 0)] * (3 * N)
        #
        x: float
        y: float
        for i in range(N):
            #
            x, y = self.screen_to_ndc(triangles[i][0].x, triangles[i][0].y)
            #
            vertices_pts[3*i] = (x, y)
            #
            x, y = self.screen_to_ndc(triangles[i][1].x, triangles[i][1].y)
            #
            vertices_pts[3*i + 1] = (x, y)
            #
            x, y = self.screen_to_ndc(triangles[i][2].x, triangles[i][2].y)
            #
            vertices_pts[3*i + 2] = (x, y)

        # Define vertices for two triangles forming the rectangle
        vertices = np.array(vertices_pts, dtype=np.float32)

        #
        vao = gl.glGenVertexArrays(1)
        vbo = gl.glGenBuffers(1)

        #
        gl.glBindVertexArray(vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glEnableVertexAttribArray(0)

        #
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3 * N)

        #
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)
        gl.glDeleteBuffers(1, [vbo])
        gl.glDeleteVertexArrays(1, [vao])


    #
    def _render_point(self, point: ND_Point, color: ND_Color) -> None:
        #
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

        vertices = np.array([*self.screen_to_ndc(point.x, point.y)], dtype=np.float32)

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
        #
        self._render_point(point=ND_Point(x, y), color=color)

    #
    def draw_hline(self, x1: int, x2: int, y: int, color: ND_Color) -> None:
        """
        Draw a horizontal line between (x1, y) and (x2, y).
        """
        #
        self._render_lines(points=[ND_Point(x1, y), ND_Point(x2, y)], color=color)

    #
    def draw_vline(self, x: int, y1: int, y2: int, color: ND_Color) -> None:
        """
        Draw a vertical line between (x, y1) and (x, y2).
        """
        #
        self._render_lines(points=[ND_Point(x, y1), ND_Point(x, y2)], color=color)

    #
    def draw_line(self, x1: int, x2: int, y1: int, y2: int, color: ND_Color) -> None:
        """
        Draw a straight line between (x1, y1) and (x2, y2).
        """
        #
        self._render_lines(points=[ND_Point(x1, y1), ND_Point(x2, y2)], color=color)

    #
    def draw_thick_line(self, x1: int, x2: int, y1: int, y2: int, line_thickness: float, color: ND_Color) -> None:
        #
        alpha: float = calc_rad_agl_about_h_axis( x1, y1, x2, y2 )

        #
        agl_above: float = ( alpha - (pi / 2) ) % (2 * pi)
        agl_below: float = ( alpha + (pi / 2) ) % (2 * pi)

        #
        ax: int
        ay: int
        ax, ay = calc_point_with_angle_and_distance_from_another_point(x1, y1, agl_above, line_thickness)

        #
        bx: int
        by: int
        bx, by = calc_point_with_angle_and_distance_from_another_point(x1, y1, agl_below, line_thickness)

        #
        cx: int
        cy: int
        cx, cy = calc_point_with_angle_and_distance_from_another_point(x2, y2, agl_above, line_thickness)

        #
        dx: int
        dy: int
        dx, dy = calc_point_with_angle_and_distance_from_another_point(x2, y2, agl_below, line_thickness)

        #
        self._render_uniform_colored_triangles(
            triangles=[
                ( ND_Point(ax, ay), ND_Point(bx, by), ND_Point(cx, cy) ),
                ( ND_Point(ax, ay), ND_Point(dx, dy), ND_Point(cx, cy) )
            ],
            color=color
        )

    #
    def draw_rounded_rect(self, x: int, y: int, width: int, height: int, radius: int, fill_color: ND_Color, border_color: ND_Color, corner_nb_points: int = 6) -> None:
        #
        self.draw_filled_rect(x=x + radius, y=y, width=width - 2 * radius, height=height, fill_color=fill_color)
        self.draw_filled_rect(x=x, y=y + radius, width=radius, height=height - 2 * radius, fill_color=fill_color)
        self.draw_filled_rect(x=x + width - radius, y=y + radius, width=radius, height=height - 2 * radius, fill_color=fill_color)
        #
        self.draw_filled_pie(x=x + radius, y=y + radius, radius=radius, angle_start=180, angle_end=270, fill_color=fill_color, pie_nb_points=corner_nb_points)
        self.draw_filled_pie(x=x + width - radius, y=y + radius, radius=radius, angle_start=270, angle_end=360, fill_color=fill_color, pie_nb_points=corner_nb_points)
        self.draw_filled_pie(x=x + width - radius, y=y + height - radius, radius=radius, angle_start=0, angle_end=90, fill_color=fill_color, pie_nb_points=corner_nb_points)
        self.draw_filled_pie(x=x + radius, y=y + height - radius, radius=radius, angle_start=90, angle_end=180, fill_color=fill_color, pie_nb_points=corner_nb_points)
        #
        self.draw_hline(x1=x + radius, x2=x + width - radius, y=y, color=border_color)
        self.draw_hline(x1=x + radius, x2=x + width - radius, y=y+height, color=border_color)
        self.draw_vline(x=x, y1=y + radius, y2=y + height - radius, color=border_color)
        self.draw_vline(x=x + width, y1=y + radius, y2=y + height - radius, color=border_color)
        #
        self.draw_arc(x=x + radius, y=y + radius, radius=radius, angle_start=180, angle_end=270, color=border_color, arc_nb_points=corner_nb_points)
        self.draw_arc(x=x + width - radius, y=y + radius, radius=radius, angle_start=270, angle_end=360, color=border_color, arc_nb_points=corner_nb_points)
        self.draw_arc(x=x + width - radius, y=y + height - radius, radius=radius, angle_start=0, angle_end=90, color=border_color, arc_nb_points=corner_nb_points)
        self.draw_arc(x=x + radius, y=y + height - radius, radius=radius, angle_start=90, angle_end=180, color=border_color, arc_nb_points=corner_nb_points)

    #
    def draw_unfilled_rect(self, x: int, y: int, width: int, height: int, outline_color: ND_Color) -> None:
        #
        self._render_lines(
            points=[
                ND_Point(x, y),
                ND_Point(x + width, y),
                ND_Point(x + width, y + height),
                ND_Point(x, y + height),
                ND_Point(x, y)
            ],
            color=outline_color
        )

    #
    def draw_filled_rect(self, x: int, y: int, width: int, height: int, fill_color: ND_Color) -> None:
        #
        self._render_uniform_colored_triangles(triangles=[
            ( ND_Point(x, y), ND_Point(x + width, y), ND_Point(x + width, y + height) ),
            ( ND_Point(x, y), ND_Point(x + width, y + height), ND_Point(x, y + height) )
            ],
            color=fill_color
        )

    #
    def draw_unfilled_circle(self, x: int, y: int, radius: int, outline_color: ND_Color, circle_nb_points: int = 36) -> None:
        #
        da: float = (2 * pi) / circle_nb_points
        #
        self._render_lines(
            points=[
                ND_Point(*calc_point_with_angle_and_distance_from_another_point(x, y, i * da, radius))
                for i in range(circle_nb_points + 1)
            ],
            color=outline_color
        )

    #
    def draw_filled_circle(self, x: int, y: int, radius: int, fill_color: ND_Color, circle_nb_points: int = 36) -> None:
        #
        da: float = (2 * pi) / circle_nb_points
        #
        center: ND_Point = ND_Point(x, y)
        #
        points: list[ND_Point] = [
            ND_Point(*calc_point_with_angle_and_distance_from_another_point(x, y, i * da, radius))
            for i in range(circle_nb_points)
        ]
        #
        self._render_uniform_colored_triangles(
            triangles=[
                ( center, points[i], points[(i+1)%circle_nb_points] )
                for i in range(circle_nb_points)
            ],
            color=fill_color
        )

    #
    def draw_unfilled_ellipse(self, x: int, y: int, rx: int, ry: int, outline_color: ND_Color, ellipse_nb_points: int = 72) -> None:
        """
        Draw an unfilled ellipse centered at (x, y) with radii (rx, ry).
        """
        da: float = (2 * pi) / ellipse_nb_points
        points: list[ND_Point] = [
            ND_Point(x + int(rx * cos(i * da)), y + int(ry * sin(i * da)))
            for i in range(ellipse_nb_points + 1)
        ]
        self._render_lines(points=points, color=outline_color)

    #
    def draw_filled_ellipse(self, x: int, y: int, rx: int, ry: int, fill_color: ND_Color, ellipse_nb_points: int = 72) -> None:
        """
        Draw a filled ellipse centered at (x, y) with radii (rx, ry).
        """
        da: float = (2 * pi) / ellipse_nb_points
        center: ND_Point = ND_Point(x, y)
        points: list[ND_Point] = [
            ND_Point(x + int(rx * cos(i * da)), y + int(ry * sin(i * da)))
            for i in range(ellipse_nb_points)
        ]
        triangles: list[tuple[ND_Point, ND_Point, ND_Point]] = [
            (center, points[i], points[(i + 1) % ellipse_nb_points])
            for i in range(ellipse_nb_points)
        ]
        self._render_uniform_colored_triangles(triangles=triangles, color=fill_color)

    #
    def draw_arc(self, x: int, y: int, radius: float, angle_start: float, angle_end: float, color: ND_Color, arc_nb_points: int = 36) -> None:
        #
        agl_start: float = convert_deg_to_rad(angle_start)
        agl_end: float = convert_deg_to_rad(angle_end)
        #
        da: float = (agl_end - agl_start) / (arc_nb_points - 1)
        #
        points: list[ND_Point] = [
            ND_Point(*calc_point_with_angle_and_distance_from_another_point(x, y, agl_start + i * da, radius))
            for i in range(arc_nb_points)
        ]
        #
        self._render_lines(points=points, color=color)

    #
    def draw_unfilled_pie(self, x: int, y: int, radius: float, angle_start: float, angle_end: float, outline_color: ND_Color, pie_nb_points: int = 36) -> None:
        #
        agl_start: float = convert_deg_to_rad(angle_start)
        agl_end: float = convert_deg_to_rad(angle_end)
        #
        da: float = (agl_end - agl_start) / (pie_nb_points - 1)
        #
        center: ND_Point = ND_Point(x, y)
        #
        points: list[ND_Point] = [center] + [
            ND_Point(*calc_point_with_angle_and_distance_from_another_point(x, y, agl_start + i * da, radius))
            for i in range(pie_nb_points)
        ] + [center]
        #
        self._render_lines(points=points, color=outline_color)

    #
    def draw_filled_pie(self, x: int, y: int, radius: float, angle_start: float, angle_end: float, fill_color: ND_Color, pie_nb_points: int = 36) -> None:
        #
        agl_start: float = convert_deg_to_rad(angle_start)
        agl_end: float = convert_deg_to_rad(angle_end)
        #
        da: float = (agl_end - agl_start) / (pie_nb_points - 1)
        #
        center: ND_Point = ND_Point(x, y)
        #
        points: list[ND_Point] = [
            ND_Point(*calc_point_with_angle_and_distance_from_another_point(x, y, agl_start + i * da, radius))
            for i in range(pie_nb_points)
        ]
        #
        triangles: list[tuple[ND_Point, ND_Point, ND_Point]]=[
            ( center, points[i], points[(i+1)%pie_nb_points] )
            for i in range(pie_nb_points)
        ]
        #
        self._render_uniform_colored_triangles(triangles=triangles, color=fill_color)

    #
    def draw_unfilled_triangle(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, outline_color: ND_Color) -> None:
        #
        self._render_lines(
            points=[
                ND_Point(x1, y1),
                ND_Point(x2, y2),
                ND_Point(x3, y3)
            ],
            color=outline_color
        )

    #
    def draw_filled_triangle(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, filled_color: ND_Color) -> None:
        #
        self._render_uniform_colored_triangles(
            triangles=[( ND_Point(x1, y1), ND_Point(x2, y2), ND_Point(x3, y3) )],
            color=filled_color
        )

    #
    def draw_unfilled_polygon(self, x_coords: list[int], y_coords: list[int], outline_color: ND_Color) -> None:
        #
        if len(x_coords) != len(y_coords) or len(x_coords) < 3:
            return

        #
        self._render_lines(
            points=[
                ND_Point(x_coords[i], y_coords[i])
                for i in range(len(x_coords))
            ],
            color=outline_color
        )

    #
    def draw_filled_polygon(self, x_coords: list[int], y_coords: list[int], fill_color: ND_Color) -> None:
        #
        if len(x_coords) != len(y_coords) or len(x_coords) < 3:
            return

        #
        points = [ND_Point(x, y) for x, y in zip(x_coords, y_coords)]
        triangles = earcut_triangulate_polygon(points)
        self._render_uniform_colored_triangles(triangles=triangles, color=fill_color)

    #
    def draw_textured_polygon(self, x_coords: list[int], y_coords: list[int], texture_id: int, texture_dx: int = 0, texture_dy: int = 0) -> None:
        #
        pass

    #
    def draw_bezier_curve(self, x_coords: list[int], y_coords: list[int], line_color: ND_Color, nb_interpolations: int = 3) -> None:
        #
        pass

    #
    def apply_area_drawing_constraint(self, x: int, y: int, w: int, h: int) -> None:
        """
        Restrict rendering to the specified area using OpenGL scissor test.
        """
        if not self.display.initialized:
            return

        self._ensure_shaderProgram_base()
        self._ensure_context()

        # Convert to OpenGL coordinate system (bottom-left origin)
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glScissor(x, self.height - (y + h), w, h)

    #
    def reset_area_drawing_constraint(self) -> None:
        """
        Remove scissor test and allow full-screen rendering.
        """
        if not self.display.initialized:
            return

        self._ensure_shaderProgram_base()
        self._ensure_context()

        gl.glDisable(gl.GL_SCISSOR_TEST)

    #
    def enable_area_drawing_constraints(self, x: int, y: int, width: int, height: int) -> None:
        """
        Enable constraints and push to stack.
        """
        self.push_to_clip_rect_stack(x, y, width, height)
        self.apply_area_drawing_constraint(x, y, width, height)

    #
    def disable_area_drawing_constraints(self) -> None:
        """
        Disable constraints and pop from stack safely.
        """
        if self.clip_rect_stack:  # Ensure stack isn't empty
            self.remove_top_of_clip_rect_stack()

        new_clip_rect: Optional[ND_Rect] = self.get_top_of_clip_rect_stack()

        if new_clip_rect is None:
            self.reset_area_drawing_constraint()
        else:
            self.apply_area_drawing_constraint(new_clip_rect.x, new_clip_rect.y, new_clip_rect.w, new_clip_rect.h)

    #
    def update_display(self) -> None:

        #
        if not self.display.initialized:
            return

        #
        sdl2.SDL_GL_MakeCurrent(self.sdl_window, self.gl_context)
        gl.glViewport(0, 0, self.width, self.height)

        gl.glClearColor(0, 0, 0, 1)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

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
        sdl2.SDL_GL_SwapWindow(self.sdl_window)


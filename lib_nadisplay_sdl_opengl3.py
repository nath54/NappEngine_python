

from typing import Optional, Any, Callable, cast, Type
from threading import Lock

import os

import numpy as np  # type: ignore

import sdl2  # type: ignore
import sdl2.sdlttf as sdlttf  # type: ignore
import sdl2.sdlimage as sdlimage  # type: ignore

# To improve speed for non development code:
#
#   import OpenGL
#   OpenGL.ERROR_LCHECKING = False
#   OpenGL.ERROR_LOGGING = False

import OpenGL.GL as gl  # type: ignore
# from OpenGL.GLUT import glutInit, glutCreateWindow, glutInitDisplayMode, GLUT_RGB, glutInitWindowSize

import ctypes

from lib_nadisplay_colors import ND_Color
from lib_nadisplay_colors import ND_Transformations
from lib_nadisplay_rects import ND_Rect, ND_Point
from lib_nadisplay import ND_MainApp, ND_Display, ND_Window, ND_Scene
from lib_nadisplay_sdl import to_sdl_color, get_display_info
from lib_nadisplay_opengl import create_and_validate_gl_shader_program


#
VERTEX_SHADER_SRC: str = """
    #version 330 core
    layout (location = 0) in vec2 position;
    layout (location = 1) in vec4 color;
    out vec4 frag_color;
    void main() {
        gl_Position = vec4(position, 0.0, 1.0);
        frag_color = color;
    }
"""

#
FRAGMENT_SHADER_SRC: str = """
    #version 330 core
    in vec4 frag_color;
    out vec4 out_color;
    void main() {
        out_color = frag_color;

    }
"""

#
VERTEX_SHADER_TEXTURES_SRC: str = """
    #version 330 core
    layout (location = 0) in vec2 position;  // Position of the vertex
    layout (location = 1) in vec2 texCoord;  // Texture coordinates
    out vec2 fragTexCoord;  // Output to fragment shader

    void main() {
        gl_Position = vec4(position, 0.0, 1.0);
        fragTexCoord = texCoord;  // Pass texture coordinates to fragment shader
    }
"""

#
FRAGMENT_SHADER_TEXTURES_SRC: str = """
    #version 330 core
    in vec2 fragTexCoord;  // Input from vertex shader
    out vec4 outColor;     // Output color
    uniform sampler2D textureSampler;  // The texture sampler

    void main() {
        outColor = texture(textureSampler, fragTexCoord);  // Sample the texture
    }
"""


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
        self.ttf_fonts: dict[str, dict[int, sdlttf.TTF_OpenFont]] = {}
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
    def get_font(self, font: str, font_size: int) -> Optional[sdlttf.TTF_OpenFont]:
        #
        if not self.initialized:
            return None

        #
        if font not in self.ttf_fonts:
            self.ttf_fonts[font] = {}
        #
        if font_size < 8:
            font_size = 8
        #
        if font_size not in self.ttf_fonts[font]:
            #
            font_path: str = self.font_names[font]
            #
            if (font_path.endswith(".ttf") or font_path.endswith(".otf")) and os.path.exists(font_path):

                self.ttf_fonts[font][font_size] = sdlttf.TTF_OpenFont(font_path.encode(encoding="utf-8"), font_size)
            else:
                return None
        #
        return self.ttf_fonts[font][font_size]


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
        sdl2.SDL_GL_SetSwapInterval(1)  # Enable vsync
        gl.glDisable(gl.GL_DEPTH_TEST)  # Disable depth test
        gl.glDisable(gl.GL_CULL_FACE)   #

        if self.gl_context is None:
            print(f"ERROR: GL context is invalid : {self.gl_context} !!!")

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

        # Compile shaders and create a program for textures
        self.shader_program_textures: int = create_and_validate_gl_shader_program(
                                            VERTEX_SHADER_TEXTURES_SRC, FRAGMENT_SHADER_TEXTURES_SRC)


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
    def blit_texture(self, texture_id: int, dst_rect: ND_Rect) -> None:
        """
        Renders a 2D texture onto a quad using VBOs and a shader program.

        :param texture_id: texture ID.
        :param dst_rect: Destination rectangle where the texture will be drawn (x, y, width, height).
        """

        #
        if not self.display.initialized:
            return

        if texture_id not in self.gl_textures:
            return

        if self.shader_program_textures <= 0:
            print("Error: Shader program for textures hasn't been initialized !")
            return

        #
        # TODO


    #
    def prepare_text_to_render(self, text: str, color: ND_Color, font_size: int, font_name: Optional[str] = None) -> int:

        #
        if not self.display.initialized:
            return -1

        #
        if font_name is None:
            font_name = self.display.default_font

        # Get font
        font: Optional[sdlttf.TTF_OpenFont] = self.display.get_font(font_name, font_size)

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
        self.blit_texture(texture_id, ND_Rect(x, y, width, height))


    #
    def get_prepared_texture_size(self, texture_id: int) -> ND_Point:
        #
        if texture_id not in self.textures_dimensions:
            return ND_Point(0, 0)
        #
        return ND_Point(*self.textures_dimensions[texture_id])


    #
    def destroy_prepared_texture(self, texture_id: int) -> None:
        with self.mutex_sdl_textures:
            if texture_id in self.gl_textures:
                gl.glDeleteTextures(1, [self.gl_textures[texture_id]])
                sdl2.SDL_FreeSurface(self.sdl_textures_surfaces[texture_id])
                del self.sdl_textures_surfaces[texture_id]
                del self.gl_textures[texture_id]


    #
    def _create_opengl_texture_from_surface(self, surface: sdl2.SDL_Surface) -> int:
        #
        if not self.display.initialized:
            return -1

        #
        # TODO

        # Generate a unique texture ID
        texture_id: int = -1
        # with self.mutex_sdl_textures:
        #     texture_id = self.next_texture_id
        #     self.next_texture_id += 1

        #     # Store both OpenGL and SDL textures
        #     self.gl_textures[texture_id] = gl_texture_id
        #     self.sdl_textures_surfaces[texture_id] = surface
        #     self.textures_dimensions[texture_id] = (width, height)

        return texture_id



    #
    def draw_text(self, txt: str, x: int, y: int, font_size: int, font_color: ND_Color, font_name: Optional[str] = None) -> None:
        #
        if not self.display.initialized:
            return

        #
        if font_name is None:
            font_name = self.display.default_font

        # No texture cache, calcul it each time

        #
        # TODO





    #
    def draw_pixel(self, x: int, y: int, color: ND_Color) -> None:
        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        gl.glUseProgram(self.shader_program)

        vertices = np.array([
            [x, y],
        ], dtype=np.float32)

        colors = np.array([
            [color.r, color.g, color.b, color.a],
        ], dtype=np.float32)

        # Create VBOs
        vbo_vertices = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_vertices)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        vbo_colors = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_colors)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, colors.nbytes, colors, gl.GL_STATIC_DRAW)

        # Set attributes
        gl.glEnableVertexAttribArray(0)  # Position
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_vertices)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glEnableVertexAttribArray(1)  # Color
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_colors)
        gl.glVertexAttribPointer(1, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # Draw
        gl.glDrawArrays(gl.GL_POINTS, 0, 1)

        # Cleanup
        gl.glDisableVertexAttribArray(0)
        gl.glDisableVertexAttribArray(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glDeleteBuffers(1, [vbo_vertices])
        gl.glDeleteBuffers(1, [vbo_colors])


    #
    def draw_hline(self, x1: int, x2: int, y: int, color: ND_Color) -> None:
        """
        Draws a horizontal line.

        Args:
            x1 (int): Starting X-coordinate.
            x2 (int): Ending X-coordinate.
            y (int): Y-coordinate.
            color (ND_Color): Line color.
        """

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        gl.glUseProgram(self.shader_program)

        vertices = np.array([
            [x1, y],
            [x2, y]
        ], dtype=np.float32)

        colors = np.array([
            [color.r, color.g, color.b, color.a],
            [color.r, color.g, color.b, color.a],
        ], dtype=np.float32)

        # Create VBOs
        vbo_vertices = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_vertices)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        vbo_colors = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_colors)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, colors.nbytes, colors, gl.GL_STATIC_DRAW)

        # Set attributes
        gl.glEnableVertexAttribArray(0)  # Position
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_vertices)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glEnableVertexAttribArray(1)  # Color
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_colors)
        gl.glVertexAttribPointer(1, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # Draw
        gl.glDrawArrays(gl.GL_LINES, 0, 2)

        # Cleanup
        gl.glDisableVertexAttribArray(0)
        gl.glDisableVertexAttribArray(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glDeleteBuffers(1, [vbo_vertices])
        gl.glDeleteBuffers(1, [vbo_colors])



    #
    def draw_vline(self, x: int, y1: int, y2: int, color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        #
        # TODO


    #
    def draw_line(self, x1: int, x2: int, y1: int, y2: int, color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        #
        # TODO


    #
    def draw_thick_line(self, x1: int, x2: int, y1: int, y2: int, line_thickness: int, color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

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
        self.draw_filled_rect(x, y, width, height, fill_color)

        #
        # TODO


    #
    def draw_unfilled_rect(self, x: int, y: int, width: int, height: int, outline_color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

        #
        # TODO


    #
    def draw_filled_rect(self, x: int, y: int, width: int, height: int, fill_color: ND_Color) -> None:
        #
        if not self.display.initialized:
            return

        #
        if self.shader_program <= 0:
            print(f"Error: shader program hasn't been initialized (={self.shader_program}).")
            return

        gl.glUseProgram(self.shader_program)

        vertices = np.array([
            [x, y],
            [x + width, y],
            [x + width, y + height],
            [x, y + height]
        ], dtype=np.float32)

        colors = np.array([
            [fill_color.r, fill_color.g, fill_color.b, fill_color.a],
            [fill_color.r, fill_color.g, fill_color.b, fill_color.a],
            [fill_color.r, fill_color.g, fill_color.b, fill_color.a],
            [fill_color.r, fill_color.g, fill_color.b, fill_color.a]
        ], dtype=np.float32)

        # Create VBOs
        vbo_vertices = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_vertices)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        vbo_colors = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_colors)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, colors.nbytes, colors, gl.GL_STATIC_DRAW)

        # Set attributes
        gl.glEnableVertexAttribArray(0)  # Position
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_vertices)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glEnableVertexAttribArray(1)  # Color
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_colors)
        gl.glVertexAttribPointer(1, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # Draw
        gl.glDrawArrays(gl.GL_TRIANGLE_FAN, 0, 4)

        # Cleanup
        gl.glDisableVertexAttribArray(0)
        gl.glDisableVertexAttribArray(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glDeleteBuffers(1, [vbo_vertices])
        gl.glDeleteBuffers(1, [vbo_colors])



    #
    def draw_unfilled_circle(self, x: int, y: int, radius: int, outline_color: ND_Color) -> None:

        #
        if not self.display.initialized:
            return

        if self.shader_program <= 0:
            print("Error: shader program hasn't been initialized.")
            return

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
        self.apply_area_drawing_constraint(x, y, width, height)



    #
    def disable_area_drawing_constraints(self) -> None:
        #
        self.remove_top_of_clip_rect_stack()
        #
        if not self.display.initialized:
            return
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
        sdl2.SDL_GL_MakeCurrent(self.sdl_window, self.gl_context)
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
        sdl2.SDL_GL_SwapWindow(self.sdl_window)


Beginning of lib_nadisplay_sdl_opengl3.py:
```py
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
from lib_nadisplay_colors import ND_Transformations
from lib_nadisplay_rects import ND_Rect, ND_Point
from lib_nadisplay import ND_MainApp, ND_Display, ND_Window, ND_Scene
from lib_nadisplay_sdl import to_sdl_color, get_display_info
from lib_nadisplay_opengl import create_and_validate_gl_shader_program

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


# Class for rendering fonts using OpenGL
class FontRenderer:
    # Initialize the font renderer
    def __init__(self, font_path: str, window: "ND_Window_SDL_OPENGL") -> None:
        self.shader_program: int = 0  # OpenGL shader program
        self.shader_projection: int = 0  # OpenGL shader projection matrix
        self.projection = glm.ortho(0, 640, 640, 0, -100000, 100000)
        self.characters: dict = {}  # Dictionary to store font character data
        self.vao: int = 0  # Vertex Array Object ID
        self.vbo: int = 0  # Vertex Buffer Object ID
        self.init_shader()  # Initialize shaders
        #
        self.window: ND_Window_SDL_OPENGL = window
        #
        self.load_font(font_path)  # Load font

    # Initialize the shaders for font rendering
    def init_shader(self) -> None:

        # Vertex shader source code for font rendering
        with open(f"{BASE_PATH}gl_shaders/font_rendering_vertex.vert", "r", encoding="utf-8") as f:
            vertex_shader_source: str = f.read()

        # Fragment shader source code for font rendering
        with open(f"{BASE_PATH}gl_shaders/font_rendering_fragment.frag", "r", encoding="utf-8") as f:
            fragment_shader_source: str = f.read()

        # Compile shaders
        vertexshader = shaders.compileShader(vertex_shader_source, gl.GL_VERTEX_SHADER)
        fragmentshader = shaders.compileShader(fragment_shader_source, gl.GL_FRAGMENT_SHADER)

        # Create the shader program
        self.shader_program = shaders.compileProgram(vertexshader, fragmentshader)
        gl.glUseProgram(self.shader_program)

        # Set up the projection matrix
        self.shader_projection = gl.glGetUniformLocation(self.shader_program, "projection")
        gl.glUniformMatrix4fv(self.shader_projection, 1, gl.GL_FALSE, glm.value_ptr(self.projection))

        # Disable byte-alignment restriction for texture
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)


    # Load font using FreeType and prepare for rendering
    def load_font(self, font_path: str) -> None:

        # Ensure OpenGL context is active
        self.window._ensure_context()

        # Disable byte-alignment restriction for texture
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)

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

        #
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        # Create VAO and VBO for rendering

        # VAO
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        # VBO
        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, 6 * 4 * 4, None, gl.GL_DYNAMIC_DRAW)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

    # Render text on the screen
    def render_text(self, text: str, x: int, y: int, scale: int, color: ND_Color) -> None:

        # Ensure OpenGL context is active
        self.window._ensure_context()

        #
        gl.glUseProgram(self.shader_program)  # Use font shader program

        # Set text color
        gl.glUniform3f(
            gl.glGetUniformLocation(self.shader_program, "textColor"),
            color.r / 255, color.g / 255, color.b / 255
        )
        gl.glActiveTexture(gl.GL_TEXTURE0)

        # Enable blending for transparency
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # Bind the VAO
        gl.glBindVertexArray(self.vao)

        # Iterate over characters in the text
        for char_ in text:

            # Convert char to int
            char: int = ord(char_)

            # Only ASCII characters are supported
            if char >= 128:
                continue

            # Get the character font glyph
            ch = self.characters[char]

            # Calculate position and size for the character
            xpos = x + ch['bearing'][0] * scale
            ypos = y - (ch['size'][1] - ch['bearing'][1]) * scale
            w = ch['size'][0] * scale
            h = ch['size'][1] * scale

            # Define vertex data for the character
            vertices = np.array([
                xpos,     ypos + h,   0.0, 0.0,
                xpos,     ypos,       0.0, 1.0,
                xpos + w, ypos,       1.0, 1.0,
                xpos,     ypos + h,   0.0, 0.0,
                xpos + w, ypos,       1.0, 1.0,
                xpos + w, ypos + h,   1.0, 0.0
            ], dtype=np.float32)

            # Update the VBO with the character's vertex data

            # Render the glyph texture over a quad
            gl.glBindTexture(gl.GL_TEXTURE_2D, ch['texture_id'])

            # Update the VBO with new vertex data
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)

            #
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

            # Render the character as triangles
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)

            # Advance the cursor to the next position (in pixels)
            x += (ch['advance'] >> 6) * scale  # Advance is in 1/64th pixels

        # Unbinding things
        gl.glBindVertexArray(0)  # Unbind the VAO
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)  # Unbind the texture

# ... (rest of the code)

```

But when I execute the main file, that uses it, I got the following error:
```
(venv) [app1/]$ python main.py 
UserWarning: Using SDL2 binaries from pysdl2-dll 2.30.10
Display initialized successfully.
 - thread <Thread(Thread-1 (thread_wrap_fn), initial)> for events created
SDL2 window created successfully.
OpenGL context created successfully.
OpenGL context made current.
Shader program created: 3
Shader program created successfully with ID: 3
Shader program created successfully.
Shader program created: 6
Shader program created successfully with ID: 6
Shader program created successfully.

Beginning of the app...


Begin to exec all init functions in order


All Init functions called


OpenGL context is current.

OpenGL Vendor: b'AMD'
OpenGL Renderer: b'AMD Radeon Graphics (radeonsi, renoir, LLVM 19.1.6, DRM 3.59, 6.12.10-arch1-1)'
OpenGL Version: b'4.6 (Core Profile) Mesa 24.3.3-arch1.2'
GLSL Version: b'4.60'
OpenGL Major Version: 4
OpenGL Minor Version: 6
OpenGL Context Flags: 0
OpenGL Context Profile Mask: 1

OpenGL context is current.

OpenGL Vendor: b'AMD'
OpenGL Renderer: b'AMD Radeon Graphics (radeonsi, renoir, LLVM 19.1.6, DRM 3.59, 6.12.10-arch1-1)'
OpenGL Version: b'4.6 (Core Profile) Mesa 24.3.3-arch1.2'
GLSL Version: b'4.60'
OpenGL Major Version: 4
OpenGL Minor Version: 6
OpenGL Context Flags: 0
OpenGL Context Profile Mask: 1
Traceback (most recent call last):
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/main.py", line 56, in <module>
    app.run()
    ~~~~~~~^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay.py", line 910, in run
    self.mainloop_without_threads()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay.py", line 837, in mainloop_without_threads
    self.display.update_display()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay.py", line 1022, in update_display
    window.update_display()
    ~~~~~~~~~~~~~~~~~~~~~^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay_sdl_opengl3.py", line 1453, in update_display
    scene.render()
    ~~~~~~~~~~~~^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay.py", line 1910, in render
    element.render()
    ~~~~~~~~~~~~~~^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay.py", line 3948, in render
    elt.render()
    ~~~~~~~~~~^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay.py", line 1992, in render
    self.window.draw_text(
    ~~~~~~~~~~~~~~~~~~~~~^
            txt=self.text,
            ^^^^^^^^^^^^^^
    ...<4 lines>...
            font_color=self.font_color
            ^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay_sdl_opengl3.py", line 845, in draw_text
    font_renderer: Optional[FontRenderer] = cast(Optional[FontRenderer], self.display.get_font(font_name, font_size, self))  # type: ignore
                                                                         ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay_sdl_opengl3.py", line 368, in get_font
    self.ttf_fonts[font] = FontRenderer(font_path, window)
                           ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay_sdl_opengl3.py", line 122, in __init__
    self.load_font(font_path)  # Load font
    ~~~~~~~~~~~~~~^^^^^^^^^^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay_sdl_opengl3.py", line 208, in load_font
    gl.glVertexAttribPointer(0, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
    ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nathan/github/NappEngine_python/venv/lib/python3.13/site-packages/OpenGL/latebind.py", line 63, in __call__
    return self.wrapperFunction( self.baseFunction, *args, **named )
           ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nathan/github/NappEngine_python/venv/lib/python3.13/site-packages/OpenGL/GL/VERSION/GL_2_0.py", line 469, in glVertexAttribPointer
    contextdata.setValue( key, array )
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "/home/nathan/github/NappEngine_python/venv/lib/python3.13/site-packages/OpenGL/contextdata.py", line 58, in setValue
    context = getContext( context )
  File "/home/nathan/github/NappEngine_python/venv/lib/python3.13/site-packages/OpenGL/contextdata.py", line 40, in getContext
    raise error.Error(
        """Attempt to retrieve context when no valid context"""
    )
OpenGL.error.Error: Attempt to retrieve context when no valid context
At exit catched

```

As a python and SDL2 and OpenGL expert, can you firsty make a full analysis of the error, then explain how to solve it ?

What can be wrong with the line `gl.glBufferData(gl.GL_ARRAY_BUFFER, 6 * 4 * 4, None, gl.GL_DYNAMIC_DRAW)` ?
Why is it at that line that the error occurs, and not elsewhere?
The ensure context is valid, the correct opengl context is created and loaded due to the `self.window._ensure_context()`.

The context validation is well done:
```py
# From class ND_Window_SDL_ND_Window_SDL_OPENGL
    def _ensure_context(self) -> None:
        """Ensure the OpenGL context is current."""
        if not self.gl_context:
            print("No OpenGL context available.")
            raise RuntimeError("No valid OpenGL context.")
        if sdl2.SDL_GL_MakeCurrent(self.sdl_window, self.gl_context) != 0:
            print("Failed to make OpenGL context current:", sdl2.SDL_GetError())
            raise RuntimeError("Failed to make OpenGL context current.")
        print("\nOpenGL context is current.\n")
        #
        log_opengl_context_info()
        log_opengl_context_attributes()
```

How to solve the error please?

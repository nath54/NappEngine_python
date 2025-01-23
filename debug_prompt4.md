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


# ... (rest of the code)

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
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay_sdl_opengl3.py", line 1464, in update_display
    scene.render()
    ~~~~~~~~~~~~^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay.py", line 1910, in render
    element.render()
    ~~~~~~~~~~~~~~^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay.py", line 3948, in render
    elt.render()
    ~~~~~~~~~~^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay.py", line 3948, in render
    elt.render()
    ~~~~~~~~~~^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay.py", line 3948, in render
    elt.render()
    ~~~~~~~~~~^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay.py", line 2499, in render
    self.window.draw_rounded_rect(x, y, self.w, self.h, self.border_radius, bg_color, fg_color)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay_sdl_opengl3.py", line 1065, in draw_rounded_rect
    self.draw_filled_rect(x, y, width, height, fill_color)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nathan/github/NappEngine_python/tests/apps/app1/../../../lib_nadisplay_sdl_opengl3.py", line 1147, in draw_filled_rect
    gl.glDrawArrays(gl.GL_QUADS, 0, 4)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "/home/nathan/github/NappEngine_python/venv/lib/python3.13/site-packages/OpenGL/error.py", line 230, in glCheckError
    raise self._errorClass(
    ...<4 lines>...
    )
OpenGL.error.GLError: GLError(
        err = 1280,
        description = b'invalid enumerant',
        baseOperation = glDrawArrays,
        cArguments = (GL_QUADS, 0, 4)
)
At exit catched

```

As a python and SDL2 and OpenGL expert, can you firsty make a full analysis of the error, then explain how to solve it ?

What can be wrong with the line `gl.glDrawArrays(gl.GL_QUADS, 0, 4)` ?

How to solve the error please?

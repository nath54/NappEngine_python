# type: ignore

"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

SDL + OPENGL backend for lib_nadisplay.

"""

# Import NumPy for numerical operations
import numpy as np  # type: ignore
#
from typing import Any

# To optimize speed in production, OpenGL error checking and logging can be disabled
# import OpenGL
# OpenGL.ERROR_CHECKING = False
# OpenGL.ERROR_LOGGING = False

# Import OpenGL functionalities for rendering
import OpenGL.GL as gl  # type: ignore
# Optionally, GLUT can be used for window management and other utilities
# from OpenGL.GLUT import glutInit, glutCreateWindow, glutInitDisplayMode, GLUT_RGB, glutInitWindowSize

# Import FreeType for font loading and rendering
import freetype  # type: ignore
# Import GLM for mathematical operations (e.g., vectors, matrices)
import glm

# Import lib_nadisplay functions
from lib_nadisplay_colors import ND_Color
from lib_nadisplay_opengl import compile_shaders


#
BASE_PATH: str = "../../../"


#
WindowOpenGLClass = Any  # "ND_Window_SDL2_OPENGL" | "ND_Window_SDL3_OPENGL" | "ND_Window_GLFW_OPENGL"


#
class FontRenderer:
    def __init__(self, font_path: str, window: WindowOpenGLClass) -> None:
        self.window: WindowOpenGLClass = window  # Reference to the window object
        self.shader_program: int = 0  # OpenGL shader program
        self.shader_projection: int = 0  # OpenGL shader projection matrix
        self.projection = glm.ortho(0, self.window.width, self.window.height, 0, -100000, 100000)  # Default projection
        self.characters: dict = {}  # Dictionary to store font character data
        self.vao: int = 0  # Vertex Array Object ID
        self.vbo: int = 0  # Vertex Buffer Object ID

        # Ensure context is current on this thread
        if hasattr(self.window, "_ensure_context"):
            #
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
        if hasattr(self.window, "_ensure_context"):
            #
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
        if hasattr(self.window, "_ensure_context"):
            #
            self.window._ensure_context()
        #
        if hasattr(self.window, "verify_context"):
            #
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

        #
        if hasattr(self.window, "_ensure_context"):
            #
            self.window._ensure_context()
        #
        if hasattr(self.window, "verify_context"):
            #
            self.window.verify_context()

        print("Calling glVertexAttribPointer")
        gl.glVertexAttribPointer(0, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)


    def handle_resize(self, new_width: int, new_height: int) -> None:
        """
        Updates the projection matrix when the window is resized.
        """
        # Ensure OpenGL context is active on this thread before making GL calls
        if hasattr(self.window, "_ensure_context"):
            #
            self.window._ensure_context()

        # Recalculate the orthographic projection matrix
        self.projection = glm.ortho(0, new_width, new_height, 0, -100000, 100000)

        # Activate the shader program to update the uniform
        gl.glUseProgram(self.shader_program)

        # Get uniform location (can store this in init if preferred)
        self.shader_projection = gl.glGetUniformLocation(self.shader_program, "projection")

        # Upload the new projection matrix
        gl.glUniformMatrix4fv(self.shader_projection, 1, gl.GL_FALSE, glm.value_ptr(self.projection))

        # Optional: Unbind the shader program
        # gl.glUseProgram(0)


    def render_text(self, text: str, x: int, y: int, scale: float, color: ND_Color) -> None:

        # Use program
        gl.glUseProgram(self.shader_program)

        #
        scale /= 50

        # Ensure OpenGL context is active
        if hasattr(self.window, "_ensure_context"):
            #
            self.window._ensure_context()

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


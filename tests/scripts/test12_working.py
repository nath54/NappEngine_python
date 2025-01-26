import glfw  # type: ignore
import OpenGL.GL as gl  # type: ignore
from PIL import Image
import numpy as np


def main():
    # Initialize GLFW
    if not glfw.init():
        raise Exception("GLFW initialization failed")

    # Create a GLFW window
    window = glfw.create_window(800, 600, "OpenGL with GLFW", None, None)
    if not window:
        glfw.terminate()
        raise Exception("GLFW window creation failed")

    glfw.make_context_current(window)

    # Set the clear color (background color)
    gl.glClearColor(0.1, 0.1, 0.1, 1.0)

    # Enable 2D textures
    gl.glEnable(gl.GL_TEXTURE_2D)

    # Create a texture
    texture = create_texture("res/sprites/apple1.png")

    # Main rendering loop
    while not glfw.window_should_close(window):
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Draw a filled triangle
        gl.glBegin(gl.GL_TRIANGLES)
        gl.glColor3f(1.0, 0.0, 0.0)  # Red
        gl.glVertex2f(0.1, 0.1)
        gl.glColor3f(0.0, 1.0, 0.0)  # Green
        gl.glVertex2f(0.2, -0.2)
        gl.glColor3f(0.0, 0.0, 1.0)  # Blue
        gl.glVertex2f(0.0, 0.0)
        gl.glEnd()

        # Draw a line
        gl.glBegin(gl.GL_LINES)
        gl.glColor3f(1.0, 1.0, 0.0)  # Yellow
        gl.glVertex2f(-0.8, 0.8)
        gl.glVertex2f(0.8, 0.8)
        gl.glEnd()

        # Draw a textured triangle
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
        gl.glBegin(gl.GL_TRIANGLES)
        gl.glTexCoord2f(0.0, 0.0)
        gl.glVertex2f(-0.5, -0.5)
        gl.glTexCoord2f(1.0, 0.0)
        gl.glVertex2f(0.5, -0.5)
        gl.glTexCoord2f(0.5, 1.0)
        gl.glVertex2f(0.0, 0.5)
        gl.glEnd()

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        # Swap buffers
        glfw.swap_buffers(window)

        # Poll for events
        glfw.poll_events()

    # Cleanup
    glfw.terminate()


def create_texture(image_path):
    # Load the image
    image = Image.open(image_path).transpose(Image.FLIP_TOP_BOTTOM)
    image_data = np.array(image, dtype=np.uint8)

    # Generate a texture ID
    texture_id = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)

    # Set texture parameters
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    # Upload the texture to the GPU
    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        gl.GL_RGBA,
        image.width,
        image.height,
        0,
        gl.GL_RGBA,
        gl.GL_UNSIGNED_BYTE,
        image_data,
    )

    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    return texture_id


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(str(e))

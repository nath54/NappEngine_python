import glfw  # type: ignore
import OpenGL.GL as gl  # type: ignore
from OpenGL.GLU import gluPerspective, gluLookAt  # type: ignore
from PIL import Image
import numpy as np
import math


def main():
    # Initialize GLFW
    if not glfw.init():
        raise Exception("GLFW initialization failed")

    # Create a GLFW window
    window = glfw.create_window(800, 600, "Rotating Cube and Sphere", None, None)
    if not window:
        glfw.terminate()
        raise Exception("GLFW window creation failed")

    glfw.make_context_current(window)
    gl.glEnable(gl.GL_DEPTH_TEST)  # Enable depth testing for 3D
    gl.glEnable(gl.GL_TEXTURE_2D)  # Enable texturing

    # Create texture
    texture = create_texture("res/sprites/apple1.png")

    # Initialize rotation angles
    cube_angle = 0
    sphere_angle = 0

    while not glfw.window_should_close(window):
        glfw.poll_events()

        # Clear buffers
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Set up projection matrix
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gluPerspective(45, 800 / 600, 0.1, 50.0)

        # Set up model-view matrix
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gluLookAt(4, 4, 10, 0, 0, 0, 0, 1, 0)

        # Draw the rotating sphere
        gl.glPushMatrix()
        gl.glTranslatef(2.5, 0, 0)  # Position the sphere
        gl.glRotatef(sphere_angle, 0, 1, 0)  # Rotate the sphere
        draw_colored_sphere()
        gl.glPopMatrix()

        # Draw the rotating cube
        gl.glPushMatrix()
        gl.glTranslatef(-2.5, 0, 0)  # Position the cube
        gl.glRotatef(cube_angle, 0, 1, 0)  # Rotate the cube
        draw_textured_cube(texture)
        gl.glPopMatrix()


        # Swap buffers
        glfw.swap_buffers(window)

        # Update rotation angles
        cube_angle += 1
        sphere_angle += 3.5

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


def draw_textured_cube(texture):
    # Bind the texture
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)

    # Draw a cube with the same texture on all sides
    gl.glBegin(gl.GL_QUADS)

    # Front face
    gl.glTexCoord2f(0.0, 0.0)
    gl.glVertex3f(-1.0, -1.0, 1.0)
    gl.glTexCoord2f(1.0, 0.0)
    gl.glVertex3f(1.0, -1.0, 1.0)
    gl.glTexCoord2f(1.0, 1.0)
    gl.glVertex3f(1.0, 1.0, 1.0)
    gl.glTexCoord2f(0.0, 1.0)
    gl.glVertex3f(-1.0, 1.0, 1.0)

    # Back face
    gl.glTexCoord2f(0.0, 0.0)
    gl.glVertex3f(-1.0, -1.0, -1.0)
    gl.glTexCoord2f(1.0, 0.0)
    gl.glVertex3f(-1.0, 1.0, -1.0)
    gl.glTexCoord2f(1.0, 1.0)
    gl.glVertex3f(1.0, 1.0, -1.0)
    gl.glTexCoord2f(0.0, 1.0)
    gl.glVertex3f(1.0, -1.0, -1.0)

    # Left face
    gl.glTexCoord2f(0.0, 0.0)
    gl.glVertex3f(-1.0, -1.0, -1.0)
    gl.glTexCoord2f(1.0, 0.0)
    gl.glVertex3f(-1.0, -1.0, 1.0)
    gl.glTexCoord2f(1.0, 1.0)
    gl.glVertex3f(-1.0, 1.0, 1.0)
    gl.glTexCoord2f(0.0, 1.0)
    gl.glVertex3f(-1.0, 1.0, -1.0)

    # Right face
    gl.glTexCoord2f(0.0, 0.0)
    gl.glVertex3f(1.0, -1.0, -1.0)
    gl.glTexCoord2f(1.0, 0.0)
    gl.glVertex3f(1.0, 1.0, -1.0)
    gl.glTexCoord2f(1.0, 1.0)
    gl.glVertex3f(1.0, 1.0, 1.0)
    gl.glTexCoord2f(0.0, 1.0)
    gl.glVertex3f(1.0, -1.0, 1.0)

    # Top face
    gl.glTexCoord2f(0.0, 0.0)
    gl.glVertex3f(-1.0, 1.0, -1.0)
    gl.glTexCoord2f(1.0, 0.0)
    gl.glVertex3f(-1.0, 1.0, 1.0)
    gl.glTexCoord2f(1.0, 1.0)
    gl.glVertex3f(1.0, 1.0, 1.0)
    gl.glTexCoord2f(0.0, 1.0)
    gl.glVertex3f(1.0, 1.0, -1.0)

    # Bottom face
    gl.glTexCoord2f(0.0, 0.0)
    gl.glVertex3f(-1.0, -1.0, -1.0)
    gl.glTexCoord2f(1.0, 0.0)
    gl.glVertex3f(1.0, -1.0, -1.0)
    gl.glTexCoord2f(1.0, 1.0)
    gl.glVertex3f(1.0, -1.0, 1.0)
    gl.glTexCoord2f(0.0, 1.0)
    gl.glVertex3f(-1.0, -1.0, 1.0)

    gl.glEnd()
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)


def draw_colored_sphere():
    slices, stacks = 40, 40
    radius = 1.0

    for i in range(slices):
        lon0 = 2 * math.pi * i / slices
        lon1 = 2 * math.pi * (i + 1) / slices

        gl.glBegin(gl.GL_QUAD_STRIP)
        for j in range(stacks + 1):
            lat = math.pi * j / stacks - math.pi / 2
            color = (i / slices, 0.5, 1.0 - i / slices)

            for lon in [lon0, lon1]:
                x = math.cos(lat) * math.cos(lon) * radius
                y = math.sin(lat) * radius
                z = math.cos(lat) * math.sin(lon) * radius
                gl.glColor3f(*color)
                gl.glVertex3f(x, y, z)

        gl.glEnd()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(str(e))

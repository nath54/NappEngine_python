"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Some utilitary functions for OpenGL backend for lib_nadisplay.

"""



import OpenGL.GL as gl  # type: ignore



#
def compile_gl_shader(source: str, shader_type: gl.GLenum | int) -> int:
    """
    Compile un shader à partir de son code source.

    :param source: Code source GLSL du shader
    :param shader_type: Type du shader (GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, etc.)
    :return: ID du shader compilé
    :raises RuntimeError: Si la compilation échoue
    """
    shader: int = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader, source)
    gl.glCompileShader(shader)

    # Vérification d'erreurs
    if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
        error: bytes | str = gl.glGetShaderInfoLog(shader)
        if isinstance(error, bytes):
            error = error.decode('utf-8')
        raise RuntimeError(f"Shader compilation failed: {error}")

    return shader


#
def create_gl_shader_program(vertex_src: str, fragment_src: str) -> int:
    """
    Creates a shader program from vertex and fragment source code.
    Adds error handling for compilation and linking errors.
    """
    try:
        vertex_shader: int = compile_gl_shader(vertex_src, gl.GL_VERTEX_SHADER)
        fragment_shader: int = compile_gl_shader(fragment_src, gl.GL_FRAGMENT_SHADER)

        program: int = gl.glCreateProgram()
        gl.glAttachShader(program, vertex_shader)
        gl.glAttachShader(program, fragment_shader)
        gl.glLinkProgram(program)

        # Check for linking errors
        if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
            error: bytes | str = gl.glGetProgramInfoLog(program)
            if isinstance(error, bytes):
                error = error.decode('utf-8')
            raise RuntimeError(f"Shader linking failed: {error}")

        # Delete shaders after linking
        gl.glDeleteShader(vertex_shader)
        gl.glDeleteShader(fragment_shader)

        return program
    except RuntimeError as e:
        print(f"Error in shader program creation: {e}")
        return 0


def create_and_validate_gl_shader_program(vertex_shader_src: str, fragment_shader_src: str) -> int:

    shader_program: int = create_gl_shader_program(vertex_shader_src, fragment_shader_src)
    print(f"Shader program created: {shader_program}")

    # Check if shader program is valid
    if shader_program <= 0:
        print("Failed to create shader program!")
        return 0
    else:
        print(f"Shader program created successfully with ID: {shader_program}")

    gl.glValidateProgram(shader_program)
    if not gl.glGetProgramiv(shader_program, gl.GL_VALIDATE_STATUS):
        error: bytes | str = gl.glGetProgramInfoLog(shader_program)
        if isinstance(error, bytes):
            error = error.decode('utf-8')
        print(f"Shader program validation failed: {error}")
        #
        return 0

    #
    return shader_program




def compile_shaders(vertex_source, fragment_source):
    vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    gl.glShaderSource(vertex_shader, vertex_source)
    gl.glCompileShader(vertex_shader)
    if not gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS):
        raise RuntimeError(gl.glGetShaderInfoLog(vertex_shader))

    fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    gl.glShaderSource(fragment_shader, fragment_source)
    gl.glCompileShader(fragment_shader)
    if not gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS):
        raise RuntimeError(gl.glGetShaderInfoLog(fragment_shader))

    shader_program = gl.glCreateProgram()
    gl.glAttachShader(shader_program, vertex_shader)
    gl.glAttachShader(shader_program, fragment_shader)
    gl.glLinkProgram(shader_program)
    if not gl.glGetProgramiv(shader_program, gl.GL_LINK_STATUS):
        raise RuntimeError(gl.glGetProgramInfoLog(shader_program))

    gl.glDeleteShader(vertex_shader)
    gl.glDeleteShader(fragment_shader)

    return shader_program


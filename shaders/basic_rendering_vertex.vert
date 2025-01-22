#version 330 core
layout (location = 0) in vec2 position;  // Vertex position input
layout (location = 1) in vec4 color;    // Vertex color input
out vec4 frag_color;                    // Pass color to fragment shader
void main() {
    gl_Position = vec4(position, 0.0, 1.0);  // Set vertex position in clip space
    frag_color = color;                      // Forward color to fragment shader
}
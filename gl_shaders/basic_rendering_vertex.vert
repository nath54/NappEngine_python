#version 330 core
layout(location = 0) in vec2 aPos; // Vertex position

void main() {
    gl_Position = vec4(aPos, 0.0, 1.0); // Pass the vertex position to the fragment shader
}
#version 330 core
layout(location = 0) in vec4 vertex; // <vec2 position, vec2 texCoords>

out vec2 TexCoords;

uniform mat4 projection; // Projection matrix

void main() {
    // Transform the vertex position using the projection matrix
    gl_Position = projection * vec4(vertex.xy, 0.0, 1.0);
    // Pass the texture coordinates to the fragment shader
    TexCoords = vertex.zw;
}
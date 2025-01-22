#version 330 core
layout (location = 0) in vec2 position;  // Vertex position input
layout (location = 1) in vec2 texCoord;  // Texture coordinate input
out vec2 fragTexCoord;  // Pass texture coordinates to fragment shader

void main() {
    gl_Position = vec4(position, 0.0, 1.0);  // Set vertex position in clip space
    fragTexCoord = texCoord;                // Pass texture coordinates
}
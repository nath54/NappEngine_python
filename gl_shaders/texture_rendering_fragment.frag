#version 330 core
in vec2 TexCoord; // Texture coordinate from vertex shader

uniform sampler2D textureSampler; // Texture sampler

out vec4 FragColor;

void main() {
    FragColor = texture(textureSampler, TexCoord); // Sample the texture
}
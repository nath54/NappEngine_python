#version 330 core
in vec2 fragTexCoord;  // Input texture coordinates from vertex shader
out vec4 outColor;     // Output color to screen
uniform sampler2D textureSampler;  // The texture sampler

void main() {
    outColor = texture(textureSampler, fragTexCoord);  // Sample texture and set output color
}
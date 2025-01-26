#version 330 core
in vec2 TexCoords; // Texture coordinates from the vertex shader

out vec4 FragColor; // Output color

uniform sampler2D text; // Texture sampler for the font atlas
uniform vec3 textColor; // Text color

void main() {
    // Sample the texture (font atlas) and use the red channel as the alpha value
    vec4 sampled = vec4(1.0, 1.0, 1.0, texture(text, TexCoords).r);
    // Combine the sampled texture with the text color
    FragColor = vec4(textColor, 1.0) * sampled;
}
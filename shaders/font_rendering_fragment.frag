#version 330 core
in vec2 TexCoords;
out vec4 color;

uniform sampler2D text;  // Texture sampler
uniform vec3 textColor;  // Font color

void main()
{
    vec4 sampled = texture(text, TexCoords);  // Sample texture
    color = vec4(textColor, 1.0) * sampled;  // Apply font color
}
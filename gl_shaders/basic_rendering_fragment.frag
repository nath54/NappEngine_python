#version 330 core
uniform vec4 color; // Uniform for the color

out vec4 FragColor;

void main() {
    FragColor = color; // Set the output color to the uniform
}
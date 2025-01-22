#version 330 core
in vec4 frag_color;   // Input color from vertex shader
out vec4 out_color;   // Output color to screen
void main() {
    out_color = frag_color;  // Set the output color
}
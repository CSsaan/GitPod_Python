#version 420 core
precision mediump float;
layout(binding = 0) uniform sampler2D tex;

in vec2 uv;
out vec4 FragColor;

void main()
{
    FragColor = texture(tex, uv);
    // FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}

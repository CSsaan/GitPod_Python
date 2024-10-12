#version 420 core
precision mediump float;
layout(binding = 0) uniform sampler2D tex;

in vec2 uv;
out vec4 FragColor;

vec2 iResolution = vec2(1920.0, 1080.0);

void main()
{
    vec4 color = texture(tex, uv);
    FragColor = vec4(color.rgb, 1.0);
}

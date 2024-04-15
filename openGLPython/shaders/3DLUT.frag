#version 420 core
precision mediump float;
layout(binding = 0) uniform sampler2D tex;
layout(binding = 1) uniform sampler2D s_inLut;

in vec2 uv;
out vec4 FragColor;

uniform float strenth;
uniform float gpow;

// **********************************************************
vec4 LUT8x8(vec4 inColor, sampler2D lutImageTexture)
{
	inColor = clamp(inColor, vec4(0.0), vec4(1.0));
    highp float blueColor = inColor.b * 63.0;
    highp vec2 quad1;
    quad1.y = floor(floor(blueColor) / 8.0);
    quad1.x = floor(blueColor) - (quad1.y * 8.0);
    highp vec2 quad2;
    quad2.y = floor(ceil(blueColor) / 7.9999);
    quad2.x = ceil(blueColor) - (quad2.y * 8.0);
    highp vec2 texPos1;
    texPos1.x = (quad1.x * 0.125) + 0.5/512.0 + ((0.125 - 1.0/512.0) * inColor.r);
    texPos1.y = (quad1.y * 0.125) + 0.5/512.0 + ((0.125 - 1.0/512.0) * inColor.g);
    highp vec2 texPos2;
    texPos2.x = (quad2.x * 0.125) + 0.5/512.0 + ((0.125 - 1.0/512.0) * inColor.r);
    texPos2.y = (quad2.y * 0.125) + 0.5/512.0 + ((0.125 - 1.0/512.0) * inColor.g);
    vec4 newColor2_1 = texture(lutImageTexture, texPos1);
    vec4 newColor2_2 = texture(lutImageTexture, texPos2);
    vec4 newColor22 = mix(newColor2_1, newColor2_2, fract(blueColor));
    return newColor22;
}


// **********************************************************
void main()
{   
    vec4 incolor = texture(tex, vec2(uv.x, 1.0-uv.y));
    // vec3 backColor = texture(tex_background, vec2(uv.x, 1.0-uv.y)).rgb;
    vec3 inlut = LUT8x8(incolor, s_inLut).rgb;

    vec3 result = mix(incolor.rgb, inlut, abs(sin(strenth)));

    FragColor = vec4(result, 1.0);

    // FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}

#version 420 core
precision mediump float;
layout(binding = 0) uniform sampler2D tex;
layout(binding = 1) uniform sampler2D tex_background;

in vec2 uv;
out vec4 FragColor;

uniform float strenth;
uniform float gpow;

// **********************************************************
vec3 greenMat(vec3 force, vec3 back, float green_strenth, float green_pow)
{
    // * 相机纹理 *
    lowp vec4 tempColor = vec4(force, 1.0);
    // * 计算纹素的红色和蓝色分量的平均强度 *
    lowp float rbAverage = tempColor.r * green_pow + tempColor.b * green_pow; //0.5
    // * 计算绿色元素强度与红蓝色强度平均值之间的差 *
    lowp float gDelta = tempColor.g*(0.45*green_strenth+0.55) - rbAverage;
    // * 如果绿色强度大于红色和蓝色强度的平均值，则根据绿色元素的强度计算 0.0 到 1.0 范围内的透明度值 *
    tempColor.a = 1.0 - smoothstep(0.0, 0.25, gDelta);  // 1.0-0.75
    // * 使用透明度值的多次幂。这样，部分透明的片段变得更加透明。这通过避免几乎但不完全不透明的碎片来锐化最终结果，这些碎片倾向于在颜色边界处形成光晕*
    //        tempColor.a = tempColor.a * tempColor.a * tempColor.a * tempColor.a;
    tempColor.a = pow(tempColor.a, 4.0);
    // *大海背景/红色背景*
    vec3 result_mix = mix(back.rgb, tempColor.rgb, tempColor.a);
    return result_mix;
}


// **********************************************************
void main()
{   
    vec3 originColor = texture(tex, vec2(uv.x, 1.0-uv.y)).rgb;
    vec3 backColor = texture(tex_background, vec2(uv.x, 1.0-uv.y)).rgb;
    vec3 result_mix = greenMat(originColor, backColor, strenth, gpow);

    FragColor = vec4(result_mix, 1.0);

    // FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}

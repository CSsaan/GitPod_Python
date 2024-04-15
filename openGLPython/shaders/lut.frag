#version 420 core
precision mediump float;
layout(binding = 0) uniform sampler2D tex; // 原图
layout(binding = 1) uniform sampler2D tex_mask; // 处理后的mask结果
layout(binding = 2) uniform sampler2D tex_lut;  // LUT

uniform float strength;

in vec2 uv;
out vec4 FragColor;

vec4 LUT4x4(vec4 inColor, sampler2D lutImageTexture)
{
    highp float blueColor = inColor.b * 15.0;
    highp vec2 quad1;
    quad1.y = floor(floor(blueColor) / 4.0);
    quad1.x = floor(blueColor) - (quad1.y * 4.0);
    highp vec2 quad2;
    quad2.y = floor(ceil(blueColor) / 3.9999);
    quad2.x = ceil(blueColor) - (quad2.y * 4.0);
    highp vec2 texPos1;
    texPos1.x = (quad1.x * 0.25) + 0.5/64.0 + ((0.25 - 1.0/64.0) * inColor.r);
    texPos1.y = (quad1.y * 0.25) + 0.5/64.0 + ((0.25 - 1.0/64.0) * inColor.g);
    highp vec2 texPos2;
    texPos2.x = (quad2.x * 0.25) + 0.5/64.0 + ((0.25 - 1.0/64.0) * inColor.r);
    texPos2.y = (quad2.y * 0.25) + 0.5/64.0 + ((0.25 - 1.0/64.0) * inColor.g);
    lowp vec4 newColor2_1 = texture(lutImageTexture, texPos1);
    lowp vec4 newColor2_2 = texture(lutImageTexture, texPos2);
    lowp vec4 newColor22 = mix(newColor2_1, newColor2_2, fract(blueColor));
    return newColor22;
}

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

void main()
{
    // blur1
    float rate = 5.0;
    vec2 resolu = vec2(960.0, 540.0);
    // gaussian blur
    const int KernelSize = 9;
    float Kernel[KernelSize] = float[](
    6.0,                  6.0,
        16.0,       16.0,      
              36.0,           
        16.0,       16.0,       
    6.0,                  6.0
    );
    vec2 Offset[KernelSize] = vec2[](
    vec2(-2.0, -2.0),                                                                 vec2(2.0, -2.0),
                            vec2(-1.0, -1.0),                      vec2(1.0, -1.0),                           
                                                vec2(0.0, 0.0),                                          
                            vec2(-1.0, 1.0),                        vec2(1.0, 1.0),                          
    vec2(-2.0, 2.0),                                                                   vec2(2.0, 2.0)
    );
    float sum = 0.0;
    for (int i = 0; i < KernelSize; i++)
    {
        float tmp = texture(tex_mask, vec2(uv.x, 1.0-uv.y) + rate * resolu * Offset[i]).r;
        sum += tmp * Kernel[i]/124.0;
    }

    // // blur2
    // const float R = 35.0;
    // vec2 uv0 = vec2(uv.x, 1.0-uv.y);
	// vec3 sum_c = texture(tex_mask, uv0).rgb;
   	// vec2 offsetx = vec2(1.0 / 1920.0, 0.0);
    // for(float i = 1.5; i <= R; i+=0.01){
    // 	sum_c += texture(tex_mask, uv0 + offsetx * i).rgb * 2.0;
    //     sum_c += texture(tex_mask, uv0 - offsetx * i).rgb * 2.0;
    // }
    // float result1 = vec4(sum_c / (800.0 * R + 1.0), 1.0).r;

   	// vec2 offsety = vec2(0.0,1.0 / 1080.0);
    // for(float i = 1.5; i <= R; i+=0.01){
    // 	sum_c += texture(tex_mask, uv0 + offsety * i).rgb * 2.0;
    //     sum_c += texture(tex_mask, uv0 - offsety * i).rgb * 2.0;
    // }
    // float result2 = vec4(sum_c / (800.0 * R + 1.0), 1.0).r;


    float mask = sum; // sum  result2

    vec4 srcColor = texture(tex, vec2(uv.x, 1.0-uv.y));
    vec4 whiten_dstColor = LUT8x8(srcColor, tex_lut); // 稍微提亮 +0.02
    // float mask = texture(tex_mask, vec2(uv.x, 1.0-uv.y)).r;
    vec4 dstColor = vec4(mix(srcColor.rgb, whiten_dstColor.rgb, mask*abs(sin(strength))), 1.0); 

    //找到变化大的部分，按照变化大小进行提亮
    float dis = distance(srcColor, dstColor);
    float smooth_dis = smoothstep(0.0, 1.0, dis);
    dstColor.rgb = srcColor.rgb + vec3(smooth_dis*2.0);
    vec3 bill_white = mix(srcColor.rgb, dstColor.rgb, 0.4);
    
    // if(uv.x>0.5)
        FragColor = vec4(vec3(bill_white), 1.0);
    // else
    //     FragColor = srcColor;
}

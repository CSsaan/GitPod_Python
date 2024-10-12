#version 420 core
precision mediump float;
layout(binding = 0) uniform sampler2D tex; // YCbCr分割结果
layout(binding = 1) uniform sampler2D tex_aimask; // AI分割结果

in vec2 uv;
out vec4 FragColor;

float fillterGreen(sampler2D localTexture, vec2 UV)
{   
    float G = texture(localTexture, vec2(UV.x, UV.y)).g;
    float B = texture(localTexture, vec2(UV.x, UV.y)).b;
    float green = (G>0.88 && B<0.4) ? 1.0:0.0;
    return green;
}
// ************************************************************************************************
void main()
{
    // 先膨胀
    float rate = 1.0;
    vec2 texelSize = rate / vec2(1920.0, 1080.0);
    vec3 dilatedAI = vec3(0.0); //texture(iChannel0, uv);
    for (int i = -3; i <= 3; i++) 
    {
        for (int j = -3; j <= 3; j++) 
        {
            float x = uv.x + float(i) * texelSize.x;
            float y = 1.0-uv.y + float(j) * texelSize.y;
            // float aimask = fillterGreen(tex_aimask, vec2(x, y));
            float aimask =  texture(tex_aimask, vec2(x, y)).r;
            dilatedAI = max(vec3(aimask), dilatedAI); // * kernel[i+1][j+1]
        }
    }

    // float Tradition = texture(tex, vec2(uv.x, uv.y)).r;
    // float aimask = fillterGreen(tex_aimask, vec2(uv.x, 1.0-uv.y));
    // float origin_aimask = aimask;

    // float result = 0.0;
    // if(origin_aimask > 0.0 && Tradition > 0.0)
    // {
    //     result = 1.0;
    // }
    // if(origin_aimask > 0.0 && Tradition == 0.0)
    // {
    //     result = 0.58;
    // }
    // if(origin_aimask == 0.0 && Tradition > 0.0 && dilatedAI.r > 0.0)
    // {
    //     result = texture(tex, vec2(uv.x, uv.y)).g;
    // }

    // result = mix(result, texture(tex, vec2(uv.x, uv.y)).g, 0.8);

    // float ori = texture(tex, uv).r;
    // if(dilatedAI.r>0.0 && ori == 0.0)
    //     dilatedAI.r = 0.5;

    // float AI_alpha_ori = smoothstep(0.0, 1.0, texture(tex_aimask, vec2(uv.x, 1.0-uv.y)).r);
    // float AI_alpha = smoothstep(0.0, 1.0, AI_alpha_ori);
    // // AI_alpha = smoothstep(0.0, 1.0, AI_alpha_ori);

    // float CbCr_alpha_ori = mix(AI_alpha_ori, texture(tex, vec2(uv.x, uv.y)).g, 0.5);
    // // float CbCr_alpha = smoothstep(0.0, 1.0, CbCr_alpha_ori);
    
    // float merge = smoothstep(0.0, 1.0, AI_alpha*CbCr_alpha_ori);
    // // merge = smoothstep(0.0, 1.0, merge);
    // FragColor = vec4(vec3(texture(tex, vec2(uv.x, uv.y)).g), 1.0); // result   texture(tex, vec2(uv.x, uv.y)).g
    // // FragColor = texture(tex, uv);

    float Tradition_Confidence = texture(tex, vec2(uv.x, uv.y)).g;
    // float mask_origin = texture(tex_aimask, vec2(uv.x, 1.0-uv.y)).r;
    // float CbCr_alpha_ori = mix(mask_origin, Tradition_Confidence, 0.5);
    // FragColor = vec4(vec3( clamp(smoothstep(0.2, 0.8, mask_origin)*CbCr_alpha_ori, 0.0, 1.0) ), 1.0);
    FragColor = vec4(vec3(Tradition_Confidence), 1.0);
}

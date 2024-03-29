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
    float rate = 5.0;
    vec2 texelSize = rate / vec2(1920.0, 1080.0);
    vec3 dilatedAI = vec3(0.0); //texture(iChannel0, uv);
    for (int i = -3; i <= 3; i++) 
    {
        for (int j = -3; j <= 3; j++) 
        {
            float x = uv.x + float(i) * texelSize.x;
            float y = 1.0-uv.y + float(j) * texelSize.y;
            float aimask = fillterGreen(tex_aimask, vec2(x, y));
            dilatedAI = max(vec3(aimask), dilatedAI); // * kernel[i+1][j+1]
        }
    }

    float Tradition = texture(tex, vec2(uv.x, uv.y)).r;
    float aimask = fillterGreen(tex_aimask, vec2(uv.x, 1.0-uv.y));
    float origin_aimask = aimask;

    float result = 0.0;
    if(origin_aimask > 0.0 && Tradition > 0.0)
    {
        result = 1.0;
    }
    if(origin_aimask > 0.0 && Tradition == 0.0)
    {
        result = 0.58;
    }
    if(origin_aimask == 0.0 && Tradition > 0.0 && dilatedAI.r > 0.0)
    {
        result = texture(tex, vec2(uv.x, uv.y)).g;
    }

    // float ori = texture(tex, uv).r;
    // if(dilatedAI.r>0.0 && ori == 0.0)
    //     dilatedAI.r = 0.5;
    FragColor = vec4(vec3(result), 1.0);
    // FragColor = texture(tex, uv);
}

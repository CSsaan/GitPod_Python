#version 420 core
precision mediump float;
layout(binding = 0) uniform sampler2D tex;

in vec2 uv;
out vec4 FragColor;

vec2 iResolution = vec2(1920.0, 1080.0);

#if 0
void main()
{
    float threshold = 0.00005 * 10.0; // 噪声阈值

    vec4 color = texture(tex, uv);
    // 计算图像的方差
    vec3 imageMean = vec3(0.0);
    vec3 imageVariance = vec3(0.0);
    for (int i = -1; i <= 1; i++)
    {
        for (int j = -1; j <= 1; j++)
        {
            vec4 neighborColor = texture(tex, uv + vec2(i, j) / iResolution.xy);
            imageMean += neighborColor.rgb;
            imageVariance += neighborColor.rgb * neighborColor.rgb;
        }
    }
    imageMean /= 9.0; // 均值
    imageVariance = (imageVariance / 9.0) - (imageMean * imageMean);
    // 进行噪声检测
    float variance = (imageVariance.r + imageVariance.g + imageVariance.b) / 3.0;
    vec4 result = color;
    if (variance > threshold)
    {
        result = vec4(1.0, 0.0, 0.0, 1.0); // 红色表示图像存在噪声
    }

    FragColor = result;
}
#endif

#if 1
/// @brief 绘制水平线、横线
/// @param position 
/// @param width 
/// @return 
float drawHorizontalLine(vec2 uv, float position, float width)
{
    vec2 lineUv = uv;
    lineUv.y -= position;
    lineUv = abs(lineUv);
    float line = ceil(lineUv.y-width);
    return line;
}
/// @brief 绘制垂直线、竖线
/// @param position 
/// @param width 
/// @return 
float drawVerticalLine(vec2 uv, float position, float width)
{
    vec2 lineUv = uv;
    lineUv.x -= position;
    lineUv = abs(lineUv);
    float line = ceil(lineUv.x-width);
    return line;
}
/// @brief 绘制圆形
/// @param position 圆心位置
/// @param radius 圆半径
/// @return 
float drawSphere(vec2 uv, vec2 position, float radius)
{
    float sphere = smoothstep(radius, 0.0, length(uv-position));
    return sphere;
}
void main()
{
    float myTime = 0.20;

    // Cosinus line ==========================================
    vec2 lUv = uv;
    lUv.y -= 0.30;
    vec2 cosUV = abs(vec2(lUv.x, lUv.y + cos(lUv.x * 3.14 * 8.0) * 0.05));

    float cosinusLine = smoothstep(0.002, 0.0055, cosUV.y);

    // Sinus line sphere
    vec2 sUv = vec2(lUv.x, lUv.y * (iResolution.y / iResolution.x));
    sUv.y = sUv.y + cos(myTime * 0.25 * 3.14 * 8.0) * 0.03;
    sUv.x -= fract(myTime * 0.25);

    float sSphere = drawSphere(sUv, vec2(0.5, 0.5), 0.01);

    // Coloring ============================================

    float topLine = (1.0 - drawHorizontalLine(uv, 0.9, 0.002)) * 0.3;
    float centerLine = (1.0 - drawHorizontalLine(uv, 0.5, 0.002)) * 0.3;
    float bottomLine = (1.0 - drawHorizontalLine(uv, 0.1, 0.002)) * 0.3;

    float topLineV = (1.0 - drawVerticalLine(uv, 0.90, 0.002)) * 0.3;
    float centerLineV = (1.0 - drawVerticalLine(uv, 0.50, 0.002)) * 0.3;
    float bottomLineV = (1.0 - drawVerticalLine(uv, 0.10, 0.002)) * 0.3;

    FragColor = vec4(topLine+topLineV+sSphere, centerLine+centerLineV, bottomLine+bottomLineV, 1.0);
}
#endif







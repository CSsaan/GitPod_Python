#iChannel0 "file://D:/OpenGlProject/ShaderToys/pic/depth/1118.png"

/*
[边缘检测]
*/


#define THRESHOLD 0.05
float radius = 0.5;  // 编译判断半径

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;

    vec2 size = iResolution.xy;

    vec4 color = texture(iChannel0, uv);
    vec4 right = texture(iChannel0, uv + vec2(radius, 0.) / size);
    vec4 left = texture(iChannel0, uv + vec2(-radius, 0.) / size);
    vec4 bottom = texture(iChannel0, uv + vec2(0., radius) / size);
    vec4 top = texture(iChannel0, uv + vec2(0., -radius) / size);
    if((left.r - color.r >= THRESHOLD) || (right.r - color.r >= THRESHOLD) || (top.r - color.r >= THRESHOLD ) || (bottom.r - color.r >= THRESHOLD))
    {
        float dx = right.r - left.r;
        float dy = bottom.r - top.r;
        vec2 tensor = (vec2(dx / sqrt(dx * dx + dy * dy), dy / sqrt(dx * dx + dy * dy)) * 0.5) + 0.5;
        fragColor = vec4(color.r - 1.0 / 100.0 , tensor, 1.0);
    } else 
    {
        fragColor = vec4(0.0);
    }
}
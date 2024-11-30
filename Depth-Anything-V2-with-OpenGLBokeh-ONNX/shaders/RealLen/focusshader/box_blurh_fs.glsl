#iChannel0 "file://D:/OpenGlProject/ShaderToys/pic/depth/1118.png"

/*
横向的方框均值滤波。
配合box_blurw_fs.glsl使用，双步骤模糊。
*/

float radius = 3.0; // 模糊半径: 1 - 10

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;

    vec4 color = vec4(0.0);
    int count = 0;

    for (float y = uv.y-radius/iResolution.y; y <= uv.y+radius/iResolution.y; y += 1.0/float(iResolution.y)) {
        color += texture(iChannel0, vec2(uv.x, y));
        count += 1;
    }

    if (count == 0) {
        fragColor = texture(iChannel0, uv);
    } else {
        fragColor = color / float(count);
    }
}
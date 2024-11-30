#iChannel0 "file://D:/OpenGlProject/ShaderToys/ReLens/focusshader/box_blurh_fs.glsl"

/*
横向的方框均值滤波。
配合box_blurh_fs.glsl使用，双步骤模糊。
*/

float radius = 3.0; // 模糊半径: 1 - 10

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;

    vec4 color = vec4(0.0);
    int count = 0;

    for (float x = uv.x-radius/iResolution.x; x <= uv.x+radius/iResolution.x; x += 1.0/float(iResolution.x)) {
        color += texture(iChannel0, vec2(x, uv.y));
        count += 1;
    }

    if (count == 0) {
        fragColor = texture(iChannel0, uv);
    } else {
        fragColor = color / float(count);
    }
}
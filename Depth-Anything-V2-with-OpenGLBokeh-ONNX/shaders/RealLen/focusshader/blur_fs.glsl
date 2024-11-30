#iChannel0 "file://D:/OpenGlProject/ShaderToys/pic/depth/1118d.png"

/*
模糊，根据中心颜色
*/

float radius = 3.0; // 模糊半径: 1 - 10

float scale = 1.0;  // 
float bias = 0.0;   // 

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;

    vec4 centralColor = texture(iChannel0, uv);

    vec4 colorAmount = vec4(0.0);
    float factorAmount = 0.0;

    for (float x = uv.x - radius/iResolution.x; x <= uv.x + radius/iResolution.x; x += 1.0/float(iResolution.x)) {
        for (float y = uv.y - radius/iResolution.y; y <= uv.y + radius/iResolution.y; y += 1.0/float(iResolution.y)) {
            vec4 color = texture(iChannel0, vec2(x, y));
            float factor = color.r + bias;
            if (color.r < centralColor.r) {
                factor *= scale;
            }
            factor += bias;
            colorAmount += color * factor;
            factorAmount += factor;
        }
    }
    if (factorAmount > 0.0) {
        fragColor =  colorAmount / factorAmount;
    } else {
        fragColor =  centralColor;
    }
}
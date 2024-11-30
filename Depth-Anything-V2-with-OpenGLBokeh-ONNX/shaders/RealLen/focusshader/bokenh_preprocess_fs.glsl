#iChannel0 "file://D:/OpenGlProject/ShaderToys/pic/depth/1118.png"
#iChannel1 "file://D:/OpenGlProject/ShaderToys/pic/depth/1118d.png"

/*
将单通道深度图，融合进原图的alpha通道。
然后进行gamma校正。
*/

float gamma1 = 12.0;
float gamma2 = 0.5;

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;

    vec4 color = texture(iChannel0, uv);

    vec3 rgb = vec3(color.rgb / (step(color.a, 0.0) + color.a));
    rgb = rgb / (gamma1 * (1.0 - rgb) + gamma2);

    float depth = 1.0-texture(iChannel1, uv).r;

    fragColor = vec4(rgb, depth);
}
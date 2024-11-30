#iChannel0 "file://D:/OpenGlProject/ShaderToys/pic/depth/0834.png"
#iChannel1 "file://D:/OpenGlProject/ShaderToys/pic/depth/0834d.png"
#iChannel2 "file://D:/OpenGlProject/ShaderToys/pic/depth/1118.png"

#define origTex iChannel0
#define pathMaskTex iChannel1
#define dstTex iChannel2

/*
[不清楚，可视化]
*/

int maskMergeMode = 1; // 1,2,3,0

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;

    vec4 origC = texture(origTex, uv);
    vec4 pathMaskC = texture(pathMaskTex, uv);
    vec4 dstC = texture(dstTex, uv);

    vec3 origOrigRgb = origC.rgb;
    vec3 pathOrigRgb = pathMaskC.rgb;
    vec3 dstOrigRgb = dstC.rgb;

    float alpha = pathMaskC.r;
    if (maskMergeMode == 1) {
        // brush:在原图上显示一下单通道的深度图
        fragColor = vec4(dstOrigRgb + pathOrigRgb - dstOrigRgb * alpha, 1.0);
        // fragColor = vec4(vec3(dstC.rgb * (1. - alpha)), 1.);
        // fragColor = vec4(dstOrigRgb.r * (1. - alpha) + pathOrigRgb.r * alpha, 0., 0., 1.);
    } else if (maskMergeMode == 2) {
        // restore
        fragColor = vec4(((dstOrigRgb * (1. - alpha) + origOrigRgb * alpha)), 1.);
    } else if (maskMergeMode == 3) {
        fragColor = vec4(origOrigRgb, 1.);
    } else if (maskMergeMode == 4) {
        fragColor = vec4(pathOrigRgb, 1.);
    } else {
        // should not reach here
        discard;
//        fragColor = vec4(1., 1., 0., 1.);
    }
}
#iChannel0 "file://D:/OpenGlProject/ShaderToys/pic/depth/0834.png"
#iChannel1 "file://D:/OpenGlProject/ShaderToys/pic/depth/0834d.png"

/*
[不清楚]
*/

int maskMergeMode = 1; // 1:near, 2:far, 3:not_reach_here

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;

    vec4 c1 = texture(iChannel0, uv);
    vec4 c2 = texture(iChannel1, uv);
    if (maskMergeMode == 1) {
        // near
        fragColor = vec4(c1.rgb + c2.rgb, 1.);
    } else if (maskMergeMode == 2) {
        // far
        fragColor = vec4(c1.rgb - c2.rgb, 1.);
    } else {
        // should not reach here
        discard;
//        gl_FragColor = vec4(1., 1., 0., 1.);
    }
}
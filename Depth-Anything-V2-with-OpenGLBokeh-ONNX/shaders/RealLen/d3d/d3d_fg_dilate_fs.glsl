#iChannel0 "file://D:/OpenGlProject/ShaderToys/pic/depth/FocusTexture.png"

/*
对于单通道mask进行膨胀处理，按照一定像素大小。
项目中用于处理前景人物mask。
*/

float radius = 3.0;  // 膨胀像素数（默认3.0）

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;

    vec2 size = iResolution.xy;

    radius = mod(iTime*10.0, 50.0); // 动态查看50个像素膨胀动态效果

    vec4 color = vec4(0.0);
    for(float i = -radius; i <= radius; i++){
        for(float j = -radius; j <= radius; j++){
            float a = texture(iChannel0, uv + vec2(i, j) / size).r;
            if (a > 0.0){
                color = vec4(1.0);
                break;
            }
        }
    }
    fragColor = color;
}
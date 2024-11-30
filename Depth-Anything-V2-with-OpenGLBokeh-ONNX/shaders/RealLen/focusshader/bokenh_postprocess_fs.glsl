#iChannel0 "file://D:/OpenGlProject/ShaderToys/pic/depth/1118.png"
#iChannel1 "file://D:/OpenGlProject/ShaderToys/pic/depth/1118d.png"
#iChannel2 "file://D:/OpenGlProject/ShaderToys/ReLens/focusshader/bokenh_process_fs.glsl"

#define inputTexture iChannel0 // 原图
#define bokehTexture iChannel2 // bokenh_preprocess_fs.glsl
#define depthTexture iChannel1 // 深度图

/*
根据对焦距离，来渲染不同程度的红蓝偏色。
*/
                                    
float focus = 0.3;       // 对焦距离 0.0 - 1.0
float xTransverse = 0.05; // 红蓝偏色方向
float yTransverse = 0.05; // 红蓝偏色方向
float distortion = 0.05;  // 鱼眼变形 -1.0 - 1.0

float gamma1 = 12.0;
float gamma2 = 0.5;
     
    
float f(float x, float i) {
    return (1.0 - i) + x * x * i;
}

vec2 ff(vec2 st, float i) {
    return st - st * 1.0/(distance(st, vec2(0.0)) + 1.) * i;
}

vec2 ff2(vec2 st, float i) {
    return st - st * distance(st, vec2(0.0)) * distance(st, vec2(0.0)) * i;
}

vec2 fisheye(vec2 uv, float distortion) {
    vec2 dif = (uv - vec2(0.5)) * 2.;
    if (distortion >= 0.0) {
        vec2 signal = sign(dif);
        uv = signal * ff(abs(dif), distortion/5.0) / 2.0 + vec2(0.5);
    } else {
        uv = ff2(dif, -distortion/20.0) / 2.0 + vec2(0.5);
    }
    return uv;
}

vec2 m_saturate(vec2 x) {
    return clamp(x, vec2(0.0), vec2(1.0));
}

vec3 getColorFromBokeh(vec4 bokehColor) {
    vec3 rgb = bokehColor.rgb;
    rgb = (gamma1 + gamma2) * rgb / (1.0 + gamma1 * rgb);
    return rgb;
}


void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;
    uv = fisheye(uv, distortion);

    float depth = 1.0-texture(depthTexture, uv).r;
    vec2 viewportSize = iResolution.xy;
    float limit = 0.01 * max(viewportSize.x, viewportSize.y) * abs(focus - depth);
    vec2 uvInPixels = uv * viewportSize;
    vec2 rUV = m_saturate((uvInPixels + vec2( xTransverse*limit, yTransverse*limit)) / viewportSize);
    vec2 gUV = m_saturate((uvInPixels + vec2(-xTransverse*limit,-yTransverse*limit)) / viewportSize);

    float a = texture(inputTexture, uv).a;
    float r = getColorFromBokeh(texture(bokehTexture, rUV)).r;
    float g = getColorFromBokeh(texture(bokehTexture, gUV)).g;
    float b = getColorFromBokeh(texture(bokehTexture, uv)).b;

    fragColor = vec4(r, g, b, a);



    // // Debug
    // vec3 oriColor = texture(inputTexture, uv).rgb;
    // vec3 result = vec3(r, g, b);
    // float change = sin(iTime*4.0)>0.0? 1.0:0.0;
    // fragColor = vec4(mix(result, oriColor, change), 1.0);
}
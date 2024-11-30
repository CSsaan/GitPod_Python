#iChannel0 "file://D:/OpenGlProject/ShaderToys/pic/depth/1118.png"

/*
曝光-对比度-饱和度-色温-色调-阴影-高光-氛围-颗粒-褪色-色相-锐化-暗角
*/

lowp mat4 colorMatrix = mat4(
    0.3588f, 0.7044f, 0.1368f, 0.0f,
    0.299f, 0.587f, 0.114f, 0.0f, 
    0.2392f, 0.4696f, 0.0912f, 0.0f, 
    0.0f, 0.0f, 0.0f, 1.0f);

highp float exposure = 0.0;  // 曝光: 0.0 - 1.0
lowp float contrast = 1.0;   // 对比度: 0.0 - 1.0 - 2.0
lowp float saturation = 1.0; // 饱和度: 0.0 - 1.0 - 2.0

/*
1000K - 4000K：偏暖色调，如黄色、橙色。
5000K - 6500K：中性色调，如白色。
7000K - 10000K：偏冷色调，如蓝色。
*/
lowp float temperature = 5000.0; // 色温 1000.0-10000

lowp float tint = 0.0;                             // 色调: -1.0 - 0.0 - 1.0

lowp vec2 vignetteCenter = vec2(0.5, 0.5);         // 暗角中心
lowp vec3 vignetteColor = vec3(0.0, 0.0, 0.0);     // 暗角颜色
highp float vignetteStart = 0.75f - (0.0 * 0.5f);  // 暗角范围: 0.0 - 1.0
highp float vignetteEnd = 0.75f; // 默认固定0.75

lowp float shadows = 0.0;                          // 阴影: -1.0 - 0.0 - 1.0
lowp float highlights = 0.0;                       // 高光: 0.0 - 1.0
lowp float ambiance = 0.0;                         // 氛围: -0.5 - 0.0 - 0.5
lowp float grain = 0.0;                            // 颗粒: 0.0 - 10.0
lowp float fade = 0.0;                             // 褪色: 0.0 - 1.0
mediump float uHue = 0.0;                          // 色相: 0.0 - 6.4 对应0到360度
float uSharpness = 0.0;                            // 锐度: 0.0 - 3.0
float uSharpnessRadius = 0.3; // 默认固定0.3

const mediump vec3 luminanceWeightingHighlight = vec3(0.3, 0.3, 0.3); // 默认固定
const mediump vec3 luminanceWeighting = vec3(0.2125, 0.7154, 0.0721); // 默认固定
const lowp vec3 warmFilter = vec3(0.93, 0.54, 0.0); // 默认固定(色温)
mediump mat3 RGBtoYIQ = mat3(0.299, 0.587, 0.114, 0.596, -0.274, -0.322, 0.212, -0.523, 0.311); // 默认固定(色调)
mediump mat3 YIQtoRGB = mat3(1.0, 0.956, 0.621, 1.0, -0.272, -0.647, 1.0, -1.105, 1.702); // 默认固定(色调)

vec3 blurSample(vec2 uv, vec2 xoff, vec2 yoff) {
    vec3 v11 = texture(iChannel0, uv + xoff).rgb;
    vec3 v12 = texture(iChannel0, uv + yoff).rgb;
    vec3 v21 = texture(iChannel0, uv - xoff).rgb;
    vec3 v22 = texture(iChannel0, uv - yoff).rgb;
    return (v11 + v12 + v21 + v22 + 2.0 * texture(iChannel0, uv).rgb) * 0.166667;
}

vec3 edgeStrength(vec2 uv, vec2 uSize) {
    float spread = uSharpnessRadius;
    vec2 offset = vec2(1.0) / vec2(uSize.x, uSize.y);
    vec2 up = vec2(0.0, offset.y) * spread;
    vec2 right = vec2(offset.x, 0.0) * spread;

    vec3 v12 = blurSample(uv + up, right, up);

    vec3 v21 = blurSample(uv - right, right, up);
    vec3 v22 = blurSample(uv, right, up);
    vec3 v23 = blurSample(uv + right, right, up);

    vec3 v32 = blurSample(uv - up, right, up);

    vec3 laplacian_of_g =  v12 *  1.0 + v21 * 1.0 + v22 * -4.0 + v23 * 1.0 + v32 * 1.0 ;
    laplacian_of_g = laplacian_of_g * (spread / 0.3 * 0.12 + 0.88);
    return laplacian_of_g.xyz;
}

vec4 adjustSharpness(vec4 color, highp vec2 uv, vec2 uSize) {
    return vec4(color.xyz - edgeStrength(uv, uSize) * uSharpness, 1.0);
}

const highp  vec4  kRGBToYPrime = vec4 (0.299, 0.587, 0.114, 0.0);
const highp  vec4  kRGBToI     = vec4 (0.595716, -0.274453, -0.321263, 0.0);
const highp  vec4  kRGBToQ     = vec4 (0.211456, -0.522591, 0.31135, 0.0);

const highp  vec4  kYIQToR   = vec4 (1.0, 0.9563, 0.6210, 0.0);
const highp  vec4  kYIQToG   = vec4 (1.0, -0.2721, -0.6474, 0.0);
const highp  vec4  kYIQToB   = vec4 (1.0, -1.1070, 1.7046, 0.0);

vec4 adjustHue(vec4 color, float mHue)
{
    highp float   YPrime  = dot (color, kRGBToYPrime);
    highp float   I      = dot (color, kRGBToI);
    highp float   Q      = dot (color, kRGBToQ);

    highp float   hue     = atan (Q, I);
    highp float   chroma  = sqrt (I * I + Q * Q);

    hue -= mHue;

    Q = chroma * sin (hue);
    I = chroma * cos (hue);

    highp vec4    yIQ   = vec4 (YPrime, I, Q, 0.0);
    color.r = dot (yIQ, kYIQToR);
    color.g = dot (yIQ, kYIQToG);
    color.b = dot (yIQ, kYIQToB);

    return color;
}

vec4 adjust(vec4 srcColor, highp vec2 uv, vec2 uSize) {
    //     if (uHue > 0.0) {
    //         srcColor = adjustHue(srcColor);
    //     }
    srcColor.r = max(srcColor.r, 0.001);
    srcColor.g = max(srcColor.g, 0.001);
    srcColor.b = max(srcColor.b, 0.001);

    mediump float luminance2 = dot(srcColor.rgb, luminanceWeightingHighlight);
    mediump float shadow;
    if (shadows > 0.0) {
        shadow = clamp((pow(luminance2, 1.0/(shadows+1.0)) + (-0.76)*pow(luminance2, 2.0/(shadows+1.0))) - luminance2, 0.0, 1.0);
    } else {
        shadow = clamp((pow(luminance2, 1.0-shadows) + (0.76)*pow(luminance2, 2.0*(1.0-shadows))) - luminance2, -1.0, 0.0);
    }

    mediump float highlight;
    if (highlights < 0.0) {
        highlight = clamp((1.0 - (pow(1.0-luminance2, 1.0/(1.0-highlights)) + (-0.8)*pow(1.0-luminance2, 2.0/(1.0-highlights)))) - luminance2, -1.0, 0.0);
    } else {
        highlight = clamp((1.0 - pow(1.0-luminance2, 1.0+highlights) + (-0.8)*pow(1.0-luminance2, 2.0*(1.0+highlights))) - luminance2, 0.0, 1.0);
    }

    lowp vec3 rs = vec3(0.0, 0.0, 0.0) + ((luminance2 + shadow + highlight) - 0.0) * ((srcColor.rgb - vec3(0.0, 0.0, 0.0))/(luminance2 - 0.0));
    lowp vec4 color = vec4(rs, srcColor.a);


    highp float x = (uv.x + 4.0) * (uv.y + 4.0) * 10.0;
    highp vec4 grain = vec4(mod((mod(x, 13.0) + 1.0) * (mod(x, 123.0) + 1.0), 0.01) - 0.005) * grain;
    highp vec4 result =  color + grain;

    // sharpen
    if (uSharpnessRadius > 0.0) {
        result = adjustSharpness(result, uv, uSize);
    }

    lowp vec4 exposureColor = vec4(result.rgb * pow(2.0, exposure), result.w);

    lowp vec4 outputColor = exposureColor * colorMatrix;
    lowp vec4 fadeColor = (fade * outputColor) + ((1.0 - fade) * exposureColor);


    lowp vec4 contrastColor = vec4(((fadeColor.rgb - vec3(0.5)) * contrast + vec3(0.5)), fadeColor.w);


    lowp float luminance = dot(contrastColor.rgb, luminanceWeighting);
    lowp vec3 greyScaleColor = vec3(luminance);
    lowp vec4 saturationColor = vec4(mix(greyScaleColor, contrastColor.rgb, saturation), contrastColor.w);


    mediump vec3 yiq = RGBtoYIQ * saturationColor.rgb; //adjusting tint
    yiq.b = clamp(yiq.b + tint*0.5226*0.1, -0.5226, 0.5226);
    lowp vec3 rgb = YIQtoRGB * yiq;
    lowp vec3 processed = vec3(
    (rgb.r < 0.5 ? (2.0 * rgb.r * warmFilter.r) : (1.0 - 2.0 * (1.0 - rgb.r) * (1.0 - warmFilter.r))), //adjusting temperature
    (rgb.g < 0.5 ? (2.0 * rgb.g * warmFilter.g) : (1.0 - 2.0 * (1.0 - rgb.g) * (1.0 - warmFilter.g))),
    (rgb.b < 0.5 ? (2.0 * rgb.b * warmFilter.b) : (1.0 - 2.0 * (1.0 - rgb.b) * (1.0 - warmFilter.b))));
    float _temperature = (temperature - 5000.0) * (5000.0 < 5000.0 ? 4.0e-4 : 6.0e-5);
    lowp vec4 seWenSeDiao = vec4(mix(rgb, processed, _temperature), saturationColor.a);


    lowp float d = distance(uv, vec2(vignetteCenter.x, vignetteCenter.y));
    lowp float percent = smoothstep(vignetteStart, vignetteEnd, d);
    lowp vec4 vignette = vec4(mix(seWenSeDiao.x, vignetteColor.x, percent), mix(seWenSeDiao.y, vignetteColor.y, percent), mix(seWenSeDiao.z, vignetteColor.z, percent), 1.0);


    lowp vec4 rsShadow = vec4(vignette.rgb, vignette.a);
    lowp float luminance3 = dot(rsShadow.rgb, luminanceWeighting);
    lowp vec3 greyScaleColorFenWei = vec3(luminance3);
    lowp vec4 fenweiSaturation;
    if (ambiance < 0.0) {
        fenweiSaturation = vec4(mix(greyScaleColorFenWei, rsShadow.rgb, abs(ambiance / 5.0) + 1.0), rsShadow.a);
    } else {
        fenweiSaturation = vec4(mix(greyScaleColorFenWei, rsShadow.rgb, ambiance * 3.0 + 1.0), rsShadow.a);
    }

    highp float lum = fenweiSaturation.r * 0.3 + fenweiSaturation.g * 0.59 + fenweiSaturation.b * 0.11;
    lowp vec4 fenweiRs = vec4(fenweiSaturation.r - fenweiSaturation.r * ambiance * (lum - 0.5),
    fenweiSaturation.g - fenweiSaturation.g * ambiance * (lum - 0.5),
    fenweiSaturation.b - fenweiSaturation.b * ambiance * (lum - 0.5),
    fenweiSaturation.a);
    return vec4(fenweiRs.rgb, fenweiRs.w);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;
    //    vec4 result = vec4(applyRGBCurve(hslToRgb(applyLuminanceCurve(rgbToHsl(result.rgb)))), result.a);
    highp vec4 color = texture(iChannel0, fract(uv));

    color = vec4(color.rgb / (color.a + step(color.a, 0.0)), 1.0); // 将透明部分变为黑色不透明

    vec2 uSize = iResolution.xy;
    color = adjust(color, uv, uSize);

    if (uHue > 0.0) {
        color = adjustHue(color, uHue);
    }
    fragColor = color;
}

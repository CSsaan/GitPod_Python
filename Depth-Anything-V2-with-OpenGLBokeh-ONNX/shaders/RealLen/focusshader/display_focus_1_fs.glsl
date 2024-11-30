#iChannel0 "file://D:/OpenGlProject/ShaderToys/ReLens/depthFix/depthFixColor.glsl"
#iChannel1 "file://D:/OpenGlProject/ShaderToys/ReLens/focusshader/blur_fs.glsl"

float focus = 0.5;

float bismoothstep(float minValue, float midValue, float maxValue, float value) {
    return smoothstep(minValue, midValue, value) * smoothstep(maxValue, midValue, value);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;

    focus = 0.5*(sin(iTime)+1.0); // mod(iTime, 2.0) / 2.0;

    float depth = 1.0-texture(iChannel1, uv).r;
    vec4 overlay = vec4(focus*focus, focus*focus, focus*focus, 1.0) * bismoothstep(focus-0.03, focus, focus+0.03, depth);
    vec4 base = texture(iChannel0, uv);
    fragColor = base + overlay - base * overlay.a;
}
#iChannel0 "file://D:/OpenGlProject/ShaderToys/pic/depth/1118.png"
#iChannel1 "file://D:/OpenGlProject/ShaderToys/pic/depth/1118d.png"

/*
    GZY color split adjust V1.0 2021/7/15 zxy
*/

#define MIN_WEIGHT 0.1
#define SHADOW_PEAK 0.25
#define MIDDLE_PEAK 0.5
#define HIGHLIGHT_PEAK 0.75

vec3 shadowTarget = vec3(0.0);
vec3 middleTarget = vec3(0.0);
vec3 highlightTarget = vec3(0.0);
vec3 globalTarget = vec3(0.0);

float shadowLum = 1.0;
float middleLum = 1.0;
float highlightLum = 1.0;
float globalLum = 0.0;
float balance = 0.0;
float blend = 0.0;

vec3 overlay(vec3 color1, vec3 color2, vec3 strength){
    vec3 result = mix(color1 * color2 / 0.5, 1. - (1. - color1) * (1. - color2) / 0.5, step(vec3(0.5), color1));
    return mix(color1, result, strength);
}

float calSat(vec3 color){
    float min_rgb = min(color.r, min(color.g, color.b));
    float max_rgb = max(color.r, max(color.g, color.b));
    if(max_rgb > min_rgb){
        return (max_rgb - min_rgb) / max_rgb;
    }else{
        return 0.;
    }
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;

    vec4 color = texture(iChannel0, uv);

    vec3 shadow_weight = exp(- pow(color.rgb - vec3(SHADOW_PEAK), vec3(2.)) / (0.04 + balance)) * (0.25 + blend);
    vec3 shadow_color = overlay(color.rgb, shadowTarget, calSat(shadowTarget) * shadow_weight);
    shadow_color = min(max(shadow_color + vec3(pow(color.rgb - vec3(1.), vec3(2.))) * (shadowLum - 0.5) * 0.5, 0.), 1.);

    vec3 middle_weight = exp(-pow(color.rgb - vec3(MIDDLE_PEAK), vec3(2.)) / (0.04 + balance)) * 0.75 * (0.25 + blend);
    vec3 middle_color = overlay(color.rgb, middleTarget,  calSat(middleTarget) * middle_weight);
    middle_color = min(max(middle_color + exp(-pow(color.rgb - vec3(0.5), vec3(2.)) / 0.04) * 0.75 * (middleLum - 0.5) * 0.5, 0.), 1.);

    vec3 highlight_weight = exp(- pow(color.rgb - vec3(HIGHLIGHT_PEAK), vec3(2.)) / (0.04 + balance)) * (0.25 + blend);
    vec3 highlight_color = overlay(color.rgb, highlightTarget, calSat(highlightTarget) * highlight_weight);
    highlight_color = min(max(highlight_color + vec3(pow(color.rgb, vec3(2.))) * (highlightLum - 0.5) * 0.5, 0.), 1.);

    color.rgb = (shadow_color * (MIN_WEIGHT + shadow_weight) + middle_color * (MIN_WEIGHT + middle_weight) + highlight_color * (MIN_WEIGHT + highlight_weight)) /
    (shadow_weight + highlight_weight + middle_weight + MIN_WEIGHT * 3.);

    color.rgb = overlay(color.rgb, globalTarget, 0.25 * vec3(calSat(globalTarget)));
    color.rgb += vec3(globalLum - 0.5) * 0.5;
    fragColor = color;   
}
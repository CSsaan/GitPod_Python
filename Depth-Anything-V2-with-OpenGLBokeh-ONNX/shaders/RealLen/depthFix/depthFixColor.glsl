// #iChannel0 "file://D:/OpenGlProject/ShaderToys/pic/depth/1118d.png"
#iChannel0 "file://D:/PythonProject/depth_1.png"

/*
深度图伪彩色可视化：
    0：原始黑白
    1.2,3：三种伪彩色
*/
int colorType = 2; // 0,1,2,3

vec4 blend(vec4 base, vec4 overlay) {
    return base + overlay - base * overlay.a;
}

vec4 colorTypeOneWithItensity(float intensity) {
    if (intensity <= 0.3333) {
        float progress = intensity / 0.3333;
        float r = progress * (150. - 7.) + 7.;
        float b = progress * (150.0 - 46.0) + 46.0;
        return vec4(r / 255.0, 0.0, b / 255.0, 1.0);
    } else if (intensity < 0.6666) {
        float progress = (intensity - 0.3333) / 0.3333;
        float r = progress * (255.0 - 155.0) + 155.0;
        float g = progress * (74.0 - 0.0) + 0.0;
        float b = progress * (0.0 - 155.0) + 155.0;
        return vec4(r / 255.0, g / 255.0, b / 255.0, 1.0);
    } else {
        float progress = (intensity - 0.6666)  / (1.0 - 0.6666);
        float g = progress * (255.0 - 74.0) + 74.0;
        float b = progress * (171.0 - 0.0) + 0.0;
        return vec4(1.0, g / 255.0, b / 255.0, 1.0);
    }
}

vec4 colorTypeTwoWithItensity(float intensity) {
    if (intensity < 0.16) {
        float progress = intensity / 0.16;
        float r = progress * (30.0 - 0.0) + 0.0;
        float g = progress * (14.0 - 6.0) + 6.0;
        float b = progress * (255.0 - 178.0) + 178.0;
        return vec4(r / 255.0, g /255.0, b / 255.0, 1.0);
    } else if (intensity < 0.32) {
        float progress = (intensity - 0.16) / (0.32 - 0.16);
        float r = progress * (14.0 - 30.0) + 30.0;
        float g = progress * (247.0 - 74.0) + 74.0;
        float b = progress * (240.0 - 255.0) + 255.0;
        return vec4(r / 255.0, g /255.0, b / 255.0, 1.0);
    } else if (intensity < 0.48) {
        float progress = (intensity - 0.32) / (0.48 - 0.32);
        float r = progress * (126.0 - 14.0) + 14.0;
        float g = progress * (255.0 - 247.0) + 247.0;
        float b = progress * (128.0 - 240.0) + 240.0;
        return vec4(r / 255.0, g /255.0, b / 255.0, 1.0);
    } else if (intensity < 0.64) {

        float progress = (intensity - 0.48) / (0.64 - 0.48);
        float r = progress * (249.0 - 126.0) + 126.0;
        float g = progress * (255.0 - 255.0) + 255.0;
        float b = progress * (6.0 - 128.0) + 128.0;
        return vec4(r / 255.0, g /255.0, b / 255.0, 1.0);
    } else if (intensity < 0.84) {
        float progress = (intensity - 0.64) / (0.84 - 0.64);
        float r = progress * (255.0 - 249.0) + 249.0;
        float g = progress * (37.0 - 255.0) + 255.0;
        float b = progress * (0.0 - 6.0) + 6.0;
        return vec4(r / 255.0, g /255.0, b / 255.0, 1.0);
    } else {
        float progress = (intensity - 0.84) / (1.0 - 0.84);
        float r = 255.0;
        float g = progress * (255.0 - 37.0) + 37.0;
        float b = progress * (255.0 - 0.0) + 0.0;
        return vec4(r / 255.0, g /255.0, b / 255.0, 1.0);
    }
}

vec4 colorTypeThreeWithItensity(float intensity) {
    if (intensity <= 0.16) {
        float progress = intensity / 0.16;
        float r = progress * (30.0 - 0.0) + 0.0;
        float g = progress * (74.0 - 6.0) + 6.0;
        float b = progress * (255.0 - 178.0) + 178.0;
        return vec4(r / 255.0, g / 255.0, b / 255.0, 1.0);
    } else if (intensity <= 0.32) {
        float progress = (intensity - 0.16) / (0.32 - 0.16);
        float r = progress * (14.0 - 30.0) + 30.0;
        float g = progress * (247.0 - 74.0) + 74.0;
        float b = progress * (240.0 - 255.0) + 255.0;
        return vec4(r / 255.0, g / 255.0, b / 255.0, 1.0);
    } else if (intensity <= 0.48) {
        float progress = (intensity - 0.32) / (0.48 - 0.32);
        float r = progress * (255.0 - 14.0) + 14.0;
        float g = progress * (100.0 - 247.0) + 247.0;
        float b = progress * (6.0 - 240.0) + 240.0;
        return vec4(r / 255.0, g / 255.0, b / 255.0, 1.0);
    } else if (intensity <= 0.64) {
        float progress = (intensity - 0.48) / (0.64 - 0.48);
        float r = progress * (249.0 - 255.0) + 255.0;
        float g = progress * (255.0 - 100.0) + 100.0;
        float b = progress * (6.0 - 6.0) + 6.0;
        return vec4(r / 255.0, g / 255.0, b / 255.0, 1.0);
    } else if (intensity <= 0.84) {
        float progress = (intensity - 0.64) / (0.84 - 0.64);
        float r = progress * (255.0 - 249.0) + 249.0;
        float g = progress * (216.0 - 255.0) + 255.0;
        float b = progress * (0.0 - 6.0) + 6.0;
        return vec4(r / 255.0, g / 255.0, b / 255.0, 1.0);
    } else {
        float progress = (intensity - 0.84) / (1.0 - 0.84);
        float r = progress * (255.0 - 255.0) + 255.0;
        float g = progress * (255.0 - 216.0) + 216.0;
        float b = progress * (255.0 - 0.0) + 0.0;
        return vec4(r / 255.0, g / 255.0, b / 255.0, 1.0);
    }
}


void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;

    float intensity = 1.0-texture(iChannel0, uv).r;
    vec4 bg = vec4(vec3(0.0), 1.0);
    if (colorType == 0) {
        fragColor = vec4(vec3(intensity), 1.0);
    } else if (colorType == 1) {
        fragColor = colorTypeOneWithItensity(intensity);
    } else if (colorType == 2) {
        fragColor = colorTypeTwoWithItensity(intensity);
    } else if (colorType == 3) {
        fragColor = colorTypeThreeWithItensity(intensity);
    } else {
        fragColor = vec4(vec3(intensity), 1.0);
    }
}
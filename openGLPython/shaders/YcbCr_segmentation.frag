#version 420 core
precision mediump float;

layout(binding = 0) uniform sampler2D tex;

in vec2 uv;
out vec4 FragColor;

// ************************************************************************************************
vec3 RGB2YCbCr(vec3 RGB)
{
    float Y = 0.257*RGB.r+0.564*RGB.g+0.098*RGB.b+16.0;
    float Cb = -0.148*RGB.r-0.291*RGB.g+0.439*RGB.b+128.0;
    float Cr = 0.439*RGB.r-0.368*RGB.g-0.071*RGB.b+128.0;
    return vec3(Y, Cb, Cr);
}

vec3 rgb2hsv(vec3 RGB)
{
    float Max = max(max(RGB.r, RGB.g), RGB.b);
    float Min = min(min(RGB.r, RGB.g), RGB.b);
    float V = Max;
    float Delta = Max - Min;
    float S = (Max == 0.0) ? 0.0 : (Delta/Max);
    float H;
    if (Max == RGB.r) {
        H = (RGB.g - RGB.b) / Delta;
    } else if (Max == RGB.g) {
        H = 2.0 + (RGB.b - RGB.r) / Delta;
    } else {
        H = 4.0 + (RGB.r - RGB.g) / Delta;
    }
    H *= 60.0;
    if (H < 0.0) H += 360.0;
    highp vec3 HSV;
    HSV.r = H/2.0;
    HSV.g = S*255.0;
    HSV.b = V*255.0;
    return HSV;
}

float gaussian_cul(float cb_cr, float u, float rou)
{
    float sq = -1.0*pow(cb_cr-u, 2.0) / (2.0*rou);
    float res = pow(2.718281828459045, sq);
    return res;
}

float scaled(float iColor, float Threshold, int pow_rate)
{   
    float up = pow((iColor+Threshold), float(pow_rate)) - pow(Threshold, float(pow_rate));
    float down = up / (pow(1.0+Threshold, float(pow_rate))-pow(Threshold, float(pow_rate)));
    return pow(smoothstep(0.0, 1.0, down), 2.0);
}

// ************************************************************************************************
void main()
{
    highp vec4 textureColor = texture(tex, uv);
    highp vec3 RGB255 = vec3(textureColor.rgb*255.0);
    highp vec3 YCbCr = RGB2YCbCr(RGB255); //0到255
    float Cb = YCbCr.y;
    float Cr = YCbCr.z;

    vec3 result = vec3(0.0);
    if (Cr>=133.0 && Cr<=173.0 && Cb>=77.0 && Cb<=127.0) 
    {
        result.r = 1.0; //textureColor;
    }
    // float dis = sqrt( pow(abs(Cr-153.0),2) + pow(abs(Cb-102.0),2) ); // sqrt(153^2+153^2) - 0  ;  216 - 0
    // dis = 1.0-dis/50.0;
    // result.g = dis;
    float gaussian_cr = gaussian_cul(Cr, 153.0, 140.0);
    float gaussian_cb = gaussian_cul(Cb, 102.0, 216.66);
    result.g = gaussian_cr*gaussian_cb*2.0; // pow(result.g, 2.0);
    result.g = clamp(result.g, 0.0, 1.0);

    // float Threshold = 0.5;
    // int pow_rate = 2;
    // result.g = scaled(result.g, Threshold, pow_rate);
    
    FragColor = vec4(result, 1.0);
}

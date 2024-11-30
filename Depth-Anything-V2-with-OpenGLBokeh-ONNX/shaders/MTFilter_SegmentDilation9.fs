#version 420 core
precision mediump float;

layout(binding = 0) uniform sampler2D tex;
layout(binding = 1) uniform sampler2D s_depth;

in vec2 uv;

out vec4 FragColor;

uniform int iResolution_x;
uniform int iResolution_y;
uniform float focusDis; // 0.0-1.0

#define USE_GAMMA // 使用gamma校正
const float gamma = 4.2;
const float hardness = 0.8; // 0.0-1.0
const float focusScale = 0.1;

float getDistance(sampler2D inTex, vec2 uv)
{
	vec3 rgb = texture(inTex, uv).rgb;
	return rgb.r;
}
float distance_to_interval(float x, float a, float b) {
    if (x >= a && x <= b) {
        return 0.0;
    } else {
        return min(abs(x - a), abs(x - b));
    }
}

float intensity(vec2 p)
{
    return smoothstep(1.0, hardness, distance(p, vec2(0.0)));
}

vec2 ff(vec2 st, float i) {
    return st - st * 1.0/(distance(st, vec2(0.0)) + 1.) * i;
}

vec2 ff2(vec2 st, float i) {
    return st - st * distance(st, vec2(0.0)) * distance(st, vec2(0.0)) * i;
}
vec2 fisheye(vec2 m_uv, float distortion) {
    vec2 dif = (m_uv - vec2(0.5)) * 2.;
    if (distortion >= 0.0) {
        vec2 signal = sign(dif);
        m_uv = signal * ff(abs(dif), distortion/5.0) / 2.0 + vec2(0.5);
    } else {
        m_uv = ff2(dif, -distortion/20.0) / 2.0 + vec2(0.5);
    }
    return m_uv;
}

vec3 blur(sampler2D tex, float size, int res, vec2 uv, float ratio)
{
    float div = 0.0;
    vec3 accumulate = vec3(0.0);
    
    for(int iy = 0; iy < res; iy++)
    {
        float y = (float(iy) / float(res))*2.0 - 1.0;
        for(int ix = 0; ix < res; ix++)
        {
            float x = (float(ix) / float(res))*2.0 - 1.0;
            vec2 p = vec2(x, y);
            float i = intensity(p);
            
            div += i;
			#ifdef USE_GAMMA
            	accumulate += pow(texture(tex, uv+p*size*vec2(1.0, ratio)).rgb, vec3(gamma)) * i;
			#else
				accumulate += texture(tex, uv+p*size*vec2(1.0, ratio)).rgb * i;
			#endif
        }
    }
    #ifdef USE_GAMMA
    	return pow(accumulate / vec3(div), vec3(1.0 / gamma));
	#else
		return accumulate / vec3(div);
	#endif
}


void main()
{
	vec2 m_uv = fisheye(uv, 0.08);

	float centerDepth = 1.0-getDistance(s_depth, m_uv);

	// float near = max(abs(sin(iTime*0.3)) - focusScale, 0.0);
	// float far = min(abs(sin(iTime*0.3)) + focusScale, 1.0);
    float near = focusDis-0.1;
    float far = focusDis+0.15;

	float dis = distance_to_interval(centerDepth, near, far) * 0.016; // 0.0-0.02

    FragColor = vec4(blur(tex, dis, 16, m_uv, float(iResolution_x)/float(iResolution_y)), 1.0);
}



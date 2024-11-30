#iChannel0 "file://D:/OpenGlProject/ShaderToys/ReLens/focusshader/bokenh_preprocess_fs.glsl"
#iChannel1 "file://D:/OpenGlProject/ShaderToys/pic/depth/edit_lens_icon_shape7.png"
#iChannel2 "file://D:/OpenGlProject/ShaderToys/pic/depth/dust/dusty_16.jpg"
#iChannel3 "file://D:/OpenGlProject/ShaderToys/pic/depth/rainbow.png"
#iChannel4 "file://D:/OpenGlProject/ShaderToys/pic/depth/dust/dusty_16.jpg"

#iChannel5 "file://D:/OpenGlProject/ShaderToys/pic/depth/rainbow.png"
#iChannel6 "file://D:/OpenGlProject/ShaderToys/pic/depth/rainbow.png"


#define preprocessedTexture iChannel0
#define sliceTexture        iChannel5 // TODO:待确认
#define slice2Texture       iChannel6 // TODO:待确认
#define shapeTexture        iChannel1
#define dustTexture         iChannel2
#define rainbowTexture      iChannel3
#define grainTexture        iChannel4

// ----------------------------------------------------
// ----- [Start] struct GrainEffectParams [Start] -----
vec2 textureSize = vec2(900.0, 1355.0);
vec2 grainTextureSize = vec2(200.0, 200.0);
float textureScale = 1.0;
float grainHighlights = 0.0;
float grainAmount = 0.1;    // 0.0 - 1.0
float grainSize = 0.1;      // 0.0 - 1.0
float grainRoughness = 0.1; // 0.0 - 1.0
// GrainEffectParams grainParams;
// ----- [End] struct GrainEffectParams [End] -----
// ------------------------------------------------

#define M_PI_F (3.1415926)

// ---------------------------------------------------------------
// ----- [Start] struct MIRBokehWithDepthNode2Params [Start] -----
vec2 viewportSize = vec2(900.0, 1355.0);
vec2 inputPreProcessedTexSize = vec2(900.0, 1355.0);

float performanceRatio = 0.11;
float performance = 0.5;      // 性能模式

int shapeTextureW = 48;
int shapeTextureH = 48;
int dustTextureW = 200;
int dustTextureH = 200;

float sharpStress = 0.0;
float sharpStressTransition = 0.0;

int sliceIndex = 20;
int sliceCount = 21;

float focus = 0.7;
float softFocus = 0.0;
float intensity = 0.5; // default: 0.5
float exponent = 0.5;  // default: 0.5
float highlight = 2.08;
float dispersion = 0.0;

float squeeze = 0.9;     // -1.0 - 1.0 缩放
float rotate = 1.0;      // 0.0 - 1.0 旋转
float smoothing = 0.6;   // 0.0 - 1.0
float bilinear = 0.0;    // 0.0 - 1.0
float distortion = -1.0; // -1.0 - 1.0
float erosion = 0.0;     // -1.0 - 1.0
float field = 0.0;       // 0.0 - 1.0
float offRotate = 0.0;   // 0.0 - 1.0 旋焦
float offRadiate = 0.0;  // 0.0 - 1.0
int shapeType = 0;      // 0, -1, ..., -15
float shapeStar = 1.0;   // 0.0 - 1.0
int dustType = 0;      // -1:开启

int rainbowType = 0;   // -1:开启
int rainbowTextureW = 256;
int rainbowTextureH = 256;

const int useTests = 0;     // 0, 1
int flag = 0;         // 0, 1
int antiOverflow = 0; // 0, 1
int showGrain = 0;    // 0, 1
// MIRBokehWithDepthNode2Params params;
// ----- [End] struct MIRBokehWithDepthNode2Params [End] -----
// -----------------------------------------------------------

const mat2x3 disperse_r = mat2x3(1., 0., 0., 1., 1., 0.);
const mat2x3 disperse_g = mat2x3(0., 1., 0., 1., 0., 1.);
const mat2x3 disperse_b = mat2x3(0., 0., 1., 0., 1., 1.);
lowp mat4 textureMat = mat4(
    1.0, 0.0, 0.0, 0.0,
    0.0, 1.0, 0.0, 0.0, 
    0.0, 0.0, 1.0, 0.0, 
    0.0, 0.0, 0.0, 1.0);


vec3 disperse_color(vec2 st) {
    st = floor(st * 30.0);
    float rand = fract(sin(dot(st, vec2(141.4123, 73.1895))) * 32895.9128387);
    float idx_f = rand * 5.999;
    float idx_r_f = floor(idx_f / 3.0);
    int idx_r = int(idx_r_f);
    int idx_c = int(floor(idx_f - idx_r_f * 3.0));
    return vec3(disperse_r[idx_r][idx_c], disperse_g[idx_r][idx_c], disperse_b[idx_r][idx_c]);
}

mat4 mir_rotate(vec3 axis, float angle) {
    vec3 unitAxis = normalize(axis);
    float ct = cos(angle);
    float st = sin(angle);
    float ci = 1.0 - ct;
    float x = unitAxis.x, y = unitAxis.y, z = unitAxis.z;
    return mat4(ct + x * x * ci, y * x * ci + z * st, z * x * ci - y * st, 0.0,
    x * y * ci - z * st, ct + y * y * ci, z * y * ci + x * st, 0.0,
    x * z * ci + y * st, y * z * ci - x * st, ct + z * z * ci, 0.0,
    0.0, 0.0, 0.0, 1.0
    );
}

vec2 shape(vec2 st, vec2 uvInPixels, vec2 size) {
    vec2 newXy = st;

    // 旋焦
    if (offRotate > 0.0 || offRadiate > 0.0) {
        vec3 axis = vec3(uvInPixels.x, uvInPixels.y, 0.0) - vec3(size.x / 2.0, size.y / 2.0, 0.0);
        vec3 rotateAxis = normalize(vec3(-1.0*(axis.y/abs(axis.y)), axis.x/axis.y*(axis.y/abs(axis.y)), 0.0));
        vec3 radiateAxis = normalize(axis);
        float maxRadian = M_PI_F;
        float dist = distance(axis.xy / size, vec2(0.0));
        float rotateT = maxRadian * offRotate;
        float radiateT = maxRadian * offRadiate;

        vec4 xyzw = vec4(newXy.x, newXy.y, 0.0, 1.0);
        mat4 r = mir_rotate(normalize(rotateAxis*rotateT + radiateAxis*radiateT), min(rotateT+radiateT, maxRadian) * dist);
        vec4 rxyzw = r * xyzw;

        newXy.x = 2.0*newXy.x - rxyzw.x;
        newXy.y = 2.0*newXy.y - rxyzw.y;
    }

    // 旋转
    float theta = 2.0 * M_PI_F * -rotate;// 负 = 逆
    mat2 rotate = mat2(cos(theta), -sin(theta),
    sin(theta), cos(theta)
    );
    vec2 rxy = rotate * newXy;
    newXy.x = rxy.x;
    newXy.y = rxy.y;

    // 缩放
    if (squeeze >= 0.0) {
        newXy.x *= 2.*(squeeze) + 1.;
    } else {
        newXy.y *= 2.*(-squeeze) + 1.;
    }

    return newXy;
}

float m_saturate(float x) {
    return clamp(x, 0.0, 1.0);
}

vec2 ff(vec2 st, float i) {
    return st - st * 1.0/(distance(st, vec2(0.0)) + 1.) * i;
    //    return vec2(st.x / f(st.y, i), st.y / f(st.x, i));
}

vec2 ff2(vec2 st, float i) {
    return st - st * distance(st, vec2(0.0)) * distance(st, vec2(0.0)) * i;
}

vec2 fisheye(vec2 uv, float distortion) {
    vec2 dif = (uv - vec2(0.5)) * 2.;
    if (distortion >= 0.) {
        vec2 signal = sign(dif);
        uv = signal * ff(abs(dif), distortion/5.) / 2. + vec2(0.5);
    } else {
        uv = ff2(dif, -distortion/20.0) / 2. + vec2(0.5);
    }
    return uv;
}

float MIRBokeh_atan2(float y, float x) {
    return x == 0.0 ? sign(y)*3.141593/2.0 : atan(y, x);
}
// 柔边二线性
float MIRBokeh_bilinear(float sd, float smoothing, float bilinear) {
    return smoothstep(-0.001, smoothing*0.9+0.1, sd) * max(pow(1.001-sd, bilinear*4.0), 0.1);
}

float MIRBokeh_sdCircle(vec2 uv, vec2 st, vec2 xy) {
    float dis = distance(xy, vec2(0.0)) / 1.0;
    float sd = 1.0 - dis;
    return sd;
}

float MIRBokeh_sdSmoothCircle(vec2 uv, vec2 st, vec2 xy) {
    float dis = distance(xy, vec2(0.0)) / 1.0;
    float sd = 1.0 - dis;
    return sd;
}

float MIRBokeh_sdHeart(vec2 uv, vec2 st, vec2 xy) {
    vec2 p = xy;
    p.y = p.y;
    p.y += .6;
    const float offset = .3;
    float k = 1.2 * p.y - sqrt(abs(p.x) + offset);
    float sd = -(p.x * p.x + k * k - 1.);
    return sd;
}

float MIRBokeh_sdStar(vec2 uv, vec2 st, vec2 xy) {
    int n = shapeType;
    float m = shapeStar * float(n - 3) + 2.;
    float r = 1.0;
    vec2 p = xy;

    float an = 3.141593/float(n);
    float en = 3.141593/m;
    vec2  acs = vec2(cos(an), sin(an));
    vec2  ecs = vec2(cos(en), sin(en));

    float ss = p.x == 0. ?1. :sign(p.x);
    float bn = mod(MIRBokeh_atan2(p.x, p.y)*ss, 2.0*an) - an;
    p = length(p)*vec2(cos(bn), abs(sin(bn)));

    p -= r*acs;
    p += ecs*clamp(-dot(p, ecs), 0.0, r*acs.y/ecs.y);
    float sd = -length(p)*sign(p.x);
    return sd;
}

float MIRBokeh_sdWaterDrop(vec2 uv, vec2 st, vec2 xy) {
    vec2 p = xy;
    p.y = p.y;
    p.y -= 0.75;
    p = vec2(p.y, p.x);
    float x = p.x;
    float y = p.y;
    float x2 = x*x;
    float y2 = y*y;
    float sd = -(1.2*(x2+y2)*(x2+y2) + 2.*x*(x2+y2) + 6.*y2);
    return sd;
}

float MIRBokeh_sdMoon(vec2 uv, vec2 st, vec2 xy) {
    vec2 p = xy;
    p.y = -p.y;
    float d = -0.7;
    float ra = 1.2;
    float rb = .95;
    p *= 1.3;
    p.y = abs(p.y);

    float a = (ra*ra - rb*rb + d*d)/(2.0*d);
    float b = sqrt(max(ra*ra-a*a, 0.0));
    if (d*(p.x*b-p.y*a) > d*d*max(b-p.y, 0.0))
    {
        return -length(p-vec2(a, b));
    }

    float sd = -max((length(p)-ra),
    -(length(p-vec2(d, 0.))-rb));
    return sd;
}

float MIRBokeh_sdClover(vec2 uv, vec2 st, vec2 xy) {
    vec2 pp = xy;
    pp.y = -pp.y;
    float he = 0.9;
    vec2 pos = pp;
    pos *= 2.0;
    pos = abs(pos);
    pos = vec2(abs(pos.x-pos.y), 1.0-pos.x-pos.y)/sqrt(2.0);

    float p = (he-pos.y-0.25/he)/(6.0*he);
    float q = pos.x/(he*he*16.0);
    float h = q*q - p*p*p;

    float x;
    if (h>0.0) { float r = sqrt(h); x = pow(q+r, 1.0/3.0) - pow(abs(q-r), 1.0/3.0)*sign(r-q); }
    else { float r = sqrt(p); x = 2.0*r*cos(acos(q/(p*r))/3.0); }
    x = min(x, sqrt(2.0)/2.0);

    vec2 z = vec2(x, he*(1.0-2.0*x*x)) - pos;
    float sd = -(length(z) * sign(z.y) - .66);
    return sd;
}

float MIRBokeh_sdFlower(vec2 uv, vec2 st, vec2 xy) {
    vec2 pp = xy;
    pp.y = -pp.y;
    float k1 = 0.0;
    {
        vec2 pos = pp;

        pos *= 2.0;
        pos = abs(pos);
        pos = vec2(abs(pos.x-pos.y), 1.0-pos.x-pos.y)/sqrt(2.0);
        float he = 0.3;

        float p = (he-pos.y-0.25/he)/(6.0*he);
        float q = pos.x/(he*he*16.0);
        float h = q*q - p*p*p;

        float x;
        if (h>0.0) { float r = sqrt(h); x = pow(q+r, 1.0/3.0) - pow(abs(q-r), 1.0/3.0)*sign(r-q); }
        else { float r = sqrt(p); x = 2.0*r*cos(acos(q/(p*r))/3.0); }
        x = min(x, sqrt(2.0)/2.0);

        vec2 z = vec2(x, he*(1.0-2.0*x*x)) - pos;
        k1 = -(length(z) * sign(z.y) - .5);
    }
    float k2 = 0.0;
    {
        float theta = 3.1415926 / 4.;
        vec2 pos = pp * mat2(cos(theta), -sin(theta),
        sin(theta), cos(theta));

        pos *= 2.0;
        pos = abs(pos);
        pos = vec2(abs(pos.x-pos.y), 1.0-pos.x-pos.y)/sqrt(2.0);
        float he = 0.3;

        float p = (he-pos.y-0.25/he)/(6.0*he);
        float q = pos.x/(he*he*16.0);
        float h = q*q - p*p*p;

        float x;
        if (h>0.0) { float r = sqrt(h); x = pow(q+r, 1.0/3.0) - pow(abs(q-r), 1.0/3.0)*sign(r-q); }
        else { float r = sqrt(p); x = 2.0*r*cos(acos(q/(p*r))/3.0); }
        x = min(x, sqrt(2.0)/2.0);

        vec2 z = vec2(x, he*(1.0-2.0*x*x)) - pos;
        k2 = -(length(z) * sign(z.y) - .5);
    }
    float sd = max(k1, k2);
    return sd;
}

float MIRBokeh_sdMusic(vec2 uv, vec2 st, vec2 xy) {
    vec2 p = xy;
    p.y = -p.y;
    float d1;
    {
        float theta = -0.25;
        vec2 pp = (p - vec2(-0.4222, -0.56)) * mat2(cos(theta), -sin(theta), sin(theta), cos(theta));
        d1 = 0.3 - sqrt(pp.x*pp.x/2. + pp.y*pp.y);
    }
    float d2;
    {
        vec2 b = vec2(0.14, 0.66);
        float r = .1;
        vec2 q = abs(p + vec2(.14, -.07))-b+r;
        d2 = -(min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - r);
    }
    float d3;
    {
        float theta = -1.;
        vec2 pp = (p - vec2(.2, .3)) * mat2(cos(theta), -sin(theta), sin(theta), cos(theta));

        vec2 b = vec2(0.12, 0.23);
        float r = .1;
        vec2 q = abs(pp + vec2(.13, -.13))-b+r;
        d3 = -(min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - r);
    }
    float d4;
    {
        vec2 p0 = vec2(0.18, 0.24);
        vec2 p1 = vec2(-0.0, 0.2);
        vec2 p2 = vec2(0.34, 0.02);
        vec2 e0 = p1-p0, e1 = p2-p1, e2 = p0-p2;
        vec2 v0 = p -p0, v1 = p -p1, v2 = p -p2;
        vec2 pq0 = v0 - e0*clamp(dot(v0, e0)/dot(e0, e0), 0.0, 1.0);
        vec2 pq1 = v1 - e1*clamp(dot(v1, e1)/dot(e1, e1), 0.0, 1.0);
        vec2 pq2 = v2 - e2*clamp(dot(v2, e2)/dot(e2, e2), 0.0, 1.0);
        float s = sign(e0.x*e2.y - e0.y*e2.x);
        vec2 d = min(min(vec2(dot(pq0, pq0), s*(v0.x*e0.y-v0.y*e0.x)),
        vec2(dot(pq1, pq1), s*(v1.x*e1.y-v1.y*e1.x))),
        vec2(dot(pq2, pq2), s*(v2.x*e2.y-v2.y*e2.x)));
        d4 = sqrt(d.x)*sign(d.y) + 0.05;
    }
    float d5;
    {
        vec2 p0 = vec2(-0.08, 0.52);
        vec2 p1 = vec2(-0.0, 0.2);
        vec2 p2 = vec2(0.05, 0.3);
        vec2 e0 = p1-p0, e1 = p2-p1, e2 = p0-p2;
        vec2 v0 = p -p0, v1 = p -p1, v2 = p -p2;
        vec2 pq0 = v0 - e0*clamp(dot(v0, e0)/dot(e0, e0), 0.0, 1.0);
        vec2 pq1 = v1 - e1*clamp(dot(v1, e1)/dot(e1, e1), 0.0, 1.0);
        vec2 pq2 = v2 - e2*clamp(dot(v2, e2)/dot(e2, e2), 0.0, 1.0);
        float s = sign(e0.x*e2.y - e0.y*e2.x);
        vec2 d = min(min(vec2(dot(pq0, pq0), s*(v0.x*e0.y-v0.y*e0.x)),
        vec2(dot(pq1, pq1), s*(v1.x*e1.y-v1.y*e1.x))),
        vec2(dot(pq2, pq2), s*(v2.x*e2.y-v2.y*e2.x)));
        d5 = sqrt(d.x)*sign(d.y) + 0.05;
    }
    float sd = max(max(max(max(d1, d2), d3), d4), d5);
    return sd;
}

float MIRBokeh_sdFlower5(vec2 uv, vec2 st, vec2 xy) {
    vec2 p = xy;
    p.y = p.y;
    p *= 1.2;
    const vec2 k1 = vec2(0.809016994375, -0.587785252292);
    const vec2 k2 = vec2(-k1.x, k1.y);
    p.x = abs(p.x);
    p -= 2.0*max(dot(k1, p), 0.0)*k1;
    p -= 2.0*max(dot(k2, p), 0.0)*k2;
    p.x = abs(p.x);
    p.y -= 0.1;
    return -(length(p*vec2(0.8, 0.3)) - 0.3);
}

float MIRBokeh_sdRing(vec2 uv, vec2 st, vec2 xy) {
    vec2 p = xy;
    p.y = -p.y;
    float r2 = 0.95, r1 = 0.7;
    float r = length((r1+r2)/(2.*length(p)) * p - p) - (r2-r1)/2.;
    return -r;
}

float MIRBokeh_sdVesica(vec2 uv, vec2 st, vec2 xy) {
    vec2 p = xy;
    p.y = -p.y;
    float r = 0.95;
    float d = 0.2;
    p = abs(p);
    float b = sqrt(r*r-d*d);
    float ret = ((p.y-b)*d>p.x*b) ? length(p-vec2(0.0, b))
    : length(p-vec2(-d, 0.0))-r;
    return -ret;
}

float MIRBokeh_sdFatPolygon(vec2 uv, vec2 st, vec2 xy, int n, float p1, float p2, float yOffset) {
    vec2 p = xy;
    p.y = -p.y;
    p.y += yOffset;
    float an = 3.141593/float(n);
    float ss = p.x == 0. ?1. :sign(p.x);
    float bn = mod(MIRBokeh_atan2(p.x, p.y)*ss, 2.0*an) - an;
    p = length(p)*vec2(cos(bn), abs(sin(bn)));
    p.y *= p1;
    float ret = length(p) - p2;
    return -ret;
}

float MIRBokeh_sdFatTriangle(vec2 uv, vec2 st, vec2 xy) {
    return MIRBokeh_sdFatPolygon(uv, st, xy, 3, 0.7, 0.8, 0.1);
}

float MIRBokeh_sdFatRectangle(vec2 uv, vec2 st, vec2 xy) {
    return MIRBokeh_sdFatPolygon(uv, st, xy, 4, 0.7, 0.8, 0.0);
}

float MIRBokeh_dot2(vec2 v) { return dot(v, v); }
float MIRBokeh_sdTrapezoid(vec2 p, float r1, float r2, float he) {
    vec2 k1 = vec2(r2, he);
    vec2 k2 = vec2(r2-r1, 2.0*he);

    p.x = abs(p.x);
    vec2 ca = vec2(max(0.0, p.x-((p.y<0.0)?r1:r2)), abs(p.y)-he);
    vec2 cb = p - k1 + k2*clamp(dot(k1-p, k2)/MIRBokeh_dot2(k2), 0.0, 1.0);

    float s = (cb.x < 0.0 && ca.y < 0.0) ? -1.0 : 1.0;

    return s*sqrt(min(MIRBokeh_dot2(ca), MIRBokeh_dot2(cb)));
}

float MIRBokeh_sdDiamond(vec2 uv, vec2 st, vec2 xy) {
    vec2 p = xy;
    p.y = p.y;

    p *= 2.0;
    float d1 = MIRBokeh_sdTrapezoid(p - vec2(0.0, 1.1), 1.65, 0.9, 0.5);
    float d2 = MIRBokeh_sdTrapezoid(p*-1. - vec2(0.0, 0.5), 1.65, 0.0, 1.1);
    float d = min(d1, d2);

    if (d < 0.0 && (abs(p.y - 3.4*abs(p.x) + 1.4) < 0.1 || (p.y > 0.6 && abs(-p.y - 1.7*abs(p.x) + 1.6) < 0.1))) {
        d = -d;
    }
    return -d;
}

vec4 MIRBokeh_lod(sampler2D t, vec2 pos, int textureW, int textureH, int sampleW, int sampleH) {
    float px = float(textureW) / float(sampleW);
    float py = float(textureH) / float(sampleH);
    float lod = max(0.5 * log2(max(px * px, py * py)), 0.0);
    return textureLod(t, pos, lod);
}

float MIRBokeh_sdSample(vec2 uv, vec2 st, vec2 xy, int xyRadius) {
    vec2 pos = xy / 2. + 0.5;
    float sd = MIRBokeh_lod(shapeTexture, pos, shapeTextureW, shapeTextureH, xyRadius*2, xyRadius*2).a;
    return sd;
}

int MIRBokeh_getMaxRaidus(vec2 viewport) {
    float r = (viewport.x > viewport.y ? viewport.x : viewport.y) * 0.04;
    return int(r);
}

int MIRBokeh_calcRadius(int maxRadius, float focus, float depth, float intensity, float field, vec2 uv) {
    float depthDiff = (depth - focus);
    depthDiff = depthDiff > 0.0 ?depthDiff :-depthDiff;
    return int(floor(float(maxRadius) * intensity * depthDiff * (1.0+field*uv.x*uv.x*uv.y*uv.y)));
}

/// Grain
float o(vec3 inputRGB){
    const vec3 b=vec3(.298839, .586811, .11435);
    return dot(inputRGB, b);
}

vec2 P(vec2 a){
    float b=sin(dot(a, vec2(12.9898, 78.233)))*43758.5453;
    return fract(vec2(1.3453, 1.3647)*b)*2.-1.;
}

vec3 N(vec3 b){
    const vec4 d=vec4(0., -1./3., 2./3., -1.);
    vec4 c = vec4(b.gb, d.xy);
    if (b.g<b.b){
        c = vec4(b.bg, d.wz);
    }
    vec4 a = vec4(b.r, c.yzx);
    if (b.r<c.x){
        a = vec4(c.xyw, b.r);
    }
    float e=a.x-min(a.w, a.y);
    return vec3(abs(a.z+(a.w-a.y)/(6.*e+1e-10)), e/(a.x+1e-10), a.x);
}

vec3 F(vec3 b){
    const vec4 a=vec4(1., 2./3., 1./3., 3.);
    vec3 c=abs(fract(b.xxx+a.xyz)*6.-a.www);
    return b.z*mix(a.xxx, clamp(c-a.xxx, 0., 1.), b.y);
}

vec3 E(vec3 b, vec3 c){
    vec3 a = N(b);
    vec3 d = N(c);
    a.x = d.x;
    return clamp(F(a), 0., 1.);
}

vec3 grainBlur(vec3 c, float i, float e, vec2 uTexCoord){
    vec2 realSize = 1. / textureSize * textureScale;
    vec2 fixedValue = realSize * e * 2. - i * realSize;
    vec2 h = P(uTexCoord) * realSize * e;
    vec2 d = (0. + h) * fixedValue;
    vec2 a = (1. + h) * fixedValue;
    vec2 b = (2. + h) * fixedValue;
    vec3 j = c;
    c= .013514*texture(grainTexture, uTexCoord.xy+vec2(-b.x, -b.y)).rgb+.027027*texture(grainTexture, uTexCoord.xy+vec2(-b.x, -a.y)).rgb
    +.040541*texture(grainTexture, uTexCoord.xy+vec2(-b.x, -d.y)).rgb+.027027*texture(grainTexture, uTexCoord.xy+vec2(-b.x, +a.y)).rgb
    +.013514*texture(grainTexture, uTexCoord.xy+vec2(-b.x, +b.y)).rgb+.027027*texture(grainTexture, uTexCoord.xy+vec2(-a.x, -b.y)).rgb
    +.054054*texture(grainTexture, uTexCoord.xy+vec2(-a.x, -a.y)).rgb+.067568*texture(grainTexture, uTexCoord.xy+vec2(-a.x, -d.y)).rgb
    +.054054*texture(grainTexture, uTexCoord.xy+vec2(-a.x, +a.y)).rgb+.027027*texture(grainTexture, uTexCoord.xy+vec2(-a.x, +b.y)).rgb
    +.040541*texture(grainTexture, uTexCoord.xy+vec2(+d.x, -b.y)).rgb+.067568*texture(grainTexture, uTexCoord.xy+vec2(+d.x, -a.y)).rgb
    +.081081*c+.067568*texture(grainTexture, uTexCoord.xy+vec2(+d.x, +a.y)).rgb+.040541*texture(grainTexture, uTexCoord.xy+vec2(+d.x, +b.y)).rgb
    +.027027*texture(grainTexture, uTexCoord.xy+vec2(+a.x, -b.y)).rgb+.054054*texture(grainTexture, uTexCoord.xy+vec2(+a.x, -a.y)).rgb
    +.067568*texture(grainTexture, uTexCoord.xy+vec2(+a.x, -d.y)).rgb+.054054*texture(grainTexture, uTexCoord.xy+vec2(+a.x, +a.y)).rgb
    +.027027*texture(grainTexture, uTexCoord.xy+vec2(+a.x, +b.y)).rgb+.013514*texture(grainTexture, uTexCoord.xy+vec2(+b.x, -b.y)).rgb
    +.027027*texture(grainTexture, uTexCoord.xy+vec2(+b.x, -a.y)).rgb+.040541*texture(grainTexture, uTexCoord.xy+vec2(+b.x, -d.y)).rgb
    +.027027*texture(grainTexture, uTexCoord.xy+vec2(+b.x, +a.y)).rgb+.013514*texture(grainTexture, uTexCoord.xy+vec2(+b.x, +b.y)).rgb;
    c=mix(c, j, (1. + i) * 2. *(1. - e));
    c=clamp(c, 0., 1.);
    c=E(c, j);
    return c;
}

vec3 grain(vec3 inputRGB, float grain_amount, float grain_highlights, float grain_size, float grain_roughness, vec2 grainTextureSize, sampler2D grainTexture, vec2 uTexCoord){
    float l = o(inputRGB);
    float p = grain_amount * (1.0 - grain_highlights);
    float i = mix(grain_amount, p, l);
    vec2 b = uTexCoord.xy * textureSize / grainTextureSize;
    vec2 newXY = b + P(b).xy / grainTextureSize / textureScale / 3.;
    vec4 c = texture(grainTexture, b);
    vec2 g = vec2(mix(c.r / c.a, c.b/ c.a, grain_size), mix(c.g/ c.a, c.a, grain_size));
    float n = mix(g.x, g.y, grain_roughness);
    vec3 j = inputRGB * n * 2.;
    vec3 outputRGB = mix(inputRGB, j, i);
    return outputRGB;
}

vec4 grainBlend(vec4 color, vec2 uTexCoord) {
    vec3 a = color.rgb;
    float f =max(0., (grainSize-.25)/.75)*pow(grainAmount, .25);
    vec3 tex = a;
    if (f != 0.){
        tex = grainBlur(a, 0., f, uTexCoord);
    }
    vec3 gr = grain(tex, grainAmount, grainHighlights, grainSize, grainRoughness, grainTextureSize, grainTexture, uTexCoord);
    vec3 mr = mix(color.rgb, gr, color.a);
    vec4 resultColor = vec4(mr, color.a);
    return resultColor;
}




void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uTexCoord = fragCoord / iResolution.xy;
    //    vec2 size = viewportSize;
    float focus = focus;
    float intensity = intensity;
    bool useTests = useTests == 1;
    bool flag = flag == 1;
    vec2 inputPreProcessedTexSize = inputPreProcessedTexSize;
    vec2 inputTexSize = inputPreProcessedTexSize;
    if (flag) {
        inputTexSize = inputPreProcessedTexSize / performance;
    }

    // textureMat负责将坐标映射到本次图片分块区域内的坐标
    vec2 uv = (textureMat * vec4(uTexCoord, 0.0, 1.0)).xy;
    vec2 uvInPixels = uv * inputTexSize;

    vec4 preprocessColor = texture(preprocessedTexture, uv);

    float depth = preprocessColor.a;

            // // todo: debug code
            // if (depth > 0.1) {
            //     fragColor = texture(preprocessedTexture, uv);
            //     return;
            // }

    int maxRadius = int(0.04 * max(inputTexSize.x, inputTexSize.y));
    int blurRadius = int(floor(float(maxRadius) * intensity * pow(m_saturate(abs(depth - focus)), exponent)
    * (1.+field*distance(uv, vec2(0.5))*distance(uv, vec2(0.5)))));
    if (useTests && !flag && float(blurRadius) <= float(maxRadius)*performanceRatio - 3.0) {
        discard;
    }
    if (useTests && !flag && float(blurRadius) > float(maxRadius)*performanceRatio) {
        discard;
    }

    float factorAmount = 0.0;
    vec3 colorAmount = vec3(0.0);

    // vec3 m_result;

    if (blurRadius > 0) {
        for (int dy = -blurRadius + sliceIndex; dy <= blurRadius; dy+=sliceCount) { // 交换xy顺序
            for (int dx = -blurRadius; dx <= blurRadius; dx++) {
                vec2 xyInPixels = uvInPixels + vec2(float(dx), float(dy));
                vec2 xy = xyInPixels / inputTexSize;
                vec4 color = texture(preprocessedTexture, xy);

                float xyDepth = color.a;
                int xyRadius = int(floor(float(maxRadius) * intensity * pow(m_saturate(abs(xyDepth - focus)), exponent)
                * (1.+field*distance(uv, vec2(0.5))*distance(uv, vec2(0.5)))));
                vec2 st = -vec2(dx, dy) / max(float(xyRadius), 1.);
                vec2 dxy = shape(st, xyInPixels, inputTexSize);

                float sd = 1.0;
                if (shapeType == 0) {
                    sd = MIRBokeh_sdCircle(xy, st, dxy);
                } 
                else if (shapeType == -1) {
                    sd = MIRBokeh_sdSample(xy, st, dxy, xyRadius);
                } else if (shapeType == -2) {
                    sd = MIRBokeh_sdHeart(xy, st, dxy);
                } else if (shapeType == -3) {
                    sd = MIRBokeh_sdWaterDrop(xy, st, dxy);
                } else if (shapeType == -4) {
                    sd = MIRBokeh_sdMoon(xy, st, dxy);
                } else if (shapeType == -5) {
                    sd = MIRBokeh_sdClover(xy, st, dxy);
                } else if (shapeType == -6) {
                    sd = MIRBokeh_sdFlower(xy, st, dxy);
                } else if (shapeType == -7){
                    sd = MIRBokeh_sdSmoothCircle(xy, st, dxy);
                } else if (shapeType == -9){
                    sd = MIRBokeh_sdFlower5(xy, st, dxy);
                } else if (shapeType == -10){
                    sd = MIRBokeh_sdRing(xy, st, dxy);
                } else if (shapeType == -11){
                    sd = MIRBokeh_sdDiamond(xy, st, dxy);
                } else if (shapeType == -12){
                    sd = MIRBokeh_sdVesica(xy, st, dxy);
                } else if (shapeType == -13){
                    sd = MIRBokeh_sdFatTriangle(xy, st, dxy);
                } else if (shapeType == -14){
                    sd = MIRBokeh_sdFatRectangle(xy, st, dxy);
                } else {
                    sd = MIRBokeh_sdStar(xy, st, dxy);
                }

                float sd2 = smoothstep(-0.001, smoothing*0.9+0.1, sd);
                sd2 *= max(pow(1.001-sd, bilinear*4.), 0.1);
                if (shapeType == -7){
                    sd2 *= sd;
                }

                // 口径蚀
                float e = 1.0 - smoothstep(1.414-0.1, 1.414, distance(((xy-0.5)*2.0*1.414*erosion), st));// 1.414 = 根号2
                sd2 *= e;

                //灰尘
                if (dustType == -1){
                    vec4 dustColor = MIRBokeh_lod(dustTexture, (st + 1.0) / 2.0, dustTextureW, dustTextureH, xyRadius*2, xyRadius*2);
                    sd2 *= 1.0 - dustColor.r;
                }

                //边缘强调
                //                sd2 = sd2 * mix(max(pow(2.0-sd2, sharpStress), 1.0), 1.0,
                //                m_saturate(1.0 - (float(xyRadius) / (float(maxRadius) * sharpStressTransition+1e-6))));

                vec3 rgb = color.rgb;
                // m_result = rgb; // TODO
                // 彩虹
                if (rainbowType == -1) {
                    vec3 rainbowColor = MIRBokeh_lod(rainbowTexture, (st + 1.0) / 2.0, rainbowTextureW, rainbowTextureH, xyRadius*2, xyRadius*2).rgb;
                    float rainbowAvg = (rainbowColor.r + rainbowColor.g + rainbowColor.b) * 0.333334;
                    vec3 tmpRgb = rgb * rainbowColor / (rainbowAvg + 0.000001);
                    tmpRgb /= max(1.0, max(tmpRgb.r, max(tmpRgb.g, tmpRgb.b)));
                    rgb = mix(rgb, tmpRgb, smoothstep(0.0, 0.7, sd));
                }
                // 柔焦
                rgb = mix(rgb, mix(preprocessColor.rgb, rgb, smoothstep(0.0, softFocus * 1.25, sd)), softFocus);

                if (sd2 > 0.) {
                    float factor = 1.0/(abs(xyDepth - depth)+0.3) * sd2 * max(1. + dot(vec3(0.3, 0.6, 0.1), rgb)*highlight, 0.01) * 0.001;// 0.01 防止上溢出 下溢出还没管
                    if (antiOverflow == 0) {
                        factor *= 0.01;
                    }
                    factorAmount += factor;
                }
            }
        }
    }
    //        if (sliceIndex > 0) {
    //            vec4 sliceColor = texture(sliceTexture, uTexCoord);
    //            colorAmount += sliceColor.rgb * sliceColor.a;
    //            factorAmount += sliceColor.a;
    //        }
    //
    //        if (factorAmount < 0.01) {
    //            fragColor = vec4(preprocessColor.rgb, 1.0);
    //        } else {
    //            fragColor = vec4(colorAmount / factorAmount, factorAmount);
    //        }

    if (sliceIndex > 0) {
        vec4 c = texture(sliceTexture, uTexCoord);
        colorAmount += c.rgb;
        factorAmount += c.a;
    }


    if (sliceIndex == sliceCount - 1) {
        if (factorAmount < 0.01) {
            fragColor = vec4(preprocessColor.rgb, 1.0);
        } else {
            vec3 tmpColor = colorAmount / factorAmount;
            if (showGrain > 0) {
                fragColor = grainBlend(vec4(tmpColor, 1.0), uTexCoord);
            } else {
                fragColor = vec4(tmpColor, 1.0);
            }
        }
    } else {
        fragColor = vec4(colorAmount, factorAmount);
    }
    // fragColor = vec4(m_result, 1.0);

//    if (antiOverflow == 1) {
//        const float exponent = 16000.0;
//        if (sliceIndex == sliceCount - 1) {
//            if (sliceIndex > 0) {
//                vec4 k = texture(slice2Texture, uv);
//                colorAmount += k.rgb * exponent;
//                factorAmount += k.a * exponent;
//            }
//            if (factorAmount < 0.01) {
//                fragColor = vec4(preprocessColor.rgb, 1.0);
//            } else {
//                vec3 tmpColor = colorAmount / factorAmount;
//                if (showGrain > 0) {
//                    fragColor = grainBlend(vec4(tmpColor, 1.0), uv);
//                } else {
//                    fragColor = vec4(tmpColor, 1.0);
//                }
//            }
//        } else {
//            vec4 ret = vec4(colorAmount, factorAmount);
//            vec4 k = floor(ret / exponent);
//            vec4 residual = ret - k * exponent;
//            fragColor = residual;
//
//            if (sliceIndex > 0) {
//                vec4 prevK = texture(slice2Texture, uv);
//                k += prevK;
//            }
//            fragColor2 = k;
//        }
//    } else {
//        if (sliceIndex == sliceCount - 1) {
//            if (factorAmount < 0.01) {
//                fragColor = vec4(preprocessColor.rgb, 1.0);
//            } else {
//                vec3 tmpColor = colorAmount / factorAmount;
//                if (showGrain > 0) {
//                    fragColor = grainBlend(vec4(tmpColor, 1.0), uv);
//                } else {
//                    fragColor = vec4(tmpColor, 1.0);
//                }
//            }
//        } else {
//            vec4 ret = vec4(colorAmount, factorAmount);
//            fragColor = ret;
//        }
//    }

//    fragColor = texture(iChannel0, uTexCoord);
}

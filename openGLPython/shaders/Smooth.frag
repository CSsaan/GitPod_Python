#version 420 core
precision mediump float;
layout(binding = 0) uniform sampler2D s_texture;
layout(binding = 1) uniform sampler2D s_textureBlur;
layout(binding = 2) uniform sampler2D s_textureMask;

in vec2 uv;
out vec4 FragColor;

uniform float intensity;
uniform vec2 windowSize;
uniform float blurCoefficient;
uniform float sharpenStrength;

// **********************************************************
float computeBlendRatio(float inColor, float blurColor) {
    float minColor = min(inColor, blurColor - 0.1);
    float adjustedColor = minColor - 0.2;
    return clamp(adjustedColor * 4.0, 0.0, 1.0);
}

vec3 calculateSharpen(vec3 inColor, float flag) {
	vec3 lowerBound = max(vec3(0.0), inColor);
	vec3 upperBound = min(vec3(1.0), inColor);
	return mix(lowerBound, upperBound, flag);
}


// **********************************************************
void main()
{   
    vec2 o_texcoord = vec2(uv.x, 1.0-uv.y);
    vec4 inColor = texture(s_texture, o_texcoord);
    lowp vec4 blurColor = texture(s_textureBlur, o_texcoord);
    vec4 maskColor = texture(s_textureMask, o_texcoord);

    // varianceColor
    highp vec3 squaredDiff = (inColor.rgb - blurColor.rgb) * 7.07;
    squaredDiff = min(squaredDiff * squaredDiff, 1.0);
    lowp vec4 varianceColor = vec4(squaredDiff, 1.0);
    varianceColor = (inColor - blurColor) * (inColor - blurColor); // 高频图

    const float threshold = 0.1;
    mediump float blendRatio = computeBlendRatio(inColor.r, blurColor.r); // R通道. 在模糊图基础上,保留黑色毛发边缘
    mediump float meanVariance = dot(varianceColor.rgb, vec3(0.33333));
    mediump float minCoefficient = (1.0 - meanVariance / (meanVariance + threshold)) * blendRatio * blurCoefficient; // 磨皮强度
    lowp vec3 finalColor = mix(inColor.rgb, blurColor.rgb, minCoefficient); 

    // finalColor's sharpen
    mediump float sum_gaussian = 0.25 * inColor.g;
    vec2 texOffset = vec2(0.5 / windowSize.x, 0.5 / windowSize.y);
    sum_gaussian += 0.125 *texture(s_texture, o_texcoord - vec2(texOffset.x, 0.0)).g;
    sum_gaussian += 0.125 *texture(s_texture, o_texcoord + vec2(texOffset.x, 0.0)).g;
    sum_gaussian += 0.125 *texture(s_texture, o_texcoord - vec2(0.0, texOffset.y)).g;
    sum_gaussian += 0.125 *texture(s_texture, o_texcoord + vec2(0.0, texOffset.y)).g;
    sum_gaussian += 0.0625*texture(s_texture, o_texcoord + vec2(texOffset.x, texOffset.y)).g;
    sum_gaussian += 0.0625*texture(s_texture, o_texcoord - vec2(texOffset.x, texOffset.y)).g;
    sum_gaussian += 0.0625*texture(s_texture, o_texcoord + vec2(-texOffset.x, texOffset.y)).g;
    sum_gaussian += 0.0625*texture(s_texture, o_texcoord + vec2(texOffset.x, -texOffset.y)).g;

    float highPassValue = inColor.g - sum_gaussian + 0.5;
    float thresholdFlag = step(0.5, highPassValue);
    vec3 sharpenColor = calculateSharpen((2.0 * highPassValue + finalColor - 1.0), thresholdFlag);
    vec3 result = mix(finalColor.rgb, sharpenColor.rgb, sharpenStrength);

    result = mix(inColor.rgb, result, maskColor.rgb * intensity);

    FragColor  = vec4(vec3(result).rgb, inColor.a);
}









// #version 420 core
// precision mediump float;
// layout(binding = 0) uniform sampler2D s_texture;
// in vec2 uv;
// //in float kernelValue[ksize*ksize];
// //in vec2 blurCoordinates[ksize*ksize];
// //*标准差 Location & Color*
// // float sigmaA = 10.0;
// // float sigmaL = 0.1;
// uniform float intensity;
// uniform float blurCoefficient;
// const int ksize = 5;
// //float sigmaS = 80.0; //*色彩空间的标准方差(磨皮程度)：越大越磨皮。   较大的参数值意味着像素邻域内较远的颜色会混合在一起。*
// //float sigmaL = 1.0;  //*坐标空间的标准方差：一般尽可能小。          参数值越大，越远的像素都会相互影响。边缘会模糊。*
// #define EPS 1e-5     //*最小限定值*
// #define sigmaA intensity*20.0
// #define sigmaL blurCoefficient*0.1

// out vec4 out_color;

// // *YUV转RGB*
// vec3 YUV2RGB(vec2 Coord)
// {
//     return texture(s_texture, Coord).rgb;
// }

// // *****************************  法一:暴力全域计算法  ***************************************************
// //void main()
// //{
// //    // *标准差 值限定不为0*
// //    float sigS = max(sigmaS, EPS); //正态高斯 标准差
// //    float sigL = max(sigmaL, EPS); //频域高斯 标准差
// //    // *负2倍标准差分之一*
// //    float facS = -1.0/(2.0*sigS*sigS);
// //    float facL = -1.0/(2.0*sigL*sigL);
// //
// //    vec3 sumC = vec3(0.0); //（双边滤波分子部分）像素值 乘以 双高斯权重的累加
// //    float sumW = 0.0;        //（双边滤波分母部分）双高斯权重的累加
// //
// //    float halfSize = sigS * 2.0;
// ////    vec2 textureSize2 = textureSize(y_samp,0); //纹理大小
// //    vec2 textureSize2 = img_size; //纹理大小
// //
// //    float L = length(YUV2RGB(TexCoord)); //当前点像素length值
// //
// //    // *对所有像素进行处理*
// //    for(float i=-halfSize; i<=halfSize; i++)
// //    {
// //        for(float j=-halfSize; j<=halfSize; j++)
// //        {
// //            ivec2 pos = ivec2(i,j); //当前像素位置
// //            vec2 posfloat = vec2(i,j);
// //
// //            vec2 offpos = vec2(posfloat/textureSize2);
// //            vec3 offsetColor = YUV2RGB(TexCoord+offpos); //临近位置像素
// //
// //            float distS = length(posfloat); //正态分布只与距离有关
// //            float distL = length(offsetColor)-L; //频域高斯分布与周围像素值有关。频域像素相近度：偏移点length-当前点length
// //
// //            float wS = exp(facS*(distS*distS)); //正态高斯权重
// //            float wL = exp(facL*(distL*distL)); //频域高斯权重
// //            float w = wS * wL; //正态分布 * 频域分布
// //
// //            sumC += offsetColor*w; //分子部分
// //            sumW += w;             //分母部分
// //        }
// //    }
// //
// //    out_color  = vec4(sumC,1.0)/sumW;
// //}


// // *****************************  法二:固定高斯正态分布内核模板  ****************************************
// // *textureCoordinate(纹理坐标TexCoord)   blurCoordinates(高斯核) distanceNormalizationFactor(差值量化因子)*
// void main()
// {
//     vec2 TexCoord = vec2(uv.x, 1.0-uv.y);
// //    float ksizeSigmaA = sigmaA/10.0; //*缩小比例*
//     float ksizeSigmaA = (2.0*sigmaA/10.0+1.0);
//     vec2 blurCoordinates[ksize*ksize];
//     //新方法
//     int multiplier = 0;
//     vec2 blurStep;
//     int k = 0;       //*核数*
//     for (int i = 0; i<ksize; i++) //*每行*
//     {
//         float multiplierHang = float(i - ((ksize-1)/2)); //-3,-2,-1, 0, 1, 2, 3
//         for(int j = 0; j<ksize; j++)
//         {
//             float multiplierLie = float(j - ((ksize-1)/2));
//             blurStep = vec2(multiplierHang*(ksizeSigmaA/1080.0), multiplierLie*(ksizeSigmaA/1920.0));
//             blurCoordinates[k] = TexCoord + blurStep;
//             k = k+1;
//         }
//     }



//     // *标准差 值限定不为0*
//     float sigS = max(sigmaA, EPS); //正态高斯 标准差
//     float sigL = max(sigmaL, EPS); //频域高斯 标准差

//     lowp vec4 centralColor;          //*输入中心点像素值*
//     lowp float gaussianWeightTotal;  //*高斯权重集合*
//     lowp vec4 sampleSum;             //*卷积和*
// //    lowp vec4 sampleColor;           //*采样点像素值*
// //    lowp float gaussianWeight;       //*采样点高斯权重*
// //    lowp float distanceFromCentralColor; //*1-的颜色权重*
// //    lowp float distanceNormalizationFactor = 0.01; //*差值量化因子0.05-0.2，越大保边越强*

//     // *初始化*
//     gaussianWeightTotal = 0.0;//*高斯权重*
//     sampleSum = vec4(0.0);  //*分子部分*

//     centralColor = vec4(YUV2RGB(blurCoordinates[((ksize*ksize)/2)-1]), 1.0); //中心像素点
//     float Len = length(centralColor.rgb); //当前点像素length值
//     float facL = -1.0/(2.0*0.1*0.1);

//     for(int i=0;i<ksize*ksize;i++)
//     {
// //        sampleColor = vec4(YUV2RGB(blurCoordinates[i]), 1.0); //*采样像素值*
// //        distanceFromCentralColor = min(distance(centralColor, sampleColor) * distanceNormalizationFactor, 1.0); //*颜色核权重*
// //        gaussianWeight = kernelValue[0] * (1.0 - distanceFromCentralColor); //*正态分布权重*颜色分布权重*
// //        gaussianWeightTotal += gaussianWeight; //*(分母部分)权重累加和*
// //        sampleSum += sampleColor * gaussianWeight; //*(分子部分)采样像素值*高斯权重*

//         vec2 pos = TexCoord; //*当前像素位置*
//         vec4 offsetColor = vec4(YUV2RGB(blurCoordinates[i]), 1.0); //*临近位置像素*
//         float distS = length(pos); //*频域高斯分布。频域像素相近度：偏移点length-当前点length*
//         float distL = length(offsetColor.rgb)-Len; //*正态分布*

//         float wS = exp(-1.0/(2.0*sigS*sigS)*float(distS*distS)); //*频域高斯权重(越小边缘越清晰)*
//         float wL = exp(-1.0/(2.0*sigL*sigL)*float(distL*distL)); //*正态高斯权重*
//         float w = wS * wL; //*频域分布 * 正态分布*

//         sampleSum += offsetColor*w; //*分子部分*
//         gaussianWeightTotal += w;   //*分母部分*
//     }
//     out_color = sampleSum / gaussianWeightTotal;
// }










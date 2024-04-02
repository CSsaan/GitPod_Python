//Convolution.cl
__kernel void kernel(__global const* srcImage,
	__global unsigned* const img_h,
	__global unsigned* const img_w,
	__global const* retResult,
	sampler_t sampler)
{

	// Gaussian Kernel is:
	// 1  2  1
	// 2  4  2
	// 1  2  1
	float kernelWeights[9] = { 1.0f, 2.0f, 1.0f,
							   2.0f, 4.0f, 2.0f,
							   1.0f, 2.0f, 1.0f };

	int2 startImageCoord = (int2) (get_global_id(0) - 1, get_global_id(1) - 1);
	int2 endImageCoord = (int2) (get_global_id(0) + 1, get_global_id(1) + 1);
	int2 outImageCoord = (int2) (get_global_id(0), get_global_id(1));

	if (outImageCoord.x < img_w && outImageCoord.y < img_h)
	{
		int weight = 0;
		float4 outColor = (float4)(0.0f, 0.0f, 0.0f, 0.0f);
		for (int y = startImageCoord.y; y <= endImageCoord.y; y++)
		{
			for (int x = startImageCoord.x; x <= endImageCoord.x; x++)
			{
				outColor += (read_imagef(srcImage, sampler, (int2)(x, y)) * (kernelWeights[weight] / 16.0f));
				weight += 1;
			}
		}

		//写入输出图像
		//write_imagef(dstImg, outImageCoord, outColor);//正常的高斯模糊后的图像
		write_imagef(retResult, outImageCoord, (float4)(1.0f, outColor.yzw));//二次处理
	}
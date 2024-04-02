//Convolution.cl
__kernel void kernel_greenMatting(__global unsigned char* srcImage,
	__global unsigned* const img_h,
	__global unsigned* const img_w,
	__global unsigned char* retResult)
{

	const int x = get_global_id(0);
	const int y = get_global_id(1);
	float green_strenth = 0.9;

	int height = *img_h;
	int width = *img_w;

	if (x < width && y < height)
	{
		int Index = y * width + x;
		//RB平均值
		float rbAverage = 0.5f * srcImage[Index * 3 + 0] + 0.5f * srcImage[Index * 3 + 2];
		//G与其的差值
		float gDelta = (srcImage[Index * 3 + 1] * (0.45f * green_strenth + 0.55f) - rbAverage)/255.0f;
		float alpha = 1.0f - smoothstep(0.0f, 0.25f, gDelta);


		//float gray = 0.299f * srcImage[Index * 3 + 0] + 0.587f * srcImage[Index * 3 + 1] + 0.114f * srcImage[Index * 3 + 2];
		retResult[Index * 3 + 0] = srcImage[Index * 3 + 0] * alpha;
		retResult[Index * 3 + 1] = srcImage[Index * 3 + 1] * alpha;
		retResult[Index * 3 + 2] = srcImage[Index * 3 + 2] * alpha + 255.0*(1.0f-alpha);
	}

}
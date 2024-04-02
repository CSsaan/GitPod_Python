//RGB2Gray.cl
__kernel void kernel_rgb2gray(__global unsigned char* srcImage,
	__global unsigned* const img_h,
	__global unsigned* const img_w,
	__global unsigned char* retResult)
{

	const int x = get_global_id(0);
	const int y = get_global_id(1);
	//printf("STEP_GLOBAL_ID global_id_0:[%d] global_id_1:[%d]\n", x, y);
	int height = *img_h;
	int width = *img_w;

	if (x < width && y < height)
	{
		int Index = y * width + x;
		retResult[Index] = 0.299f * srcImage[Index * 3 + 0] +
			0.587f * srcImage[Index * 3 + 1] +
			0.114f * srcImage[Index * 3 + 2];
	}

}
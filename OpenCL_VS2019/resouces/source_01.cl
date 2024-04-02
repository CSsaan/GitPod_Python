//Convolution.cl
__kernel void convolve(const __global uint* const input, __constant uint* const mask, __global uint* const output)
{
	const int x = get_global_id(0);
	const int y = get_global_id(1);

	uint sum = 0;
	for (int r = 0; r < 3; r++)
	{
		const int idxIntmp = (y + r) * 6 + x;
		for (int c = 0; c < 3; c++)
		{
			sum += mask[(r * 3) + c] * input[idxIntmp + c];
		}
	}
	output[y * get_global_size(0) + x] = sum;

	/*int k = 0;
	for (int r = 0; r < 8; r++)
	{
		for (int c = 0; c < 8; c++)
		{
			output[k] = input[k] + 1;
			k += 1;
		}
	}*/
}
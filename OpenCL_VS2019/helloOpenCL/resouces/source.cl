__kernel void test(__global const *host_vector1, __global const *host_vector2, __global int *result)
{
	int index = get_global_id(0);
	result[index] = host_vector1[index]+host_vector2[index];
	
}
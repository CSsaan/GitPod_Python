#include <iostream>
#include <fstream>
#include <sstream>
#include <string.h>

#ifdef __APPLE__
#include <OpenCL/cl.h>
#else
#include <CL/cl.h>
#endif

#include <FreeImage.h>

//在第一个平台中创建只包括GPU的上下文
cl_context CreateContext()
{
	cl_int errNum;
	cl_uint numPlatforms;
	cl_platform_id firstPlatformId;
	cl_context context = NULL;

	// 选择第一个平台
	errNum = clGetPlatformIDs(1, &firstPlatformId, &numPlatforms);
	if (errNum != CL_SUCCESS || numPlatforms <= 0)
	{
		std::cerr << "Failed to find any OpenCL platforms." << std::endl;
		return NULL;
	}

	// 接下来尝试通过GPU设备建立上下文
	cl_context_properties contextProperties[] =
	{
		CL_CONTEXT_PLATFORM,
		(cl_context_properties)firstPlatformId,
		0
	};
	context = clCreateContextFromType(contextProperties, CL_DEVICE_TYPE_GPU,
		NULL, NULL, &errNum);
	if (errNum != CL_SUCCESS)
	{
		std::cout << "Could not create GPU context, trying CPU..." << std::endl;
		context = clCreateContextFromType(contextProperties, CL_DEVICE_TYPE_CPU,
			NULL, NULL, &errNum);
		if (errNum != CL_SUCCESS)
		{
			std::cerr << "Failed to create an OpenCL GPU or CPU context." << std::endl;
			return NULL;
		}
	}

	return context;
}

//在第一个设备上创建命令队列
cl_command_queue CreateCommandQueue(cl_context context, cl_device_id* device)
{
	cl_int errNum;
	cl_device_id* devices;
	cl_command_queue commandQueue = NULL;
	size_t deviceBufferSize = -1;

	// 首先获得设备的信息
	errNum = clGetContextInfo(context, CL_CONTEXT_DEVICES, 0, NULL, &deviceBufferSize);
	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Failed call to clGetContextInfo(...,GL_CONTEXT_DEVICES,...)";
		return NULL;
	}

	if (deviceBufferSize <= 0)
	{
		std::cerr << "No devices available.";
		return NULL;
	}

	//为设备分配内存
	devices = new cl_device_id[deviceBufferSize / sizeof(cl_device_id)];
	errNum = clGetContextInfo(context, CL_CONTEXT_DEVICES, deviceBufferSize, devices, NULL);
	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Failed to get device IDs";
		return NULL;
	}

	// 选择第一个设备并为其创建命令队列
	commandQueue = clCreateCommandQueue(context, devices[0], 0, NULL);
	if (commandQueue == NULL)
	{
		std::cerr << "Failed to create commandQueue for device 0";
		return NULL;
	}

	//释放信息
	*device = devices[0];
	delete[] devices;
	return commandQueue;
}

//  创建OpenCL程序对象
cl_program CreateProgram(cl_context context, cl_device_id device, const char* fileName)
{
	cl_int errNum;
	cl_program program;

	std::ifstream kernelFile(fileName, std::ios::in);
	if (!kernelFile.is_open())
	{
		std::cerr << "Failed to open file for reading: " << fileName << std::endl;
		return NULL;
	}

	std::ostringstream oss;
	oss << kernelFile.rdbuf();

	std::string srcStdStr = oss.str();
	const char* srcStr = srcStdStr.c_str();
	program = clCreateProgramWithSource(context, 1,
		(const char**)&srcStr,
		NULL, NULL);
	if (program == NULL)
	{
		std::cerr << "Failed to create CL program from source." << std::endl;
		return NULL;
	}

	errNum = clBuildProgram(program, 0, NULL, NULL, NULL, NULL);
	if (errNum != CL_SUCCESS)
	{
		// 输出错误信息
		char buildLog[16384];
		clGetProgramBuildInfo(program, device, CL_PROGRAM_BUILD_LOG,
			sizeof(buildLog), buildLog, NULL);

		std::cerr << "Error in kernel: " << std::endl;
		std::cerr << buildLog;
		clReleaseProgram(program);
		return NULL;
	}

	return program;
}


//清除资源
void Cleanup(cl_context context, cl_command_queue commandQueue,
	cl_program program, cl_kernel kernel, cl_mem imageObjects[2],
	cl_sampler sampler)
{
	for (int i = 0; i < 2; i++)
	{
		if (imageObjects[i] != 0)
			clReleaseMemObject(imageObjects[i]);
	}
	if (commandQueue != 0)
		clReleaseCommandQueue(commandQueue);

	if (kernel != 0)
		clReleaseKernel(kernel);

	if (program != 0)
		clReleaseProgram(program);

	if (sampler != 0)
		clReleaseSampler(sampler);

	if (context != 0)
		clReleaseContext(context);

}

///加载图像
cl_mem LoadImage(cl_context context, char* fileName, int& width, int& height)
{
	FREE_IMAGE_FORMAT format = FreeImage_GetFileType(fileName, 0);
	FIBITMAP* image = FreeImage_Load(format, fileName);

	// 转变为32位
	FIBITMAP* temp = image;
	image = FreeImage_ConvertTo32Bits(image);
	FreeImage_Unload(temp);

	width = FreeImage_GetWidth(image);
	height = FreeImage_GetHeight(image);

	char* buffer = new char[width * height * 4];
	memcpy(buffer, FreeImage_GetBits(image), width * height * 4);

	FreeImage_Unload(image);

	// 创建OpenCL图像对象
	cl_image_format clImageFormat;//图像格式属性
	clImageFormat.image_channel_order = CL_RGBA;
	clImageFormat.image_channel_data_type = CL_UNORM_INT8;

	cl_int errNum;
	cl_mem clImage;
	clImage = clCreateImage2D(context,
		CL_MEM_READ_ONLY | CL_MEM_COPY_HOST_PTR,
		&clImageFormat,
		width,
		height,
		0,
		buffer,
		&errNum);

	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Error creating CL image object" << std::endl;
		return 0;
	}

	return clImage;
}

//  利用freeimage库保存一张图片
//
bool SaveImage(char* fileName, char* buffer, int width, int height)
{
	FREE_IMAGE_FORMAT format = FreeImage_GetFIFFromFilename(fileName);
	FIBITMAP* image = FreeImage_ConvertFromRawBits((BYTE*)buffer, width,
		height, width * 4, 32,
		0xFF000000, 0x00FF0000, 0x0000FF00);
	return (FreeImage_Save(format, image, fileName) == TRUE) ? true : false;
}

//获取最接近的倍数
size_t RoundUp(int groupSize, int globalSize)
{
	int r = globalSize % groupSize;
	if (r == 0)
	{
		return globalSize;
	}
	else
	{
		return globalSize + groupSize - r;
	}
}


int main()
{
	cl_context context = 0;
	cl_command_queue commandQueue = 0;
	cl_program program = 0;
	cl_device_id device = 0;
	cl_kernel kernel = 0;
	cl_mem imageObjects[2] = { 0, 0 };
	cl_sampler sampler = 0;
	cl_int errNum;




	// 创建上下文
	context = CreateContext();
	if (context == NULL)
	{
		std::cerr << "Failed to create OpenCL context." << std::endl;
		return 1;
	}

	// 创建命令队列
	commandQueue = CreateCommandQueue(context, &device);
	if (commandQueue == NULL)
	{
		Cleanup(context, commandQueue, program, kernel, imageObjects, sampler);
		return 1;
	}

	// 确保设备支持这种图像格式
	cl_bool imageSupport = CL_FALSE;
	clGetDeviceInfo(device, CL_DEVICE_IMAGE_SUPPORT, sizeof(cl_bool),
		&imageSupport, NULL);
	if (imageSupport != CL_TRUE)
	{
		std::cerr << "OpenCL device does not support images." << std::endl;
		Cleanup(context, commandQueue, program, kernel, imageObjects, sampler);
		return 1;
	}

	// 加载图像
	int width, height;
	imageObjects[0] = LoadImage(context, "123.png", width, height);
	if (imageObjects[0] == 0)
	{
		std::cerr << "Error loading: " << std::string("123.png") << std::endl;
		Cleanup(context, commandQueue, program, kernel, imageObjects, sampler);
		return 1;
	}

	// 创建输出的图像对象
	cl_image_format clImageFormat;
	clImageFormat.image_channel_order = CL_RGBA;
	clImageFormat.image_channel_data_type = CL_UNORM_INT8;
	imageObjects[1] = clCreateImage2D(context,
		CL_MEM_WRITE_ONLY,
		&clImageFormat,
		width,
		height,
		0,
		NULL,
		&errNum);

	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Error creating CL output image object." << std::endl;
		Cleanup(context, commandQueue, program, kernel, imageObjects, sampler);
		return 1;
	}


	// 创建采样器对象
	sampler = clCreateSampler(context,
		CL_FALSE, // 非规范化坐标
		CL_ADDRESS_CLAMP_TO_EDGE,
		CL_FILTER_NEAREST,
		&errNum);

	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Error creating CL sampler object." << std::endl;
		Cleanup(context, commandQueue, program, kernel, imageObjects, sampler);
		return 1;
	}

	// 创建OpenCL程序对象
	program = CreateProgram(context, device, "ImageFilter2D.cl");
	if (program == NULL)
	{
		Cleanup(context, commandQueue, program, kernel, imageObjects, sampler);
		return 1;
	}

	// 创建OpenCL核
	kernel = clCreateKernel(program, "gaussian_filter", NULL);
	if (kernel == NULL)
	{
		std::cerr << "Failed to create kernel" << std::endl;
		Cleanup(context, commandQueue, program, kernel, imageObjects, sampler);
		return 1;
	}

	// 设定参数
	errNum = clSetKernelArg(kernel, 0, sizeof(cl_mem), &imageObjects[0]);
	errNum |= clSetKernelArg(kernel, 1, sizeof(cl_mem), &imageObjects[1]);
	errNum |= clSetKernelArg(kernel, 2, sizeof(cl_sampler), &sampler);
	errNum |= clSetKernelArg(kernel, 3, sizeof(cl_int), &width);
	errNum |= clSetKernelArg(kernel, 4, sizeof(cl_int), &height);
	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Error setting kernel arguments." << std::endl;
		Cleanup(context, commandQueue, program, kernel, imageObjects, sampler);
		return 1;
	}

	size_t localWorkSize[2] = { 16, 16 };
	size_t globalWorkSize[2] = { RoundUp(localWorkSize[0], width),
								  RoundUp(localWorkSize[1], height) };

	// 将内核排队
	errNum = clEnqueueNDRangeKernel(commandQueue, kernel, 2, NULL,
		globalWorkSize, localWorkSize,
		0, NULL, NULL);
	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Error queuing kernel for execution." << std::endl;
		Cleanup(context, commandQueue, program, kernel, imageObjects, sampler);
		return 1;
	}

	// 将输出缓冲区读回主机
	char* buffer = new char[width * height * 4];
	size_t origin[3] = { 0, 0, 0 };
	size_t region[3] = { size_t(width), size_t(height), 1 };
	errNum = clEnqueueReadImage(commandQueue, imageObjects[1], CL_TRUE,
		origin, region, 0, 0, buffer,
		0, NULL, NULL);
	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Error reading result buffer." << std::endl;
		Cleanup(context, commandQueue, program, kernel, imageObjects, sampler);
		return 1;
	}

	std::cout << std::endl;
	std::cout << "Executed program succesfully." << std::endl;

	//保存输出图像
	if (!SaveImage("456.png", buffer, width, height))
	{
		std::cerr << "Error writing output image: " << "456.png" << std::endl;
		Cleanup(context, commandQueue, program, kernel, imageObjects, sampler);
		delete[] buffer;
		return 1;
	}

	delete[] buffer;
	Cleanup(context, commandQueue, program, kernel, imageObjects, sampler);
	return 0;
}
/*C///////////////////////////////////////////////////////////////////////////////////////
//                           OPENCL EXAMPLE
//
//该文件代码主要是OpenCL的例程，任务是完成两个相同长度的数组/vector对应元素相加，并从相应Device
//读取计算的结果并打印。
//
//S*/

#ifndef _CRT_SECURE_NO_WARNINGS
#define _CRT_SECURE_NO_WARNINGS
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string>

#include <fstream>
#include <sstream>

#include <iostream>
#include <vector>
using namespace std;

#ifdef __APPLE__
#include <OpenCL/opencl.h>
#else
#include <CL/cl.h>
#endif

#include<opencv2/opencv.hpp>
#include <opencv2/highgui.hpp>
using namespace cv;

/*******************************************************************************/
/*******************************************************************************/
#define IMG_DIR "../resouces/03.jpg"
#define KERNEL_DIR "../resouces/source_04.cl"
#define KERNEL_FUNCTION_NAME "kernel"

/************ 函数定义 *************************************************************/
/**
* brief 初始化申请的指针内存空间的数组，值设为索引下标
* @param *buf 待初始化的指针
* @param len 数组长度
*/
void init_buf(int* buf, int len)
{
	for (int i = 0; i < len; i++)
	{
		buf[i] = i + 1;
	}
}

/**
* brief 初始化申请的vector，值设为索引下标
* @param *buf 待初始化的指针
* @param len 数组长度
*/
void init_vector(std::vector<int>& buf, int len)
{
	for (int i = 0; i < len; i++)
	{
		buf[i] = i + 1;
	}
}

/**
* brief 从文件中读取kernel代码
* @param codeFilePath 文件路径
* @return 代码string字符串（进一步.c_str()转成const char*）
*/
string loadCodeFromFile(const char* codeFilePath)
{
	// 1. 从文件路径中获取文件
	std::string kernelCode;
	std::ifstream kernelFile;
	// 保证ifstream对象可以抛出异常:
	kernelFile.exceptions(std::ifstream::failbit | std::ifstream::badbit);
	try
	{
		// 打开文件
		kernelFile.open(codeFilePath);
		std::stringstream kernelStream;
		// 读取文件的缓冲内容到数据流中
		kernelStream << kernelFile.rdbuf();
		// 关闭文件处理器
		kernelFile.close();
		// 转换数据流到string
		kernelCode = kernelStream.str();
	}
	catch (std::ifstream::failure& e)
	{
		std::cout << "[" << codeFilePath << "]" << endl;
		std::cout << "[" << __FILE__ << "]:" << "[" << __LINE__ << "]:" << "ERROR::加载读取文件失败: " << e.what() << std::endl;
	}
	//char* kernelSource = kernelCode.c_str();
	return kernelCode;
}

/**
* brief 检测返回句柄是否错误
* @param err 返回的句柄
* @param name 自己命名的代码段的名字
*/
inline void checkErr(cl_int err, const char* name)
{
	if (err != CL_SUCCESS)
	{
		std::cerr << "ERROR: " << name << "失败！" << " (" << err << ")" << std::endl;
		exit(EXIT_FAILURE);
	}
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
		return globalSize + (int)groupSize - r;
	}
}

/************ mian()函数 *************************************************************/
int main()
{
	cl_int ret, ret2, ret3, retResult, retSampler;
	/*******************************************************************************/
	/** step1: 获取平台platform (中餐厅、西餐厅？)  */
	/*******************************************************************************/
	cout << "[1.]开始‘获取platform’" << endl;
	/* 获取platform数量 */
	cl_uint num_platforms; //初始化platform数
	ret = clGetPlatformIDs(0, NULL, &num_platforms); //获取platform数(返回成功与否)
	if ((CL_SUCCESS != ret) || (num_platforms < 1))
	{
		cout << "获取platform数量失败！" << endl;
		return -1;
	}
	/* 获取platform id */
	cl_platform_id platform_id = NULL; //初始化platform id
	ret = clGetPlatformIDs(1, &platform_id, NULL); //获取platform id
	if (CL_SUCCESS != ret)
	{
		cout << "获取platform id失败！" << endl;
		return -1;
	}

	/*******************************************************************************/
	/** step2: 获取Device (哪件厨房？)  */
	/*******************************************************************************/
	cout << "[2.]开始‘获取Device’" << endl;
	/* 获取Device数量 */
	cl_uint num_devices;
	ret = clGetDeviceIDs(platform_id, CL_DEVICE_TYPE_GPU, 0, NULL, &num_devices);
	if ((CL_SUCCESS != ret) || (num_devices < 1))
	{
		cout << "获取Device数量失败！" << endl;
		return -1;
	}
	/* 获取Device id */
	cl_device_id device_id = NULL;
	ret = clGetDeviceIDs(platform_id, CL_DEVICE_TYPE_GPU, 1, &device_id, NULL);
	checkErr(ret, "获取device id");

	/*******************************************************************************/
	/** step3: 创建Context (炒菜锅、电饭锅？)  */
	/*******************************************************************************/
	cout << "[3.]开始‘创建Context’" << endl;
	cl_context_properties props[] = { CL_CONTEXT_PLATFORM, (cl_context_properties)platform_id,0 };
	cl_context context = NULL;
	context = clCreateContext(props, 1, &device_id, NULL, NULL, &ret);
	if ((CL_SUCCESS != ret) || (NULL == context))
	{
		cout << "创建Context失败！" << endl;
		return -1;
	}

	/*******************************************************************************/
	/** step4: 创建Command Queue （炒菜步骤） */
	/*******************************************************************************/
	cout << "[4.]开始‘创建Command Queue’" << endl;
	cl_command_queue command_queue = NULL;
	command_queue = clCreateCommandQueue(context, device_id, 0, &ret);
	if ((CL_SUCCESS != ret) || (NULL == command_queue))
	{
		cout << "创建Command Queue失败！" << endl;
		return -1;
	}

	/*******************************************************************************/
	/*******************************************************************************/
	/** step5: 创建Memory Object (锅的大小)  */
	/*******************************************************************************/
	cout << "[5.]开始‘创建Memory Object’" << endl;
	//输入的图片
	Mat srcImage = imread(IMG_DIR);
	int img_h = srcImage.rows;
	int img_w = srcImage.cols;
	Mat outImage(img_h, img_w, srcImage.type(), Scalar(0, 0, 0));

	cl_mem mem_obj1 = NULL;
	cl_mem mem_obj2 = NULL;
	cl_mem mem_obj3 = NULL;
	cl_mem mem_objResult = NULL;
	cl_sampler mem_sampler = NULL;

	const int ARRAY_SIZE = 3 * img_h * img_w;
	const int ARRAY_OUT_SIZE = 3 * img_h * img_w;

	const int BUF1_RGBImage_SIZE = ARRAY_SIZE * sizeof(uchar);
	const int BUF2_img_h_SIZE = sizeof(int);
	const int BUF3_img_w_SIZE = sizeof(int);
	const int BUF4_OutImage_SIZE = ARRAY_OUT_SIZE * sizeof(uchar);

	//OpenCL的图片格式
	cl_image_format clImageFormat;//图像格式属性
	clImageFormat.image_channel_order = CL_RGBA;
	clImageFormat.image_channel_data_type = CL_UNORM_INT8;

	cl_image_desc image_desc;
	image_desc.image_type = CL_MEM_OBJECT_IMAGE2D;
	image_desc.image_width = img_w;
	image_desc.image_height = img_h;

	//法一：创建数组指针
	///* 申请buffer内存&初始化 */
	//int* host_buffer = NULL;
	//host_buffer = (int*)malloc(BUF_SIZE);
	//init_buf(host_buffer, ARRAY_SIZE); //初始化buffer
	///* 创建buffer */
	//mem_obj = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_USE_HOST_PTR, BUF_SIZE, host_buffer, &ret);

	//法二：创建vector
	/* 申请buffer内存&初始化 */
	/*std::vector<int> host_vector1(ARRAY_SIZE), host_vector2(ARRAY_SIZE), result(ARRAY_SIZE);
	init_vector(host_vector1, ARRAY_SIZE);
	init_vector(host_vector2, ARRAY_SIZE);*/
	mem_obj1 = clCreateImage2D(context, CL_MEM_READ_WRITE | CL_MEM_USE_HOST_PTR, &clImageFormat, img_w, img_h, 0, srcImage.data, &ret);
	checkErr(ret, "ret");
	if (NULL == mem_obj1)
	{
		cout << "mem_obj1失败！" << endl;
	}
	mem_obj2 = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_USE_HOST_PTR, BUF2_img_h_SIZE, &img_h, &ret2);
	checkErr(ret2, "mem_obj2");
	mem_obj3 = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_USE_HOST_PTR, BUF3_img_w_SIZE, &img_w, &ret3);
	checkErr(ret3, "mem_obj3");
	mem_objResult = clCreateBuffer(context, CL_MEM_WRITE_ONLY, BUF4_OutImage_SIZE, NULL, &retResult);
	checkErr(retResult, "mem_objResult");
	mem_sampler = clCreateSampler(context, CL_FALSE, CL_ADDRESS_CLAMP_TO_EDGE, CL_FILTER_NEAREST, &retSampler);
	checkErr(retSampler, "mem_sampler");
	// 检查错误
	if ((CL_SUCCESS != ret) || (CL_SUCCESS != ret2) || (CL_SUCCESS != ret3) || (CL_SUCCESS != retResult) || (NULL == mem_obj1) || (NULL == mem_obj2) || (NULL == mem_objResult) || (NULL == retSampler))
	{
		cout << "创建Memory Object失败！" << endl;
		clReleaseMemObject(mem_obj1);
		clReleaseMemObject(mem_obj2);
		clReleaseMemObject(mem_objResult);
		clReleaseCommandQueue(command_queue);
		clReleaseContext(context);
		clReleaseDevice(device_id);
		return -1;
	}

	/*******************************************************************************/
	/** step6: 创建&编译Program （菜谱的提前翻译） */
	/*******************************************************************************/
	cout << "[6.]开始‘创建&编译Program’" << endl;
	/* kernel代码 */
	// 法一：从文件读取kernel代码
	string strkernelSource = loadCodeFromFile(KERNEL_DIR);
	const char* kernelSource = strkernelSource.c_str(); // string转const char*字符串
	if (NULL == kernelSource)
	{
		cout << "kernel代码加载失败！" << endl;
		return -1;
	}
	// 法二：从字符串指针读取kernel代码
	/*const char* kernelSource =
		"__kernel void test(__global int *pInOut)\n"
		"{\n"
		" int index = get_global_id(0);\n"
		" pInOut[index] += pInOut[index];\n"
		"}\n";*/

		/* 创建program */
	cl_program program = NULL;
	program = clCreateProgramWithSource(context, 1, (const char**)&kernelSource, NULL, &ret);
	if ((CL_SUCCESS != ret) || (NULL == program))
	{
		cout << "创建Program失败！" << endl;
		return -1;
	}
	/* 编译program */
	ret = clBuildProgram(program, 1, &device_id, NULL, NULL, NULL);
	checkErr(ret, "编译Program");

	/*******************************************************************************/
	/*******************************************************************************/
	/** step7: 创建Kernel （看菜谱） */
	/*******************************************************************************/
	cout << "[7.]开始‘创建Kernel’" << endl;
	cl_kernel kernel = NULL;
	kernel = clCreateKernel(program, KERNEL_FUNCTION_NAME, &ret);
	if ((CL_SUCCESS != ret) || (NULL == kernel))
	{
		cout << "创建Kernel失败！" << endl;
		return -1;
	}

	/*******************************************************************************/
	/*******************************************************************************/
	/** step8: 设置Kernel Arg参数 （菜谱设置不同风味做法） */
	/*******************************************************************************/
	cout << "[8.]开始‘设置Kernel参数’" << endl;
	ret = clSetKernelArg(kernel, 0, sizeof(cl_mem), (void*)&mem_obj1);
	ret |= clSetKernelArg(kernel, 1, sizeof(cl_mem), (void*)&mem_obj2);
	ret |= clSetKernelArg(kernel, 2, sizeof(cl_mem), (void*)&mem_obj3);
	ret |= clSetKernelArg(kernel, 3, sizeof(cl_mem), (void*)&mem_objResult);
	ret |= clSetKernelArg(kernel, 4, sizeof(cl_sampler), (void*)&mem_sampler);
	checkErr(ret, "设置Kernel参数");

	/*******************************************************************************/
	/*******************************************************************************/
	/** step9: 设置GroupSize （并行炒菜的锅的个数） */
	/*******************************************************************************/
	cout << "[9.]开始‘设置GroupSize’" << endl;
	cout << "  本设备最大支持并行维数:" << CL_DEVICE_MAX_WORK_ITEM_DIMENSIONS << endl;
	cl_uint work_dim = 2; //一般设备最大支持维数为3
	size_t local_work_size[2] = { 16, 16 };
	size_t global_work_size[2] = { RoundUp(local_work_size[0], img_w),
								   RoundUp(local_work_size[1], img_h) };


	/*******************************************************************************/
	/** step10: Kernel入队执行 （正式炒菜） */
	/*******************************************************************************/
	cout << "[10.]开始‘Kernel入队执行’" << endl;
	ret = clEnqueueNDRangeKernel(command_queue, kernel, work_dim, NULL, global_work_size, local_work_size, 0, NULL, NULL);
	checkErr(ret, "Kernel入队执行");

	/*******************************************************************************/
	/*******************************************************************************/
	/** step11: 读取结果 （上菜品尝） */
	/*******************************************************************************/
	//【法一】：映射内存读取图片指针
	//cout << "[11.]开始‘读取结果’" << endl;
	//uchar* device_buffer = (uchar*)clEnqueueMapBuffer(command_queue, mem_objResult, CL_TRUE, CL_MAP_READ | CL_MAP_WRITE, 0, BUF4_GRAYImage_SIZE, 0, NULL, NULL, &ret);
	//if ((CL_SUCCESS != ret) || (NULL == device_buffer))
	//{
	//	cout << "读取结果失败！" << endl;
	//	return -1;
	//}
	////还原回原图片格式
	//Mat grayImage = Mat(img_h, img_w, CV_8UC1, Scalar(0));  //创建同尺寸灰度图
	//grayImage.data = device_buffer; //uchar*转Mat

	//【法二】：直接读取图片缓冲buffer
	ret = clEnqueueReadBuffer(command_queue, mem_objResult, CL_TRUE, 0, sizeof(uchar) * img_h * img_w * 3, outImage.data, 0, NULL, NULL);
	checkErr(ret, "读取结果");

	//显示结果
	imshow("srcImage", srcImage);
	imshow("grayImage", outImage);
	waitKey(0);


	/*******************************************************************************/
	/** step12: 释放资源 （洗碗收拾） */
	/*******************************************************************************/
	cout << "[12.]开始‘释放资源’" << endl;
	if (NULL != kernel) // step 7
	{
		clReleaseKernel(kernel);
	}
	if (NULL != program) // step 6
	{
		clReleaseProgram(program);
	}
	if ((NULL != mem_obj1) && (NULL != mem_obj2) && (NULL != mem_objResult)) // step 5
	{
		clReleaseMemObject(mem_obj1);
		clReleaseMemObject(mem_obj2);
		clReleaseMemObject(mem_objResult);
	}
	if (NULL != command_queue) // step 4
	{
		clReleaseCommandQueue(command_queue);
	}
	if (NULL != context) // step 3
	{
		clReleaseContext(context);
	}
	if (NULL != device_id) // step 2
	{
		clReleaseDevice(device_id);
	}
	//if (NULL != host_buffer) // step 5
	//{
	//	free(host_buffer);
	//}
	cout << "[全部执行结束]" << endl;
	return 0;
}

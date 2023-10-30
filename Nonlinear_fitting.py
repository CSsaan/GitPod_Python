# 四参方程  三次样条插值

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


########################################################################################
# 拟合曲线
########################################################################################
# USE_BAIDU = 1

# # 给定一组非线性数据
# xdata = np.array([0.53, 0.61, 0.69, 0.76, 0.84, 0.91, 1.07, 1.22, 1.37, 1.52,
#                  1.68, 1.83, 2.13, 2.44, 3.05, 3.66, 4.57, 6.1, 9.14, 18.2])
# ydata = np.array([0.0, 0.057029096, 0.210707504, 0.301353752, 0.388998469, 
#                  0.453831547, 0.55648392, 0.621917305, 0.672343032, 0.712563553,
#                  0.744980092,0.769592649, 0.806811639, 0.834725881, 0.871344564,
#                  0.894756508, 0.917267994, 0.939179173, 0.95988974, 0.98])

# xfitdata = np.array([0.53,0.58, 0.61,0.65, 0.69, 0.7,0.76,0.8, 0.84,0.87, 0.91,1.0, 1.07,1.15, 1.22,1.3, 1.37,1.4, 1.52,1.6,
#                  1.68,1.7, 1.83,2.0, 2.13,2.2, 2.44,2.8, 3.05,3.3, 3.66,4.1, 4.57,4.9, 6.1,8.1, 9.14,12.0,15.0, 18.2])

# # xdata = np.array([1, 2, 3, 4, 5])
# # ydata = np.array([0.5, 0.8, 1.2, 1.6, 2.0])

# if(USE_BAIDU):
#     # (1)定义对数函数模型
#     def log_func(x, a, b):
#         return a + b * np.log(x)
#     # (2)定义多项式函数模型
#     def multix_func(x, a, b, c, d, e, f):
#         return a*x + b*x**2 + c*x**3 + d*x**4 + e*x**5 + f
#     # (3)定义4参数方程拟合
#     def params4_func(x, a, b, c, d):
#         return (a - d) / (1 + (x / c) ** b) + d
#     # 使用最小二乘法等优化算法，求解出参数 a 和 b 的最优解
#     # popt, pcov = curve_fit(log_func, xdata, ydata)
#     # popt, pcov = curve_fit(multix_func, xdata, ydata)
#     popt, pcov = curve_fit(params4_func, xdata, ydata)
#     # 输出拟合参数 a 和 b 的值
#     # print("a = %.3f, b = %.3f" % (popt[0], popt[1]))
#     for _iter in popt:
#         print(_iter)
#     # 使用求得的参数 a 和 b，得出每个 x 值所对应的 y 值
#     # yfit = log_func(xdata, *popt) # (1)
#     # yfit = multix_func(xdata, *popt) # (2)
#     yfit = params4_func(xfitdata, *popt) # (3)
#     # 绘制拟合曲线和原始数据
#     plt.plot(xfitdata, yfit, 'r-', label='log fit')
#     plt.plot(xdata, ydata, 'bo', label='original data')
#     plt.legend()
#     plt.savefig('output/log_plot_baidu.jpg')

# else:
#     # 定义对数回归函数形式
#     def logarithmic_func(x, a, b):
#         return a * np.log(x) + b
#     # # 创建示例数据
#     # x = np.array([1, 2, 3, 4, 5, 6])
#     # y = np.array([1.2, 2.5, 3.6, 4.0, 4.2, 4.3]) # 1.2, 2.5, 3.6, 4.0, 4.2, 4.3        100, 200, 300, 400, 500, 600
#     # 使用curve_fit函数进行对数回归拟合
#     params, covariance = curve_fit(logarithmic_func, xdata, ydata)
#     # 从参数中获取拟合结果
#     a, b = params
#     # 打印拟合参数
#     print("a =", a)
#     print("b =", b)
#     # 使用拟合结果绘制拟合曲线
#     x_fit = np.linspace(1, 6, 100)  # 创建用于拟合曲线的新x值
#     y_fit = logarithmic_func(x_fit, a, b)
#     # 绘制原始数据和拟合曲线
#     plt.scatter(xdata, ydata, label='Data')
#     plt.plot(x_fit, y_fit, 'r-', label='Logarithmic Fit')
#     plt.xlabel('X')
#     plt.ylabel('Y')
#     plt.legend()
#     plt.savefig('output/log_plot_gpt.jpg')
    


########################################################################################
# draw line(对数曲线)
########################################################################################
# def logarithmic_func(x):
#         return 0.258932358692724 * np.log(x) + 0.247368521715951
#         # return 2.718281828459045**((x-0.247368521715951)*4.0)
# x_look_point = np.array([0.38694447, 0.47167076, 0.57494891, 0.7008411, 0.85429895, 1.04135829, 1.2693766, 1.54732234, 1.88612774, 2.29911879, 2.80253934, 3.41619006, 4.16420722, 5.076012, 6.18746773, 7.54229048, 9.19376846, 11.20685801, 13.66073847, 16.65192646, 20.29807214]) # np.linspace(0.50, 18.3, 20)
# y_look_point = logarithmic_func(x_look_point)

# x_fit = x_look_point # np.linspace(0.01, 18.3, 100)  # 创建用于拟合曲线的新x值
# y_fit = logarithmic_func(x_fit)
# # 绘制原始数据和拟合曲线
# plt.scatter(np.zeros(len(x_look_point)), y_look_point, s=2, c='b', label='look tick')
# plt.scatter(x_look_point, y_look_point, label='look Data')
# plt.plot(x_fit, y_fit, 'r-', label='Logarithmic')
# plt.xlabel('X')
# plt.ylabel('Y')
# plt.legend()
# plt.savefig('output/log_plot_line.jpg')


# # for i in range(len(x_look_point)):
# #         print(x_look_point[i], "m: ", y_look_point[i])




# def fan_logarithmic_func(x):
#         return 2.718**((x-0.247)*4.0) # 2.718281828459045**((x-0.247368521715951)*4.0)   
#         # 为降低运算，近似泰勒级数展开： 1 + ((x-0.247)*4.0) + (((x-0.247)*4.0)^2 / 2!) + (((x-0.247)*4.0)^3 / 3!) + (((x-0.247)*4.0)^4 / 4!)
# x_fit = np.linspace(0.01, 1.0, 21)
# y_fit = fan_logarithmic_func(x_fit)
# print(x_fit) # [0.01, 0.0595, 0.109, 0.1585, 0.208, 0.2575, 0.307, 0.3565, 0.406, 0.4555, 0.505, 0.5545, 0.604, 0.6535, 0.703, 0.7525, 0.802, 0.8515, 0.901, 0.9505, 1.0]
# print(y_fit) # [ 0.38694447, 0.47167076, 0.57494891, 0.7008411, 0.85429895, 1.04135829, 1.2693766, 1.54732234, 1.88612774, 2.29911879, 
#              #   2.80253934, 3.41619006, 4.16420722, 5.076012, 6.18746773, 7.54229048, 9.19376846, 11.20685801, 13.66073847, 16.65192646, 20.29807214]



########################################################################################
# draw line(二次函数曲线)
########################################################################################
def quadratic_func(x):  # x:0-18  -> y:0-1
        x = 1.0/x
        return 0.113*x*x - 0.830*x + 0.984
        # return (384.36*x*x - 2822.77*x + 3347.42)/3400.0

def AFStep2Dis(step):
        rrr = np.zeros(len(step))
        for i in range(len(step)):
                delta = 0.830**2 - 4*0.113*(0.984 - step[i])
                if delta >= 0:
                        z1 = (0.830 + np.sqrt(delta)) / (2.0 * 0.113)
                        result = 1.0/((0.830 - np.sqrt(delta)) / (2.0 * 0.113))
                        # if(result<0):
                        #         result = 0
                        print(i+1, ":",result)
                        rrr[i] = result
                        # print(rrr[i])
                
        return rrr
x_look_point = np.linspace(0.0, 1.0, 100) # np.array([0.38694447, 0.47167076, 0.57494891, 0.7008411, 0.85429895, 1.04135829, 1.2693766, 1.54732234, 1.88612774, 2.29911879, 2.80253934, 3.41619006, 4.16420722, 5.076012, 6.18746773, 7.54229048, 9.19376846, 11.20685801, 13.66073847, 16.65192646, 20.29807214]) 
y_look_point = AFStep2Dis(x_look_point)
print(y_look_point)

# 绘制原始数据和拟合曲线
plt.scatter(np.zeros(len(x_look_point)), y_look_point, s=2, c='b', label='look tick')
plt.scatter(x_look_point, y_look_point, label='look Data')
plt.plot(x_look_point, y_look_point, 'r-', label='Logarithmic')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.savefig('output/log_plot_line.jpg')


# for i in range(len(x_look_point)):
#         print(x_look_point[i], "m: ", y_look_point[i])


print(quadratic_func(1.62167287185891))
# print(quadratic_func(18.08076053706008))
# print(quadratic_func(6))
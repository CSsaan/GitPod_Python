import numpy as np
import cv2
from pprint import pprint


__main_name__ = "__main3__"

x_data = np.array([0.141, 0.144, 0.147, 0.15, 0.16, 0.166, 0.181, 0.197, 0.225, 0.256,
                   0.272, 0.304, 0.344, 0.378, 0.419, 0.469, 0.516, 0.559, 0.594, 0.625,
                   0.662, 0.696, 0.728, 0.762, 0.781, 0.806, 0.819, 0.834, 0.844, 0.853,
                   0.856, 0.859, 0.862, 0.219, 0.266, 0.319, 0.362, 0.382, 0.397, 0.36,
                   0.319, 0.262, 0.588, 0.638, 0.684, 0.738, 0.775, 0.74, 0.69, 0.644,
                   0.588, 0.262, 0.288, 0.325, 0.36, 0.378, 0.35, 0.325, 0.284, 0.606,
                   0.622, 0.656, 0.694, 0.725, 0.7, 0.662, 0.622, 0.384, 0.432, 0.466,
                   0.491, 0.518, 0.556, 0.603, 0.588, 0.55, 0.497, 0.447, 0.412], dtype=np.float32)

y_data = np.array([0.508, 0.536, 0.57, 0.603, 0.645, 0.689, 0.724, 0.756, 0.782, 0.810,
                   0.835, 0.86, 0.888, 0.912, 0.935, 0.946, 0.954, 0.942, 0.932, 0.918,
                   0.896, 0.872, 0.842, 0.81, 0.774, 0.738, 0.705, 0.672, 0.638, 0.606,
                   0.578, 0.54, 0.497, 0.446, 0.425, 0.422, 0.427, 0.432, 0.45, 0.452,
                   0.45, 0.448, 0.441, 0.427, 0.422, 0.425, 0.444, 0.45, 0.448, 0.452,
                   0.452, 0.52, 0.501, 0.497, 0.508, 0.534, 0.542, 0.54, 0.534, 0.534,
                   0.515, 0.503, 0.503, 0.522, 0.538, 0.542, 0.542, 0.786, 0.77, 0.766,
                   0.77, 0.766, 0.773, 0.788, 0.812, 0.838, 0.844, 0.835, 0.816], dtype=np.float32)
print(len(x_data), len(y_data))

if __main_name__ == "__main1__":
    y_data = (y_data+1.0)*0.5
    new_data = []
    for i in y_data:
        new_data.append(round(i, 3))

    for i in range(0, len(new_data), 10):
        sublist = new_data[i:i+10]
        sublist_str = ', '.join(str(x) for x in sublist)
        print(sublist_str)


#########################
# 箱型图
#########################
import matplotlib.pyplot as plt
import pandas as pd
import pickle
# 多组列表数据
# pre_data = [6,4,5,6, ..., ]
# infer_data = [12,12, ..., ]
# render_data = [5,5,4, ..., ]
# all_data = [23,24,22, ..., ]
# # 将四个列表保存到文件
# with open('lists_data.pkl', 'wb') as file:
#     pickle.dump([pre_data, infer_data, render_data, all_data], file)
if __main_name__ == "__main2__":
    # 加载保存的文件
    with open('lists_data.pkl', 'rb') as file:
        loaded_lists = pickle.load(file)
    print(len(loaded_lists))
    pre_data, infer_data, render_data, all_data = loaded_lists
    # 绘制箱型图，并显示各个值
    data = [pre_data, infer_data, render_data, all_data]
    df = pd.DataFrame(all_data)
    print(df.describe())
    plt.boxplot(data, showfliers=True, whis=1.5)
    # 设置箱子标题
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    plt.xticks([1, 2, 3, 4], ['前处理', '推理', '渲染+肤色统一调色', '总计'])
    # 设置图表标题和坐标轴标签
    plt.title('Boxplot of Multiple Data Groups')
    plt.xlabel('Group')
    plt.ylabel('Time(ms)')
    # 显示图表
    plt.show()



#########################
# 绘制点
#########################
import math
import matplotlib.pyplot as plt
def calculate_extended_point(x1, y1, x2, y2, distance_ratio):
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    cos_theta = (x2 - x1) / distance
    sin_theta = (y2 - y1) / distance
    new_x = x2 + cos_theta * distance * distance_ratio
    new_y = y2 + sin_theta * distance * distance_ratio
    print("new_x, new_y: ", new_x, new_y)
    return new_x, new_y

if __main_name__ == "__main3__":
    # 两个点的坐标
    x1, y1 = 1, 5
    x2, y2 = 4, 2
    # 计算延长线上的第三个点的坐标
    extended_x, extended_y = calculate_extended_point(x1, y1, x2, y2, 0.5)
    # 绘制图像
    plt.plot([x1, x2], [y1, y2], 'ro-')  # 画出两点之间的连线
    plt.plot([x2, extended_x], [y2, extended_y], 'bo-')  # 画出延长线
    plt.plot(x1, y1, 'ro')  # 标记第一个点
    plt.plot(x2, y2, 'ro')  # 标记第二个点
    plt.plot(extended_x, extended_y, 'bo')  # 标记延长线上的第三个点
    plt.text(x1, y1, '  ({}, {})'.format(x1, y1))  # 添加坐标标签
    plt.text(x2, y2, '  ({}, {})'.format(x2, y2))  # 添加坐标标签
    plt.text(extended_x, extended_y, '  ({}, {})'.format(round(extended_x, 2), round(extended_y, 2)))  # 添加坐标标签
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Points and Lines')
    plt.grid(True)
    plt.show()
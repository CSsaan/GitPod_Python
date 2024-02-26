import numpy as np

# 定义直线方程
def line_equation(x):
    return -1.0 * (1.0/np.tan(np.deg2rad(33))) * x # 肤色线

# 计算点到直线的距离
def distance_to_line(point):
    x0, y0 = point
    k = -1.0 * (1.0/np.tan(np.deg2rad(33)))
    b = 0
    distance =  np.abs(k * x0 - y0 + b) / np.sqrt(1 + k**2)
    return distance

if __name__ == '__main__':
    # 假设points是包含所有点坐标的数组
    points = np.array([[1, 2], [3, 4], [5, 6]])
    # 计算每个点到直线的距禂
    distances = [distance_to_line(point) for point in points]
    # 计算距离的均值
    mean_distance = np.mean(distances)
    print(distances)
    print(mean_distance)

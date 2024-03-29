

'''
功能: 将rgb图片转为亮度波形图(亮度累加)
'''
import matplotlib.pyplot as plt
import numpy as np
import cv2

def load_reshape_img(file_path):
    # 加载图片
    rawdata = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    # opencv resize
    rawdata = cv2.resize(rawdata, (1024, 1024))
    
    # 将图片转换为单通道的NumPy数组
    rawdata = np.array(rawdata)
    print(rawdata.shape[0], rawdata.shape[1])
    return rawdata

# 
def get_result_img(img, size_y):
    """
    img (cv.mat): 待统计的单通道原数据
    size_y (int): 需要生成的结果波形图的高
    return: 结果波形图
    """
    intensity = 5.11 # 累加亮度值
    rate = 1.3 # 亮度倍率
    # 现在用厘米为格子数，1500cm为15m
    vertical = np.zeros((size_y+1, img.shape[1]), dtype=float)
    print("vertical_shape:", vertical.shape)

    height, width = img.shape[0:2]
    for w in range(0, width):
        for h in range(0, height):
            depth = round(img[h][w]/255*size_y) # 0-1500cm
        #    depth = round(depth/10)   ## 把毫米转为厘米进行绘图
            vertical[depth][w] += intensity*rate
    # vertical = cv2.resize(vertical, (int(height * 2), int(width * 2)))
    return vertical

def save_result(result_vertical, save_dir = "./output/10meter.png"):
    result = result_vertical.astype(np.uint8)
    # result = cv2.equalizeHist(result)
    cv2.imwrite(save_dir, result, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    print("saved result:", save_dir, ", size:",result.shape)

if __name__ == "__main__":
    file = "./srcImg/facemask.jpg"

    reshapedata = load_reshape_img(file)
    
    size_y = round(240*1.4)
    result_vertical = get_result_img(reshapedata, size_y)

    save_result(result_vertical, "./output/10meter.png")
    
        
        
    
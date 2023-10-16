

'''
功能: 将软件中导出的raw深度图文件转为俯视距离图，并保存为png格式
Author: swortain
Date: 2021-12-31 17:45:22
LastEditTime: 2022-01-22 14:40:25
'''
import itertools
# import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import glob
import cv2


if __name__ == "__main__":
    file_path = "./srcImg/testlidar.jpg"
    print(file_path)

    # rawdata = np.fromfile(file, dtype="uint16")
    # print(rawdata.shape)
    # rawdata = rawdata.reshape(-1, 320)
    # print(rawdata.shape)
    # 打开图片
    image = Image.open(file_path).convert("RGBA")
    width, height = image.size
    # 获取图片的像素数据
    rawdata = image.load()

    ## 现在用厘米为格子数，1500为15米， 默认值为0，即表现为黑色
    vertical = np.zeros((256,width),dtype=int)  
    print(vertical.shape)
    # print("vertical",vertical)
    # height = rawdata.shape[0]
    # width = rawdata.shape[1]
    print("height",height)
    print("width",width)
  
    for h in range(0,height):
        for w in range(0,width):
           depth,_g,_b,_a = rawdata[w,h]
           depth = round(depth)   ## 把毫米转为厘米进行绘图
           vertical[255-depth][w] = 255  ## 有深度复制为255 ，绘制为白色

    # 转存为png格式
    img = vertical.astype(np.uint8)
    img = cv2.equalizeHist(img)
    out_file = "./output/10meter.png"
    if out_file:
        cv2.imwrite(out_file, img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        
        
    
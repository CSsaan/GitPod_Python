

'''
功能: 将软件中导出的raw深度图文件转为俯视距离图，并保存为png格式
Author: swortain
Date: 2021-12-31 17:45:22
LastEditTime: 2022-01-22 14:40:25
'''
import itertools
import matplotlib.pyplot as plt
import numpy as np
import glob
import cv2


if __name__ == "__main__":
    file = "./10meter.raw"
    print(file)

    # file = "./_2023_07_13_18_41_48depth_16b.raw"
    rawdata = np.fromfile(file, dtype="uint16")
    print(rawdata.shape)
    rawdata = rawdata.reshape(-1, 320)
    print(rawdata.shape)

    ## 现在用厘米为格子数，1500为15米，
    vertical = np.zeros((1500,320),dtype=int)
    print(vertical.shape)
    # print("vertical",vertical)
    height = rawdata.shape[0]
    width = rawdata.shape[1]
    print("height",rawdata.shape[0])
    print("width",rawdata.shape[1])
  
    for h in range(0,height):
        for w in range(0,width):
           depth = rawdata[h][w]
           depth = round(depth/10)   ## 把毫米转为厘米进行绘图
           vertical[depth][w] = 255


    img = vertical.astype(np.uint8)
    img = cv2.equalizeHist(img)
    out_file = "./10meter.png"
    if out_file:
        cv2.imwrite(out_file, img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        
        
    
import cv2
import os
import numpy as np

arr = np.zeros((156,4080,3))
print(arr.shape)

for i in range(arr.shape[0]):
    for j in range(arr.shape[1]):
        arr[i][j][:] = j/16
        # 上下双条
        if(156/2<=i<156):
            if(0<=j<8*16):
                arr[i][j][:] = np.array([176,106,123])
            elif(8*16<=j<=10*16):
                arr[i][j][:] = np.array([190,117,2])
            elif(97*16<=j<=108*16):
                arr[i][j][:] = np.array([64,194,129])
            elif(133*16<=j<=143*16):
                arr[i][j][:] = np.array([183,137,244])
            elif(248*16<=j<253*16):
                arr[i][j][:] = np.array([60,242,254])
            elif(253*16<j):
                arr[i][j][:] = np.array([45,47,238])

        # 单条
        # if(0<=j<8*16):
        #     arr[i][j][:] = np.array([176,106,123])
        # elif(8*16<=j<=10*16):
        #     arr[i][j][:] = np.array([190,117,2])
        # elif(97*16<=j<=108*16):
        #     arr[i][j][:] = np.array([64,194,129])
        # elif(133*16<=j<=143*16):
        #     arr[i][j][:] = np.array([183,137,244])
        # elif(248*16<=j<253*16):
        #     arr[i][j][:] = np.array([60,242,254])
        # elif(253*16<j):
        #     arr[i][j][:] = np.array([45,47,238])
        
save_dir = os.getcwd() + "/LUT/output"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

cv2.imwrite(save_dir + "/falseLUT.jpg", arr,[cv2.IMWRITE_JPEG_QUALITY, 100])
print("done.")
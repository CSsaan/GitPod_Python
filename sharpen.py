import cv2
import numpy as np

# 读取图像
img = cv2.imread('R.jpg')

# 定义锐化卷积核(以拉普拉斯算子为例)
kernel = np.array([[-1,-1,-1],
                   [-1, 9,-1],
                   [-1,-1,-1]])

# 应用锐化卷积核
sharp_img = cv2.filter2D(img, -1, kernel)

# 显示原图和锐化后的图像
# cv2.imshow('Original Image', img)
cv2.imwrite('Sharpened Image.jpg', sharp_img)
cv2.waitKey(0)

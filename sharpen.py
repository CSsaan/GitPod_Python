import cv2
import numpy as np

# 读取图像
img = cv2.imread('./srcImg/R.jpg')

# 定义锐化卷积核(以拉普拉斯算子为例)
kernel = np.array([[-1,-1,-1],
                   [-1, 9,-1],
                   [-1,-1,-1]])

# 应用锐化卷积核
sharp_img = cv2.filter2D(img, -1, kernel)
sharp_img = cv2.addWeighted(img, 0.4, sharp_img, 0.6, 0)

# 显示原图和锐化后的图像
# cv2.imshow('Original Image', img)
cv2.imwrite('SharpenedImage.jpg', sharp_img)
cv2.waitKey(0)


# ----------------------------------------------------------------------------------

# # 反锐化掩膜
# import cv2
# import numpy as np

# def unsharp_masking(image, sigma=1.0, strength=5.5):
#     blurred = cv2.GaussianBlur(image, (0, 0), sigma)
#     sharpened = cv2.addWeighted(image, 1 + strength, blurred, -strength, 0)
#     return sharpened

# # 读取图像
# image = cv2.imread('./srcImg/R.jpg')
# # 请将image替换为你的图像数据
# sharpened_image = unsharp_masking(image)
# # 显示原图和锐化后的图像
# # cv2.imshow('Original Image', img)
# cv2.imwrite('SharpenedImage.jpg', sharpened_image)
# cv2.waitKey(0)
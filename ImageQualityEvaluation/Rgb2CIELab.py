import cv2
import numpy as np
from PIL import Image

# [1]. RGB to CIELAB
pngFile = "/workspace/GitPod_Python/ImageQualityEvaluation/dataset/face5.png"
img = cv2.imread(pngFile)
# img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
img32 = img * (1./255)
img_lab = cv2.cvtColor(np.float32(img32), cv2.COLOR_BGR2LAB)
cv2.imwrite("/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-CIElab.png", img_lab)

# CIELAB to RGB
img_RGB = cv2.cvtColor(img_lab, cv2.COLOR_LAB2BGR)  # 转RGB
img_RGB = img_RGB / (1./255)
cv2.imwrite("/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-rgb.png", img_RGB)

# [2]. 分离L\A\B通道
l_channel, a_channel, b_channel = cv2.split(img_lab)
cv2.imwrite('/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-l_channel.jpg', l_channel)
cv2.imwrite('/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-a_channel.jpg', a_channel)
cv2.imwrite('/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-b_channel.jpg', b_channel)

# [3]. 细节层
l_channel_uint8 = cv2.convertScaleAbs(l_channel) # 将l_channel转换为CV_8U深度的图像
# l_channel_edges = cv2.Canny(l_channel_uint8, 5, 20)
l_channel_edges = cv2.Sobel(l_channel_uint8, cv2.CV_64F, 1, 1, ksize=5)
cv2.imwrite('/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-l_channel_edges.jpg', l_channel_edges)



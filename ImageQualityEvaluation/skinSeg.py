import cv2
import numpy as np

def RGBSkin(my_texture):
    # result = np.zeros_like(my_texture)
    result = np.copy(my_texture)
    R = my_texture[:,:,2]
    G = my_texture[:,:,1]
    B = my_texture[:,:,0]
    condition1 = (R > 95.0) & (G > 40.0) & (B > 20.0) & ((np.maximum(R, np.maximum(G, B)) - np.minimum(R, np.minimum(G, B)) > 15.0)) & (np.abs(R - G) > 15.0) & (R > G) & (R > B)
    condition2 = (R > 200.0) & (G > 210.0) & (B > 170.0) & (np.abs(R - G) <= 15.0) & (R > B) & (G > B)
    # result[condition1 | condition2] =  [255, 255, 255]
    result[~(condition1 | condition2)] = [0, 0, 0]  # 这里的[0, 0, 51, 255]对应vec4(0.0, 0.0, 0.2, 1.0)
    return result

def SkinInsight(imageA, imageB):
    imageB = imageB.astype('float32')
    # 将图像B转换为灰度图像
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    # 将灰度图像转换为单精度浮点型图像
    normalized_grayB = grayB.astype('float64') / 255.0
    # 融合图像A和归一化的灰度图像B
    result = cv2.addWeighted(imageA, 1.0, imageB, normalized_grayB, 0.0)
    return result


if __name__ == "__main__":
    # 读取图像
    pngFile = "/workspace/GitPod_Python/ImageQualityEvaluation/dataset/face5.png"
    image = cv2.imread(pngFile)
    # 调用RGBSkin函数进行mask获取
    skin_image = RGBSkin(image)
    # 显示结果图像
    cv2.imwrite('/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-l_skinSeg.jpg', skin_image)


    
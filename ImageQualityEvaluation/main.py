import cv2
import numpy as np

from skinSeg import *
from Rgb2CIELab import ImageProcessingLab



if __name__ == "__main__":
    # 读取图像
    pngFile = "/workspace/GitPod_Python/ImageQualityEvaluation/dataset/face5.png"
    image = cv2.imread(pngFile)
    # image[:, :, 1] = image[:, :, 1] + 8
    skin_image = RGBSkin(image)

    # 转LAB
    output_folder = "/workspace/GitPod_Python/ImageQualityEvaluation/result"
    image_processor_lab = ImageProcessingLab(skin_image)
    _l, _a, _b = image_processor_lab.split_channels(output_folder)

    # 直方图均衡化
    _l = image_processor_lab.normalHist(_l)
    _a = image_processor_lab.normalHist(_a)
    _b = image_processor_lab.normalHist(_b)
    cv2.imwrite(output_folder + '/l_channel_normal.jpg', _l)
    cv2.imwrite(output_folder + '/a_channelnormal.jpg', _a)
    cv2.imwrite(output_folder + '/b_channelnormal.jpg', _b)

    # 统计LAB中L/A/B
    width, height = skin_image.shape[:2]
    summ_L, summ_A, summ_B, summ_AB = 0, 0, 0, 0
    average_L, average_A, average_B, average_AB = 0, 0, 0, 0
    i = 0
    for w in range(width):
        for h in range(height):
            if(_l[w, h] != 0.0):
                i += 1
                summ_L += _l[w, h]
                summ_A += _a[w, h]
                summ_B += _b[w, h]
                summ_AB += (_a[w, h] + _b[w, h])*0.5
                # print(f"wh:[{w} ,{h}]: {(_a[w, h] + _b[w, h])*0.5}")
    average_L = summ_L/i
    average_A = summ_A/i
    average_B = summ_B/i
    average_AB = summ_AB/i
    print(f"average_L:{average_L}, average_A:{average_A}, average_B:{average_B}, average_AB:{average_AB}")

    # 统计磨皮前后变化
    diff = wrinkles(_l, '/workspace/GitPod_Python/ImageQualityEvaluation/result/wrinkles.jpg', "GaussianBlur") # 几种模糊"GaussianBlur"、"blur"、"medianBlur"、"bilateralFilter"
    sum_diff = np.sum(diff) # 统计差值结果图像的像素和
    print(f"磨皮磨去量：{sum_diff}")

    # 显示结果图像
    cv2.imwrite('/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-l_skinSeg.jpg', skin_image)
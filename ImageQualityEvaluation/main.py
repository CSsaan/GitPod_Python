import cv2
import numpy as np
import matplotlib.pyplot as plt

from skinSeg import *
from Rgb2CIELab import ImageProcessingLab
from adjustHSL import adjust_image_hls

# 统计LAB函数
def skin_statistics(skin_image, adjust_name, hist_normal=False):
    # 转LAB
    output_folder = "/workspace/GitPod_Python/ImageQualityEvaluation/result/hist_normal"
    image_processor_lab = ImageProcessingLab(skin_image)
    _l, _a, _b = image_processor_lab.split_channels(output_folder)
    cv2.imwrite(f'{output_folder}/origion/l_{adjust_name}.jpg', _l)
    cv2.imwrite(f'{output_folder}/origion/a_{adjust_name}.jpg', _a)
    cv2.imwrite(f'{output_folder}/origion/b_{adjust_name}.jpg', _b)
    # 直方图均衡化
    if(hist_normal):
        _l = image_processor_lab.normalHist(_l)
        _a = image_processor_lab.normalHist(_a)
        _b = image_processor_lab.normalHist(_b)
        cv2.imwrite(f'{output_folder}/after/l_{adjust_name}.jpg', _l)
        cv2.imwrite(f'{output_folder}/after/a_{adjust_name}.jpg', _a)
        cv2.imwrite(f'{output_folder}/after/b_{adjust_name}.jpg', _b)
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
    # print(f"average_L:{average_L}, average_A:{average_A}, average_B:{average_B}, average_AB:{average_AB}")
    return average_L, average_A, average_B, average_AB

def static_all(skin_image, use_HBS, hist_normal=False):
    '''
    use_HBS: H : hue_factor, B : brightness_factor, S : saturation_factor
    '''
    all_A, all_B, all_AB = [], [], []
    hue_factor, brightness_factor, saturation_factor = 0.0, 1.0, 1.0
    for shift in range(-10, 11, 2):
        # 设置调整参数
        if(use_HBS == 'H'):
            hue_factor = 0.0 + shift  # 色相调整值，可以是负值
        if(use_HBS == 'B'):
            brightness_factor = 1.0 + shift*0.05 # 亮度调整值，大于1增加亮度，小于1降低亮度
        if(use_HBS == 'S'):
            saturation_factor = 1.0 + shift*0.05 # 饱和度调整值，大于1增加饱和度，小于1降低饱和度
        adjusted_image = adjust_image_hls(skin_image, hue_factor, brightness_factor, saturation_factor)
        adjust_name = f'h{hue_factor}_b{brightness_factor}_s{saturation_factor}'
        _, average_A, average_B, average_AB = skin_statistics(adjusted_image, adjust_name, hist_normal=hist_normal)
        all_A.append((shift, average_A))
        all_B.append((shift, average_B))
        all_AB.append((shift, average_AB))
    return np.array(all_A), np.array(all_B), np.array(all_AB)


if __name__ == "__main__":
    # ------------------------------------------------ 亮度 ------------------------------------------------
    # 【LAB颜色空间分析】
    # ------------------------------------------------------------------------------------------------------
    # 读取皮肤图像
    pngFile = "/workspace/GitPod_Python/ImageQualityEvaluation/dataset/face5.png"
    image = cv2.imread(pngFile)
    skin_image = RGBSkin(image)
    cv2.imwrite('/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-l_skinSeg.jpg', skin_image)

    # 统计不同色度、亮度、饱和度的A\B\AB均值
    mode = 'B' # Hue, Brightness, Saturation
    all_A, all_B, all_AB = static_all(skin_image, use_HBS=mode, hist_normal=False)
    print("all_A: ", all_A)
    print("all_B: ", all_B)
    print("all_AB: ", all_AB)

    # 绘制多组点图\折线
    colors = ['b', 'g', 'r']
    names = ['Average_A', 'Average_B', 'Average_AB']
    _ALL_ = [all_A, all_B, all_AB]
    for i, dataset in enumerate(_ALL_):
        x, y = dataset[:, 0], dataset[:, 1]
        plt.scatter(x, y, color=colors[i], label=names[i]) # 绘制点
        plt.plot(x, y, color=colors[i]) # 绘制曲线
        # 拟合曲线
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        plt.plot(x, p(x), color=colors[i], linestyle='dashed')
        
    plt.xlabel(f'shift of {mode}')
    plt.ylabel('Value')
    plt.title('Skin LAB static, with shift of hue_factor, brightness_factor, saturation_factor')
    plt.legend()
    plt.savefig('/workspace/GitPod_Python/ImageQualityEvaluation/result/plt.jpg')

    # ------------------------------------------------ 亮度 ------------------------------------------------
    # 【YCbCr颜色空间分析】
    # ------------------------------------------------------------------------------------------------------





   # ---------------------------------------------- 清晰度 -------------------------------------------------
    '''
    # TODO:（清晰度）
    # （清晰度）统计磨皮前后变化
    diff = wrinkles(_l, '/workspace/GitPod_Python/ImageQualityEvaluation/result/wrinkles.jpg', "GaussianBlur") # 几种模糊"GaussianBlur"、"blur"、"medianBlur"、"bilateralFilter"
    sum_diff = np.sum(diff) # 统计差值结果图像的像素和
    print(f"磨皮磨去量：{sum_diff}")
    '''

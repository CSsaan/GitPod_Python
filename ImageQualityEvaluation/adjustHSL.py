import cv2
import numpy as np

def adjust_image_hls(image, hue_factor, brightness_factor, saturation_factor):
    # 将图像从 BGR 转换为 HLS 格式
    hls_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)

    # 调整色相
    hls_image[:, :, 0] = (hls_image[:, :, 0] + hue_factor) % 180

    # 调整亮度
    hls_image[:, :, 1] = np.clip(hls_image[:, :, 1] * brightness_factor, 0, 255)

    # 调整饱和度
    hls_image[:, :, 2] = np.clip(hls_image[:, :, 2] * saturation_factor, 0, 255)

    # 将图像从 HLS 转换回 BGR 格式
    result_image = cv2.cvtColor(hls_image, cv2.COLOR_HLS2BGR)

    return result_image


if __name__ == "__main__":
    # 读取图像
    image_path = "/workspace/GitPod_Python/ImageQualityEvaluation/dataset/face5.png"
    original_image = cv2.imread(image_path)

    # 设置调整参数
    hue_factor = 5  # 色相调整值，可以是负值
    brightness_factor = 1.0  # 亮度调整值，大于1增加亮度，小于1降低亮度
    saturation_factor = 1.0  # 饱和度调整值，大于1增加饱和度，小于1降低饱和度

    # 调整图像
    adjusted_image = adjust_image_hls(original_image, hue_factor, brightness_factor, saturation_factor)

    # 保存结果
    output_folder = "/workspace/GitPod_Python/ImageQualityEvaluation/result"
    cv2.imwrite(f"{output_folder}/h{hue_factor}_b{brightness_factor}_s{saturation_factor}.jpg", adjusted_image)

    print('saved png : ' + output_folder)
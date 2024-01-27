import cv2
import numpy as np

def RGBSkin(my_texture):
    # result = np.zeros_like(my_texture)
    result = np.copy(my_texture)
    R = my_texture[:,:,2]
    G = my_texture[:,:,1]
    B = my_texture[:,:,0]
    shift = 8.0 # 控制范围
    condition1 = (R > 95.0 + shift) & (G > 40.0 + shift) & (B > 20.0 + shift) & ((np.maximum(R, np.maximum(G, B)) - np.minimum(R, np.minimum(G, B)) > 15.0 + shift)) & (np.abs(R - G) > 15.0 + shift) & (R > G) & (R > B)
    condition2 = (R > 200.0 + shift) & (G > 210.0 + shift) & (B > 170.0 + shift) & (np.abs(R - G) <= 15.0 - shift) & (R > B) & (G > B)
    # result[condition1 | condition2] =  [255, 255, 255]
    result[~(condition1 | condition2)] = [0, 0, 0]  # 这里的[0, 0, 51, 255]对应vec4(0.0, 0.0, 0.2, 1.0)
    return result

def YCrCbSkin(my_texture): 
    # opencv转YCrCb
    img_YCrCb = cv2.cvtColor(my_texture, cv2.COLOR_RGB2YCrCb)
    # 判断条件Cr>=133.0 && Cr<=173.0 && Cb>=77.0 && Cb<=127.0
    skin_region = np.where((img_YCrCb[:, :, 1] >= 133.0) & (img_YCrCb[:, :, 1] <= 173.0) & (img_YCrCb[:, :, 2] >= 77.0) & (img_YCrCb[:, :, 2] <= 127.0))
    # 满足skin_region条件，则是原图像素，否则是黑色
    img_skin = np.zeros(my_texture.shape, np.uint8)
    img_skin[skin_region] = my_texture[skin_region]
    return img_skin

def HSVSkin(my_texture):
    img_skin = np.copy(my_texture)
    img_hsv = cv2.cvtColor(my_texture, cv2.COLOR_RGB2HSV)
    # 判断条件 HSV.x>=0.0 && HSV.x<=20.0 && HSV.y>=48.0 && HSV.z>=50.0
    # skin_region = np.where((img_hsv[:, :, 0] >= 0.0) & (img_hsv[:, :, 0] <= 20.0) & (img_hsv[:, :, 1] >= 48.0) & (img_hsv[:, :, 1] <= 50.0))
    H = img_hsv[:,:,0]
    S = img_hsv[:,:,1]
    V = img_hsv[:,:,2]
    shift = 2.0 # 控制范围
    condition = (H>=0.0 + shift) & (H<=20.0 - shift) & (S>=48.0 + shift) & (V>=50.0 + shift)
    # 满足skin_region条件，则是原图像素，否则是黑色
    img_skin[~(condition)] = [0, 0, 0]
    return img_skin

def SkinInsight(imageA, imageB):
    imageB = imageB.astype('float32')
    # 将图像B转换为灰度图像
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    # 将灰度图像转换为单精度浮点型图像
    normalized_grayB = grayB.astype('float64') / 255.0
    # 融合图像A和归一化的灰度图像B
    result = cv2.addWeighted(imageA, 1.0, imageB, normalized_grayB, 0.0)
    return result

def wrinkles(img, output_folder, mode):
    '''
    皮肤光滑度：毛孔、 斑点和皱纹等瑕疵
    '''
    if(mode == "GaussianBlur"):
        img_blur = cv2.GaussianBlur(img, (9, 9), 0) # opencv高斯模糊
    if(mode == "blur"):
        img_blur = cv2.blur(img, (5, 5)) # opencv均值模糊
    if(mode == "medianBlur"):
        img_blur = cv2.medianBlur(img, 5) # opencv中值模糊
    if(mode == "bilateralFilter"):
        img_blur = cv2.bilateralFilter(img, 9, 75, 75) # opencv双边滤波
    cv2.imwrite('/workspace/GitPod_Python/ImageQualityEvaluation/result/img_blur.jpg', img_blur)
    diff = cv2.absdiff(img, img_blur) # 原图与模糊图差的可视化
    cv2.imwrite(output_folder, diff)
    return diff

if __name__ == "__main__":
    # 读取图像
    pngFile = "/workspace/GitPod_Python/ImageQualityEvaluation/dataset/face5.png"
    image = cv2.imread(pngFile)
    # 调用RGBSkin函数进行mask获取
    skin_image = RGBSkin(image)
    # 显示结果图像
    cv2.imwrite('/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-l_skinSeg.jpg', skin_image)
    print('saved png : ' + '/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-l_skinSeg.jpg')


    
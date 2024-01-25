# import cv2
# import numpy as np
# from PIL import Image

# # [1]. RGB to CIELAB
# pngFile = "/workspace/GitPod_Python/ImageQualityEvaluation/dataset/face5.png"
# img = cv2.imread(pngFile)
# # img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
# img32 = img * (1./255)
# img_lab = cv2.cvtColor(np.float32(img32), cv2.COLOR_BGR2LAB)
# cv2.imwrite("/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-CIElab.png", img_lab)

# # CIELAB to RGB
# img_RGB = cv2.cvtColor(img_lab, cv2.COLOR_LAB2BGR)  # 转RGB
# img_RGB = img_RGB / (1./255)
# cv2.imwrite("/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-rgb.png", img_RGB)

# # [2]. 分离L\A\B通道
# l_channel, a_channel, b_channel = cv2.split(img_lab)
# cv2.imwrite('/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-l_channel.jpg', l_channel)
# cv2.imwrite('/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-a_channel.jpg', a_channel)
# cv2.imwrite('/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-b_channel.jpg', b_channel)

# # [3]. 细节层
# l_channel_uint8 = cv2.convertScaleAbs(l_channel) # 将l_channel转换为CV_8U深度的图像
# # l_channel_edges = cv2.Canny(l_channel_uint8, 5, 20)
# l_channel_edges = cv2.Sobel(l_channel_uint8, cv2.CV_64F, 1, 1, ksize=5)
# cv2.imwrite('/workspace/GitPod_Python/ImageQualityEvaluation/result/face5-l_channel_edges.jpg', l_channel_edges)


import cv2
import matplotlib.pyplot as plt
import numpy as np

class ImageProcessingLab:
    def __init__(self, img):
        self.l_channel = None
        self.a_channel = None
        self.b_channel = None
        self.img = img
        self.img_lab = cv2.cvtColor(np.float32(self.img) * (1./255), cv2.COLOR_BGR2LAB)

    def convert_lab_to_rgb(self, output_path):
        img_rgb = cv2.cvtColor(self.img_lab, cv2.COLOR_LAB2BGR)  # 转RGB
        img_rgb = img_rgb / (1./255)
        cv2.imwrite(output_path, img_rgb)

    def split_channels(self, output_folder):
        """
        # l_channel : 0.0 - 100.0
        # a_channel : -120.0 - +120.0
        # b_channel : -120.0 - +120.0
        """
        self.l_channel, self.a_channel, self.b_channel = cv2.split(self.img_lab)
        cv2.imwrite(output_folder + '/l_channel.jpg', self.l_channel)
        cv2.imwrite(output_folder + '/a_channel.jpg', self.a_channel)
        cv2.imwrite(output_folder + '/b_channel.jpg', self.b_channel)
        return self.l_channel, self.a_channel, self.b_channel

    def extract_detail_layer(self, output_path):
        l_channel_uint8 = cv2.convertScaleAbs(self.img_lab[:,:,0])  # 将l_channel转换为CV_8U深度的图像
        l_channel_edges = cv2.Sobel(l_channel_uint8, cv2.CV_64F, 1, 1, ksize=5)
        cv2.imwrite(output_path, l_channel_edges)
        return l_channel_edges

    # 归一化函数
    def normalHist(self, img):
        a = 0
        b = 255
        c = img.min()
        d = img.max()
        img = (b-a)/(d-c)*(img-c)+a
        # img = img .astype(np.uint8)
        return img

    def hist(self, img, output_folder):
        img1 = img.copy()
        img1 = self.normalHist(img1)
        # hist1 = plt.hist(img1.reshape(-1),bins=255,rwidth=0.85,range=(0,255))
        hist1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
        hist_list = hist1.flatten().tolist()
        print(f"直方图列表长度: {len(hist_list)}")
        plt.plot(hist1, color='gray')
        plt.savefig(output_folder + '/normalHist.jpg')
        # return hist1



if __name__ == "__main__":
    # 使用示例
    file_path = "/workspace/GitPod_Python/ImageQualityEvaluation/dataset/face5.png"
    output_folder = "/workspace/GitPod_Python/ImageQualityEvaluation/result"

    img = cv2.imread(file_path)

    image_processor_lab = ImageProcessingLab(img)
    # image_processor_lab.convert_lab_to_rgb(output_folder + "/face5-rgb.png")
    _l, _a, _b = image_processor_lab.split_channels(output_folder)
    image_processor_lab.hist(_a, output_folder)
    _detail = image_processor_lab.extract_detail_layer(output_folder + "/face5-l_channel_edges.jpg")
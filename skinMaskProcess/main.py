import os
import cv2
import numpy as np

from skinSeg import *

class VideoProcessor:
    def __init__(self, video_path):
        # 检查文件是否存在
        if not os.path.isfile(video_path):
            raise FileNotFoundError("视频文件不存在")
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.video_writer = None
        self.init_video_bool = False
    
    def get_cap_status(self):
        return self.cap.isOpened()

    def get_frame(self, frame_number=None):
        if(frame_number != None):
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("无法读取视频帧")
        return frame

    def rgb_to_gray(self, rgb_image):
        gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)
        return gray_image

    def binarize_image(self, image, threshold):
        image = self.rgb_to_gray(image)
        _, binary_image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
        return binary_image

    def filter_green(self, rgb_image):
        green_mask = rgb_image[:,:,1] > 200
        red_mask = rgb_image[:,:,2] < 100
        filtered_mask = np.logical_and(green_mask, red_mask).astype(np.uint8) * 255
        filtered_image = cv2.bitwise_and(rgb_image, rgb_image, mask=filtered_mask)
        return filtered_image

    def dilate_image(self, image, kernel_size):
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        dilated_image = cv2.dilate(image, kernel, iterations=1)
        return dilated_image

    def merge_mask(self, skin_YCrCb, distance, origin_frame, dilated_mask):
        Tradition = skin_YCrCb[:,:,2]
        result = np.zeros(Tradition.shape, np.uint8)
        # 遍历单通道图像的所有像素值

        condition1 = (origin_frame > 0) & (Tradition > 0)
        condition2 = (origin_frame > 0) & (Tradition == 0)
        condition3 = (origin_frame == 0) & (Tradition > 0) & (dilated_mask > 0)
        result[(condition1)] = 255
        result[(condition2)] = 150
        result[(condition3)] = distance[condition3]
        return result
    
    def gaussian_blur(self, mergeMask, kernel_size=15):
        blurred_image = cv2.GaussianBlur(mergeMask, (0, 0), kernel_size)
        return blurred_image

    def blend_images(self, image1, image2, mask):
        blended = cv2.seamlessClone(image1, image2, mask, (mask.shape[1]//2, mask.shape[0]//2), cv2.NORMAL_CLONE)
        return blended

    def save_image(self, image, filename):
        cv2.imwrite(filename, image)

    def init_video_writer(self, height, width, output_path, fps=30):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height), True)
        self.init_video_bool = True
    
    def count_frames(self):
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return total_frames

    def save_video(self, frame, output_path):
        if(self.init_video_bool == False):
            height, width, _ = frame.shape
            self.init_video_writer(height, width, output_path, fps=30)
        try:
            self.video_writer.write(frame)
        except Exception as e:
            print(e)
            self.video_writer.release()
    
    def quite_cap(self):
        self.cap.release()

def images_to_video(input_folder, output_path, fps=30):
    image_files = [f for f in os.listdir(input_folder) if f.endswith('.jpg')]

    if not image_files:
        print("文件夹中没有图片文件！")
        return

    first_image = cv2.imread(os.path.join(input_folder, image_files[0]))
    height, width, _ = first_image.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for image_file in image_files:
        image_path = os.path.join(input_folder, image_file)
        frame = cv2.imread(image_path)
        out.write(frame)

    out.release()

if __name__ == "__main__":
    # 进行单帧效果测试
    USE_SINGLE_TEST = True
    if USE_SINGLE_TEST:
        print("Single Test")
        frame_n = 426
        # 拿取原视频第 frame_n 帧
        video_processor0 = VideoProcessor('/workspace/GitPod_Python/skinMaskProcess/dataset/origin.mp4')
        frame0 = video_processor0.get_frame(frame_n)
        video_processor0.save_image(frame0, f'/workspace/GitPod_Python/skinMaskProcess/result/origin_{frame_n}.jpg')
        # 
        skin_YCrCb, distance = MaxHSVYCbCrSkin(frame0)
        video_processor0.save_image(distance, f'/workspace/GitPod_Python/skinMaskProcess/result/distance_{frame_n}.jpg')
        video_processor0.save_image(skin_YCrCb, f'/workspace/GitPod_Python/skinMaskProcess/result/origin_{frame_n}_skin.jpg')

        # 拿取AIMask第 frame_n 帧
        video_processor = VideoProcessor('/workspace/GitPod_Python/skinMaskProcess/dataset/AImask.avi')
        frame = video_processor.get_frame(frame_n)
        video_processor.save_image(frame, f'/workspace/GitPod_Python/skinMaskProcess/result/AImask_{frame_n}.jpg')
        frame = video_processor.filter_green(frame)
        # gray_frame = video_processor.rgb_to_gray(frame)
        binarize_frame = video_processor.binarize_image(frame, threshold=1)
        video_processor.save_image(binarize_frame, f'/workspace/GitPod_Python/skinMaskProcess/result/AImask_{frame_n}_binarize.jpg')

        # AI结果进行膨胀
        dilated_mask = video_processor.dilate_image(binarize_frame, kernel_size=80)
        video_processor.save_image(dilated_mask, f'/workspace/GitPod_Python/skinMaskProcess/result/AImask_{frame_n}_dilated.jpg')

        # 融合 skin_YCrCb + dilated_mask
        mergeMask = video_processor.merge_mask(skin_YCrCb, distance, binarize_frame, dilated_mask)
        video_processor.save_image(mergeMask, f'/workspace/GitPod_Python/skinMaskProcess/result/mergeMask_{frame_n}.jpg')

        # 高斯模糊
        blurred_mask = video_processor.gaussian_blur(mergeMask, kernel_size=21)
        video_processor.save_image(blurred_mask, f'/workspace/GitPod_Python/skinMaskProcess/result/mergeMaskBlurred_{frame_n}.jpg')

        # # LUT调色
        # # 根据mask融合两张图
        # height, width, _ = frame0.shape
        # red_image = np.full((height, width, 3), (0, 0, 255), dtype=np.uint8)
        # result = video_processor.blend_images(red_image, frame0, 0.5)
        # video_processor.save_image(result, f'/workspace/GitPod_Python/skinMaskProcess/result/result_{frame_n}.jpg')

    # 进行所有帧效果测试
    else:
        print("Processing all frames...")
        # # 创建一个名为Frame的窗口，并设置窗口大小
        # cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
        # cv2.resizeWindow('Frame', 620*2, 1080)  # 设置窗口大小为800x600
        frame_n = 1 # AI视频帧定位

        video_processor = VideoProcessor('./skinMaskProcess/dataset/AImask.avi') # AI视频加载器
        video_processor0 = VideoProcessor("./skinMaskProcess/dataset/origin.mp4") # 原视频加载器

        total_frames = video_processor0.count_frames()

        while video_processor0.get_cap_status():
            frame0 = video_processor0.get_frame()
            skin_YCrCb, distance = MaxHSVYCbCrSkin(frame0)

            try:
                frameAI = video_processor.get_frame(frame_n)
            except:
                print("AI视频帧定位失败")
                break
            frame_n += 1
            print("\r" + f'{frame_n}/{total_frames}' + "\r")
            frame = video_processor.filter_green(frameAI)
            binarize_frame = video_processor.binarize_image(frame, threshold=1)
            dilated_mask = video_processor.dilate_image(binarize_frame, kernel_size=81)
            mergeMask = video_processor.merge_mask(skin_YCrCb, distance, binarize_frame, dilated_mask)
            mergeMask = video_processor.gaussian_blur(mergeMask, kernel_size=5)

            height, width, _ = frame0.shape
            red_image = np.full((height, width, 3), (0, 0, 255), dtype=np.uint8)
            # blended = cv2.addWeighted(frame0, 0.6, red_image, 0.4, 0)
            # mergeMask由单通道变为三通道
            # mergeMask = cv2.cvtColor(mergeMask, cv2.COLOR_GRAY2BGR)
            mergeMask = mergeMask.astype(float) / 255
            blended = np.zeros_like(frame0)
            blended[:, :, 0] = frame0[:, :, 0] * (1 - mergeMask) + red_image[:, :, 0] * mergeMask
            blended[:, :, 1] = frame0[:, :, 1] * (1 - mergeMask) + red_image[:, :, 1] * mergeMask
            blended[:, :, 2] = frame0[:, :, 2] * (1 - mergeMask) + red_image[:, :, 2] * mergeMask

            result = cv2.hconcat([frameAI, blended])
            # resize
            result = cv2.resize(result, (960, 1080))
            print(result.shape)
            # # 保存每一帧
            video_processor0.save_image(result, f'/workspace/GitPod_Python/skinMaskProcess/result/frames/{frame_n-1:05d}.jpg')
            # 保存视频
            # video_processor0.save_video(result, '/workspace/GitPod_Python/skinMaskProcess/result/output_video.mp4')
            
  
            # # 显示查看一下
            # cv2.imshow("Frame", skin_YCrCb)
            # key = cv2.waitKey(30)
            # if key == ord('q') or key == 27:
            #     print("Exiting...")
            #     video_processor0.quite_cap()
            #     video_processor.quite_cap()
            #     cv2.destroyAllWindows()
            #     break

        # 将文件夹下所有图片保存为mp4
        print("saving video...")
        images_to_video('/workspace/GitPod_Python/skinMaskProcess/result/frames', '/workspace/GitPod_Python/skinMaskProcess/result/output_video.mp4')

        # # 释放视频对象和关闭窗口
        # video_processor0.quite_cap()
        # video_processor.quite_cap()
        # cv2.destroyAllWindows()

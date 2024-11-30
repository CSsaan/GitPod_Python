import numpy as np
from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO
from utils.shader import Shader
from utils.texture import Texture
from utils.window import Window
from utils.myUtils import ensure_directory_exists
from utils.framebuffer import FBO
import argparse
import cv2
import os
import nanogui
from dynamo import DepthAnythingInference
from libfacedetection import FaceDetection, denormalize_coordinates, process_face_rectangle
from libfacedetection import KalmanFilter, KalmanFilterFrame

class VideoRenderer:
    def __init__(self, args):

        ensure_directory_exists(os.path.dirname(args.saveVideo_path))
        ensure_directory_exists(args.saveFrames_path)
        # 帧数
        self.frame_n = 1
        self.cap = cv2.VideoCapture(args.inputVideo_path)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))

        # 保存视频
        self.window_w, self.window_h = self.video_width, self.video_height # video_width//2, video_height//2
        self.video_writer = cv2.VideoWriter(args.saveVideo_path, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, (self.window_w*2 if args.concat_ori_result else self.window_w, self.window_h), True)

        # 创建窗口
        print(f"window size:[{self.window_w},{self.window_h}]")
        self.w = Window(self.window_w, self.window_h, args.project_name)


        # 加载深度估计模型
        self.model_input_size = [420, 420]
        self.model = DepthAnythingInference(height=self.model_input_size[0], width=self.model_input_size[1])
        # 加载人脸检测模型
        self.face_detection = FaceDetection()
        self.max_face_loc = None
        self.median_depth = 0.3
        # 单值卡尔曼滤波
        self.kalman_filter = KalmanFilter(processNoise=0.0003, measurementNoise=0.5)
        # 帧卡尔曼滤波
        self.kalman_frame_filter = KalmanFilterFrame(self.model_input_size[0], self.model_input_size[1])


        # 顶点数据
        self.triangle = np.array(
            [-1.0, -1.0, 0.0,  0.0, 1.0,
            1.0, -1.0, 0.0,  1.0, 1.0, 
            1.0,  1.0, 0.0,  1.0, 0.0,	 
            -1.0, -1.0, 0.0,  0.0, 1.0,
            1.0,  1.0, 0.0,  1.0, 0.0,	 
            -1.0,  1.0, 0.0,  0.0, 0.0	], dtype=np.float32)
        assert self.triangle.nbytes % (6*5) == 0, "不能被整除"
        every_size = self.triangle.nbytes//(6*5)
        print(self.triangle.nbytes, every_size)

        # VAO & VBO
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = VBO(self.triangle, GL_STATIC_DRAW)
        self.vbo.bind()

        # Dilation
        self.shader1 = Shader("./shaders/MTFilter_SegmentDilation9.vs", "./shaders/MTFilter_SegmentDilation9.fs") # dilate  YcbCr_segmentation
        self.shader1.setAttrib(0, 3, GL_FLOAT, every_size*5, 0)
        self.shader1.setAttrib(1, 2, GL_FLOAT, every_size*5, every_size*3)
        # normal 2D
        self.shader_2D = Shader("./shaders/base.vert", "./shaders/base.frag")
        self.shader_2D.setAttrib(0, 3, GL_FLOAT, every_size*5, 0)
        self.shader_2D.setAttrib(1, 2, GL_FLOAT, every_size*5, every_size*3)

        # 创建Fbo&Texture [shader result]
        self.fbo1 = FBO(self.window_w, self.window_h)
        # 创建Fbo
        self.fbo_2d = FBO(self.window_w, self.window_h)


        # 创建纹理
        # tex = Texture(idx=0, "./resource/sight.jpg")
        self.tex = Texture(idx=0, texType=GL_TEXTURE_2D, imgType=GL_RGB, innerType=GL_RGB, dataType=GL_UNSIGNED_BYTE, w=self.video_width, h=self.video_height)
        self.tex_depth = Texture(idx=1, texType=GL_TEXTURE_2D, imgType=GL_RGB, innerType=GL_RGB, dataType=GL_UNSIGNED_BYTE, w=self.model_input_size[0], h=self.model_input_size[1])

    def quite_cap(self):
        self.cap.release()

    # 渲染循环
    def render(self):
        # 读取每一帧
        # img = cv2.imread("./resource/sight.jpg")
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_n)
        ret, img = self.cap.read()
        
        # 最大人脸检测
        max_face = self.face_detection.process_image(img)
        if max_face is not None:
            print('largest face: top-left coordinates: ({:.2f}, {:.2f}), box width: {:.2f}, box height {:.2f}, score: {:.2f}'.format(
                max_face[0], max_face[1], max_face[2], max_face[3], max_face[4]))
            self.max_face_loc = max_face
        else:
            print('not detect face.')
        # 深度估计 & 卡尔曼滤波
        img_depth = self.model.infer(img)
        img_depth = self.kalman_frame_filter.process_video(img_depth)

        # 对焦人脸距离 & 卡尔曼滤波
        if self.max_face_loc is not None:
            ori_median_depth = process_face_rectangle(self.max_face_loc, img_depth, draw_roi=False)
            measurement = np.array([[ori_median_depth], [0]], np.float32)
            predicted, state_post = self.kalman_filter.update(measurement)
            self.median_depth = predicted[0][0]
            print(f'ori_median_depth:{ori_median_depth}, median_depth:{self.median_depth}')

        self.frame_n += 1
        print("\r" + f'{self.frame_n}/{self.total_frames}')

        # -----------------------------------------------
        # [shader1]
        self.fbo1.bind()
        self.shader1.use()
        glBindVertexArray(self.vao)
        self.tex.updateTex(self.shader1, "tex", img) # 原视频纹理
        self.tex_depth.updateTex(self.shader1, "s_depth", img_depth)
        self.shader1.setUniform("iResolution_x",  self.video_width)
        self.shader1.setUniform("iResolution_y",  self.video_height)
        self.shader1.setUniform("focusDis", 1.0-self.median_depth)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindTexture(GL_TEXTURE_2D, GL_NONE)
        glBindVertexArray(0)
        glUseProgram(GL_NONE)
        self.fbo1.unbind()

        # -----------------------------------------------
        # draw normal 2D on screen
        if(not args.show_on_screen):
            self.fbo_2d.bind()
        self.shader_2D.use()
        glBindVertexArray(self.vao)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.fbo1.uTexture)
        self.shader_2D.setUniform("tex", 0)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindTexture(GL_TEXTURE_2D, GL_NONE)
        glBindVertexArray(0)
        glUseProgram(GL_NONE)
        
        # save
        if(args.save_video or args.save_frames):
            data = glReadPixels(0, 0, self.window_w, self.window_h, GL_BGR, GL_UNSIGNED_BYTE)  # 注意这里使用BGR通道顺序
            image = np.frombuffer(data, dtype=np.uint8).reshape(self.window_h, self.window_w, 3)
            image = cv2.flip(image, 0)

            if(args.concat_ori_result):
                img = cv2.resize(img, (image.shape[1], image.shape[0]))
                img_depth = cv2.resize(img_depth, (image.shape[1], image.shape[0]))
                result = cv2.hconcat([img, img_depth])
                result = cv2.hconcat([result, image])
            else:
                result = image

            try:
                if(args.save_frames):
                    cv2.imwrite(f"{args.saveFrames_path}/{self.frame_n-1}.png", result)
                if(args.save_video):
                    self.video_writer.write(result)
            except Exception as e:
                print(e)
                self.video_writer.release()
        if(not args.show_on_screen):
            self.fbo_2d.unbind()

if __name__ == '__main__':
    # w.loop(render)

    parser = argparse.ArgumentParser()
    parser.add_argument('--project_name', default="Test by CS", type=str, help="Window's name")
    parser.add_argument('--inputVideo_path', default="D:/Users/Desktop/Vloggopro6.mp4", type=str, help='input a video to render frames')
    parser.add_argument('--save_video', default=False, type=bool, help='if save frames to a video')
    parser.add_argument('--saveVideo_path', default="./result/640-2.mp4", type=str, help='save frames to a video')
    parser.add_argument('--concat_ori_result', default=False, type=bool, help='concat origin & result') 
    parser.add_argument('--save_frames', default=True, type=bool, help='if save frames to a folder')
    parser.add_argument('--saveFrames_path', default="./result/frames", type=str, help='save frames to a folder')
    parser.add_argument('--show_on_screen', default=False, type=bool, help='show result on screen')
    args = parser.parse_args()

    video_renderer = VideoRenderer(args)
    video_renderer.w.loop(video_renderer.render)


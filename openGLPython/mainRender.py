import numpy as np
from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO
from utils.shader import Shader
from utils.texture import Texture
from utils.window import Window
from utils.myUtils import ensure_directory_exists
import argparse
import cv2
import os

parser = argparse.ArgumentParser()
parser.add_argument('--project_name', default="Test CS", type=str, help="Window's name")
parser.add_argument('--inputVideo_path', default="./resource/input.mp4", type=str, help='input a video to render frames')
parser.add_argument('--save_video', default=True, type=bool, help='if save frames to a video')
parser.add_argument('--saveVideo_path', default="./result/output.mp4", type=str, help='save frames to a video')
parser.add_argument('--save_frames', default=False, type=bool, help='if save frames to a folder')
parser.add_argument('--saveFrames_path', default="./result/frames", type=str, help='save frames to a folder')
args = parser.parse_args()

ensure_directory_exists(os.path.dirname(args.saveVideo_path))
ensure_directory_exists(args.saveFrames_path)

# 帧数
frame_n = 1
cap = cv2.VideoCapture(args.inputVideo_path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
# 保存视频
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(args.saveVideo_path, fourcc, fps, (video_width, video_height), True)

# 创建窗口
w = Window(video_width, video_height, args.project_name)

# 顶点数据
triangle = np.array(
    [-1.0, -1.0, 0.0,  0.0, 1.0,
      1.0, -1.0, 0.0,  1.0, 1.0, 
      1.0,  1.0, 0.0,  1.0, 0.0,	 
     -1.0, -1.0, 0.0,  0.0, 1.0,
      1.0,  1.0, 0.0,  1.0, 0.0,	 
     -1.0,  1.0, 0.0,  0.0, 0.0	], dtype=np.float32)
print(triangle.nbytes)

# VAO & VBO
vao = glGenVertexArrays(1)
glBindVertexArray(vao)
vbo = VBO(triangle, GL_STATIC_DRAW)
vbo.bind()

# 导入顶点着色器文件和片元着色器文件
shader = Shader("./shaders/base.vert", "./shaders/YcbCr_segmentation.frag")
shader.setAttrib(0, 3, GL_FLOAT, 20, 0)
shader.setAttrib(1, 2, GL_FLOAT, 20, 12)
# 创建并设置纹理
# tex = Texture(idx=0, "./resource/sight.jpg")
tex = Texture(idx=0, texType=GL_TEXTURE_2D, imgType=GL_RGB, innerType=GL_RGB, dataType=GL_UNSIGNED_BYTE, w=video_width, h=video_height)

def quite_cap(self):
    cap.release()
# 渲染循环
def render():
    # img = cv2.imread("./resource/sight.jpg")
    global frame_n
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_n)
    ret, img = cap.read()
    if not ret:
        raise ValueError("无法读取视频帧")
    frame_n += 1
    print("\r" + f'{frame_n}/{total_frames}')
    # draw
    shader.use()
    glBindVertexArray(vao)
    tex.updateTex(shader, "tex", img)
    glDrawArrays(GL_TRIANGLES, 0, 6)
    # save
    if(args.save_video):
        data = glReadPixels(0, 0, video_width, video_height, GL_BGR, GL_UNSIGNED_BYTE)  # 注意这里使用BGR通道顺序
        image = np.frombuffer(data, dtype=np.uint8).reshape(video_height, video_width, 3)
        image = cv2.flip(image, 0)
        try:
            if(args.save_frames):
                cv2.imwrite(f"{args.saveFrames_path}/output_{frame_n-1}.png", image)
            video_writer.write(image)
            pass
        except Exception as e:
            print(e)
            video_writer.release()


if __name__ == '__main__':
    w.loop(render)

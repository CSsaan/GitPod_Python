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

POINTS_NUM = 8


parser = argparse.ArgumentParser()
parser.add_argument('--project_name', default="Test CS", type=str, help="Window's name")
parser.add_argument('--inputVideo_path', default="./resource/toothMask.mp4", type=str, help='input a video to render frames')
parser.add_argument('--inputMask_path', default="./resource/640/6.avi", type=str, help='input a ai mask result video to render frames')
parser.add_argument('--save_video', default=False, type=bool, help='if save frames to a video')
parser.add_argument('--saveVideo_path', default="./result/640-2.mp4", type=str, help='save frames to a video')
parser.add_argument('--concat_ori_result', default=False, type=bool, help='concat origin & result') 
parser.add_argument('--save_frames', default=False, type=bool, help='if save frames to a folder')
parser.add_argument('--saveFrames_path', default="./result/frames", type=str, help='save frames to a folder')
parser.add_argument('--show_on_screen', default=True, type=bool, help='show result on screen')
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

cap_aimask = cv2.VideoCapture(args.inputMask_path)

# 保存视频
window_w, window_h = video_width, video_height # video_width//2, video_height//2
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(args.saveVideo_path, fourcc, fps, (window_w*2 if args.concat_ori_result else window_w, window_h), True)

# 创建窗口
print(f"window size:[{window_w},{window_h}]")
w = Window(window_w, window_h, args.project_name)

# Program segment
shader = Shader("./shaders/ToothWhiten/toothMask.vert", "./shaders/ToothWhiten/toothMask.frag") # dilate  Green_segmentation
shader_2D = Shader("./shaders/base.vert", "./shaders/base.frag") # normal 2D

# 顶点数据
vert2D = np.array(
    [-1.0, -1.0, 0.0,  0.0, 1.0,
      1.0, -1.0, 0.0,  1.0, 1.0, 
      1.0,  1.0, 0.0,  1.0, 0.0,	 
     -1.0, -1.0, 0.0,  0.0, 1.0,
      1.0,  1.0, 0.0,  1.0, 0.0,	 
     -1.0,  1.0, 0.0,  0.0, 0.0	], dtype=np.float32)
triangle = np.array(
    [-0.690, -0.242, 0.0,  0.154639, 0.378788,
     -0.202, -0.606, 0.0,  0.398625, 0.196970,
      0.024, -0.424, 0.0,  0.512027, 0.287879,
      0.223, -0.575, 0.0,  0.611684, 0.212121,
      0.740, -0.242, 0.0,  0.872852, 0.378788,
      0.278,  0.696, 0.0,  0.639176, 0.848485,
      0.040,  0.272, 0.0,  0.522337, 0.636364,
     -0.202,  0.666, 0.0,  0.398625, 0.833333 ], dtype=np.float32)
assert triangle.nbytes % (POINTS_NUM*5) == 0, "不能被整除"
every_size = triangle.nbytes//(POINTS_NUM*5)
print(triangle.nbytes, every_size)

# VAO & VBO
vao = glGenVertexArrays(1)
glBindVertexArray(vao)
vbo = VBO(triangle, GL_STATIC_DRAW)
vbo.bind()
shader.setAttrib(0, 3, GL_FLOAT, every_size*5, 0)
shader.setAttrib(1, 2, GL_FLOAT, every_size*5, every_size*3)


vao2D = glGenVertexArrays(1)
glBindVertexArray(vao2D)
vbo2D = VBO(vert2D, GL_STATIC_DRAW)
vbo2D.bind()
shader_2D.setAttrib(0, 3, GL_FLOAT, every_size*5, 0)
shader_2D.setAttrib(1, 2, GL_FLOAT, every_size*5, every_size*3)

# 创建Fbo&Texture [shader result]
fbo_green = FBO(window_w, window_h)
# 创建Fbo
fbo_2d = FBO(window_w, window_h)

# 创建纹理
tex = Texture(idx=0, texType=GL_TEXTURE_2D, imgType=GL_RGB, innerType=GL_RGB, dataType=GL_UNSIGNED_BYTE, w=video_width, h=video_height)
tex_background = Texture(idx=1, imgPath="./resource/sight.jpg")

def quite_cap(self):
    cap.release()
    cap_aimask.release()

# 渲染循环
def render():
    glDisable(GL_CULL_FACE)
    # 读取每一帧
    # img = cv2.imread("./resource/sight.jpg")
    global frame_n
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_n)
    ret, img = cap.read()
    cap_aimask.set(cv2.CAP_PROP_POS_FRAMES, frame_n)
    ret_aimask, img_aimask = cap_aimask.read()
    if not ret and not ret_aimask:
        raise ValueError("无法读取视频帧")
    frame_n += 1
    print("\r" + f'{frame_n}/{total_frames}')

    # -----------------------------------------------
    # update VBO
    increment = np.array(
        # ( x      y      z )  (  x      1-y )
        [-0.690, -0.242, 0.0,  0.154639, 0.621,
         -0.202, -0.606, 0.0,  0.398625, 0.803,
          0.024, -0.424, 0.0,  0.512027, 0.712,
          0.223, -0.575, 0.0,  0.611684, 0.787,
          0.740, -0.242, 0.0,  0.872852, 0.621,
          0.278,  0.696, 0.0,  0.639176, 0.151,
          0.040,  0.692, 0.0,  0.522337, 0.153,
         -0.202,  0.696, 0.0,  0.398625, 0.156 ], dtype=np.float32)
    vbo.set_array(increment)
    vbo.bind()
    # draw framebuffer [Green]
    fbo_green.bind()
    shader.use()
    glBindVertexArray(vao)
    tex.updateTex(shader, "tex", img) # 原视频纹理
    tex_background.useTex(shader, "tex_background") # 背景
    shader.setUniform("strenth", 0.9)
    shader.setUniform("gpow", 0.5)
    
    indices = np.array(
        [0, 1, 7,
         7, 1, 6,
         1, 6, 2,
         2, 6, 3,
         5, 6, 3,
         5, 3, 4 ], dtype=np.int8)

    glDrawElements(GL_TRIANGLES, indices.nbytes, GL_UNSIGNED_SHORT, indices)
    # glDrawArrays(GL_TRIANGLES, 0, 6)
    glBindTexture(GL_TEXTURE_2D, GL_NONE)
    glBindVertexArray(0)
    glUseProgram(GL_NONE)
    fbo_green.unbind()
    # -----------------------------------------------
    # draw normal 2D on screen
    if(not args.show_on_screen):
        fbo_2d.bind()
    shader_2D.use()
    glBindVertexArray(vao2D)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, fbo_green.uTexture)
    shader_2D.setUniform("tex", 0)
    glDrawArrays(GL_TRIANGLES, 0, 6)
    glBindTexture(GL_TEXTURE_2D, GL_NONE)
    glBindVertexArray(0)
    glUseProgram(GL_NONE)
    
    # save
    if(args.save_video or args.save_frames):
        data = glReadPixels(0, 0, window_w, window_h, GL_BGR, GL_UNSIGNED_BYTE)  # 注意这里使用BGR通道顺序
        image = np.frombuffer(data, dtype=np.uint8).reshape(window_h, window_w, 3)
        image = cv2.flip(image, 0)

        if(args.concat_ori_result):
            img = cv2.resize(img, (image.shape[1], image.shape[0]))
            result = cv2.hconcat([img, image])
        else:
            result = image

        try:
            if(args.save_frames):
                cv2.imwrite(f"{args.saveFrames_path}/output_{frame_n-1}.png", result)
            if(args.save_video):
                video_writer.write(result)
        except Exception as e:
            print(e)
            video_writer.release()
    if(not args.show_on_screen):
        fbo_2d.unbind()

if __name__ == '__main__':
    w.loop(render)

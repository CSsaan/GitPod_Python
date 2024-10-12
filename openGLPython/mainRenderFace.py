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

parser = argparse.ArgumentParser()
parser.add_argument('--project_name', default="Test CS", type=str, help="Window's name")
parser.add_argument('--inputVideo_path', default="./resource/faceMask.mp4", type=str, help='input a video to render frames')
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
     
POINTS_NUM = 79
triangle = np.array(
      # ( x      y      z )  (  x  纹理坐标的y为1-y )
       [-0.719, 0.016, 0.0,    0.141, 0.492,
        -0.713, 0.072, 0.0,    0.144, 0.464,
        -0.706, 0.142, 0.0,    0.147, 0.429,
        -0.700, 0.206, 0.0,    0.150, 0.397,
        -0.681, 0.290, 0.0,    0.159, 0.355,
        -0.669, 0.378, 0.0,    0.166, 0.311,
        -0.637, 0.448, 0.0,    0.181, 0.276,
        -0.606, 0.513, 0.0,    0.197, 0.244,
        -0.550, 0.564, 0.0,    0.225, 0.218,
        -0.488, 0.619, 0.0,    0.256, 0.190,
        -0.456, 0.671, 0.0,    0.272, 0.165,
        -0.394, 0.722, 0.0,    0.303, 0.139,
        -0.312, 0.777, 0.0,    0.344, 0.111,
        -0.244, 0.824, 0.0,    0.378, 0.088,
        -0.162, 0.870, 0.0,    0.419, 0.065,
        -0.062, 0.893, 0.0,    0.469, 0.053,
        0.031, 0.907, 0.0,    0.516, 0.046,
        0.119, 0.884, 0.0,    0.559, 0.058,
        0.188, 0.865, 0.0,    0.594, 0.067,
        0.250, 0.838, 0.0,    0.625, 0.081,
        0.325, 0.791, 0.0,    0.662, 0.104,
        0.394, 0.745, 0.0,    0.697, 0.128,
        0.456, 0.684, 0.0,    0.728, 0.158,
        0.525, 0.619, 0.0,    0.762, 0.190,
        0.562, 0.550, 0.0,    0.781, 0.225,
        0.613, 0.476, 0.0,    0.806, 0.262,
        0.637, 0.411, 0.0,    0.819, 0.295,
        0.669, 0.346, 0.0,    0.834, 0.327,
        0.688, 0.276, 0.0,    0.844, 0.362,
        0.706, 0.211, 0.0,    0.853, 0.394,
        0.712, 0.155, 0.0,    0.856, 0.422,
        0.719, 0.081, 0.0,    0.859, 0.459,
        0.725, -0.007, 0.0,    0.863, 0.503,
        -0.562, -0.109, 0.0,    0.219, 0.555,
        -0.469, -0.151, 0.0,    0.266, 0.575,
        -0.363, -0.155, 0.0,    0.319, 0.578,
        -0.275, -0.146, 0.0,    0.362, 0.573,
        -0.238, -0.137, 0.0,    0.381, 0.568,
        -0.206, -0.100, 0.0,    0.397, 0.550,
        -0.281, -0.095, 0.0,    0.359, 0.548,
        -0.363, -0.100, 0.0,    0.319, 0.550,
        -0.475, -0.104, 0.0,    0.263, 0.552,
        0.175, -0.118, 0.0,    0.588, 0.559,
        0.275, -0.146, 0.0,    0.637, 0.573,
        0.369, -0.155, 0.0,    0.684, 0.578,
        0.475, -0.151, 0.0,    0.738, 0.575,
        0.550, -0.114, 0.0,    0.775, 0.557,
        0.481, -0.100, 0.0,    0.741, 0.550,
        0.381, -0.104, 0.0,    0.691, 0.552,
        0.288, -0.095, 0.0,    0.644, 0.548,
        0.175, -0.095, 0.0,    0.588, 0.548,
        -0.475, 0.039, 0.0,    0.263, 0.480,
        -0.425, 0.002, 0.0,    0.287, 0.499,
        -0.350, -0.007, 0.0,    0.325, 0.503,
        -0.281, 0.016, 0.0,    0.359, 0.492,
        -0.244, 0.067, 0.0,    0.378, 0.466,
        -0.300, 0.086, 0.0,    0.350, 0.457,
        -0.350, 0.081, 0.0,    0.325, 0.459,
        -0.431, 0.067, 0.0,    0.284, 0.466,
        0.212, 0.067, 0.0,    0.606, 0.466,
        0.244, 0.030, 0.0,    0.622, 0.485,
        0.312, 0.007, 0.0,    0.656, 0.497,
        0.387, 0.007, 0.0,    0.694, 0.497,
        0.450, 0.044, 0.0,    0.725, 0.478,
        0.400, 0.077, 0.0,    0.700, 0.462,
        0.325, 0.086, 0.0,    0.662, 0.457,
        0.244, 0.086, 0.0,    0.622, 0.457,
        -0.231, 0.573, 0.0,    0.384, 0.213,
        -0.137, 0.541, 0.0,    0.431, 0.230,
        -0.069, 0.531, 0.0,    0.466, 0.234,
        -0.019, 0.541, 0.0,    0.491, 0.230,
        0.038, 0.531, 0.0,    0.519, 0.234,
        0.113, 0.545, 0.0,    0.556, 0.227,
        0.206, 0.578, 0.0,    0.603, 0.211,
        0.175, 0.624, 0.0,    0.588, 0.188,
        0.100, 0.675, 0.0,    0.550, 0.162,
        -0.006, 0.689, 0.0,    0.497, 0.155,
        -0.106, 0.671, 0.0,    0.447, 0.165,
        -0.175, 0.633, 0.0,    0.412, 0.183 ], dtype=np.float32)
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
    # glDisable(GL_CULL_FACE)
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
       # ( x      y      z )  (  x    1-y )
       [-0.719, 0.016, 0.0,    0.141, 0.492,
        -0.713, 0.072, 0.0,    0.144, 0.464,
        -0.706, 0.142, 0.0,    0.147, 0.429,
        -0.700, 0.206, 0.0,    0.150, 0.397,
        -0.681, 0.290, 0.0,    0.159, 0.355,
        -0.669, 0.378, 0.0,    0.166, 0.311,
        -0.637, 0.448, 0.0,    0.181, 0.276,
        -0.606, 0.513, 0.0,    0.197, 0.244,
        -0.550, 0.564, 0.0,    0.225, 0.218,
        -0.488, 0.619, 0.0,    0.256, 0.190,
        -0.456, 0.671, 0.0,    0.272, 0.165,
        -0.394, 0.722, 0.0,    0.303, 0.139,
        -0.312, 0.777, 0.0,    0.344, 0.111,
        -0.244, 0.824, 0.0,    0.378, 0.088,
        -0.162, 0.870, 0.0,    0.419, 0.065,
        -0.062, 0.893, 0.0,    0.469, 0.053,
        0.031, 0.907, 0.0,    0.516, 0.046,
        0.119, 0.884, 0.0,    0.559, 0.058,
        0.188, 0.865, 0.0,    0.594, 0.067,
        0.250, 0.838, 0.0,    0.625, 0.081,
        0.325, 0.791, 0.0,    0.662, 0.104,
        0.394, 0.745, 0.0,    0.697, 0.128,
        0.456, 0.684, 0.0,    0.728, 0.158,
        0.525, 0.619, 0.0,    0.762, 0.190,
        0.562, 0.550, 0.0,    0.781, 0.225,
        0.613, 0.476, 0.0,    0.806, 0.262,
        0.637, 0.411, 0.0,    0.819, 0.295,
        0.669, 0.346, 0.0,    0.834, 0.327,
        0.688, 0.276, 0.0,    0.844, 0.362,
        0.706, 0.211, 0.0,    0.853, 0.394,
        0.712, 0.155, 0.0,    0.856, 0.422,
        0.719, 0.081, 0.0,    0.859, 0.459,
        0.725, -0.007, 0.0,    0.863, 0.503,
        -0.562, -0.109, 0.0,    0.219, 0.555,
        -0.469, -0.151, 0.0,    0.266, 0.575,
        -0.363, -0.155, 0.0,    0.319, 0.578,
        -0.275, -0.146, 0.0,    0.362, 0.573,
        -0.238, -0.137, 0.0,    0.381, 0.568,
        -0.206, -0.100, 0.0,    0.397, 0.550,
        -0.281, -0.095, 0.0,    0.359, 0.548,
        -0.363, -0.100, 0.0,    0.319, 0.550,
        -0.475, -0.104, 0.0,    0.263, 0.552,
        0.175, -0.118, 0.0,    0.588, 0.559,
        0.275, -0.146, 0.0,    0.637, 0.573,
        0.369, -0.155, 0.0,    0.684, 0.578,
        0.475, -0.151, 0.0,    0.738, 0.575,
        0.550, -0.114, 0.0,    0.775, 0.557,
        0.481, -0.100, 0.0,    0.741, 0.550,
        0.381, -0.104, 0.0,    0.691, 0.552,
        0.288, -0.095, 0.0,    0.644, 0.548,
        0.175, -0.095, 0.0,    0.588, 0.548,
        -0.475, 0.039, 0.0,    0.263, 0.480,
        -0.425, 0.002, 0.0,    0.287, 0.499,
        -0.350, -0.007, 0.0,    0.325, 0.503,
        -0.281, 0.016, 0.0,    0.359, 0.492,
        -0.244, 0.067, 0.0,    0.378, 0.466,
        -0.300, 0.086, 0.0,    0.350, 0.457,
        -0.350, 0.081, 0.0,    0.325, 0.459,
        -0.431, 0.067, 0.0,    0.284, 0.466,
        0.212, 0.067, 0.0,    0.606, 0.466,
        0.244, 0.030, 0.0,    0.622, 0.485,
        0.312, 0.007, 0.0,    0.656, 0.497,
        0.387, 0.007, 0.0,    0.694, 0.497,
        0.450, 0.044, 0.0,    0.725, 0.478,
        0.400, 0.077, 0.0,    0.700, 0.462,
        0.325, 0.086, 0.0,    0.662, 0.457,
        0.244, 0.086, 0.0,    0.622, 0.457,
        -0.231, 0.573, 0.0,    0.384, 0.213,
        -0.137, 0.541, 0.0,    0.431, 0.230,
        -0.069, 0.531, 0.0,    0.466, 0.234,
        -0.019, 0.541, 0.0,    0.491, 0.230,
        0.038, 0.531, 0.0,    0.519, 0.234,
        0.113, 0.545, 0.0,    0.556, 0.227,
        0.206, 0.578, 0.0,    0.603, 0.211,
        0.175, 0.624, 0.0,    0.588, 0.188,
        0.100, 0.675, 0.0,    0.550, 0.162,
        -0.006, 0.689, 0.0,    0.497, 0.155,
        -0.106, 0.671, 0.0,    0.447, 0.165,
        -0.175, 0.633, 0.0,    0.412, 0.183 ], dtype=np.float32)
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
     [  50,  49,  60,
        14,  76,  15,
        76,  14,  77,
        1,   0,  51,
        39,  54,  53,
        54,  39,  38,
        2,   1,  51,
        17,  75,  18,
        75,  17,  76,
        3,   2,  58,
        7,  67,   8,
        67,   7,   6,
        4,   3,  58,
        5,   4,  57,
        19,  75,  20,
        75,  19,  18,
        6,   5,  56,
        77,  13,  12,
        13,  77,  14,
        67,  10,   9,
        10,  67,  11,
        9,   8,  67,
        76,  17,  16,
        12,  11,  78,
        15,  76,  16,
        78,  11,  67,
        56,  68,  67,
        68,  56,  69,
        20,  75,  74,
        69,  55,  59,
        55,  69,  56,
        65,  27,  26,
        27,  65,  64,
        21,  20,  74,
        22,  21,  74,
        57,   4,  58,
        23,  22,  73,
        6,  56,  67,
        24,  23,  73,
        25,  24,  73,
        26,  25,  73,
        28,  64,  29,
        64,  28,  27,
        56,   5,  57,
        30,  29,  64,
        51,  41,  52,
        41,  51,  33,
        31,  30,  63,
        33,  51,   0,
        32,  31,  63,
        50,  60,  59,
        42,  38,  37,
        38,  42,  50,
        42,  37,  43,
        2,  51,  58,
        40,  39,  53,
        41,  40,  52,
        63,  47,  46,
        47,  63,  62,
        63,  46,  32,
        48,  47,  62,
        61,  48,  62,
        48,  61,  49,
        50,  55,  38,
        55,  50,  59,
        40,  53,  52,
        54,  38,  55,
        66,  71,  59,
        71,  66,  72,
        72,  66,  65,
        49,  61,  60,
        63,  30,  64,
        65,  26,  73,
        71,  69,  59,
        65,  73,  72,
        22,  74,  73,
        77,  12,  78 ], dtype=np.int8)

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

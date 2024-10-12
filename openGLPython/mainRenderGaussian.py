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
parser.add_argument('--inputVideo_path', default="./result/111.mp4", type=str, help='input a video to render frames')
parser.add_argument('--save_video', default=True, type=bool, help='if save frames to a video')
parser.add_argument('--saveVideo_path', default="./result/640-2.mp4", type=str, help='save frames to a video')
parser.add_argument('--concat_ori_result', default=True, type=bool, help='concat origin & result') 
parser.add_argument('--save_frames', default=True, type=bool, help='if save frames to a folder')
parser.add_argument('--saveFrames_path', default="./result/frames", type=str, help='save frames to a folder')
parser.add_argument('--show_on_screen', default=False, type=bool, help='show result on screen')
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
window_w, window_h = video_width, video_height # video_width//2, video_height//2
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(args.saveVideo_path, fourcc, fps, (window_w*2 if args.concat_ori_result else window_w, window_h), True)

# 创建窗口
print(f"window size:[{window_w},{window_h}]")
w = Window(window_w, window_h, args.project_name)

# 顶点数据
triangle = np.array(
    [-1.0, -1.0, 0.0,  0.0, 1.0,
      1.0, -1.0, 0.0,  1.0, 1.0, 
      1.0,  1.0, 0.0,  1.0, 0.0,	 
     -1.0, -1.0, 0.0,  0.0, 1.0,
      1.0,  1.0, 0.0,  1.0, 0.0,	 
     -1.0,  1.0, 0.0,  0.0, 0.0	], dtype=np.float32)
assert triangle.nbytes % (6*5) == 0, "不能被整除"
every_size = triangle.nbytes//(6*5)
print(triangle.nbytes, every_size)

# VAO & VBO
vao = glGenVertexArrays(1)
glBindVertexArray(vao)
vbo = VBO(triangle, GL_STATIC_DRAW)
vbo.bind()

# Dilation
shader1 = Shader("./shaders/Gaussian/MTFilter_Gaussian.vs", "./shaders/Gaussian/MTFilter_Gaussian.fs") # dilate  YcbCr_segmentation
shader1.setAttrib(0, 3, GL_FLOAT, every_size*5, 0)
shader1.setAttrib(1, 2, GL_FLOAT, every_size*5, every_size*3)
# Erosion
shader2 = Shader("./shaders/Gaussian/MTFilter_Gaussian.vs", "./shaders/Gaussian/MTFilter_Gaussian.fs")
shader2.setAttrib(0, 3, GL_FLOAT, every_size*5, 0)
shader2.setAttrib(1, 2, GL_FLOAT, every_size*5, every_size*3)
# LUT
shader3 = Shader("./shaders/Gaussian/MTFilter_Gaussian.vs", "./shaders/Gaussian/MTFilter_Gaussian.fs")
shader3.setAttrib(0, 3, GL_FLOAT, every_size*5, 0)
shader3.setAttrib(1, 2, GL_FLOAT, every_size*5, every_size*3)
# normal 2D
shader_2D = Shader("./shaders/base.vert", "./shaders/base.frag")
shader_2D.setAttrib(0, 3, GL_FLOAT, every_size*5, 0)
shader_2D.setAttrib(1, 2, GL_FLOAT, every_size*5, every_size*3)

# 创建Fbo&Texture [shader result]
fbo1 = FBO(window_w, window_h)
# 创建Fbo
fbo2 = FBO(window_w, window_h)
# 创建Fbo
fbo3 = FBO(window_w, window_h)
# 创建Fbo
fbo_2d = FBO(window_w, window_h)


# 创建纹理
# tex = Texture(idx=0, "./resource/sight.jpg")
tex = Texture(idx=0, texType=GL_TEXTURE_2D, imgType=GL_RGB, innerType=GL_RGB, dataType=GL_UNSIGNED_BYTE, w=video_width, h=video_height)
tex_aimask = Texture(idx=1, texType=GL_TEXTURE_2D, imgType=GL_RGB, innerType=GL_RGB, dataType=GL_UNSIGNED_BYTE, w=video_width, h=video_height)
tex_lut = Texture(idx=2, imgPath="./resource/whiting.png")

def quite_cap(self):
    cap.release()

# 渲染循环
iTime = 0.0
def render():
    # 读取每一帧
    # img = cv2.imread("./resource/sight.jpg")
    global frame_n
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_n)
    ret, img = cap.read()
    frame_n += 1
    print("\r" + f'{frame_n}/{total_frames}')

    # -----------------------------------------------
    # [shader1]
    fbo1.bind()
    shader1.use()
    glBindVertexArray(vao)
    tex.updateTex(shader1, "tex", img) # 原视频纹理
    glDrawArrays(GL_TRIANGLES, 0, 6)
    glBindTexture(GL_TEXTURE_2D, GL_NONE)
    glBindVertexArray(0)
    glUseProgram(GL_NONE)
    fbo1.unbind()

    # -----------------------------------------------
    # [shader2]
    fbo2.bind()
    shader2.use()
    glBindVertexArray(vao)
    # 
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, fbo1.uTexture) # shader1结果纹理
    shader2.setUniform("tex", 0)
    #
    glDrawArrays(GL_TRIANGLES, 0, 6)
    glBindTexture(GL_TEXTURE_2D, GL_NONE)
    glBindVertexArray(0)
    glUseProgram(GL_NONE)
    fbo2.unbind()

    # -----------------------------------------------
    # glViewport(0, 0, window_w//2, window_h//2)
    # [shader3]
    fbo3.bind()
    shader3.use()
    glBindVertexArray(vao)
    #
    # tex.updateTex(shader3, "tex", img) # 原视频纹理
    # 
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, fbo2.uTexture) # shader2结果纹理
    shader3.setUniform("tex", 0)
    #
    # tex_lut.useTex(shader3, "tex_lut")
    #
    # global iTime
    # iTime += 0.5
    # shader3.setUniform("strength", iTime)
    #
    glDrawArrays(GL_TRIANGLES, 0, 6)
    glBindTexture(GL_TEXTURE_2D, GL_NONE)
    glBindVertexArray(0)
    glUseProgram(GL_NONE)
    fbo3.unbind()

    # -----------------------------------------------
    # draw normal 2D on screen
    if(not args.show_on_screen):
        fbo_2d.bind()
    shader_2D.use()
    glBindVertexArray(vao)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, fbo3.uTexture)
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

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
parser.add_argument('--inputVideo_path', default="./resource/origin/2.mp4", type=str, help='input a video to render frames')
parser.add_argument('--inputMask_path', default="./resource/640/2.avi", type=str, help='input a ai mask result video to render frames')
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

# YCbCr segment
shader = Shader("./shaders/base.vert", "./shaders/YcbCr_segmentation.frag") # dilate  YcbCr_segmentation
shader.setAttrib(0, 3, GL_FLOAT, every_size*5, 0)
shader.setAttrib(1, 2, GL_FLOAT, every_size*5, every_size*3)
# dilate
shader_dilate = Shader("./shaders/base.vert", "./shaders/dilate.frag")
shader_dilate.setAttrib(0, 3, GL_FLOAT, every_size*5, 0)
shader_dilate.setAttrib(1, 2, GL_FLOAT, every_size*5, every_size*3)
# LUT
shader_lut = Shader("./shaders/base.vert", "./shaders/lut.frag")
shader_lut.setAttrib(0, 3, GL_FLOAT, every_size*5, 0)
shader_lut.setAttrib(1, 2, GL_FLOAT, every_size*5, every_size*3)
# normal 2D
shader_2D = Shader("./shaders/base.vert", "./shaders/base.frag")
shader_2D.setAttrib(0, 3, GL_FLOAT, every_size*5, 0)
shader_2D.setAttrib(1, 2, GL_FLOAT, every_size*5, every_size*3)

# 创建Fbo&Texture [shader result]
fbo_ycbcr = FBO(window_w, window_h)
# 创建Fbo
fbo_dilate = FBO(window_w, window_h)
# 创建Fbo
fbo_lut = FBO(window_w, window_h)
# 创建Fbo
fbo_2d = FBO(window_w, window_h)


# 创建纹理
# tex = Texture(idx=0, "./resource/sight.jpg")
tex = Texture(idx=0, texType=GL_TEXTURE_2D, imgType=GL_RGB, innerType=GL_RGB, dataType=GL_UNSIGNED_BYTE, w=video_width, h=video_height)
tex_aimask = Texture(idx=1, texType=GL_TEXTURE_2D, imgType=GL_RGB, innerType=GL_RGB, dataType=GL_UNSIGNED_BYTE, w=video_width, h=video_height)
tex_lut = Texture(idx=2, imgPath="./resource/whiting.png")

def quite_cap(self):
    cap.release()
    cap_aimask.release()

# 渲染循环
def render():
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
    # draw framebuffer [YCbCr]
    fbo_ycbcr.bind()
    shader.use()
    glBindVertexArray(vao)
    tex.updateTex(shader, "tex", img) # 原视频纹理
    glDrawArrays(GL_TRIANGLES, 0, 6)
    glBindTexture(GL_TEXTURE_2D, GL_NONE)
    glBindVertexArray(0)
    glUseProgram(GL_NONE)
    fbo_ycbcr.unbind()

    # -----------------------------------------------
    # draw framebuffer [dilate]
    fbo_dilate.bind()
    shader_dilate.use()
    glBindVertexArray(vao)
    # 
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, fbo_ycbcr.uTexture) # YCbCr结果纹理
    shader_dilate.setUniform("tex", 0)
    #
    tex_aimask.updateTex(shader_dilate, "tex_aimask", img_aimask) # 原视频纹理
    #
    glDrawArrays(GL_TRIANGLES, 0, 6)
    glBindTexture(GL_TEXTURE_2D, GL_NONE)
    glBindVertexArray(0)
    glUseProgram(GL_NONE)
    fbo_dilate.unbind()

    # -----------------------------------------------
    # draw framebuffer [lut]
    fbo_lut.bind()
    shader_lut.use()
    glBindVertexArray(vao)
    #
    tex.updateTex(shader_lut, "tex", img) # 原视频纹理
    # 
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, fbo_dilate.uTexture) # mask结果纹理
    shader_lut.setUniform("tex_mask", 1)
    #
    tex_lut.useTex(shader_lut, "tex_lut")
    #
    glDrawArrays(GL_TRIANGLES, 0, 6)
    glBindTexture(GL_TEXTURE_2D, GL_NONE)
    glBindVertexArray(0)
    glUseProgram(GL_NONE)
    fbo_lut.unbind()

    # -----------------------------------------------
    # draw normal 2D on screen
    if(not args.show_on_screen):
        fbo_2d.bind()
    shader_2D.use()
    glBindVertexArray(vao)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, fbo_lut.uTexture)
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

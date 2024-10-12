import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
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
import glfw

def fit_video_to_screen(w, h, screen_w, screen_h):
    # 计算宽度和高度的比例
    width_ratio = screen_w / w
    height_ratio = screen_h / h
    # 选择缩放比例，使得视频不会超出屏幕的任何一边
    scale_ratio = min(width_ratio, height_ratio)
    # 计算新的宽度和高度
    new_w = w * scale_ratio
    new_h = h * scale_ratio
    return int(new_w), int(new_h)

parser = argparse.ArgumentParser()
parser.add_argument('--project_name', default="SkinSmooth CS", type=str, help="Window's name")
parser.add_argument('--inputVideo_path', default=r"D:\OpenGlProject\OpenGLPython\resource\origin\out.mp4", type=str, help='input a video to render frames')
parser.add_argument('--inputMask_path', default=r"D:\OpenGL_CMake_CS\res\picture\alpha_mask_1.jpg", type=str, help='input a skin mask image')
parser.add_argument('--save_video', default=False, type=bool, help='if save frames to a video')
parser.add_argument('--saveVideo_path', default="./result/640-2.mp4", type=str, help='save frames to a video')
parser.add_argument('--concat_ori_result', default=False, type=bool, help='concat origin & result') 
parser.add_argument('--save_frames', default=True, type=bool, help='if save frames to a folder')
parser.add_argument('--saveFrames_path', default="./result/frames", type=str, help='save frames to a folder')
parser.add_argument('--show_on_screen', default=True, type=bool, help='show result on screen')
parser.add_argument('--show_first_frame', default=False, type=bool, help='just show first frame on screen')
args = parser.parse_args()

ensure_directory_exists(os.path.dirname(args.saveVideo_path))
ensure_directory_exists(args.saveFrames_path)

# 滑动条
cv2.namedWindow('Adjustments')
cv2.resizeWindow('Adjustments', 300, 150)
# 第一个参数是滑动条的名字，第二个参数是窗口的名字，第三个参数是滑动条的值范围，第四个参数是回调函数
cv2.createTrackbar('intensity', 'Adjustments', 0, 100, lambda x: None) # 0-100的范围
cv2.createTrackbar('blurKernel', 'Adjustments', 3, 55, lambda x: None) # 0-100的范围
cv2.createTrackbar('blur', 'Adjustments', 0, 100, lambda x: None)      # 0-100的范围
cv2.createTrackbar('sharpen', 'Adjustments', 0, 100, lambda x: None)   # 0-100的范围

# 帧数
frame_n = 1
cap = cv2.VideoCapture(args.inputVideo_path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# 获取主监视器分辨率
if not glfw.init():
    print("Failed to initialize GLFW")
monitor = glfw.get_primary_monitor()
video_mode = glfw.get_video_mode(monitor).size
screen_w, screen_h = video_mode.width, video_mode.height
print(f"Current screen resolution: {screen_w} x {screen_h}")
# 适配占满屏幕
new_w, new_h = fit_video_to_screen(video_width, video_height, screen_w, screen_h)
print(f"new wh:{new_w} x {new_h}")

# 保存视频
window_w, window_h = new_w, new_h # video_width, video_height
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(args.saveVideo_path, fourcc, fps, (window_w*2 if args.concat_ori_result else window_w, window_h), True)

# 创建窗口
print(f"window size:[{window_w},{window_h}]")
w = Window(window_w, window_h, args.project_name)

# 获取显卡信息
renderer = glGetString(GL_RENDERER)
vendor = glGetString(GL_VENDOR)
version = glGetString(GL_VERSION)
print(f"Renderer: {renderer.decode('utf-8')}")
print(f"Vendor: {vendor.decode('utf-8')}")
print(f"OpenGL Version: {version.decode('utf-8')}")

# #########################################################################
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

# Green segment
shader = Shader("./shaders/base.vert", "./shaders/Smooth.frag") # dilate  Green_segmentation
shader.setAttrib(0, 3, GL_FLOAT, every_size*5, 0)
shader.setAttrib(1, 2, GL_FLOAT, every_size*5, every_size*3)
# normal 2D
shader_2D = Shader("./shaders/base.vert", "./shaders/base.frag")
shader_2D.setAttrib(0, 3, GL_FLOAT, every_size*5, 0)
shader_2D.setAttrib(1, 2, GL_FLOAT, every_size*5, every_size*3)

# 创建Fbo&Texture [shader result]
fbo_green = FBO(window_w, window_h)
# 创建Fbo
fbo_2d = FBO(window_w, window_h)

# 创建纹理
tex = Texture(idx=0, texType=GL_TEXTURE_2D, imgType=GL_RGB, innerType=GL_RGB, dataType=GL_UNSIGNED_BYTE, w=video_width, h=video_height)
tex_blur = Texture(idx=1, texType=GL_TEXTURE_2D, imgType=GL_RGB, innerType=GL_RGB, dataType=GL_UNSIGNED_BYTE, w=video_width, h=video_height)
tex_mask = Texture(idx=2, imgPath=r"D:\OpenGL_CMake_CS\res\picture\alpha_mask_1.jpg")

def quite_cap(self):
    cap.release()

# 渲染循环
def render():
    # 读取每一帧
    # img = cv2.imread("./resource/sight.jpg")
    global frame_n
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_n)
    ret, img = cap.read()
    if not args.show_first_frame:
        frame_n += 1
    print("\r" + f'{frame_n}/{total_frames}', end="")
    # -----------------------------------------------
    # draw framebuffer [Smooth]
    fbo_green.bind()
    shader.use()
    glBindVertexArray(vao)
    tex.updateTex(shader, "s_texture", img) # 原视频纹理
    blurKernel = 3 if(cv2.getTrackbarPos('blurKernel', 'Adjustments')) < 3 else cv2.getTrackbarPos('blurKernel', 'Adjustments')
    if blurKernel % 2 != 1:
        blurKernel=blurKernel+1
    for _ in range(blurKernel):
        img = cv2.blur(img, (9, 9))
    tex_blur.updateTex(shader, "s_textureBlur", img) # 均值模糊  
    tex_mask.useTex(shader, "s_textureMask") # mask
    shader.setUniform("intensity", cv2.getTrackbarPos('intensity', 'Adjustments')/100.0)
    glUniform2fv(glGetUniformLocation(shader.shader, "windowSize"), 1, [video_width, video_height])
    shader.setUniform("blurCoefficient", cv2.getTrackbarPos('blur', 'Adjustments')/100.0)
    shader.setUniform("sharpenStrength", cv2.getTrackbarPos('sharpen', 'Adjustments')/100.0)
    glDrawArrays(GL_TRIANGLES, 0, 6)
    glBindTexture(GL_TEXTURE_2D, GL_NONE)
    glBindVertexArray(0)
    glUseProgram(GL_NONE)
    fbo_green.unbind()
    # -----------------------------------------------
    # draw normal 2D on screen
    if(not args.show_on_screen):
        fbo_2d.bind()
    shader_2D.use()
    glBindVertexArray(vao)
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

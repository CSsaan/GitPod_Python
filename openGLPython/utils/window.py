from OpenGL.GL import *	# 导入PyOpenGL
import glfw				# 导入GLFW


class Window:
    def __init__(self, width, height, title, bgColor=(0.0, 0.0, 0.0, 1.0)):
        # 初始化GLFW
        if not glfw.init():
            raise RuntimeError("GLFW初始化失败！")
        # 创建窗口
        self.width, self.height, self.title, self.bgColor = width, height, title, bgColor
        # 设置窗口属性
        glfw.window_hint(glfw.SAMPLES, 4)  # 设置4倍多重采样抗锯齿
        self.window = glfw.create_window(width, height, title, None, None)
        # 显示窗口
        self.show()
        glViewport(0, 0, self.width, self.height)

    def cbfun_callback(self, window, width, height):
        print(f"w:{width}, h:{height}")
        glViewport(0, 0, width, height)

    def show(self):
        glfw.make_context_current(self.window)
        
        # 设置交换间隔为 0，以解除垂直同步
        glfw.swap_interval(0)
        
        glfw.set_window_size_limits(self.window, self.width, self.height, self.width, self.height) # 固定窗口大小
        # glfw.set_framebuffer_size_callback(self.window, self.cbfun_callback) # 调整窗口大小的回调函数
        # glViewport(0, 0, self.width, self.height)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)

    def loop(self, render_func):
        while not glfw.window_should_close(self.window):
            glClearColor(*self.bgColor)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # 在此处可以绘制物体
            # ...
            render_func()

            glfw.swap_buffers(self.window)
            glfw.poll_events()
            if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
                glfw.set_window_should_close(self.window, True)

        glfw.destroy_window(self.window)
        glfw.terminate()

def print1():
    print(1)

if __name__ == '__main__':
    w = Window(1920, 1080, "Test")
    w.loop(print1)

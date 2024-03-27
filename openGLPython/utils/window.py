from OpenGL.GL import *	# 导入PyOpenGL
import glfw				# 导入GLFW


class Window:
    def __init__(self, width, height, title, bgColor=(0.0, 0.0, 0.0, 1.0)):
        # 初始化GLFW
        if not glfw.init():
            raise RuntimeError("GLFW初始化失败！")
        # 创建窗口
        self.width, self.height, self.title, self.bgColor = width, height, title, bgColor
        self.window = glfw.create_window(width, height, title, None, None)
        # 显示窗口
        self.show()

    def show(self):
        glfw.make_context_current(self.window)
        glfw.set_window_size_limits(self.window, self.width, self.height, self.width, self.height)
        glViewport(0, 0, self.width, self.height)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

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

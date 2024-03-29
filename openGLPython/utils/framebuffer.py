import numpy as np
from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *
from OpenGL.GL.ARB.framebuffer_object import glGenFramebuffers, glBindFramebuffer, glFramebufferTexture2D, glCheckFramebufferStatus

class FBO:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.FBO = glGenFramebuffers(1)
        self.uTexture = glGenTextures(1)

        print(f"[GenFBO&Texture] FboId:{self.FBO}, uTextureId:{self.uTexture}")
        
        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)
        
        glBindTexture(GL_TEXTURE_2D, self.uTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.uTexture, 0)
        
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            print("Framebuffer creation failed!")
        
        glBindTexture(GL_TEXTURE_2D, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)

    def unbind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

if __name__ == "__main__":
    # 使用示例
    width = 800
    height = 600
    framebuffer = FBO(width, height)

from OpenGL.GL import *
from utils.myUtils import check_error
# from PIL import Image
import cv2
import numpy as np


class Texture:
    def __init__(self, idx, imgPath=None, texType=GL_TEXTURE_2D,
                 imgType=GL_RGB, innerType=None, dataType=GL_UNSIGNED_BYTE, w=None, h=None):
        
        if not innerType:
            innerType = imgType
        self.innerType = innerType
        self.dataType = dataType
        self.idx = idx

        if(imgPath is not None):
            # 创建纹理对象
            self.tex = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.tex)
            # 读取纹理数据
            img = cv2.imread(imgPath)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.w, self.h, _ = img.shape
            img = np.array(img, np.int8)
            print(imgPath, ": ", self.h, self.w)
            check_error("glTexImage2D")
            # 将纹理数据传给GPU
            glTexImage2D(texType, 0, innerType, self.h, self.w, 0, imgType, dataType, img)
            glGenerateMipmap(texType)
            # 纹理设置
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glBindTexture(texType, GL_NONE)
        else:
            assert(h != None and w != None)
            # 创建纹理对象
            self.tex = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.tex)
            self.w, self.h = w, h
            glTexImage2D(texType, 0, innerType, self.w, self.h, 0, imgType, dataType, None)
            glGenerateMipmap(texType)
            # 纹理设置
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glBindTexture(texType, GL_NONE)

    def useTex(self, shader, name=None):
        """ 设置纹理索引 """
        if not name:
            name = "tex" + str(self.idx)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glActiveTexture(GL_TEXTURE0 + self.idx)
        shader.setUniform(name, self.idx)

    def updateTex(self, shader, name, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        _w, _h, _ = img.shape
        img = np.array(img, np.int8)
        #
        glActiveTexture(GL_TEXTURE0 + self.idx)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.w, self.h, self.innerType, self.dataType, img)
        shader.setUniform(name, self.idx)

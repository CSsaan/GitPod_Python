import OpenGL.GL as gl
import os 

def check_error(msg):
    error = gl.glGetError()
    if error != gl.GL_NO_ERROR:
        print(f"[{msg}] error: {error}")

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
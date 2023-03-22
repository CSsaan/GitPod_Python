import numpy as np
 
from PIL import Image
 
paths = ['oriImg/B191.jpg', 'oriImg/B255.jpg', 'oriImg/G191.jpg', 'oriImg/G255.jpg', 'oriImg/R191.jpg', 'oriImg/R255.jpg']
img_array = ''
img = ''
for i, v in enumerate(paths):
    if i == 0:
        img = Image.open(v)  # 打开图片
        img_array = np.array(img)  # 转化为np array对象
    if i > 0:
        img_array2 = np.array(Image.open(v))
        img_array = np.concatenate((img_array, img_array2), axis=1)  # 横向拼接
        # img_array = np.concatenate((img_array, img_array2), axis=0)  # 纵向拼接
        img = Image.fromarray(img_array)
 
 
 
# 保存图片
img.save('outImg/test.jpg')
print("done.")
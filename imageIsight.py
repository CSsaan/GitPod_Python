import numpy as np
import matplotlib.pyplot as plt
import cv2
import pandas as pd
import win32com.client as win32
from pathlib import Path

# 假设img是单通道图片的像素值矩阵，w为宽度，h为高度
Img = cv2.imread("testlidar.jpg")
# Img = cv2.rotate(Img, cv2.ROTATE_90_COUNTERCLOCKWISE)
# Img = cv2.resize(Img,dsize=(20,20),fx=1,fy=1,interpolation=cv2.INTER_LINEAR)
imGray = cv2.cvtColor(Img, cv2.COLOR_BGR2GRAY)
w, h = imGray.shape[:2]
print(w, h)


# 创建DataFrame保存像素值
data_df = pd.DataFrame(imGray)

# 将文件写入excel表格中
writer = pd.ExcelWriter('hhh.xlsx')  #关键2，创建名称为hhh的excel表格
data_df = data_df.style.background_gradient(cmap='coolwarm')
data_df.to_excel(writer,'page_1',float_format='%.5f')
writer._save()

out_file = Path.cwd() / "hhh.xlsx"
excel = win32.gencache.EnsureDispatch('Excel.Application')
excel.Visible = True
excel.Workbooks.Open(out_file)

excel_file_path = 'path_to_your_excel_file.xlsx'
os.system(f'start excel {excel_file_path}')
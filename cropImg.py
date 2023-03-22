import cv2 as cv
import os

def crop_image(image_dir, output_path, size):   # image_dir 批量处理图像文件夹 size 裁剪后的尺寸
    # 获取图片路径列表
    file_path_list = []
    for filename in os.listdir(image_dir):
        file_path = os.path.join(image_dir, filename)
        file_path_list.append(file_path)

    # 逐张读取图片剪裁
    for counter, image_path in enumerate(file_path_list):
        image = cv.imread(image_path)
        h, w = image.shape[0:2]
        w_begin = size[0]
        w_end = size[1]

        
        cropped_img = image[w_begin:w_end, : , : ]
        cv.imwrite(output_path + '/' + file_path_list[counter][7:-4] + '.jpg', cropped_img)
        print(output_path + '/' + file_path_list[counter][8:-4] + '.jpg')


if __name__ == "__main__":
    image_dir = "oriImg/"
    output_path = "outImg/"
    size = [1050, 1700]
    crop_image(image_dir, output_path, size)

from PIL import Image

def process_image(file_path):
    # 打开图片
    image = Image.open(file_path).convert("RGBA")
    width, height = image.size

    # 获取图片的像素数据
    pixel_data = image.load()

    # 遍历每个像素
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixel_data[x, y]

            # 如果alpha大于0，则将alpha值设置为0.8
            if a > 0:
                pixel_data[x, y] = (r, g, b, int(0.6 * 255))

    # 保存修改后的图片
    image.save("output/arrowblack.png")
    print("done.")


def set_border_to_black(image_path):
    # 打开图片
    image = Image.open(image_path)

    # 获取图片的宽度和高度
    width, height = image.size

    # 将图片周围一圈的像素值设置为黑色
    for x in range(width):
        for y in range(height):
            if (x == 0 or x == width - 1 or y == 0 or y == height - 1) or (x == 1 or x == width - 2 or y == 1 or y == height - 2) or (x == 2 or x == width - 3 or y == 2 or y == height - 3):
                image.putpixel((x, y), (0, 0, 0))  # 设置像素值为黑色

    # 保存修改后的图片
    image.save("output/map.jpg")
    print("done..")


def change_rgb_size(image_path):
    # 打开原始图片
    image = Image.open(image_path)

    # 获取图片的宽度和高度
    width, height = image.size

    # 创建一个新的图片对象，与原始图片大小相同
    new_image = Image.new('RGB', (width, height))

    # 遍历每个像素点，将RGB值除以20，并设置到新的图片对象中
    for x in range(width):
        for y in range(height):
            r, g, b = image.getpixel((x, y))
            r = r // 20
            g = g // 20
            b = b // 20
            new_image.putpixel((x, y), (r, g, b))
    # 保存新的图片
    new_image.save('output/testlidar_result.jpg')
    print('done.')


if __name__ == "__main__":
    # 调用函数处理图片
    # process_image("srcImg/arrowblack.png")

    # 调用函数并传入图片路径
    # set_border_to_black("srcImg/map.jpg")

    # 调整像素值，最大值不超过13
    change_rgb_size("srcImg/testlidar.jpg")
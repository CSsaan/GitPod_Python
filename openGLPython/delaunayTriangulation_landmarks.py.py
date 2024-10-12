import numpy as np
import cv2
import random

# -------------------- data ----------------------
# mask图
eyes_img_path = r'D:\AndroidStudioProject\SOBeauty\Beauty\3_CameraSpecialEffect-FBOFaceReshape\app\src\main\assets\resource\eyes.png'
lip_img_path = r'D:\AndroidStudioProject\SOBeauty\Beauty\3_CameraSpecialEffect-FBOFaceReshape\app\src\main\assets\resource\teeth_mask.jpg'
face_img_path = r'D:\AndroidStudioProject\SOBeauty\Beauty\3_CameraSpecialEffect-FBOFaceReshape\app\src\main\assets\resource\facemask.jpg'
# mask上对应的关键点归一化坐标
# 嘴唇(8个关键点)
x_lip = [0.154639, 0.398625, 0.512027, 0.611684, 0.872852, 0.639176, 0.522337, 0.398625]
y_lip = [0.378788, 0.196970, 0.287879, 0.212121, 0.378788, 0.848485, 0.846364, 0.843333]
# 眼睛(16个关键点)
x_eyes = [0.102, 0.175, 0.370, 0.446, 0.353, 0.197, 0.566, 0.659, 0.802, 0.884, 0.812, 0.681, 0.273, 0.275, 0.721, 0.739]
y_eyes = [0.465, 0.301, 0.310, 0.603, 0.732, 0.689, 0.629, 0.336, 0.318, 0.465, 0.681, 0.750, 0.241, 0.758, 0.275, 0.758]
# 脸(79个关键点)
x_face = [0.141, 0.144, 0.147, 0.15, 0.16, 0.166, 0.181, 0.197, 0.225, 0.256,     0.272, 0.304, 0.344, 0.378, 0.419, 0.469, 0.516, 0.559, 0.594, 0.625,
          0.662, 0.696, 0.728, 0.762, 0.781, 0.806, 0.819, 0.834, 0.844, 0.853,   0.856, 0.859, 0.862, 0.219, 0.266, 0.319, 0.362, 0.382, 0.397, 0.36,
          0.319, 0.262, 0.588, 0.638, 0.684, 0.738, 0.775, 0.74, 0.69, 0.644,     0.588, 0.262, 0.288, 0.325, 0.36, 0.378, 0.35, 0.325, 0.284, 0.606,
          0.622, 0.656, 0.694, 0.725, 0.7, 0.662, 0.622, 0.384, 0.432, 0.466,     0.491, 0.518, 0.556, 0.603, 0.588, 0.55, 0.497, 0.447, 0.412]
y_face = [0.508, 0.536, 0.57, 0.603, 0.645, 0.689, 0.724, 0.756, 0.782, 0.810,    0.835, 0.86, 0.888, 0.912, 0.935, 0.946, 0.954, 0.942, 0.932, 0.918,
          0.896, 0.872, 0.842, 0.81, 0.774, 0.738, 0.705, 0.672, 0.638, 0.606,    0.578, 0.54, 0.497, 0.446, 0.425, 0.422, 0.427, 0.432, 0.45, 0.452,
          0.45, 0.448, 0.441, 0.427, 0.422, 0.425, 0.444, 0.45, 0.448, 0.452,     0.452, 0.52, 0.501, 0.497, 0.508, 0.534, 0.542, 0.54, 0.534, 0.534,
          0.515, 0.503, 0.503, 0.522, 0.538, 0.542, 0.542, 0.786, 0.77, 0.766,    0.77, 0.766, 0.773, 0.788, 0.812, 0.838, 0.844, 0.835, 0.816]
# ------------------------------------------------

def load_image_and_get_size(choice, upscale=1):
    switch = {
        "lip": lip_img_path,
        "eyes": eyes_img_path,
        "face": face_img_path,
        # 可以根据需要继续添加其他选择
    }
    image_path = switch.get(choice)
    if image_path is not None:
        img = cv2.imread(image_path)
        img = cv2.resize(img, (img.shape[1]*upscale, img.shape[0]*upscale))
        height, width = img.shape[:2]
        return img, width, height
    else:
        return None, None, None

def get_points(widthHeight, choice="lip"):
    switch = {
        "lip": (x_lip, y_lip),
        "eyes": (x_eyes, y_eyes),
        "face": (x_face, y_face),
        # 可以根据需要继续添加其他选择
    }
    x_data, y_data = switch.get(choice, (None, None))
    if x_data is not None and y_data is not None:
        points = list(map(lambda i: (round(x_data[i]*widthHeight[0]), round(y_data[i]*widthHeight[1])), range(len(x_data))))
        return points
    else:
        return None

#Check if a point is insied a rectangle
def rect_contains(rect, point):
    if point[0] <rect[0]:
        return False
    elif point[1]<rect[1]:
        return  False
    elif point[0]>rect[2]:
        return False
    elif point[1] >rect[3]:
        return False
    return True

# Draw a point
def draw_point(img, p, color):
    cv2.circle(img, p, 2, color)

def crop_triangle(image, vertices):
    # 三角形区域全1
    triangle_area = np.array([[vertices[0][0],vertices[0][1]], [vertices[1][0],vertices[1][1]], [vertices[2][0],vertices[2][1]]], np.int32)
    triangle_area = triangle_area.reshape((-1, 1, 2))
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, [triangle_area], (255, 255, 255))
    _, ori_binary = cv2.threshold(mask, 125, 1, cv2.THRESH_BINARY)
    # 三角形区域mask占比
    vertices = vertices.reshape((-1, 1, 2))
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, [vertices], (255, 255, 255))
    cropped_image = cv2.bitwise_and(image, mask)
    _, binary = cv2.threshold(cropped_image, 100, 1, cv2.THRESH_BINARY)
    iou = np.sum(binary) / np.sum(ori_binary)
    return cropped_image, iou

#Draw delaunay triangles
def draw_delaunay(img, subdiv, delaunay_color, points, points_id_xy, print_index=False):
    trangleList = subdiv.getTriangleList()
    size = img.shape
    r = (0, 0, size[1], size[0])
    print("OpenGL的glDrawElements所有三角形的indices:")
    for t in  trangleList:
        # print("t:", t, type(t))
        pt1 = (int(t[0]), int(t[1]))
        pt2 = (int(t[2]), int(t[3]))
        pt3 = (int(t[4]), int(t[5]))
        if (rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3)):
            cv2.line(img, pt1, pt2, delaunay_color, 1)
            cv2.line(img, pt2, pt3, delaunay_color, 1)
            cv2.line(img, pt3, pt1, delaunay_color, 1)
        p1 = points.index(pt1)
        p2 = points.index(pt2)
        p3 = points.index(pt3)
        if(print_index):
            # 判断三角形区域是否为mask
            if(points_id_xy is not None):
                # print("now Triangle: ", points_id_xy[p1], points_id_xy[p2], points_id_xy[p3])
                pts = np.array([[points_id_xy[p1][0], points_id_xy[p1][1]], [points_id_xy[p2][0], points_id_xy[p2][1]], [points_id_xy[p3][0], points_id_xy[p3][1]]], np.int32) # 三角形顶点
                cropped_triangle, iou = crop_triangle(img, pts) # 裁剪三角形
                # print("iou: ",iou)
                if (iou > 0.5):
                    print(f"{p1:3d}, {p2:3d}, {p3:3d},")
        else:
            print("pass")
    print("已经自动排除非mask区域的三角形")

# Draw voronoi diagram
def draw_voronoi(img,subdiv):
    (facets, centers) = subdiv.getVoronoiFacetList([])
    for i in range(0, len(facets)):
        ifacet_arr = []
        for f in facets[i]:
            ifacet_arr.append(f)
        ifacet = np.array(ifacet_arr, np.int_)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        cv2.fillConvexPoly(img, ifacet, color)
        ifacets = np.array([ifacet])
        cv2.polylines(img, ifacets, True, (0, 0, 0), 1)
        cv2.circle(img, (int(centers[i][0]), int(centers[i][1])), 3, (0, 0, 0))


# Draw number
def draw_number(img, subdiv):
    result = {}  # 创建一个空字典 id:(x,y)
    height, width = img.shape[:2]
    (facets, centers) = subdiv.getVoronoiFacetList([])
    # print(len(centers),type(centers),centers[0])
    for i in range(0, len(centers)):
        # 图片 添加的文字 位置 字体 字体大小 字体颜色 字体粗细
        print(f"pointID:{i:2d}, gl_Position+textureUV:({centers[i][0]/width*2.0-1.0:.3f}, {centers[i][1]/height*2.0-1.0:.3f}, 0.0,    {centers[i][0]/width:.3f}, {1.0-centers[i][1]/height:.3f})")
        cv2.putText(img, str(i)+f"({centers[i][0]/width:.3f},{centers[i][1]/height:.3f})", (int(centers[i][0]), int(centers[i][1]-10)), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(255, 90, 125), thickness=1)
        result[i] = (int(centers[i][0]), int(centers[i][1]))
    return result


if __name__ == '__main__':

    # --------------- config params ------------------
    chosen_name = "face" # 选择对应区域的mask：例如 eyes \ lip \ face \ ...
    upscale = 1          # 图像放大倍率（默认1）
    animate = False      # 动态显示绘制三角剖分动画
    # ------------------------------------------------

    # 加载图像
    chosen_image, image_width, image_height = load_image_and_get_size(chosen_name, upscale)
    assert chosen_image is not None, "chosen_image加载图像失败, 为None."
    print("成功加载图像 - 宽度：{}，高度：{}.".format(image_width, image_height))
    # 加载关键点
    chosen_points = get_points((image_width, image_height), chosen_name)
    print("all points: ", chosen_points)
    # 在图像上绘制每个点
    for point in chosen_points:
        cv2.circle(chosen_image, point, 2, (0, 255, 0), -1)
    cv2.imshow('Image with points', chosen_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 绘制三角剖分图
    img = chosen_image.copy()
    img_orig = img.copy()
    #Rectangle to be used with Subdiv2D
    size = img.shape
    rect = (0, 0, size[1], size[0])
    #Create an instance of Subdiv2d
    subdiv = cv2.Subdiv2D(rect)
    #Insert points into subdiv
    for p in chosen_points:
        subdiv.insert(p)
        #Show animate # 动态绘制
        if animate:
            img_copy = img_orig.copy()
            #Draw delaunay triangles
            draw_delaunay(img_copy, subdiv, (0,0,255), chosen_points, None, print_index=False)
            cv2.imshow("三角剖分(Delaunay Triangulation)", img_copy)
            cv2.waitKey(50) 
    #Draw delaunary triangles
    points_id_xy = draw_number(img, subdiv)
    print("points_id-xy: ", points_id_xy)
    draw_delaunay(img, subdiv, (0,0,255), chosen_points, points_id_xy, print_index=True)
    #Draw points
    for p in chosen_points:
        draw_point(img, p, (0,0,255))
    #Allocate space for Voroni Diagram
    img_voronoi = np.zeros(img.shape, dtype = img.dtype)
    #Draw Voonoi diagram
    draw_voronoi(img_voronoi, subdiv)
    #Show results
    cv2.imshow("三角剖分(Delaunay Triangulation)", img)
    cv2.imshow("维诺图(Voronoi Diagram)", img_voronoi)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("done.")

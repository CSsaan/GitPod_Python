import cv2
import numpy as np
import random

#Check if a point is insied a rectangle
def rect_contains(rect,point):
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
def draw_point(img,p,color):
    cv2.circle(img,p,2,color)

#Draw delaunay triangles
def draw_delaunay(img,subdiv,delaunay_color,points):
    trangleList = subdiv.getTriangleList()
    size = img.shape
    r = (0,0,size[1],size[0])
    print("glDrawElements所有三角形的indices:")
    for t in  trangleList:
        # print("t:",t,type(t))
        pt1 = (int(t[0]),int(t[1]))
        pt2 = (int(t[2]),int(t[3]))
        pt3 = (int(t[4]),int(t[5]))
        if (rect_contains(r,pt1) and rect_contains(r,pt2) and rect_contains(r,pt3)):
            cv2.line(img,pt1,pt2,delaunay_color,1)
            cv2.line(img,pt2,pt3,delaunay_color,1)
            cv2.line(img,pt3,pt1,delaunay_color,1)
        p1 = points.index(pt1)
        p2 = points.index(pt2)
        p3 = points.index(pt3)
        print(p1,p2,p3)

# Draw voronoi diagram
def draw_voronoi(img,subdiv):
    (facets,centers) = subdiv.getVoronoiFacetList([])
    for i in range(0,len(facets)):
        ifacet_arr = []
        for f in facets[i]:
            ifacet_arr.append(f)
        ifacet = np.array(ifacet_arr,np.int_)
        color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        cv2.fillConvexPoly(img,ifacet,color)
        ifacets = np.array([ifacet])
        cv2.polylines(img,ifacets,True,(0,0,0),1)
        cv2.circle(img,(int(centers[i][0]),int(centers[i][1])),3,(0,0,0))


# Draw number
def draw_number(img,subdiv):
    (facets,centers) = subdiv.getVoronoiFacetList([])
    # print(len(centers),type(centers),centers[0])
    for i in range(0,len(centers)):
        # 图片 添加的文字 位置 字体 字体大小 字体颜色 字体粗细
        cv2.putText(img, str(i), (int(centers[i][0]), int(centers[i][1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255, 0, 0), 1)


if __name__ == '__main__':
    #Define window names;
    win_delaunary = "Delaunay Triangulation"
    win_voronoi = "Voronoi Diagram"

    #Turn on animations while drawing triangles
    animate = True

    #Define colors for drawing
    delaunary_color = (255,255,255)
    points_color = (0,0,255)

    #Read in the image
    img_path = "srcImg/facemask.jpg"

    img = cv2.imread(img_path)
    cv2.pyrUp(img, img) 
    cv2.pyrUp(img, img) 
    cv2.pyrUp(img, img) 

    #Keep a copy   around
    img_orig = img.copy()

    #Rectangle to be used with Subdiv2D
    size = img.shape
    rect = (0,0,size[1],size[0])

    #Create an instance of Subdiv2d
    subdiv = cv2.Subdiv2D(rect)
    #Create an array of points
    points = []
    #Read in the points from a text file
    with open("dataset/points.txt") as file:
        for line in file:
            x,y = line.split()
            points.append((int(x),int(y)))
    #Insert points into subdiv
    for p in points:
        subdiv.insert(p)

        # #Show animate # 动态绘制
        # if animate:
        #     img_copy = img_orig.copy()
        #     #Draw delaunay triangles
        #     draw_delaunay(img_copy,subdiv,(255,255,255))
        #     # cv2.imshow(win_delaunary,img_copy)
        #     # cv2.waitKey(10) 

    #Draw delaunary triangles
    draw_delaunay(img,subdiv,(0,0,255),points)
    draw_number(img,subdiv)

    #Draw points
    for p in points:
        draw_point(img,p,(0,0,255))

    #Allocate space for Voroni Diagram
    img_voronoi = np.zeros(img.shape,dtype = img.dtype)

    #Draw Voonoi diagram
    draw_voronoi(img_voronoi,subdiv)

    #Show results
    # cv2.imshow(win_delaunary,img)
    # cv2.imshow(win_voronoi,img_voronoi)
    # cv2.waitKey(0)
    cv2.imwrite("outImg/img.jpg", img,[cv2.IMWRITE_JPEG_QUALITY, 100])
    # cv2.imwrite("outImg/img_copy.jpg", img_copy,[cv2.IMWRITE_JPEG_QUALITY, 100])
    cv2.imwrite("outImg/img_voronoi.jpg", img_voronoi,[cv2.IMWRITE_JPEG_QUALITY, 100])
    print("done.")

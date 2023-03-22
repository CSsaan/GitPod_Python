import  cv2

img = cv2.imread('tick.jpg')
print(img.shape)

# 分离通道,最后是alpha
b, g, r = cv2.split(img)
w,h = b.shape

sum = 0
for i in range(w):
    for j in range(h):
        
        if(img[i,j,2] < 240):
            sum+=1
            print(img[i,j,2])
            # img[i,j,3] = 255
        else:
            img[i,j,0] = 0
            img[i,j,1] = 0
            img[i,j,2] = 0

            
print(sum/(w*h))

cv2.imwrite("new.jpg", img)
    
    

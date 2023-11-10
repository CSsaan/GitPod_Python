# import  cv2

# img = cv2.imread('tick.jpg')
# print(img.shape)

# # 分离通道,最后是alpha
# b, g, r = cv2.split(img)
# w,h = b.shape

# sum = 0
# for i in range(w):
#     for j in range(h):
        
#         if(img[i,j,2] < 240):
#             sum+=1
#             print(img[i,j,2])
#             # img[i,j,3] = 255
#         else:
#             img[i,j,0] = 0
#             img[i,j,1] = 0
#             img[i,j,2] = 0

            
# print(sum/(w*h))

# cv2.imwrite("new.jpg", img)
    
    
import difflib

file1 = r'E:\test\aaaa\aaa\aa.txt'
file2 = r'E:\test\aaaa\aaa\bb.txt'

with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
    content1 = f1.read()
    content2 = f2.read()

print(difflib.SequenceMatcher(None, content1, content2).ratio())
print(content1)
print(content2)

diff = [(i, j) for i, (a, b) in enumerate(zip(content1, content2)) for j, (c, d) in enumerate(zip(content1, content2)) if a != c or b != d]

for i, j in diff:
    print(f'Difference at position {i} in file1 and position {j} in file2: {content1[i]} vs {content2[j]}')
print("done")

# 49 50 51 52  [13 10]
# 53 54 55 56

# 50 51 53 12 10
# 53 54 55 56
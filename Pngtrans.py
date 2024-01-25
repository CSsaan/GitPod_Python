import numpy, cv2
hald = cv2.imread('srcImg/arrowblack.png')
size = int(hald.shape[0] ** (1.0/3.0) + .5)
clut = numpy.concatenate([
    numpy.concatenate(hald.reshape((size, size, size**2, size**2, 3))[row], axis=1)
    for row in range(size)
])
cv2.imwrite("False.jpg", clut)
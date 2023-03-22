import numpy, cv2
import os
for filepath,dirnames,filenames in os.walk(r'./LUT'):
    for filename in filenames:
        now_path = os.path.join(filepath,filename)
        hald = cv2.imread(now_path)
        size = int(hald.shape[0] ** (1.0/3.0) + .5)
        clut = numpy.concatenate([
            numpy.concatenate(hald.reshape((size, size, size**2, size**2, 3))[row], axis=1)
            for row in range(size)
        ])
        cv2.imwrite("./2DLUT/"+ filename[:-4] +".png", clut)
        print("./2DLUT/"+ filename[:-4] +".png")
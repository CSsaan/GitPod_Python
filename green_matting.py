import cv2
import numpy as np

def guidedFilter(I, p, winSize, eps):
    
    I = I.astype('float') / 255.0
    p = p.astype('float') / 255.0
    
    #I的均值平滑
    mean_I = cv2.blur(I, winSize)
    
    #p的均值平滑
    mean_p = cv2.blur(p, winSize)
    
    #I*I和I*p的均值平滑
    mean_II = cv2.blur(I*I, winSize)
    
    mean_Ip = cv2.blur(I*p, winSize)
    
    #方差
    var_I = mean_II - mean_I * mean_I #方差公式
    
    #协方差
    cov_Ip = mean_Ip - mean_I * mean_p
   
    a = cov_Ip / (var_I + eps)
    b = mean_p - a*mean_I
    
    #对a、b进行均值平滑
    mean_a = cv2.blur(a, winSize)
    mean_b = cv2.blur(b, winSize)
    
    q = mean_a*I + mean_b
    q *= 255.0
    
    q[q < 0] = 0
    q[q > 255] = 255
    
    return q.astype('uint8')
    

def guidedFilter_Fast(I, p, winSize, eps, s=4):
    
    #输入图像的高、宽
    h, w = I.shape[:2]
    
    #缩小图像
    size = (int(round(w*s)), int(round(h*s)))
    
    small_I = cv2.resize(I, size, interpolation=cv2.INTER_CUBIC)
    small_p = cv2.resize(I, size, interpolation=cv2.INTER_CUBIC)
    
    #缩小滑动窗口
    X = winSize[0]
    small_winSize = (int(round(X*s)), int(round(X*s)))
    
    #I的均值平滑
    mean_small_I = cv2.blur(small_I, small_winSize)
    
    #p的均值平滑
    mean_small_p = cv2.blur(small_p, small_winSize)
    
    #I*I和I*p的均值平滑
    mean_small_II = cv2.blur(small_I*small_I, small_winSize)
    
    mean_small_Ip = cv2.blur(small_I*small_p, small_winSize)
    
    #方差
    var_small_I = mean_small_II - mean_small_I * mean_small_I #方差公式
    
    #协方差
    cov_small_Ip = mean_small_Ip - mean_small_I * mean_small_p
   
    small_a = cov_small_Ip / (var_small_I + eps)
    small_b = mean_small_p - small_a*mean_small_I
    
    #对a、b进行均值平滑
    mean_small_a = cv2.blur(small_a, small_winSize)
    mean_small_b = cv2.blur(small_b, small_winSize)
    
    #放大
    size1 = (w, h)
    mean_a = cv2.resize(mean_small_a, size1, interpolation=cv2.INTER_LINEAR)
    mean_b = cv2.resize(mean_small_b, size1, interpolation=cv2.INTER_LINEAR)
    
    q = mean_a*I + mean_b
    
    return q



def cal_Threshold_OSTU(La):
    # 统计像素值(0-255)的直方图
    hist,unq = np.histogram(La, np.arange(257))  # hist.shape[0] = unq.shape[0]-1
    print("直方图数据 (hist):", hist)
    print("唯一值 (unq):", unq)
    # 绘制直方图
    import matplotlib.pyplot as plt
    plt.bar(unq[:-1], hist, width=1, align='edge', edgecolor='black')
    plt.xlabel('像素值')
    plt.ylabel('频率')
    plt.title('直方图')
    plt.xlim(0, 256)  # 设置 x 轴范围
    plt.xticks(np.arange(0, 257, 16))  # 设置 x 轴刻度
    plt.grid(axis='y')  # 添加网格
    plt.show()
    print('=>hist.shape=',hist.shape,'unq=',unq.shape)
    
    # 归一化
    total = La.shape[0] * La.shape[1]
    hist  = hist.astype('float') / total 
    
    # 均值
    avg = np.arange(256).dot(hist)
    print('avg=',avg)
    
    w,u,t,max_var,th = 0,0,0,0,0
    for z in range(256):
        w += hist[z]
        u += z * hist[z]
        t = avg * w - u
        if w > 0.0 and w < 1.0:
           var = t * t / (w * (1.0 - w)) # 类间方差
           if var > max_var:
              max_var = var
              th = z  # 分割阈值
    print('=>th=',th)
    return th
    

if __name__ == '__main__':
    pic = cv2.imread('test.png')
    h,w,c = pic.shape
    pic = cv2.resize(pic,(w//4,h//4))

    # # 转HSV
    # hsv = cv2.cvtColor(pic, cv2.COLOR_BGR2HSV)


    # 导向滤波 => 平滑边缘
    Lab = cv2.cvtColor(pic, cv2.COLOR_BGR2Lab)
    # cv2.imwrite('Lab.png',Lab[:,:,1]) # Lab->a

    Lab_a = Lab[:,:,1]

    # 阈值对Lab_a进行分割
    TH = cal_Threshold_OSTU(Lab_a)
    _, mask = cv2.threshold(Lab_a, TH, 255, cv2.THRESH_BINARY_INV)



    alpha = guidedFilter(Lab_a, mask, [30,30], 0.0007)
    alpha = 255 - alpha
    cv2.imwrite('v2_alpha.png',alpha)


    result = pic.copy()
    result = result.astype('float')
    alpha  = alpha.astype('float') / 255.0
    result[:,:,0] *= alpha
    result[:,:,1] *= alpha
    result[:,:,2] *= alpha
    result = result.astype('uint8')


    h,w = alpha.shape

    # 颜色溢出抑制
    for y in range(h):
        for x in range(w):
            bgr = result[y,x,:]
            bgr[1] = min(bgr[1], (int(bgr[0]) + int(bgr[2])) // 2)
            result[y,x,:] = bgr



    #保存文件到结果
    cv2.imwrite('v2_result.png',result)

 




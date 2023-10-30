import cv2

OPENCV_OBJECT_TRACKERS = {
	"csrt": cv2.legacy.TrackerCSRT_create,
	"kcf": cv2.legacy.TrackerKCF_create,
	"boosting": cv2.legacy.TrackerBoosting_create,
	"mil": cv2.legacy.TrackerMIL_create,
	"tld": cv2.legacy.TrackerTLD_create,
	"medianflow": cv2.legacy.TrackerMedianFlow_create,
	"mosse": cv2.legacy.TrackerMOSSE_create
}

# tracker = cv2.legacy.TrackerCSRT_create()#使用csrt算法，引用伴生函数，并赋值给tracker
tracker = OPENCV_OBJECT_TRACKERS[args['csrt']]()

cap = cv2.VideoCapture('./video/in.mp4')#读取视频流

ret, frame = cap.read() #先读取第一帧
print(ret, frame.shape)

# bbox = cv2.selectROI('A', frame, fromCenter=False, showCrosshair=True)#使用selectROI（前景），画框将目标框起，并赋值给bbox
bbox = (82, 534, 106, 122)

tracker.init(frame, bbox)#初始化tracker，将上面的两个值传入

# while True:
#     ret,frame = cap.read()#读取每一帧

#     ok,box = tracker.update(frame)#根据每一帧来跟新tracker

#     # 若读取成功，我们就定位画框，并跟随
#     if ok :
#         (x,y,w,h) = [int(v) for v in box]
#         cv2.rectangle(frame,pt1=(int(x),int(y)),pt2=(int(x)+int(w),int(y)+int(h)),color=(0,255,0),thickness=2)

#     cv2.imshow('A', frame)#显示视频流

#     if cv2.waitKey(50) == ord(' '):#等待50毫秒或键盘按空格键退出
#         break

# # 释放视频流，释放窗口
# cap.release()
# cv2.destroyAllWindows()
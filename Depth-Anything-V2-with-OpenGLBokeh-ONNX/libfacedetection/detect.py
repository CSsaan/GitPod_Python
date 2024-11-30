import argparse
import numpy as np
import cv2
import onnx

def denormalize_coordinates(x_norm, y_norm, w_norm, h_norm, image_width, image_height):
    x = x_norm * image_width
    y = y_norm * image_height
    w = w_norm * image_width
    h = h_norm * image_height
    return int(x), int(y), int(w), int(h)

def process_face_rectangle(max_face_loc, img_depth, draw_roi=False):
    if max_face_loc is not None:
        # 将归一化后的坐标值转换为真实坐标值
        x, y, w, h = denormalize_coordinates(max_face_loc[0], max_face_loc[1], max_face_loc[2], max_face_loc[3], img_depth.shape[1], img_depth.shape[0])
        # 在原图像上绘制矩形框
        if draw_roi:
            cv2.rectangle(img_depth, (x, y), (x + w, y + h), (0, 255, 0), 1)
        # 提取矩形框区域
        roi = img_depth[y:y + h, x:x + w]
        # 提取 R 通道
        r_channel = roi[:, :, 2]  # OpenCV 中的通道顺序是 BGR，所以 R 通道是索引 2
        # 计算中位数并归一化
        median_depth = np.median(r_channel) / 255.0
        return median_depth
    else:
        return None

class FaceDetection:
    def __init__(self, model_path="libfacedetection/face_detection_yunet_2023mar.onnx", backend=cv2.dnn.DNN_BACKEND_DEFAULT, target=cv2.dnn.DNN_TARGET_CPU,
                 score_threshold=0.6, nms_threshold=0.3, top_k=5000):
        self.model_path = model_path
        self.backend = backend
        self.target = target
        self.score_threshold = score_threshold
        self.nms_threshold = nms_threshold
        self.top_k = top_k
        
        self.yunet = self.load_model()

    def load_model(self):
        model = onnx.load(self.model_path)
        onnx.checker.check_model(model)
        
        return cv2.FaceDetectorYN.create(
            model=self.model_path,
            config='',
            input_size=(320, 320),
            score_threshold=self.score_threshold,
            nms_threshold=self.nms_threshold,
            top_k=self.top_k,
            backend_id=self.backend,
            target_id=self.target
        )

    @staticmethod
    def str2bool(v: str) -> bool:
        if v.lower() in ['true', 'yes', 'on', 'y', 't']:
            return True
        elif v.lower() in ['false', 'no', 'off', 'n', 'f']:
            return False
        else:
            raise NotImplementedError

    @staticmethod
    def visualize(image, faces, print_flag=False, fps=None):
        output = image.copy()

        if fps:
            cv2.putText(output, 'FPS: {:.2f}'.format(fps), (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

        for idx, face in enumerate(faces):
            if print_flag:
                print('Face {}, top-left coordinates: ({:.0f}, {:.0f}), box width: {:.0f}, box height {:.0f}, score: {:.2f}'.format(
                    idx, face[0], face[1], face[2], face[3], face[-1]))

            coords = face[:-1].astype(np.int32)
            cv2.rectangle(output, (coords[0], coords[1]), (coords[0]+coords[2], coords[1]+coords[3]), (0, 255, 0), 2)
            cv2.circle(output, (coords[4], coords[5]), 2, (255, 0, 0), 2)
            cv2.circle(output, (coords[6], coords[7]), 2, (0, 0, 255), 2)
            cv2.circle(output, (coords[8], coords[9]), 2, (0, 255, 0), 2)
            cv2.circle(output, (coords[10], coords[11]), 2, (255, 0, 255), 2)
            cv2.circle(output, (coords[12], coords[13]), 2, (0, 255, 255), 2)
            cv2.putText(output, '{:.4f}'.format(face[-1]), (coords[0], coords[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

        return output
    
    def find_largest_face(self, faces):
        if faces is None:
            return None
        max_face_idx = -1
        max_face_area = 0
        for idx, face in enumerate(faces):
            face_area = face[2] * face[3]  # 计算人脸框面积
            if face_area > max_face_area:
                max_face_area = face_area
                max_face_idx = idx
        if max_face_idx != -1:
            max_face = faces[max_face_idx]
            return max_face
        else:
            return None

    def detect_faces(self, image):
        self.yunet.setInputSize((image.shape[1], image.shape[0]))
        _, faces = self.yunet.detect(image)
        return faces

    def normalize_coordinates(self, coordx, coordy, image_width, image_height):
        return coordx / image_width, coordy / image_height

    def process_image(self, image, save_result=False, visualize_result=False):
        faces = self.detect_faces(image)
        if save_result:
            vis_image = self.visualize(image, faces, print_flag=True)
            cv2.imwrite('result.jpg', vis_image)
            print('result.jpg saved.')
        if visualize_result:
            vis_image = self.visualize(image, faces, print_flag=True)
            cv2.namedWindow("Test Faces by CS", cv2.WINDOW_AUTOSIZE)
            cv2.imshow("Test Faces by CS", vis_image)
            cv2.waitKey(0)
        # find largest face
        largest_face = self.find_largest_face(faces)
        if largest_face is not None:
            x, y, w, h, score = largest_face[0], largest_face[1], largest_face[2], largest_face[3], largest_face[-1]
            image_width = image.shape[1]
            image_height = image.shape[0]
            # 将坐标值归一化为 0.0 到 1.0 的比例坐标
            x_norm, y_norm = self.normalize_coordinates(x,y, image_width,image_height)
            w_norm, h_norm = self.normalize_coordinates(w,h, image_width,image_height)
        else:
            return None
        return (x_norm, y_norm, w_norm, h_norm, score)

    def process_video(self):
        device_id = 0
        cap = cv2.VideoCapture(device_id)
        frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.yunet.setInputSize([frame_w, frame_h])

        tm = cv2.TickMeter()
        while cv2.waitKey(1) < 0:
            has_frame, frame = cap.read()
            if not has_frame:
                print('No frames grabbed!')
                break

            tm.start()
            faces = self.detect_faces(frame)
            tm.stop()

            frame = self.visualize(frame, faces, fps=tm.getFPS())
            cv2.imshow('libfacedetection demo', frame)

            tm.reset()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A demo for running libfacedetection using OpenCV\'s DNN module.')
    parser.add_argument('--input', '-i', default=r"pic/1118.png", help='Path to the image. Omit to call default camera')
    parser.add_argument('--model', '-m', type=str, default=r"libfacedetection/face_detection_yunet_2023mar.onnx", help='Path to .onnx model file.')
    parser.add_argument('--score_threshold', default=0.6, type=float, help='Threshold for filtering out faces with conf < conf_thresh.')
    parser.add_argument('--nms_threshold', default=0.3, type=float, help='Threshold for non-max suppression.')
    parser.add_argument('--top_k', default=5000, type=int, help='Keep keep_top_k for results outputing.')
    parser.add_argument('--vis', default=True, type=FaceDetection.str2bool, help='Set True to visualize the result image. Invalid when using camera.')
    parser.add_argument('--save', default=False, type=FaceDetection.str2bool, help='Set True to save as result.jpg. Invalid when using camera.')
    args = parser.parse_args()

    face_detection = FaceDetection(model_path=args.model, score_threshold=args.score_threshold,
                                    nms_threshold=args.nms_threshold, top_k=args.top_k)

    if args.input is not None:
        image = cv2.imread(args.input)
        max_face_loc = face_detection.process_image(image, save_result=args.save, visualize_result=args.vis)
        if max_face_loc is not None:
            print('largest face: top-left coordinates: ({:.2f}, {:.2f}), box width: {:.2f}, box height {:.2f}, score: {:.2f}'.format(
                max_face_loc[0], max_face_loc[1], max_face_loc[2], max_face_loc[3], max_face_loc[4]))
        else:
            print('not detect face.')
        # print('largest face: top-left coordinates: ({:.0f}, {:.0f}), box width: {:.0f}, box height {:.0f}, score: {:.2f}'.format(
        #     largest_face[0], largest_face[1], largest_face[2], largest_face[3], largest_face[-1]))
    else:
        face_detection.process_video()
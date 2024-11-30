import cv2
import numpy as np
import matplotlib.pyplot as plt

class KalmanFilter:
    def __init__(self, processNoise=0.03, measurementNoise=0.5):
        self.kalman = cv2.KalmanFilter(4, 2)  # 4 状态变量，2 观测值
        self.kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                                  [0, 1, 0, 0]], np.float32)
        self.kalman.transitionMatrix = np.array([[1, 1, 0, 0],
                                                 [0, 1, 0, 0],
                                                 [0, 0, 1, 1],
                                                 [0, 0, 0, 1]], np.float32)
        self.kalman.processNoiseCov = np.array([[1, 0, 0, 0],
                                                 [0, 1, 0, 0],
                                                 [0, 0, 1, 0],
                                                 [0, 0, 0, 1]], np.float32) * processNoise
        self.kalman.measurementNoiseCov = np.array([[1, 0],
                                                     [0, 1]], np.float32) * measurementNoise

    def update(self, measurement):
        # 预测
        predicted = self.kalman.predict()
        # 更新
        self.kalman.correct(measurement.astype(np.float32))
        return predicted, self.kalman.statePost



class KalmanFilterFrame:
    def __init__(self, video_width, video_height, kal_q=0.1, kal_r=0.1, movement_threshold=0.5):
        self.video_width = int(video_width)
        self.video_height = int(video_height)
        
        self.previous_mask = np.zeros((self.video_height, self.video_width), dtype=np.float32)
        self.predicted_mask = np.zeros((self.video_height, self.video_width), dtype=np.float32)
        self.p_mask = np.full((self.video_height, self.video_width), 255.0, dtype=np.float32)
        
        self.kal_q = kal_q
        self.kal_r = kal_r
        self.movement_threshold = movement_threshold

    def kalman_filter_single_frame(self, current_mask):
        # 预测步骤
        covariance_matrix = self.p_mask.copy()  # 使用p_mask作为协方差矩阵
        covariance_matrix += np.full(covariance_matrix.shape, self.kal_q)  # 预测误差协方差

        # 计算当前帧和前一帧的差异
        if np.any(self.previous_mask):  # 检查previous_mask是否为零
            movement_level = np.mean(np.abs(current_mask - self.previous_mask))  # 计算差异程度
        else:
            movement_level = 0

        # 更新步骤
        kalman_gain = covariance_matrix / (covariance_matrix + self.kal_r)  # 卡尔曼增益
        
        # 根据运动的级别动态调整 K
        if movement_level > self.movement_threshold:  # 如果帧间差异较大，认为是快速运动
            kalman_gain = np.clip(kalman_gain, 0.2, 0.3)  # 快速运动时 K 更大，偏向观测值
        else:  # 缓慢移动时 K 更小，偏向先验估计
            kalman_gain = np.clip(kalman_gain, 0.4, 0.8)

        # 更新状态
        self.predicted_mask += kalman_gain * (current_mask - self.predicted_mask)
        self.p_mask *= (1 - kalman_gain)  # 更新协方差矩阵

        # 更新previous_mask
        self.previous_mask = current_mask

    def process_video(self, gray):
        if len(gray.shape) != 2:
            gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        self.kalman_filter_single_frame(gray)
        _predicted_mask = np.clip(self.predicted_mask, 0, 255).astype(np.uint8)
        result_rgb = cv2.cvtColor(_predicted_mask, cv2.COLOR_GRAY2BGR)
        return result_rgb


if __name__ == "__main__":

    mode = "frame_filter" #  "single_value_filter"  or  "frame_filter"

    # ------------------------- 单值 滤波 -------------------------------------
    if mode == "single_value_filter":
        # 主程序
        kalman_filter = KalmanFilter(processNoise=0.00003, measurementNoise=0.5)
        
        # 深度估计
        median_depths = np.arange(0, 1.0, 0.01) + np.random.normal(0, 0.05, 100)
        predicted_depths = []
        
        for median_depth in median_depths:
            # 将中位数深度值作为测量值
            measurement = np.array([[median_depth], [0]], np.float32)  # 这里假设第二个观测值为 0
            predicted, state_post = kalman_filter.update(measurement)
            print(predicted[0])
            predicted_depths.append(predicted[0])

        # 绘制折线图
        plt.figure()
        plt.plot(median_depths, label='Measured Depth')
        plt.plot(predicted_depths, label='Predicted Depth')
        plt.xlabel('Index')
        plt.ylabel('Depth')
        plt.legend()
        plt.show()

    # ------------------------- 帧 滤波 -------------------------------------
    else:
        video_path = 'D:/Users/Desktop/1117.mp4'
        cap = cv2.VideoCapture(video_path)
        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 实例化卡尔曼滤波
        kalman_filter = KalmanFilterFrame(video_width, video_height)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 获取滤波结果
            result = kalman_filter.process_video(gray)

            # 显示平滑后的图像
            cv2.imshow('Kalman Filter', result)
            if cv2.waitKey(30) & 0xFF == 27:  # 按Esc键退出
                break
        self.cap.release()
        cv2.destroyAllWindows()
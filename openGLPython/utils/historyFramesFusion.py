import cv2
import numpy as np

class HistoryFrameFusion:
    def __init__(self, num_frames=3, alpha=0.5):
        self.num_frames = num_frames
        self.alpha = alpha
        self.frame_buffer = []

    def update_frame(self, frame):
        if len(self.frame_buffer) == self.num_frames:
            self.frame_buffer.pop(0)
        self.frame_buffer.append(frame)

    def fuse_frames(self, current_frame):
        if len(self.frame_buffer) == 0:
            return current_frame

        average_frame = np.zeros_like(current_frame, dtype=np.float32)
        for frame in self.frame_buffer:
            average_frame += frame.astype(np.float32)
        average_frame /= len(self.frame_buffer)

        fused_frame = cv2.addWeighted(current_frame.astype(np.float32), 1 - self.alpha, average_frame, self.alpha, 0)
        return fused_frame.astype(np.uint8)

if __name__=="__main__":
    # 使用示例
    use_pre_nums = 15
    history_fusion = HistoryFrameFusion(num_frames=use_pre_nums, alpha=0.5)

    for i in range(0, 825):
        current_frame = cv2.imread(f'./result/frames/output_{i+1}.png')
        history_fusion.update_frame(current_frame)
        # 第use_pre_nums帧开始融合
        if(i >= use_pre_nums):
            fused_frame = history_fusion.fuse_frames(current_frame)
            current_frame = fused_frame
        # # 在图像左上角添加文字
        # cv2.putText(fused_frame, f'{i}/825', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow('fused_frame', current_frame)
        cv2.imwrite(f"./result/frames1/output_{i+1}.jpg", current_frame)
        cv2.waitKey(1)

    # # 处理下一帧
    # next_frame = cv2.imread('./result/frames0/output_43.png')
    # fused_frame = history_fusion.fuse_frames(next_frame)
    # cv2.imshow('fused_frame', fused_frame)
    # cv2.waitKey(0)
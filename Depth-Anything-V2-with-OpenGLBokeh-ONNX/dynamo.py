import cv2
import os
import onnxruntime as ort
from tqdm import tqdm
from natsort import natsorted

class DepthAnythingInference:
    def __init__(self, model_path='weights/depth_anything_v2_vits_17.onnx', height=420, width=420, device='cpu', restore_size=False):
        self.model_path = model_path
        self.height = height
        self.width = width
        self.device = device
        self.session = self._load_model()
        self.restore_size = restore_size

    def _load_model(self):
        """加载 ONNX 模型并创建推理会话。"""
        sess_options = ort.SessionOptions()
        sess_options.enable_profiling = False
        providers = ['CPUExecutionProvider'] if self.device=='cpu' else ['CUDAExecutionProvider']  # 根据需要更改为 'CUDAExecutionProvider'
        return ort.InferenceSession(self.model_path, sess_options=sess_options, providers=providers)

    def infer(self, image, output_path=None):
        """进行深度推理。"""
        
        h, w = image.shape[:2]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) / 255.0
        image = cv2.resize(image, (self.width, self.height), interpolation=cv2.INTER_CUBIC)
        image = (image - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
        image = image.transpose(2, 0, 1)[None].astype("float32")

        # Inference
        binding = self.session.io_binding()
        ort_input = self.session.get_inputs()[0].name
        binding.bind_cpu_input(ort_input, image)
        ort_output = self.session.get_outputs()[0].name
        binding.bind_output(ort_output)

        self.session.run_with_iobinding(binding)  # 实际推理发生在这里。

        depth = binding.get_outputs()[0].numpy()

        # 后处理
        depth = (depth - depth.min()) / (depth.max() - depth.min()) * 255.0
        depth = depth.transpose(1, 2, 0).astype("uint8")
        if self.restore_size:
            depth = cv2.resize(depth, (w, h), interpolation=cv2.INTER_CUBIC)

        if output_path:
            cv2.imwrite(str(output_path), depth)
        depth = cv2.cvtColor(depth, cv2.COLOR_GRAY2RGB)
        return depth


def images_to_video(input_folder, output_path, down_scale=False):
    image_files = [f for f in os.listdir(input_folder) if f.endswith('.jpg') or f.endswith('.png')]
    image_files = natsorted(image_files)
    first_image = cv2.imread(os.path.join(input_folder, image_files[0]))
    cv2.waitKey(0)
    height, width, _ = first_image.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 30.0, (width//3, height//3) if down_scale else (width, height))
    for image_file in tqdm(image_files, desc="Converting images to video"):
        image_path = os.path.join(input_folder, image_file)
        frame = cv2.imread(image_path)
        frame = cv2.resize(frame, (width//3, height//3) if down_scale else (width, height))
        out.write(frame)
    out.release()

# 使用示例
if __name__ == "__main__":
    model = DepthAnythingInference()

    # --------------------------------------------------------------
    image_path = "pic/1118.png"
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"FileNotFoundError: {image_path}")
    image = cv2.imread(str(image_path))

    depth = model.infer(image)

    cv2.imshow("depth", depth)
    cv2.waitKey(0)

    # --------------------------------------------------------------
    # video_path = r"D:\Users\Desktop\视频防抖-高-GoPro Hero 6(1).mp4"
    # """处理视频的每一帧。"""
    # cap = cv2.VideoCapture(video_path)
    # if not cap.isOpened():
    #     raise FileNotFoundError(f"Cannot open video: {video_path}")
    # while True:
    #     ret, frame = cap.read()
    #     if not ret:
    #         break  # 视频结束
    #     # 调用模型进行推理
    #     depth = model.infer(frame)
    #     # 显示深度图像
    #     cv2.imshow("Depth Map", depth)
    #     # 按 'q' 键退出
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
    # cap.release()
    # cv2.destroyAllWindows()

    # --------------------------------------------------------------
    # images_to_video("./result/frames", "./result/640-2.mp4", down_scale=False)
    
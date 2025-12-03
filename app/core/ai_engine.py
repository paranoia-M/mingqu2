# app/core/ai_engine.py
import cv2

class AIEngine:
    def __init__(self):
        self.model = None
        # self.model = YOLO("yolov8n.pt") # 真实环境取消注释

    def detect(self, frame):
        """
        接收 OpenCV 图片，返回处理后的图片和识别到的物体数量
        """
        # --- 模拟 AI 识别逻辑 ---
        h, w, _ = frame.shape
        # 模拟画框
        cv2.rectangle(frame, (w//2-60, h//2-60), (w//2+60, h//2+60), (0, 255, 0), 2)
        cv2.putText(frame, "Simulating AI...", (w//2-60, h//2-70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 返回 (图像, 漂浮物数量)
        return frame, 0
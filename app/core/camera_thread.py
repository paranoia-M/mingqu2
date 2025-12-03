# app/core/camera_thread.py
import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from app.core.ai_engine import AIEngine
from app.config import AppConfig

class CameraThread(QThread):
    frame_signal = Signal(np.ndarray) # 发送图像信号

    def __init__(self):
        super().__init__()
        self.running = True
        self.ai_enabled = False
        self.ai_engine = AIEngine()

    def run(self):
        cap = cv2.VideoCapture(0) if not AppConfig.USE_MOCK_CAMERA else None
        
        while self.running:
            if cap and cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    if self.ai_enabled:
                        frame, count = self.ai_engine.detect(frame)
                    self.frame_signal.emit(frame)
            else:
                # 模拟噪点图
                noise = np.random.randint(0, 50, (480, 640, 3), dtype=np.uint8)
                self.frame_signal.emit(noise)
                self.msleep(100)
            
            self.msleep(30) # 限制帧率约 30fps

    def stop(self):
        self.running = False
        self.wait()
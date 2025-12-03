# app/core/camera_thread.py
import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from app.core.ai_engine import AIEngine

class CameraThread(QThread):
    # 信号改为发送：图像, 识别数量, 警告文本
    frame_signal = Signal(object, int, str) 

    def __init__(self):
        super().__init__()
        self.running = True      # 线程生命周期
        self.camera_active = False # 摄像头是否开启采集
        self.ai_enabled = False  # AI 是否开启
        self.ai_engine = AIEngine()

    def run(self):
        cap = cv2.VideoCapture(0)
        # Mac 可能需要设置分辨率以提高性能
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while self.running:
            if self.camera_active:
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        count = 0
                        msg = ""
                        # 翻转镜像 (Mac摄像头通常需要镜像)
                        # frame = cv2.flip(frame, 1) 
                        
                        if self.ai_enabled:
                            frame, count, msg = self.ai_engine.detect(frame)
                        else:
                            # 即使不开AI，也画个简单的十字，表示正在运行
                            h, w, _ = frame.shape
                            cv2.line(frame, (w//2-10, h//2), (w//2+10, h//2), (100,100,100), 1)
                            cv2.line(frame, (w//2, h//2-10), (w//2, h//2+10), (100,100,100), 1)

                        self.frame_signal.emit(frame, count, msg)
                    else:
                        self.send_noise()
                else:
                    # 尝试重连
                    cap.open(0)
                    self.msleep(500)
            else:
                # 摄像头关闭状态，发送黑屏或待机图
                self.send_black_screen()
                self.msleep(100) # 省电模式
            
            self.msleep(30) # ~30 FPS

        cap.release()

    def send_noise(self):
        noise = np.random.randint(0, 50, (480, 640, 3), dtype=np.uint8)
        self.frame_signal.emit(noise, 0, "")

    def send_black_screen(self):
        # 创建一个带有 "CAMERA OFF" 文字的黑图
        black = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(black, "SENSOR STANDBY", (200, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
        self.frame_signal.emit(black, 0, "")

    def stop(self):
        self.running = False
        self.wait()
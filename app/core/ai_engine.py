# app/core/ai_engine.py
import cv2
import numpy as np
import datetime

class AIEngine:
    def __init__(self):
        # 定义绿色的 HSV 范围 (根据光线可能需要微调)
        # H: 色相 (35-85 覆盖了大部分植物绿)
        # S: 饱和度 (43-255)
        # V: 亮度 (46-255)
        self.lower_green = np.array([35, 43, 46])
        self.upper_green = np.array([85, 255, 255])

    def detect(self, frame):
        """
        检测绿色浮萍，并绘制 HUD 界面
        返回: (处理后的图像, 识别到的物体数量, 警报信息)
        """
        # 1. 转换颜色空间 BGR -> HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 2. 创建绿色掩膜 (Mask)
        mask = cv2.inRange(hsv, self.lower_green, self.upper_green)
        
        # 3. 腐蚀与膨胀 (去除噪点)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        # 4. 寻找轮廓
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_count = 0
        alert_msg = None
        
        # 5. 绘制结果
        for c in contours:
            # 过滤掉太小的噪点 (面积 < 500 忽略)
            area = cv2.contourArea(c)
            if area < 500:
                continue
            
            detected_count += 1
            
            # 获取边界框
            (x, y, w, h) = cv2.boundingRect(c)
            # 画框 (绿色)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # 标文字
            cv2.putText(frame, f"Duckweed: {int(area)}px", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # 6. 绘制 HUD (工业风格覆盖层)
        h, w, _ = frame.shape
        cy = h // 2
        cx = w // 2
        
        # 画十字准星
        cv2.line(frame, (cx - 20, cy), (cx + 20, cy), (255, 255, 255), 1)
        cv2.line(frame, (cx, cy - 20), (cx, cy + 20), (255, 255, 255), 1)
        
        # 画四角括弧
        color = (0, 255, 255) # 黄色
        thick = 2
        len_ = 30
        # 左上
        cv2.line(frame, (20, 20), (20 + len_, 20), color, thick)
        cv2.line(frame, (20, 20), (20, 20 + len_), color, thick)
        # 右上
        cv2.line(frame, (w - 20, 20), (w - 20 - len_, 20), color, thick)
        cv2.line(frame, (w - 20, 20), (w - 20, 20 + len_), color, thick)
        # 左下
        cv2.line(frame, (20, h - 20), (20 + len_, h - 20), color, thick)
        cv2.line(frame, (20, h - 20), (20, h - 20 - len_), color, thick)
        # 右下
        cv2.line(frame, (w - 20, h - 20), (w - 20 - len_, h - 20), color, thick)
        cv2.line(frame, (w - 20, h - 20), (w - 20, h - 20 - len_), color, thick)

        # 时间戳
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"REC {timestamp}", (30, h - 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        if detected_count > 0:
            alert_msg = f"检测到 {detected_count} 处浮萍堆积"

        return frame, detected_count, alert_msg
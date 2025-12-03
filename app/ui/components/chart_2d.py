from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPoint  # <--- 【关键修复】这里导入 QPoint
from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QPolygon, QFont

class Channel2DWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.water_depth = 2.0  
        self.max_depth = 5.0    
        self.velocity = 0.0     
        # 设置背景色
        self.setStyleSheet("background-color: #1e1e1e; border-radius: 8px; border: 1px solid #333;")
        self.setMinimumHeight(200)

    def set_data(self, depth, velocity):
        """接收外部数据并刷新界面"""
        self.water_depth = depth
        self.velocity = velocity
        self.update() # 触发重绘

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # 1. 绘制背景
        painter.fillRect(0, 0, w, h, QColor("#1e1e1e"))
        
        # 2. 计算比例
        margin_x = 40
        margin_y = 30
        effective_h = h - 2 * margin_y
        
        bottom_w = w - 2 * margin_x - 100
        top_w = w - 2 * margin_x
        
        channel_bottom_y = h - margin_y
        channel_top_y = margin_y
        
        # 3. 绘制渠道轮廓
        p1 = (margin_x, channel_top_y)
        p2 = (margin_x + (top_w - bottom_w)//2, channel_bottom_y)
        p3 = (w - margin_x - (top_w - bottom_w)//2, channel_bottom_y)
        p4 = (w - margin_x, channel_top_y)
        
        points = [p1, p2, p3, p4]
        
        # --- 【关键修复】使用 QPoint 而不是 Qt.QPoint ---
        poly_points = [QPoint(int(x), int(y)) for x, y in points]
        # -----------------------------------------------
        
        pen = QPen(QColor("#555"), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPolyline(poly_points)
        
        # 4. 绘制水体
        water_ratio = min(self.water_depth / self.max_depth, 1.0)
        water_pixel_height = water_ratio * effective_h
        water_surface_y = channel_bottom_y - water_pixel_height
        
        wp2 = p2
        wp3 = p3
        
        slope = (p2[0] - p1[0]) / effective_h if effective_h != 0 else 0
        offset = slope * (effective_h - water_pixel_height)
        
        wp1 = (p1[0] + offset, water_surface_y)
        wp4 = (p4[0] - offset, water_surface_y)
        
        # --- 【关键修复】使用 QPoint ---
        water_poly = [
            QPoint(int(wp1[0]), int(wp1[1])),
            QPoint(int(wp2[0]), int(wp2[1])),
            QPoint(int(wp3[0]), int(wp3[1])),
            QPoint(int(wp4[0]), int(wp4[1])),
        ]
        
        water_color = QColor(0, 188, 212, 150)
        painter.setBrush(QBrush(water_color))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(QPolygon(water_poly))
        
        # 5. 绘制文字
        painter.setPen(QColor("#fff"))
        painter.setFont(QFont("Microsoft YaHei", 10))
        painter.drawText(int(wp1[0]) + 10, int(wp1[1]) - 5, f"▼ {self.water_depth:.2f}m")
        
        # 6. 绘制流速箭头
        center_x = w // 2
        center_y = int(water_surface_y + (channel_bottom_y - water_surface_y)/2)
        if self.water_depth > 0.1:
            arrow_len = min(self.velocity * 20, 80)
            painter.setPen(QPen(QColor("#00e676"), 3))
            painter.drawLine(center_x - int(arrow_len/2), center_y, center_x + int(arrow_len/2), center_y)
            painter.drawLine(center_x + int(arrow_len/2), center_y, center_x + int(arrow_len/2)-5, center_y-5)
            painter.drawLine(center_x + int(arrow_len/2), center_y, center_x + int(arrow_len/2)-5, center_y+5)
            painter.drawText(center_x - 20, center_y - 10, f"v={self.velocity:.2f}m/s")
        
        # QPainter 会在函数结束时自动销毁，结束绘制状态
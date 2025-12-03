# app/ui/views/dashboard.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
                               QListWidget, QListWidgetItem, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Slot, QTimer, QSize
from PySide6.QtGui import QColor, QIcon

from app.ui.components.chart_3d import Channel3DWidget
from app.core.camera_thread import CameraThread
from app.core.calculator import HydraulicCalculator
from app.core.shared_state import SharedState
from app.db.database import DatabaseManager

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.db = DatabaseManager()
        self.state = SharedState()
        
        # --- 区域1: 顶部监控 (3D + 摄像头) ---
        top_section = QHBoxLayout()
        self.chart_3d = Channel3DWidget()
        self.chart_3d.setFixedHeight(280)
        
        self.cam_label = QLabel("正在连接视觉传感器...")
        self.cam_label.setStyleSheet("border: 1px solid #333; background: #000; color: #666;")
        self.cam_label.setAlignment(Qt.AlignCenter)
        self.cam_label.setFixedSize(360, 280)

        top_section.addWidget(self.chart_3d, stretch=2)
        top_section.addWidget(self.cam_label, stretch=1)
        self.layout.addLayout(top_section)

        # --- 区域2: 核心指标卡片 ---
        self.metrics_layout = QHBoxLayout()
        self.metric_labels = {}
        self.create_metrics_cards()
        self.layout.addLayout(self.metrics_layout)

        # --- 区域3: 预警中心 (新功能) ---
        self.layout.addWidget(QLabel("🔔 实时预警系统"))
        self.alert_list = QListWidget()
        self.alert_list.setStyleSheet("""
            QListWidget { background-color: #1e1e1e; border: 1px solid #333; border-radius: 4px; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #2a2a2a; }
        """)
        self.alert_list.setFixedHeight(150)
        self.layout.addWidget(self.alert_list)

        # --- 启动线程 ---
        self.cam_thread = CameraThread()
        self.cam_thread.frame_signal.connect(self.update_cam_ui)
        self.cam_thread.start()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system)
        self.timer.start(800) # 800ms 刷新一次

    def create_metrics_cards(self):
        metrics = [
            ("实时水深 (h)", "m"), 
            ("平均流速 (v)", "m/s"), 
            ("断面流量 (Q)", "m³/s"), 
            ("Froude数", "-"), 
            ("流态判定", "Type")
        ]
        for name, unit in metrics:
            card = QFrame()
            card.setStyleSheet(".QFrame {background-color: #1e1e1e; border-radius: 8px; border: 1px solid #333;}")
            vbox = QVBoxLayout(card)
            lbl_title = QLabel(name)
            lbl_title.setStyleSheet("color: #888; font-size: 12px;")
            lbl_val = QLabel("--")
            lbl_val.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
            vbox.addWidget(lbl_title)
            vbox.addWidget(lbl_val)
            self.metrics_layout.addWidget(card)
            self.metric_labels[name] = lbl_val

    def update_system(self):
        # 1. 获取数据 (从模拟器单例中获取)
        depth = self.state.depth
        vel = self.state.velocity
        
        # 2. 水力学计算
        # 假设矩形断面，宽 5m
        area = depth * 5.0 
        q = HydraulicCalculator.calc_flow_rate(area, vel)
        fr = HydraulicCalculator.calc_froude(vel, depth)
        flow_state = HydraulicCalculator.determine_flow_state(fr)

        # 3. 更新 UI
        self.metric_labels["实时水深 (h)"].setText(f"{depth:.2f}")
        self.metric_labels["平均流速 (v)"].setText(f"{vel:.2f}")
        self.metric_labels["断面流量 (Q)"].setText(f"{q:.2f}")
        self.metric_labels["Froude数"].setText(f"{fr:.2f}")
        self.metric_labels["流态判定"].setText(flow_state)
        
        # 颜色动态变化
        state_color = "#00e676" if "缓流" in flow_state else "#ff5252" # 急流变红
        self.metric_labels["流态判定"].setStyleSheet(f"color: {state_color}; font-size: 20px; font-weight: bold;")

        # 4. 预警逻辑检查
        alerts = HydraulicCalculator.check_alerts(depth, vel, flow_state)
        if alerts:
            for alert in alerts:
                self.add_alert_to_ui(alert['level'], alert['msg'])
                # 写入数据库 (防止重复频繁写入，实际项目中需要去重逻辑)
                # self.db.add_alert(alert['level'], alert['msg']) 
        
        # 5. 记录数据
        self.db.insert_record({
            "depth": depth, "velocity": vel, "flow_rate": q,
            "fr": fr, "state": flow_state, "float_count": 0
        })

    def add_alert_to_ui(self, level, msg):
        # 避免刷屏，只保留最新的 5 条
        if self.alert_list.count() > 5:
            self.alert_list.takeItem(0)
            
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        icon = "🔴" if level == "RED" else "🟡"
        item = QListWidgetItem(f"{timestamp} {icon} [{level}] {msg}")
        item.setForeground(QColor("#ff5252") if level == "RED" else QColor("#ffab00"))
        self.alert_list.addItem(item)
        self.alert_list.scrollToBottom()

    @Slot(object)
    def update_cam_ui(self, frame):
        from PySide6.QtGui import QImage, QPixmap
        import cv2
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        qt_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.cam_label.setPixmap(QPixmap.fromImage(qt_img).scaled(360, 280, Qt.KeepAspectRatio))
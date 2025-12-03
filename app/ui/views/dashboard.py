import datetime
import math
import random
import cv2
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                               QTabWidget, QSizePolicy, QGridLayout)
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QImage, QPixmap, QColor, QFont

# 引入组件
from app.ui.components.chart_3d import Channel3DWidget
from app.ui.components.chart_2d import Channel2DWidget
from app.core.camera_thread import CameraThread
from app.core.calculator import HydraulicCalculator
from app.core.shared_state import SharedState
from app.db.database import DatabaseManager

# --- 指标卡片类 ---
class MetricCard(QFrame):
    def __init__(self, title, unit, is_highlight=False):
        super().__init__()
        self.setObjectName("Card")
        # 允许略微伸缩
        self.setMinimumHeight(90)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        
        # 1. 标题行 (Title + Unit)
        top_row = QHBoxLayout()
        self.lbl_title = QLabel(title)
        self.lbl_title.setObjectName("MetricLabel")
        self.lbl_title.setStyleSheet("color: #8da2c0; font-size: 13px; font-weight: 500;")
        top_row.addWidget(self.lbl_title)
        
        if unit:
            self.lbl_unit = QLabel(unit)
            self.lbl_unit.setObjectName("MetricUnit")
            self.lbl_unit.setStyleSheet("color: #555; font-size: 12px; font-weight: bold;")
            top_row.addWidget(self.lbl_unit, 0, Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(top_row)
        
        # 2. 动态数值 (Big Number)
        self.lbl_value = QLabel("--")
        self.lbl_value.setObjectName("MetricBigVal")
        
        # 字体样式
        font_size = "34px" if not is_highlight else "26px"
        # 默认青色，使用等宽数字字体防止跳动
        self.lbl_value.setStyleSheet(f"""
            color: #00e5ff; 
            font-size: {font_size}; 
            font-family: 'Bahnschrift', 'Segoe UI', sans-serif;
            font-weight: bold;
        """)
        self.lbl_value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.lbl_value)

    def set_value(self, val, color=None):
        self.lbl_value.setText(str(val))
        if color:
            current_font_size = "26px" if "流" in str(val) or "非" in str(val) else "34px"
            self.lbl_value.setStyleSheet(f"""
                color: {color}; 
                font-size: {current_font_size};
                font-family: 'Bahnschrift', 'Segoe UI', sans-serif;
                font-weight: bold;
            """)

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)
        
        self.db = DatabaseManager()
        self.state = SharedState()
        self.tick_counter = 0 
        
        # ================= 左侧栏 =================
        left_container = QVBoxLayout()
        left_container.setSpacing(15)
        
        # 1. 上半部分：可视化模型 (Tab)
        self.vis_tabs = QTabWidget()
        self.vis_tabs.setDocumentMode(True)
        self.chart_2d = Channel2DWidget()
        self.vis_tabs.addTab(self.chart_2d, "🌊 2D 断面孪生")
        self.chart_3d = Channel3DWidget()
        self.vis_tabs.addTab(self.chart_3d, "🧊 3D 空间模型")
        left_container.addWidget(self.vis_tabs, stretch=45)
        
        # 2. 下半部分：全参数矩阵 (4行2列)
        metrics_container = QFrame()
        grid_layout = QGridLayout(metrics_container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(12) # 卡片间距
        
        self.metric_cards = {}
        
        # 创建卡片
        self.metric_cards["depth"] = MetricCard("实时水深 (H)", "m")
        self.metric_cards["vel"] = MetricCard("断面流速 (V)", "m/s")
        self.metric_cards["flow"] = MetricCard("实时流量 (Q)", "m³/s")
        self.metric_cards["width"] = MetricCard("水面宽 (B)", "m")
        self.metric_cards["sediment"] = MetricCard("悬移质含沙量", "kg/m³")
        self.metric_cards["slope"] = MetricCard("底坡 (SLOPE)", "i")
        self.metric_cards["regime"] = MetricCard("流态判别 (REGIME)", "Fr数", is_highlight=True)
        self.metric_cards["uniformity"] = MetricCard("工况判别 (CONDITION)", "类型", is_highlight=True)
        
        # 布局排版
        grid_layout.addWidget(self.metric_cards["depth"], 0, 0)
        grid_layout.addWidget(self.metric_cards["vel"], 0, 1)
        grid_layout.addWidget(self.metric_cards["flow"], 1, 0)
        grid_layout.addWidget(self.metric_cards["width"], 1, 1)
        grid_layout.addWidget(self.metric_cards["sediment"], 2, 0)
        grid_layout.addWidget(self.metric_cards["slope"], 2, 1)
        grid_layout.addWidget(self.metric_cards["regime"], 3, 0)
        grid_layout.addWidget(self.metric_cards["uniformity"], 3, 1)
        
        left_container.addWidget(metrics_container, stretch=55)
        self.layout.addLayout(left_container, stretch=6)

        # ================= 右侧栏 =================
        right_container = QVBoxLayout()
        right_container.setSpacing(15)
        
        # 1. 摄像头
        cam_frame = QFrame()
        cam_frame.setObjectName("Card")
        cam_layout = QVBoxLayout(cam_frame)
        cam_layout.setContentsMargins(2, 2, 2, 2)
        cam_layout.setSpacing(0)
        cam_header = QLabel(" 🔴 LIVE VISION FEED | 漂浮物监测")
        cam_header.setStyleSheet("background: #000; color: #ff5252; font-weight: bold; padding: 6px; font-size: 11px;")
        cam_layout.addWidget(cam_header)
        self.cam_label = QLabel("SENSOR STANDBY")
        self.cam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cam_label.setStyleSheet("color: #444; font-weight: bold; background-color: #080808; letter-spacing: 2px;")
        self.cam_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        cam_layout.addWidget(self.cam_label)
        right_container.addWidget(cam_frame, stretch=4)

        # 2. 控制按钮
        control_frame = QFrame()
        control_frame.setObjectName("Card")
        ctrl_layout = QVBoxLayout(control_frame)
        btn_row = QHBoxLayout()
        self.btn_cam = QPushButton("🔌 开启传感器")
        self.btn_cam.setCheckable(True)
        self.btn_cam.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cam.clicked.connect(self.toggle_camera)
        self.btn_ai = QPushButton("🧠 启动 AI 识别")
        self.btn_ai.setCheckable(True)
        self.btn_ai.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ai.setEnabled(False)
        self.btn_ai.clicked.connect(self.toggle_ai)
        btn_row.addWidget(self.btn_cam)
        btn_row.addWidget(self.btn_ai)
        ctrl_layout.addLayout(btn_row)
        right_container.addWidget(control_frame)

        # 3. 日志
        log_frame = QFrame()
        log_frame.setObjectName("Card")
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(1, 1, 1, 1)
        log_title = QLabel(" SYSTEM LOGS")
        log_title.setStyleSheet("background: #151924; color: #8da2c0; font-size: 11px; padding: 5px; border-bottom: 1px solid #2a3040;")
        log_layout.addWidget(log_title)
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(3)
        self.log_table.setHorizontalHeaderLabels(["TIME", "TYPE", "DESC"])
        header = self.log_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.setShowGrid(False)
        self.log_table.setStyleSheet("border: none;")
        log_layout.addWidget(self.log_table)
        right_container.addWidget(log_frame, stretch=2)
        
        self.layout.addLayout(right_container, stretch=4)

        # 线程与定时器
        self.cam_thread = CameraThread()
        self.cam_thread.frame_signal.connect(self.update_cam_ui)
        self.cam_thread.start()
        
        # --- 【关键】数据刷新定时器 ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(150) # 150ms 刷新一次，让数据动得更自然

    def toggle_camera(self):
        is_on = self.btn_cam.isChecked()
        self.cam_thread.camera_active = is_on
        self.btn_cam.setText("🔌 关闭传感器" if is_on else "🔌 开启传感器")
        self.btn_ai.setEnabled(is_on)
        if not is_on: 
            self.btn_ai.setChecked(False)
            self.toggle_ai()
            self.cam_label.setText("SENSOR STANDBY")

    def toggle_ai(self):
        is_on = self.btn_ai.isChecked()
        self.cam_thread.ai_enabled = is_on
        self.btn_ai.setText("🧠 AI 识别中..." if is_on else "🧠 启动 AI 识别")

    def add_log(self, type_, desc):
        row = self.log_table.rowCount()
        self.log_table.insertRow(row)
        t_item = QTableWidgetItem(datetime.datetime.now().strftime("%H:%M:%S"))
        t_item.setForeground(QColor("#666"))
        self.log_table.setItem(row, 0, t_item)
        type_item = QTableWidgetItem(type_)
        type_item.setForeground(QColor("#ff5252" if type_ == "ALERT" else "#00bcd4"))
        self.log_table.setItem(row, 1, type_item)
        msg_item = QTableWidgetItem(desc)
        msg_item.setForeground(QColor("#ccc"))
        self.log_table.setItem(row, 2, msg_item)
        self.log_table.scrollToBottom()

    @Slot(object, int, str)
    def update_cam_ui(self, frame, count, msg):
        if frame is None or frame.size == 0: return
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        qt_img = QImage(rgb_frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.cam_label.setPixmap(QPixmap.fromImage(qt_img.copy()))
        if count > 0 and msg:
            last = self.log_table.item(self.log_table.rowCount()-1, 2)
            if not last or last.text() != msg: self.add_log("ALERT", msg)

    def update_simulation(self):
        """让数据动起来的核心逻辑"""
        self.tick_counter += 1
        
        # 1. 获取基础值 (来自 SharedState)
        base_depth = self.state.depth
        base_vel = self.state.velocity
        
        # 2. 【关键】生成“呼吸感”波动
        # 正弦波 (周期变化) + 随机噪声 (瞬时抖动)
        wave = math.sin(self.tick_counter * 0.08) * 0.03  # 3cm 左右的规则波动
        jitter = random.uniform(-0.005, 0.005)            # 5mm 左右的随机抖动
        
        current_depth = max(0, base_depth + wave + jitter)
        current_vel = max(0, base_vel + (wave * 0.5) + jitter)
        
        # 3. 水力计算
        area, top_width, _ = HydraulicCalculator.calc_geometry(current_depth)
        q = HydraulicCalculator.calc_flow_rate(area, current_vel)
        fr = HydraulicCalculator.calc_froude(current_vel, current_depth)
        
        regime = HydraulicCalculator.determine_flow_regime(fr)
        uniformity = HydraulicCalculator.determine_flow_uniformity(current_depth, current_vel)
        
        # 模拟含沙量 (随流速波动)
        sediment = 0.0
        if current_vel > 0.1:
            sediment = (current_vel ** 1.5) * 0.6 + random.uniform(-0.05, 0.05)
            sediment = max(0, sediment)

        # 4. 更新图表
        self.chart_2d.set_data(current_depth, current_vel)
        self.chart_3d.update_water_level(current_depth)
        
        # 5. 【关键】更新所有卡片数据
        self.metric_cards["depth"].set_value(f"{current_depth:.3f}")
        self.metric_cards["vel"].set_value(f"{current_vel:.3f}")
        self.metric_cards["flow"].set_value(f"{q:.2f}")
        self.metric_cards["width"].set_value(f"{top_width:.2f}")
        self.metric_cards["sediment"].set_value(f"{sediment:.2f}")
        self.metric_cards["slope"].set_value(f"{HydraulicCalculator.BED_SLOPE}")
        
        # 流态高亮
        regime_color = "#ff5252" if "急流" in regime else "#00e676"
        self.metric_cards["regime"].set_value(f"{fr:.2f} | {regime.split(' ')[0]}", regime_color)
        
        uni_color = "#00e676" if "均匀" in uniformity and "非" not in uniformity else "#ffab00"
        self.metric_cards["uniformity"].set_value(uniformity.split(' ')[0], uni_color)
            
        # 6. 存入数据库
        self.db.insert_record({
            "depth": current_depth, "velocity": current_vel, "flow_rate": q,
            "fr": fr, "state": regime, "float_count": 0
        })
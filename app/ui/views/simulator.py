# app/ui/views/simulator.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QFrame, QHBoxLayout
from PySide6.QtCore import Qt
from app.core.shared_state import SharedState

class SimulatorView(QWidget):
    def __init__(self):
        super().__init__()
        self.state = SharedState()
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        title = QLabel("💻 环境模拟器 (手动控制)")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00bcd4;")
        layout.addWidget(title)
        
        layout.addWidget(QLabel("通过调整下方参数，模拟极端工况以测试系统响应。"))

        # 控制面板
        control_panel = QFrame()
        control_panel.setObjectName("Card")
        cp_layout = QVBoxLayout(control_panel)

        # 1. 水深控制
        self.lbl_depth = QLabel(f"🌊 模拟水深: {self.state.depth} m")
        self.slider_depth = self.create_slider(0, 50, int(self.state.depth * 10)) # 0.0 - 5.0m
        self.slider_depth.valueChanged.connect(self.update_depth)
        cp_layout.addWidget(self.lbl_depth)
        cp_layout.addWidget(self.slider_depth)

        cp_layout.addSpacing(20)

        # 2. 流速控制
        self.lbl_vel = QLabel(f"🚀 模拟流速: {self.state.velocity} m/s")
        self.slider_vel = self.create_slider(0, 100, int(self.state.velocity * 10)) # 0.0 - 10.0m/s
        self.slider_vel.valueChanged.connect(self.update_vel)
        cp_layout.addWidget(self.lbl_vel)
        cp_layout.addWidget(self.slider_vel)

        layout.addWidget(control_panel)
        layout.addStretch()

    def create_slider(self, min_val, max_val, current):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(current)
        slider.setStyleSheet("""
            QSlider::groove:horizontal { background: #333; height: 8px; border-radius: 4px; }
            QSlider::handle:horizontal { background: #00bcd4; width: 18px; margin: -5px 0; border-radius: 9px; }
        """)
        return slider

    def update_depth(self, value):
        real_val = value / 10.0
        self.state.depth = real_val
        self.lbl_depth.setText(f"🌊 模拟水深: {real_val} m")

    def update_vel(self, value):
        real_val = value / 10.0
        self.state.velocity = real_val
        self.lbl_vel.setText(f"🚀 模拟流速: {real_val} m/s")
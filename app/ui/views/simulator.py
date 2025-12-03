import numpy as np
import datetime  # <--- 标准导入
import matplotlib
matplotlib.use('qtagg') 

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
                               QSlider, QPushButton, QTextEdit, QProgressBar, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from app.core.shared_state import SharedState
from app.core.calculator import HydraulicCalculator

# --- 1. 专业图表：比能曲线 (Specific Energy Curve) ---
class EnergyCurveChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.fig = Figure(figsize=(5, 3), dpi=100, facecolor='#151924')
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.canvas)
        
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#151924')
        
        # 初始绘制
        self.plot(2.0, 1.5)

    def plot(self, current_h, current_v):
        self.ax.clear()
        
        # 计算比能曲线 E = h + v^2 / 2g
        # 假设单宽流量 q = h * v (常数)
        g = 9.81
        if current_h <= 0: current_h = 0.1
        q = current_h * current_v 
        
        # 生成 h 序列 (避免 0)
        h_vals = np.linspace(0.1, 6.0, 100)
        # 对应的 E 值
        e_vals = h_vals + (q**2) / (2 * g * h_vals**2)
        
        # 绘制曲线
        self.ax.plot(e_vals, h_vals, color='#444', linewidth=1.5, linestyle='--', label='比能曲线')
        
        # 计算当前点的 E
        current_e = current_h + (current_v**2) / (2 * g)
        
        # 绘制当前状态点
        self.ax.scatter([current_e], [current_h], color='#00e5ff', s=100, zorder=5, label='当前工况')
        
        # 绘制临界水深线 (Fr=1)
        hc = (q**2 / g)**(1/3)
        self.ax.axhline(y=hc, color='#ff5252', linestyle=':', alpha=0.5, label='临界水深')

        # 样式
        self.ax.set_title(f"断面比能曲线 (q={q:.1f} m²/s)", color='white', fontsize=10)
        self.ax.set_xlabel('比能 E (m)', color='#888', fontsize=8)
        self.ax.set_ylabel('水深 h (m)', color='#888', fontsize=8)
        self.ax.tick_params(colors='#666', labelsize=8)
        self.ax.grid(True, linestyle=':', alpha=0.2)
        
        # 去边框
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#333')

        self.canvas.draw()

# --- 2. 主模拟器视图 ---
class SimulatorView(QWidget):
    def __init__(self):
        super().__init__()
        self.state = SharedState()
        
        # 主布局：左右分栏
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # ================= 左侧：控制台 (Controls) =================
        left_frame = QFrame()
        left_frame.setObjectName("Card")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setSpacing(20)

        # 标题
        title = QLabel("🛠️ 环境模拟参数设定")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00e5ff; border-bottom: 1px solid #333; padding-bottom: 10px;")
        left_layout.addWidget(title)

        # 1. 场景预设按钮
        scene_layout = QHBoxLayout()
        self.create_scene_btn("🌊 洪水工况", 4.5, 4.0, scene_layout)
        self.create_scene_btn("🍂 枯水工况", 0.8, 0.5, scene_layout)
        self.create_scene_btn("🔧 检修工况", 0.0, 0.0, scene_layout)
        left_layout.addLayout(scene_layout)

        # 2. 滑块控制区
        left_layout.addWidget(QLabel("手动参数微调:"))
        
        # 水深滑块
        self.lbl_depth = QLabel(f"模拟水深: {self.state.depth} m")
        self.lbl_depth.setStyleSheet("color: #ccc; font-weight: bold;")
        left_layout.addWidget(self.lbl_depth)
        
        self.slider_depth = self.create_slider(0, 50, int(self.state.depth * 10))
        self.slider_depth.valueChanged.connect(self.update_depth)
        left_layout.addWidget(self.slider_depth)

        # 流速滑块
        self.lbl_vel = QLabel(f"模拟流速: {self.state.velocity} m/s")
        self.lbl_vel.setStyleSheet("color: #ccc; font-weight: bold;")
        left_layout.addWidget(self.lbl_vel)
        
        self.slider_vel = self.create_slider(0, 80, int(self.state.velocity * 10)) # Max 8.0 m/s
        self.slider_vel.valueChanged.connect(self.update_vel)
        left_layout.addWidget(self.slider_vel)

        left_layout.addStretch()
        
        # 安全评分条
        left_layout.addWidget(QLabel("🛡️ 当前工况安全评分:"))
        self.progress_safe = QProgressBar()
        self.progress_safe.setFixedHeight(10)
        self.progress_safe.setTextVisible(False)
        self.progress_safe.setStyleSheet("""
            QProgressBar { border: none; background: #333; border-radius: 5px; }
            QProgressBar::chunk { background-color: #00e676; border-radius: 5px; }
        """)
        self.progress_safe.setValue(100)
        left_layout.addWidget(self.progress_safe)

        self.layout.addWidget(left_frame, stretch=4)

        # ================= 右侧：决策中心 (Analytics) =================
        right_frame = QFrame()
        right_frame.setObjectName("Card")
        right_layout = QVBoxLayout(right_frame)
        
        # 标题
        r_title = QLabel("🧠 智能决策分析中心")
        r_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffab00; border-bottom: 1px solid #333; padding-bottom: 10px;")
        right_layout.addWidget(r_title)

        # 1. 比能曲线图表
        self.chart = EnergyCurveChart()
        right_layout.addWidget(self.chart, stretch=2)

        # 2. 决策建议文本框
        right_layout.addWidget(QLabel("📋 AI 辅助决策建议:"))
        self.txt_advice = QTextEdit()
        self.txt_advice.setReadOnly(True)
        self.txt_advice.setStyleSheet("""
            background-color: #111; border: 1px solid #333; color: #bbb; 
            padding: 10px; font-family: 'Consolas', monospace; font-size: 13px;
        """)
        right_layout.addWidget(self.txt_advice, stretch=1)

        self.layout.addWidget(right_frame, stretch=6)
        
        # 初始化一次分析
        self.run_analysis()

    def create_slider(self, min_val, max_val, current):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(current)
        slider.setStyleSheet("""
            QSlider::groove:horizontal { background: #2a3040; height: 6px; border-radius: 3px; }
            QSlider::handle:horizontal { background: #00e5ff; width: 16px; margin: -5px 0; border-radius: 8px; }
            QSlider::sub-page:horizontal { background: #0097a7; border-radius: 3px; }
        """)
        return slider

    def create_scene_btn(self, text, d, v, layout):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # 使用闭包传递参数
        btn.clicked.connect(lambda: self.apply_scene(d, v))
        layout.addWidget(btn)

    def apply_scene(self, depth, vel):
        """应用场景预设"""
        self.slider_depth.setValue(int(depth * 10))
        self.slider_vel.setValue(int(vel * 10))

    def update_depth(self, value):
        real_val = value / 10.0
        self.state.depth = real_val
        self.lbl_depth.setText(f"模拟水深: {real_val} m")
        self.run_analysis()

    def update_vel(self, value):
        real_val = value / 10.0
        self.state.velocity = real_val
        self.lbl_vel.setText(f"模拟流速: {real_val} m/s")
        self.run_analysis()

    def run_analysis(self):
        """核心决策逻辑：分析当前参数，给出建议"""
        h = self.state.depth
        v = self.state.velocity
        
        # 1. 更新图表
        if h > 0:
            self.chart.plot(h, v)

        # 2. 水力计算
        fr = HydraulicCalculator.calc_froude(v, h)
        
        # 3. 生成决策建议
        advice = []
        score = 100
        
        # --- 【修复】正确使用 datetime.datetime.now() ---
        now_str = datetime.datetime.now().strftime('%H:%M:%S')
        advice.append(f"⏱️ 分析时间: {now_str}")
        advice.append(f"📊 当前状态: Fr={fr:.2f}")
        advice.append("-" * 30)

        if h <= 0.1:
            advice.append("🔴 [严重] 渠道干涸！")
            advice.append("   - 建议: 立即检查上游闸门开启情况。")
            advice.append("   - 建议: 停止所有引水作业。")
            score = 0
        elif fr > 1.2:
            advice.append("🔴 [警告] 出现急流 (Supercritical Flow)")
            advice.append("   - 风险: 渠底冲刷风险极高，消力池可能失效。")
            advice.append(f"   - 建议: 需降低流速至 {v*0.8:.1f} m/s 以下。")
            advice.append("   - 建议: 增大下游糙率或启用跌水消能。")
            score -= 40
        elif fr < 1.0 and v > 3.0:
            advice.append("🟡 [注意] 流速过大")
            advice.append("   - 风险: 可能对衬砌造成磨损。")
            score -= 20
        elif fr < 0.5:
            advice.append("🟢 [正常] 缓流状态，水流平稳。")
            advice.append("   - 适宜进行流量观测和水质取样。")
        else:
            advice.append("🟡 [临界] 接近临界流状态 (Fr ≈ 1)")
            advice.append("   - 风险: 水面极不稳定，易产生波状跳跃。")
            advice.append("   - 建议: 调整工况避开 Fr=1.0 区域。")
            score -= 10
            
        if h > 4.0:
            advice.append("🔴 [报警] 水位接近堤顶！")
            advice.append("   - 建议: 紧急开启泄洪闸。")
            score -= 50

        # 更新 UI
        self.txt_advice.setText("\n".join(advice))
        
        # 更新评分条颜色和数值
        score = max(0, score)
        self.progress_safe.setValue(score)
        if score > 80:
            self.progress_safe.setStyleSheet("QProgressBar::chunk { background-color: #00e676; }")
        elif score > 50:
            self.progress_safe.setStyleSheet("QProgressBar::chunk { background-color: #ffab00; }")
        else:
            self.progress_safe.setStyleSheet("QProgressBar::chunk { background-color: #ff5252; }")
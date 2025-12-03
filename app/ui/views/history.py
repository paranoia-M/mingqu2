import datetime
import numpy as np
import matplotlib
matplotlib.use('qtagg') # 强制使用 Qt 后端防止崩溃

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QLabel, QHeaderView, QPushButton, 
                               QComboBox, QFrame, QSizePolicy, QDateEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from app.db.database import DatabaseManager

# --- 1. 趋势图组件 (嵌入在历史页面中) ---
class HistoryTrendChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 黑色背景图表
        self.fig = Figure(figsize=(8, 3), dpi=100, facecolor='#1e1e1e')
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.canvas)
        
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.set_facecolor('#1e1e1e')
        self.ax2 = self.ax1.twinx() # 双坐标轴

    def plot(self, times, depths, velocities):
        self.ax1.clear()
        self.ax2.clear()
        
        # 转换时间格式以便显示
        x = range(len(times))
        
        # 绘制水深 (左轴 - 青色)
        self.ax1.plot(x, depths, color='#00bcd4', label='水深 (m)', linewidth=2)
        self.ax1.set_ylabel('水深 (m)', color='#00bcd4')
        self.ax1.tick_params(axis='y', labelcolor='#00bcd4')
        self.ax1.tick_params(axis='x', labelcolor='#888')
        
        # 填充水深下方的区域
        self.ax1.fill_between(x, depths, color='#00bcd4', alpha=0.1)

        # 绘制流速 (右轴 - 绿色)
        self.ax2.plot(x, velocities, color='#00e676', label='流速 (m/s)', linewidth=2, linestyle='--')
        self.ax2.set_ylabel('流速 (m/s)', color='#00e676')
        self.ax2.tick_params(axis='y', labelcolor='#00e676')
        
        # 样式调整
        self.ax1.grid(True, linestyle=':', alpha=0.3, color='#555')
        self.ax1.spines['top'].set_visible(False)
        self.ax2.spines['top'].set_visible(False)
        self.ax1.spines['bottom'].set_color('#444')
        self.ax1.spines['left'].set_color('#444')
        self.ax2.spines['right'].set_color('#444')
        
        # 标题
        self.ax1.set_title("水力要素变化趋势分析", color='white', pad=10)
        
        self.canvas.draw()

# --- 2. 统计卡片组件 ---
class StatCard(QFrame):
    def __init__(self, title, value, color):
        super().__init__()
        self.setStyleSheet(f"background-color: #252525; border-radius: 6px; border-left: 4px solid {color};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(lbl_t)
        
        self.lbl_v = QLabel(value)
        self.lbl_v.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold;")
        layout.addWidget(self.lbl_v)

    def set_value(self, val):
        self.lbl_v.setText(str(val))

# --- 3. 主视图 ---
class HistoryView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.db = DatabaseManager()
        
        # === 顶部工具栏 ===
        tool_bar = QHBoxLayout()
        tool_bar.addWidget(QLabel("📅 数据筛选:"))
        
        # 数量筛选
        self.combo_limit = QComboBox()
        self.combo_limit.addItems(["最近 50 条", "最近 200 条", "最近 1000 条", "全部数据"])
        self.combo_limit.setStyleSheet("background: #252525; color: white; padding: 5px;")
        self.combo_limit.currentIndexChanged.connect(self.load_data)
        tool_bar.addWidget(self.combo_limit)
        
        tool_bar.addStretch()
        
        # 刷新和导出按钮
        btn_refresh = QPushButton("🔄 刷新")
        btn_refresh.clicked.connect(self.load_data)
        
        btn_export = QPushButton("📥 导出报表")
        btn_export.setStyleSheet("background-color: #2e7d32; color: white;")
        btn_export.clicked.connect(self.export_data)
        
        tool_bar.addWidget(btn_refresh)
        tool_bar.addWidget(btn_export)
        layout.addLayout(tool_bar)
        
        # === 统计摘要区 ===
        stats_layout = QHBoxLayout()
        self.card_max_depth = StatCard("历史最高水位", "0.00 m", "#ff5252")
        self.card_avg_vel = StatCard("平均流速", "0.00 m/s", "#00bcd4")
        self.card_alert_count = StatCard("急流报警次数", "0 次", "#ffab00")
        
        stats_layout.addWidget(self.card_max_depth)
        stats_layout.addWidget(self.card_avg_vel)
        stats_layout.addWidget(self.card_alert_count)
        layout.addLayout(stats_layout)

        # === 趋势图区域 ===
        self.chart = HistoryTrendChart()
        self.chart.setMinimumHeight(250)
        layout.addWidget(self.chart)

        # === 数据表格 ===
        layout.addWidget(QLabel("📋 详细数据列表"))
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["时间", "水深(m)", "流速(m/s)", "流量(m³/s)", "Fr数", "流态"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #1e1e1e; alternate-background-color: #252525; }
            QTableWidget::item { padding: 5px; }
        """)
        self.table.setAlternatingRowColors(True) # 斑马纹
        layout.addWidget(self.table)
        
        # 初始加载
        self.load_data()

    def load_data(self):
        # 1. 获取筛选条件
        limit_text = self.combo_limit.currentText()
        if "50" in limit_text: limit = 50
        elif "200" in limit_text: limit = 200
        elif "1000" in limit_text: limit = 1000
        else: limit = 5000
        
        # 2. 从数据库读取
        rows = self.db.get_history(limit)
        
        # 准备数据用于绘图和统计
        times = []
        depths = []
        vels = []
        alert_count = 0
        
        self.table.setRowCount(len(rows))
        
        # 3. 填充表格 & 收集数据
        for i, row in enumerate(rows):
            # row: (id, time, depth, vel, q, fr, state, float)
            t_str, h, v, q, fr, state = row[1], row[2], row[3], row[4], row[5], row[6]
            
            times.append(t_str)
            depths.append(h)
            vels.append(v)
            
            if "急流" in state:
                alert_count += 1
            
            # 填表
            self.table.setItem(i, 0, QTableWidgetItem(str(t_str)))
            self.table.setItem(i, 1, QTableWidgetItem(f"{h:.3f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{v:.3f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{q:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{fr:.3f}"))
            
            item_state = QTableWidgetItem(state)
            # 智能高亮：如果是急流，把这一行的状态标红
            if "急流" in state:
                item_state.setForeground(QColor("#ff5252"))
                item_state.setBackground(QColor(60, 0, 0)) # 深红背景
            elif "缓流" in state:
                item_state.setForeground(QColor("#00e676"))
                
            self.table.setItem(i, 5, item_state)

        # 4. 更新趋势图 (翻转数据，因为数据库是倒序出来的)
        if len(times) > 0:
            self.chart.plot(list(reversed(times)), list(reversed(depths)), list(reversed(vels)))
            
            # 5. 更新统计面板
            max_h = max(depths)
            avg_v = sum(vels) / len(vels)
            
            self.card_max_depth.set_value(f"{max_h:.3f} m")
            self.card_avg_vel.set_value(f"{avg_v:.3f} m/s")
            self.card_alert_count.set_value(f"{alert_count} 次")
        else:
            self.card_max_depth.set_value("--")
            self.card_avg_vel.set_value("--")
            self.card_alert_count.set_value("0")

    def export_data(self):
        from PySide6.QtWidgets import QMessageBox
        path = self.db.export_to_csv()
        QMessageBox.information(self, "导出成功", f"数据已保存至:\n{path}")
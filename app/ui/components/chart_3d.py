# app/ui/components/chart_3d.py
from PySide6.QtWidgets import QFrame, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from app.config import Colors

class Channel3DWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        
        # 初始化 Matplotlib 画布
        fig = Figure(figsize=(5, 4), dpi=100, facecolor=Colors.PANEL_BG)
        self.canvas = FigureCanvasQTAgg(fig)
        self.axes = fig.add_subplot(111, projection='3d')
        self.axes.set_facecolor(Colors.PANEL_BG)
        
        self.layout.addWidget(self.canvas)
        self.plot_dummy_data()

    def plot_dummy_data(self):
        self.axes.clear()
        x = np.linspace(0, 10, 20)
        y = np.linspace(0, 2, 10)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X/2) * 0.2 + 1.0
        
        self.axes.plot_surface(X, Y, Z, cmap='winter', alpha=0.8, edgecolor='#00bcd4', linewidth=0.2)
        self.axes.axis('off') # 隐藏坐标轴，更美观
        self.canvas.draw()
# app/ui/components/chart_3d.py
import matplotlib
matplotlib.use('qtagg') 

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np

class Channel3DWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. 更加精致的绘图参数配置
        # facecolor='#1e1e1e' 与界面背景融合
        self.fig = Figure(figsize=(6, 4), dpi=100, facecolor='#1e1e1e')
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.canvas)
        
        self.axes = self.fig.add_subplot(111, projection='3d')
        # 绘图区背景设为透明，防止出现白色/灰色色块
        self.axes.set_facecolor((0, 0, 0, 0)) 
        
        # 渠道物理尺寸
        self.len = 10.0
        self.wid = 2.0
        self.max_h = 3.5
        
        # 预计算网格 (高分辨率，使表面更平滑)
        self.X, self.Y = np.meshgrid(
            np.linspace(0, self.len, 50), 
            np.linspace(0, self.wid, 10)
        )
        
        # 初始绘制
        self.update_water_level(2.0)

    def update_water_level(self, depth):
        self.axes.clear()
        
        # 限制显示范围
        d = min(depth, self.max_h)
        
        # ================== 1. 绘制极简风格的渠壁 (Frame) ==================
        # 我们不画网格，而是画几根垂直的“刻度柱”，更有科技感
        # 底部线条 (左右两条)
        self.axes.plot([0, self.len], [0, 0], [0, 0], color='#444', linewidth=1)
        self.axes.plot([0, self.len], [self.wid, self.wid], [0, 0], color='#444', linewidth=1)
        
        # 顶部线条 (左右两条)
        self.axes.plot([0, self.len], [0, 0], [self.max_h, self.max_h], color='#333', linewidth=0.5, linestyle='--')
        self.axes.plot([0, self.len], [self.wid, self.wid], [self.max_h, self.max_h], color='#333', linewidth=0.5, linestyle='--')
        
        # 垂直柱子 (每隔1米画一根，类似标尺)
        for x in range(0, int(self.len) + 1, 2): # 每2米一根
            # 左墙柱子
            self.axes.plot([x, x], [0, 0], [0, self.max_h], color='#333', linewidth=0.5)
            # 右墙柱子
            self.axes.plot([x, x], [self.wid, self.wid], [0, self.max_h], color='#333', linewidth=0.5)
            # 底部连接线
            self.axes.plot([x, x], [0, self.wid], [0, 0], color='#333', linewidth=0.5)

        # ================== 2. 绘制水体 (Water Body) ==================
        Z_water = np.full_like(self.X, d)
        
        # 绘制水面：去掉了 edgecolor (网格线)，只留纯净的半透明面
        # alpha=0.4 让它看起来像玻璃/水
        surf = self.axes.plot_surface(self.X, self.Y, Z_water, color='#00bcd4', alpha=0.4, 
                                    rstride=5, cstride=5, shade=True, antialiased=True)
        
        # ================== 3. 绘制高亮水位线 (Neon Edge) ==================
        # 这是精致感的关键：在水面边缘画一圈发光的亮线
        # 左边缘
        self.axes.plot([0, self.len], [0, 0], [d, d], color='#00e5ff', linewidth=2, alpha=0.9)
        # 右边缘
        self.axes.plot([0, self.len], [self.wid, self.wid], [d, d], color='#00e5ff', linewidth=2, alpha=0.9)
        # 前边缘
        self.axes.plot([0, 0], [0, self.wid], [d, d], color='#00e5ff', linewidth=2, alpha=0.9)
        
        # ================== 4. 绘制渠底 (Bed) ==================
        # 用半透明深色填充底部，增加体积感
        Z_bed = np.zeros_like(self.X)
        self.axes.plot_surface(self.X, self.Y, Z_bed, color='#222', alpha=0.8, shade=False)

        # ================== 5. 坐标轴与视角优化 ==================
        # 设定比例：拉长长度，使透视更真实
        self.axes.set_box_aspect((4, 1, 1.2)) 
        
        self.axes.set_xlim(0, self.len)
        self.axes.set_ylim(0, self.wid)
        self.axes.set_zlim(0, self.max_h)
        
        # 彻底移除背景板 (Panes) - 让图表悬浮在背景上
        self.axes.xaxis.pane.fill = False
        self.axes.yaxis.pane.fill = False
        self.axes.zaxis.pane.fill = False
        
        # 移除背景板边框线
        self.axes.xaxis.pane.set_edgecolor('w')
        self.axes.yaxis.pane.set_edgecolor('w')
        self.axes.zaxis.pane.set_edgecolor('w')
        self.axes.xaxis.pane.set_alpha(0)
        self.axes.yaxis.pane.set_alpha(0)
        self.axes.zaxis.pane.set_alpha(0)
        
        # 去掉网格线 (Grid)
        self.axes.grid(False)
        
        # 自定义刻度样式
        self.axes.tick_params(axis='x', colors='#666', labelsize=8)
        self.axes.tick_params(axis='y', colors='#666', labelsize=8)
        self.axes.tick_params(axis='z', colors='#00bcd4', labelsize=9) # Z轴高亮
        
        # 标签
        self.axes.set_xlabel('Length (m)', color='#666', labelpad=-5, fontsize=9)
        self.axes.set_ylabel('Width (m)', color='#666', labelpad=-5, fontsize=9)
        self.axes.set_zlabel('Depth (m)', color='#00bcd4', labelpad=-5, fontsize=10, fontweight='bold')
        
        # 最佳视角
        self.axes.view_init(elev=25, azim=-50)
        
        self.canvas.draw()
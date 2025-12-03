from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal, Qt

class Sidebar(QFrame):
    # 定义一个信号，传递页面名称
    page_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        
        # --- 【修改点 1】增加宽度 (原 220 -> 250) ---
        self.setFixedWidth(250)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 30, 10, 20) # 调整边距
        
        # --- 【修改点 2】优化标题显示 ---
        # 手动加 \n 换行，或者开启 setWordWrap
        title = QLabel("明渠非均匀流\n流量监测系统")
        title.setObjectName("AppLogo") # 使用 QSS 中的大字体样式
        title.setWordWrap(True)      # 允许自动换行
        title.setAlignment(Qt.AlignmentFlag.AlignCenter) # 居中对齐
        
        # 局部样式微调：字号适当调整，增加行高
        title.setStyleSheet("""
            color: #00e5ff; 
            font-size: 22px; 
            font-weight: bold; 
            padding-bottom: 20px;
            border-bottom: 1px solid #252a3d;
            margin-bottom: 10px;
        """)
        self.layout.addWidget(title)
        
        # 导航按钮配置 (显示文本, 信号标识)
        self.nav_btns = [
            ("📡 实时大屏", "dashboard"),
            ("📊 历史数据", "history"),
            ("💻 模拟器", "simulator"),
            ("📥 导出报表", "export"),
            ("🚪 退出系统", "exit")
        ]
        
        for text, page_id in self.nav_btns:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # 使用闭包绑定 page_id
            btn.clicked.connect(lambda checked=False, pid=page_id: self.page_signal.emit(pid))
            self.layout.addWidget(btn)
            
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
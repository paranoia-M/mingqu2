# app/ui/components/sidebar.py
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal

class Sidebar(QFrame):
    # 定义一个信号，传递页面名称
    page_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(220)
        self.layout = QVBoxLayout(self)
        
        # Logo
        title = QLabel("🌊 监测控制台")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 15px;")
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
            # 使用闭包绑定 page_id
            btn.clicked.connect(lambda checked=False, pid=page_id: self.page_signal.emit(pid))
            self.layout.addWidget(btn)
            
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
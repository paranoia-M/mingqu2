# app/ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from app.ui.components.sidebar import Sidebar
from app.ui.views.dashboard import DashboardView
from app.ui.views.history import HistoryView
from app.ui.views.simulator import SimulatorView  # 导入新页面

class MainWindow(QMainWindow):
    def __init__(self, username="Admin"):
        super().__init__()
        self.resize(1600, 900)
        self.setWindowTitle(f"监测控制台 - 当前用户: {username}")
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.page_signal.connect(self.switch_page)
        self.main_layout.addWidget(self.sidebar)

        self.pages = QStackedWidget()
        self.main_layout.addWidget(self.pages)
        
        # 实例化页面
        self.view_dashboard = DashboardView()
        self.view_history = HistoryView()
        self.view_simulator = SimulatorView() # 实例化模拟器
        
        self.pages.addWidget(self.view_dashboard) # 0
        self.pages.addWidget(self.view_history)   # 1
        self.pages.addWidget(self.view_simulator) # 2
        
        self.pages.setCurrentIndex(0)

    def switch_page(self, page_name):
        if page_name == "dashboard":
            self.pages.setCurrentWidget(self.view_dashboard)
        elif page_name == "history":
            self.view_history.load_data()
            self.pages.setCurrentWidget(self.view_history)
        elif page_name == "simulator":
            self.pages.setCurrentWidget(self.view_simulator)
        elif page_name == "export":
            # 跳转到历史页并触发导出（简化交互）
            self.view_history.load_data()
            self.view_history.export_data()
            self.pages.setCurrentWidget(self.view_history)
        elif page_name == "exit":
            self.close()
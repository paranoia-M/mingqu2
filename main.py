# main.py
import sys
import os

# --- 【关键修复】解决 macOS 下 Matplotlib 与 Qt 冲突导致的闪退 ---
# 必须在导入 PySide6 之前设置
os.environ["QT_MAC_WANTS_LAYER"] = "1"
# -------------------------------------------------------------

from PySide6.QtWidgets import QApplication
from app.ui.views.login import LoginWindow
from app.ui.main_window import MainWindow

# 全局变量引用，防止窗口被垃圾回收
main_win = None

def get_resource_path(relative_path):
    """
    获取资源的绝对路径。
    兼容开发环境（直接运行）和 PyInstaller 打包后的环境（.exe/.app）。
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def start_main_app(username):
    """
    登录成功后的回调：关闭登录窗口，打开主窗口
    """
    global main_win
    main_win = MainWindow(username)
    main_win.show()

if __name__ == "__main__":
    # 初始化 Qt 应用
    app = QApplication(sys.argv)
    
    # --- 加载 QSS 样式表 ---
    # 使用 get_resource_path 确保打包后也能找到样式文件
    style_path = get_resource_path(os.path.join('assets', 'style.qss'))
    
    if os.path.exists(style_path):
        with open(style_path, 'r', encoding='utf-8') as f:
            # 将样式应用到整个 APP
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: Style file not found at {style_path}")
    # -----------------------

    # 1. 实例化登录窗口
    login = LoginWindow()
    
    # 2. 连接信号：当登录成功时，执行 start_main_app
    login.login_success.connect(start_main_app)
    
    # 3. 显示登录窗口
    login.show()

    # 4. 进入事件循环
    sys.exit(app.exec())
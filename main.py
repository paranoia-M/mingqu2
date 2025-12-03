# main.py
import sys
import os
from PySide6.QtWidgets import QApplication
from app.ui.views.login import LoginWindow
from app.ui.main_window import MainWindow

# 全局变量引用
main_win = None

def get_resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和 PyInstaller 打包后的环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def start_main_app(username):
    global main_win
    main_win = MainWindow(username)
    main_win.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # --- 加载样式表 ---
    style_path = get_resource_path(os.path.join('assets', 'style.qss'))
    
    if os.path.exists(style_path):
        with open(style_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: Style file not found at {style_path}")
    # ------------------

    login = LoginWindow()
    login.login_success.connect(start_main_app)
    login.show()

    sys.exit(app.exec())
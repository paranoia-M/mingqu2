# app/ui/views/login.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from app.db.database import DatabaseManager

class LoginWindow(QWidget):
    login_success = Signal(str) # 信号：登录成功，传递用户名

    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统登录 - 渠道数字孪生平台")
        self.resize(400, 500)
        self.setStyleSheet("background-color: #121212; color: #e0e0e0; font-family: 'Microsoft YaHei';")
        self.db = DatabaseManager()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # 容器
        card = QFrame()
        card.setStyleSheet("background-color: #1e1e1e; border-radius: 10px; border: 1px solid #333;")
        card.setFixedSize(320, 380)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(30, 30, 30, 30)

        # 标题
        lbl_title = QLabel("用户登录")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00bcd4; margin-bottom: 20px;")
        card_layout.addWidget(lbl_title)

        # 输入框
        self.txt_user = QLineEdit()
        self.txt_user.setPlaceholderText("用户名 (admin)")
        self.txt_user.setStyleSheet("padding: 10px; border: 1px solid #444; border-radius: 4px; background: #252525; color: white;")
        
        self.txt_pass = QLineEdit()
        self.txt_pass.setPlaceholderText("密码 (123456)")
        self.txt_pass.setEchoMode(QLineEdit.Password)
        self.txt_pass.setStyleSheet("padding: 10px; border: 1px solid #444; border-radius: 4px; background: #252525; color: white;")

        card_layout.addWidget(self.txt_user)
        card_layout.addWidget(self.txt_pass)

        # 按钮
        btn_login = QPushButton("登 录")
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.setStyleSheet("""
            QPushButton { background-color: #00bcd4; color: black; font-weight: bold; padding: 12px; border-radius: 4px; }
            QPushButton:hover { background-color: #00acc1; }
        """)
        btn_login.clicked.connect(self.check_login)
        card_layout.addWidget(btn_login)

        # 错误提示
        self.lbl_msg = QLabel("")
        self.lbl_msg.setStyleSheet("color: #ff5252; font-size: 12px;")
        self.lbl_msg.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.lbl_msg)

        layout.addWidget(card)

    def check_login(self):
        user = self.txt_user.text()
        pwd = self.txt_pass.text()
        
        role = self.db.authenticate(user, pwd)
        if role:
            self.lbl_msg.setText("登录成功，正在跳转...")
            self.login_success.emit(user)
            self.close()
        else:
            self.lbl_msg.setText("用户名或密码错误")
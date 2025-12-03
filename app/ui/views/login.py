# app/ui/views/login.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, 
                               QFrame, QStackedWidget, QHBoxLayout, QGraphicsDropShadowEffect)
# 【关键修复】这里必须导入 QTimer
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QColor, QFont

from app.db.database import DatabaseManager

# --- 高级样式表 (内嵌) ---
LOGIN_STYLESHEET = """
QWidget {
    background-color: #0f121a;
    font-family: 'Segoe UI', 'Microsoft YaHei';
}
QFrame#LoginCard {
    background-color: #1a202e;
    border-radius: 12px;
    border: 1px solid #2a3040;
}
QLabel#AppLogo {
    color: #00e5ff;
    font-size: 28px;
    font-weight: bold;
    letter-spacing: 2px;
}
QLabel#SubTitle {
    color: #8da2c0;
    font-size: 13px;
    margin-bottom: 20px;
}
QLineEdit {
    background-color: #111520;
    border: 1px solid #353f54;
    border-radius: 6px;
    color: #e0e6ed;
    padding: 12px;
    font-size: 14px;
    selection-background-color: #00e5ff;
}
QLineEdit:focus {
    border: 1px solid #00e5ff;
    background-color: #151924;
}
QPushButton#PrimaryBtn {
    background-color: #00e5ff;
    color: #000;
    font-weight: bold;
    border-radius: 6px;
    padding: 12px;
    font-size: 14px;
}
QPushButton#PrimaryBtn:hover {
    background-color: #33ebff;
}
QPushButton#PrimaryBtn:pressed {
    background-color: #00b8cc;
}
QPushButton#LinkBtn {
    background: transparent;
    color: #8da2c0;
    border: none;
    font-size: 12px;
}
QPushButton#LinkBtn:hover {
    color: #00e5ff;
    text-decoration: underline;
}
QLabel#ErrorLabel {
    color: #ff5252;
    font-size: 12px;
}
"""

class LoginWindow(QWidget):
    # 定义登录成功信号
    login_success = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("身份认证 - 数字孪生平台")
        self.resize(450, 600)
        self.setStyleSheet(LOGIN_STYLESHEET)
        self.db = DatabaseManager()

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. 卡片容器
        self.card = QFrame()
        self.card.setObjectName("LoginCard")
        self.card.setFixedSize(380, 500)
        
        # 阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(10)

        # 2. LOGO 区域
        lbl_logo = QLabel("欢迎来到")
        lbl_logo.setObjectName("AppLogo")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_logo)

        self.lbl_subtitle = QLabel("明渠非均匀流流量监测系统")
        self.lbl_subtitle.setObjectName("SubTitle")
        self.lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.lbl_subtitle)

        # 3. 多页面堆叠 (登录/注册)
        self.stack = QStackedWidget()
        self.init_login_ui()
        self.init_register_ui()
        card_layout.addWidget(self.stack)

        main_layout.addWidget(self.card)

    def init_login_ui(self):
        """初始化登录页面 (Index 0)"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)

        self.txt_user_login = QLineEdit()
        self.txt_user_login.setPlaceholderText("用户名")
        self.txt_user_login.setText("admin") # 方便调试，默认填入
        
        self.txt_pass_login = QLineEdit()
        self.txt_pass_login.setPlaceholderText("密码")
        self.txt_pass_login.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pass_login.setText("123456") # 方便调试

        btn_login = QPushButton("立即登录")
        btn_login.setObjectName("PrimaryBtn")
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.clicked.connect(self.do_login)

        # 底部链接
        link_layout = QHBoxLayout()
        link_layout.addStretch()
        btn_to_reg = QPushButton("没有账号？去注册")
        btn_to_reg.setObjectName("LinkBtn")
        btn_to_reg.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_to_reg.clicked.connect(lambda: self.switch_page(1))
        link_layout.addWidget(btn_to_reg)
        link_layout.addStretch()

        self.lbl_msg_login = QLabel("")
        self.lbl_msg_login.setObjectName("ErrorLabel")
        self.lbl_msg_login.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.txt_user_login)
        layout.addWidget(self.txt_pass_login)
        layout.addSpacing(10)
        layout.addWidget(btn_login)
        layout.addWidget(self.lbl_msg_login)
        layout.addStretch()
        layout.addLayout(link_layout)
        
        self.stack.addWidget(page)

    def init_register_ui(self):
        """初始化注册页面 (Index 1)"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)

        self.txt_user_reg = QLineEdit()
        self.txt_user_reg.setPlaceholderText("设置用户名")
        
        self.txt_pass_reg = QLineEdit()
        self.txt_pass_reg.setPlaceholderText("设置密码")
        self.txt_pass_reg.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.txt_pass_confirm = QLineEdit()
        self.txt_pass_confirm.setPlaceholderText("确认密码")
        self.txt_pass_confirm.setEchoMode(QLineEdit.EchoMode.Password)

        btn_reg = QPushButton("创建账户")
        btn_reg.setObjectName("PrimaryBtn")
        btn_reg.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reg.clicked.connect(self.do_register)

        # 底部链接
        link_layout = QHBoxLayout()
        link_layout.addStretch()
        btn_to_login = QPushButton("已有账号？返回登录")
        btn_to_login.setObjectName("LinkBtn")
        btn_to_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_to_login.clicked.connect(lambda: self.switch_page(0))
        link_layout.addWidget(btn_to_login)
        link_layout.addStretch()

        self.lbl_msg_reg = QLabel("")
        self.lbl_msg_reg.setObjectName("ErrorLabel")
        self.lbl_msg_reg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.txt_user_reg)
        layout.addWidget(self.txt_pass_reg)
        layout.addWidget(self.txt_pass_confirm)
        layout.addSpacing(10)
        layout.addWidget(btn_reg)
        layout.addWidget(self.lbl_msg_reg)
        layout.addStretch()
        layout.addLayout(link_layout)

        self.stack.addWidget(page)

    def switch_page(self, index):
        """切换页面并清空错误信息"""
        self.stack.setCurrentIndex(index)
        self.lbl_msg_login.setText("")
        self.lbl_msg_reg.setText("")
        self.lbl_subtitle.setText("明渠非均匀流流量监测系统 " if index == 0 else "创建您的管理员账户")

    def do_login(self):
        u = self.txt_user_login.text().strip()
        p = self.txt_pass_login.text().strip()
        
        if not u or not p:
            self.lbl_msg_login.setText("请输入用户名和密码")
            return

        role = self.db.authenticate(u, p)
        if role:
            self.lbl_msg_login.setStyleSheet("color: #00e676;")
            self.lbl_msg_login.setText("登录成功，正在进入系统...")
            # 【关键修复】使用闭包确保信号在窗口关闭前发出
            QTimer.singleShot(500, lambda: self.finish_login(u))
        else:
            self.lbl_msg_login.setStyleSheet("color: #ff5252;")
            self.lbl_msg_login.setText("用户名或密码错误")

    def finish_login(self, username):
        """登录完成后的回调"""
        self.login_success.emit(username) # 先发信号
        self.close() # 后关闭

    def do_register(self):
        u = self.txt_user_reg.text().strip()
        p = self.txt_pass_reg.text().strip()
        p2 = self.txt_pass_confirm.text().strip()
        
        if not u or not p:
            self.lbl_msg_reg.setText("所有字段均为必填")
            return
        
        if p != p2:
            self.lbl_msg_reg.setText("两次输入的密码不一致")
            return
            
        success, msg = self.db.register_user(u, p)
        if success:
            self.lbl_msg_reg.setStyleSheet("color: #00e676;")
            self.lbl_msg_reg.setText("注册成功！请返回登录")
            # 清空输入框
            self.txt_user_reg.clear()
            self.txt_pass_reg.clear()
            self.txt_pass_confirm.clear()
        else:
            self.lbl_msg_reg.setStyleSheet("color: #ff5252;")
            self.lbl_msg_reg.setText(msg)
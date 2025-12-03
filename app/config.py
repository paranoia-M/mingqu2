# app/config.py

class Colors:
    BACKGROUND = "#121212"
    PANEL_BG = "#1e1e1e"
    TEXT_PRIMARY = "#e0e0e0"
    TEXT_SECONDARY = "#888888"
    ACCENT_CYAN = "#00bcd4"
    ACCENT_GREEN = "#00e676"
    ACCENT_RED = "#ff5252"
    BORDER = "#333333"

class AppConfig:
    WINDOW_TITLE = "明渠非均匀流流量监测系统"
    WINDOW_WIDTH = 1600
    WINDOW_HEIGHT = 900
    USE_MOCK_CAMERA = False # 如果没有摄像头改为 True
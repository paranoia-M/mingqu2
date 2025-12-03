# app/core/shared_state.py
class SharedState:
    """
    单例模式，用于在不同页面间共享实时数据
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedState, cls).__new__(cls)
            # 设置初始值，防止界面显示 --
            cls._instance.depth = 2.0      # 默认水深 2.0m
            cls._instance.velocity = 1.5   # 默认流速 1.5m/s
            cls._instance.sediment = 0.5   # 默认含沙量
            cls._instance.is_simulation_mode = True 
        return cls._instance
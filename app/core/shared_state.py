# app/core/shared_state.py
class SharedState:
    """
    单例模式，用于在不同页面间共享实时数据
    模拟器修改这里的数据，仪表盘读取这里的数据
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedState, cls).__new__(cls)
            # 初始化默认值
            cls._instance.depth = 2.0      # 水深 m
            cls._instance.velocity = 1.5   # 流速 m/s
            cls._instance.sediment = 0.5   # 含沙量 kg/m³
            cls._instance.is_simulation_mode = True # 是否开启模拟器控制
        return cls._instance
# app/core/calculator.py
import math

class HydraulicCalculator:
    """水力学核心计算引擎"""
    
    @staticmethod
    def calc_flow_rate(area: float, velocity: float) -> float:
        """计算流量 Q = A * V"""
        return area * velocity

    @staticmethod
    def calc_froude(velocity: float, depth: float) -> float:
        """计算 Froude 数 Fr = V / sqrt(g * h)"""
        g = 9.81
        if depth <= 0: return 0.0
        return velocity / math.sqrt(g * depth)

    @staticmethod
    def determine_flow_state(fr: float) -> str:
        """流态判别"""
        if fr < 0.95:
            return "缓流 (Subcritical)"
        elif fr > 1.05:
            return "急流 (Supercritical)"
        else:
            return "临界流 (Critical)"

    @staticmethod
    def check_alerts(depth, velocity, flow_state):
        """预警规则判断"""
        alerts = []
        if depth > 3.5:
            alerts.append({"level": "RED", "msg": "水位超限警报！"})
        if "急流" in flow_state:
            alerts.append({"level": "YELLOW", "msg": "流态转为急流，注意冲刷"})
        return alerts
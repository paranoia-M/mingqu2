# app/core/calculator.py
import math

class HydraulicCalculator:
    """水力学核心计算引擎"""
    
    # 渠道几何参数
    BOTTOM_WIDTH = 3.0  # 底宽 b (m)
    SIDE_SLOPE = 1.0    # 边坡系数 m (1:m)
    BED_SLOPE = 0.0002  # 底坡 i
    ROUGHNESS = 0.014   # 糙率 n

    @staticmethod
    def calc_geometry(depth):
        """计算断面几何参数 (关键修复：确保此方法存在)"""
        # 防止深度为负数导致错误
        if depth <= 0: return 0.0, HydraulicCalculator.BOTTOM_WIDTH, 0.0
        
        b = HydraulicCalculator.BOTTOM_WIDTH
        m = HydraulicCalculator.SIDE_SLOPE
        
        # 水面宽 B = b + 2mh
        top_width = b + 2 * m * depth
        
        # 过流面积 A = (b + mh)h
        area = (b + m * depth) * depth
        
        # 湿周 P = b + 2h * sqrt(1 + m^2)
        wetted_perimeter = b + 2 * depth * math.sqrt(1 + m**2)
        
        # 水力半径 R = A / P
        hydraulic_radius = area / wetted_perimeter if wetted_perimeter > 0 else 0
        
        return area, top_width, hydraulic_radius

    @staticmethod
    def calc_flow_rate(area, velocity):
        return area * velocity

    @staticmethod
    def calc_froude(velocity, depth):
        if depth <= 0: return 0.0
        g = 9.81
        # 简化计算：Fr = v / sqrt(g*h)
        # 如果需要更精确，可以用 hydraulic_depth = Area / Top_Width
        return velocity / math.sqrt(g * depth)

    @staticmethod
    def determine_flow_regime(fr):
        if fr < 0.95: return "缓流 (Subcritical)"
        elif fr > 1.05: return "急流 (Supercritical)"
        else: return "临界流 (Critical)"

    @staticmethod
    def determine_flow_uniformity(depth, velocity):
        """判别均匀流"""
        area, top_width, r = HydraulicCalculator.calc_geometry(depth)
        n = HydraulicCalculator.ROUGHNESS
        i = HydraulicCalculator.BED_SLOPE
        
        if r <= 0: return "非均匀流 (Non-uniform)"
        
        # 曼宁公式计算正常流速
        v_normal = (1.0 / n) * (r**(2/3)) * (i**(0.5))
        
        if abs(velocity - v_normal) / (v_normal + 0.001) < 0.1:
            return "均匀流 (Uniform)"
        else:
            return "非均匀流 (Non-uniform)"
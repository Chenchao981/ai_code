import re

# 调整类定义顺序，将函数放入类内部
class CPLogParser:
    def __init__(self, data_dir):
        """
        初始化日志解析器
        
        Args:
            data_dir (str): 数据目录
        """
        self.data_dir = data_dir
        self.target_params = ["BVDSS1"]

    def _parse_limit_value(self, limit_str):
        """
        解析限制值
        """
        # 新增单位转换逻辑
        unit_multipliers = {
            'V': 1,
            'mV': 1e-3,
            'uV': 1e-6,
            'nV': 1e-9,
            'A': 1,
            'mA': 1e-3,
            'uA': 1e-6,
            'nA': 1e-9
        }

        try:
            # 提取数值和单位
            value_part = re.findall(r"[-+]?\d*\.?\d+", limit_str)[0]
            unit_part = re.findall(r"[A-Za-z]+", limit_str)[0] if re.search(r"[A-Za-z]+", limit_str) else ''
            
            # 转换数值
            value = float(value_part) * unit_multipliers.get(unit_part, 1)
            return value
        except Exception as e:
            print(f"解析限制值错误: {limit_str} - {str(e)}")
            return None

    def parse_all_files(self):
        """
        解析所有文件
        
        Returns:
            tuple: (DataFrame, limits_dict)
        """
        # 示例数据供调试
        import pandas as pd
        dummy_df = pd.DataFrame({
            'BVDSS1': [700.0, 680.0, 750.0],
            'Lot': ['LOT01', 'LOT01', 'LOT02']
        })
        dummy_limits = {'BVDSS1': {'upper': 900.0, 'lower': 660.0}}
        return dummy_df, dummy_limits

# 确保没有外部函数定义
import re
import os
import pandas as pd
import glob

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
        
        Args:
            limit_str (str): 限制值字符串，如 "900.0V"
            
        Returns:
            float: 解析后的数值
        """
        # 单位转换字典
        unit_multipliers = {
            'V': 1,
            'mV': 1e-3,
            'uV': 1e-6,
            'nV': 1e-9,
            'A': 1,
            'mA': 1e-3,
            'uA': 1e-6,
            'nA': 1e-9,
            'OHM': 1,
            'mOHM': 1e-3,
            '-': 1  # 对于无单位的情况
        }

        try:
            # 提取数值和单位
            value_part = re.findall(r"[-+]?\d*\.?\d+", limit_str)[0]
            unit_part = re.findall(r"[A-Za-z]+", limit_str)[0] if re.search(r"[A-Za-z]+", limit_str) else '-'
            
            # 转换数值
            value = float(value_part) * unit_multipliers.get(unit_part, 1)
            return value
        except Exception as e:
            print(f"解析限制值错误: {limit_str} - {str(e)}")
            return None

    def _parse_file(self, file_path):
        """
        解析单个CP测试文件
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            tuple: (数据字典列表, 参数限制字典)
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # 提取文件头信息
            lot_number = None
            wafer_number = None
            
            for i, line in enumerate(lines[:10]):  # 假设头部信息在前10行
                if 'Lot number' in line:
                    lot_number = line.split('\t')[1].strip()
                elif 'Wafer number' in line:
                    wafer_number = int(line.split('\t')[1].strip())
            
            if lot_number is None or wafer_number is None:
                print(f"错误: 无法从文件 {file_path} 提取批次号或晶圆片号")
                return [], {}
                
            # 提取参数名称
            params_line_idx = None
            for i, line in enumerate(lines):
                if line.startswith('No.U'):
                    params_line_idx = i
                    break
                    
            if params_line_idx is None:
                print(f"错误: 无法从文件 {file_path} 提取参数名称")
                return [], {}
                
            # 解析参数名称
            param_names = lines[params_line_idx].strip().split('\t')
            
            # 解析参数限制
            limit_u = lines[params_line_idx + 1].strip().split('\t')
            limit_l = lines[params_line_idx + 2].strip().split('\t')
            
            # 创建参数限制字典
            limits = {}
            for i, param in enumerate(param_names):
                if param in self.target_params:
                    if i < len(limit_u) and i < len(limit_l):
                        limits[param] = {
                            'upper': self._parse_limit_value(limit_u[i]) if limit_u[i] else None,
                            'lower': self._parse_limit_value(limit_l[i]) if limit_l[i] else None
                        }
            
            # 查找数据起始行
            data_start_idx = None
            for i in range(params_line_idx + 1, len(lines)):
                if lines[i].strip() and lines[i][0].isdigit():
                    data_start_idx = i
                    break
                    
            if data_start_idx is None:
                print(f"错误: 无法从文件 {file_path} 提取数据起始行")
                return [], {}
                
            # 解析数据
            data_records = []
            
            for i in range(data_start_idx, len(lines)):
                line = lines[i].strip()
                if not line:
                    continue
                    
                values = line.split('\t')
                
                # 确保有足够的值
                if len(values) < len(param_names):
                    continue
                    
                record = {
                    'Lot': lot_number,
                    'Wafer': f"{wafer_number:02d}"  # 格式化为两位数字
                }
                
                # 添加目标参数的值
                for param in self.target_params:
                    if param in param_names:
                        param_idx = param_names.index(param)
                        if param_idx < len(values):
                            try:
                                value = float(values[param_idx])
                                record[param] = value
                            except ValueError:
                                # 无效值跳过
                                continue
                
                # 只有包含所有目标参数的记录才添加
                if all(param in record for param in self.target_params):
                    data_records.append(record)
            
            return data_records, limits
            
        except Exception as e:
            print(f"解析文件 {file_path} 出错: {str(e)}")
            return [], {}
            
    def parse_all_files(self):
        """
        解析所有CP测试文件
        
        Returns:
            tuple: (DataFrame, limits_dict)
        """
        # 获取所有txt文件
        file_pattern = os.path.join(self.data_dir, "*.TXT")
        file_paths = glob.glob(file_pattern)
        
        if not file_paths:
            print(f"错误: 在目录 {self.data_dir} 中未找到.TXT文件")
            return None, None
            
        all_records = []
        all_limits = {}
        
        for file_path in file_paths:
            records, limits = self._parse_file(file_path)
            all_records.extend(records)
            
            # 合并参数限制
            for param, limit_values in limits.items():
                if param not in all_limits:
                    all_limits[param] = limit_values
        
        if not all_records:
            print("错误: 未能从任何文件中提取有效数据")
            return None, None
            
        # 转换为DataFrame
        df = pd.DataFrame(all_records)
        
        return df, all_limits

# 确保没有外部函数定义
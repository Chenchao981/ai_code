import os
import re
import pandas as pd
import numpy as np
from pathlib import Path
import glob

class CPLogParser:
    """
    解析晶圆厂CP测试数据文件
    """
    def __init__(self, data_dir):
        """
        初始化解析器
        
        Args:
            data_dir (str): CP测试数据文件所在目录
        """
        self.data_dir = data_dir
        self.target_params = ["BVDSS1", "BVDSS2", "DELTABV", "IDSS1", "VTH", 
                             "RDSON1", "VFSDS", "IGSS2", "IGSSR2", "IDSS2"]
        self.all_data = []
        self.limits = {}  # 存储每个参数的上下限
        
    def parse_scientific_notation(self, value_str):
        """
        解析科学计数法表示的数值
        
        Args:
            value_str (str): 科学计数法字符串，如 "1.20E-08"
            
        Returns:
            float: 转换后的浮点数
        """
        try:
            return float(value_str)
        except ValueError:
            # 处理特殊值，如 "999.9"
            if value_str == "999.9":
                return np.nan
            return np.nan
            
    def parse_unit_value(self, value_str):
        """
        解析带单位的数值，如 "900.0V", "4.000uA" 等
        
        Args:
            value_str (str): 带单位的数值字符串
            
        Returns:
            float: 转换后的浮点数
        """
        # 移除单位并转换为浮点数
        try:
            # 处理特殊情况，如 "50.00-" 或 "10.00-"
            if value_str.endswith('-'):
                return float(value_str[:-1])
            
            # 提取数值部分
            match = re.match(r'([-+]?\d*\.?\d+)([a-zA-Z]*)', value_str)
            if match:
                value, unit = match.groups()
                value = float(value)
                
                # 根据单位进行转换
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
                    'mOHM': 1e-3
                }
                
                if unit in unit_multipliers:
                    return value * unit_multipliers[unit]
                return value
            return float(value_str)
        except (ValueError, TypeError):
            return np.nan
    
    def parse_file(self, file_path):
        """
        解析单个CP测试数据文件
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            dict: 解析后的数据
        """
        file_data = {
            'file_path': file_path,
            'program_name': '',
            'lot_number': '',
            'wafer_number': '',
            'date': '',
            'time': '',
            'parameters': {},
            'limits': {},
            'data': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # 解析文件头信息
            for i, line in enumerate(lines[:10]):
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split('\t')
                if len(parts) >= 2:
                    if parts[0] == 'Program name':
                        file_data['program_name'] = parts[1]
                    elif parts[0] == 'Lot number':
                        file_data['lot_number'] = parts[1]
                    elif parts[0] == 'Wafer number':
                        file_data['wafer_number'] = parts[1]
                    elif parts[0] == 'Date':
                        file_data['date'] = parts[1]
                    elif parts[0] == 'Time':
                        file_data['time'] = parts[1]
            
            # 查找参数行、上下限行和数据行
            param_line_idx = -1
            limit_u_idx = -1
            limit_l_idx = -1
            data_start_idx = -1
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split('\t')
                if parts[0] == 'No.U':
                    param_line_idx = i
                elif parts[0] == 'LimitU':
                    limit_u_idx = i
                elif parts[0] == 'LimitL':
                    limit_l_idx = i
                elif parts[0].isdigit() and data_start_idx == -1:
                    data_start_idx = i
            
            if param_line_idx == -1 or limit_u_idx == -1 or limit_l_idx == -1 or data_start_idx == -1:
                print(f"文件格式错误: {file_path}")
                return file_data
            
            # 解析参数名称
            param_names = lines[param_line_idx].strip().split('\t')
            
            # 解析上下限
            limit_u_values = lines[limit_u_idx].strip().split('\t')
            limit_l_values = lines[limit_l_idx].strip().split('\t')
            
            # 存储目标参数的上下限
            for i, param in enumerate(param_names):
                if param in self.target_params:
                    if i < len(limit_u_values):
                        file_data['limits'][param] = {
                            'upper': self.parse_unit_value(limit_u_values[i]),
                            'lower': self.parse_unit_value(limit_l_values[i])
                        }
                        
                        # 更新全局限制
                        if param not in self.limits:
                            self.limits[param] = file_data['limits'][param]
            
            # 解析数据行
            for i in range(data_start_idx, len(lines)):
                line = lines[i].strip()
                if not line:
                    continue
                    
                parts = line.split('\t')
                if not parts[0].isdigit():
                    continue
                    
                data_row = {'No.U': int(parts[0])}
                
                for j, param in enumerate(param_names):
                    if j < len(parts) and param in self.target_params:
                        data_row[param] = self.parse_scientific_notation(parts[j])
                
                file_data['data'].append(data_row)
            
            return file_data
            
        except Exception as e:
            print(f"解析文件 {file_path} 时出错: {str(e)}")
            return file_data
    
    def parse_all_files(self):
        """
        解析目录下所有CP测试数据文件
        
        Returns:
            list: 所有文件的解析结果
        """
        all_files = []
        
        # 遍历目录下所有文件
        for root, dirs, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith('.txt') or file.endswith('.log') or file.endswith('.dat'):
                    file_path = os.path.join(root, file)
                    file_data = self.parse_file(file_path)
                    if file_data['data']:  # 只添加有效数据
                        all_files.append(file_data)
        
        self.all_data = all_files
        return all_files
    
    def get_combined_dataframe(self):
        """
        将所有解析的数据合并为一个DataFrame
        
        Returns:
            pd.DataFrame: 合并后的数据框
        """
        if not self.all_data:
            self.parse_all_files()
            
        all_rows = []
        
        for file_data in self.all_data:
            lot_number = file_data['lot_number']
            wafer_number = file_data['wafer_number']
            
            for row in file_data['data']:
                row_data = {
                    'Lot': lot_number,
                    'Wafer': wafer_number,
                    'No.U': row['No.U']
                }
                
                for param in self.target_params:
                    if param in row:
                        row_data[param] = row[param]
                
                all_rows.append(row_data)
        
        return pd.DataFrame(all_rows)
    
    def get_limits(self):
        """
        获取所有参数的上下限
        
        Returns:
            dict: 参数上下限字典
        """
        return self.limits
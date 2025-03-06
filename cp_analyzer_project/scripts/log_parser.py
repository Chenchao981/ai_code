#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
晶圆厂CP测试数据日志解析模块
负责解析CP测试日志文件
"""

import os
import re
import pandas as pd
import numpy as np
from collections import defaultdict

class CPLogParser:
    """
    CP测试数据日志解析类
    """
    def __init__(self, data_dir):
        """
        初始化日志解析器
        
        Args:
            data_dir (str): 数据目录
        """
        self.data_dir = data_dir
        self.target_params = ["BVDSS1"]  # 简化为只分析BVDSS1参数
        # self.target_params = ["BVDSS1", "BVDSS2", "DELTABV", "IDSS1", "VTH", 
        #                      "RDSON1", "VFSDS", "IGSS2", "IGSSR2", "IDSS2"]
        
    def find_log_files(self):
        """
        查找日志文件
        
        Returns:
            list: 日志文件路径列表
        """
        # 检查数据目录是否存在
        if not os.path.exists(self.data_dir):
            print(f"错误: 数据目录 {self.data_dir} 不存在")
            return None
            
        # 查找所有文件
        all_files = []
        for root, _, files in os.walk(self.data_dir):
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)
                
        # 筛选CP测试日志文件
        log_files = [f for f in all_files if self.is_cp_log(f)]
        
        if not log_files:
            print(f"警告: 在目录 {self.data_dir} 中未找到CP测试日志文件")
            
        return log_files
    
    def is_cp_log(self, file_path):
        """
        判断文件是否为CP测试日志文件
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            bool: 是否为CP测试日志文件
        """
        # 检查文件扩展名
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in ['.txt', '.log', '.dat', '']:
            return False
            
        # 检查文件内容
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # 读取前几行
                header_lines = [f.readline() for _ in range(10)]
                header = ''.join(header_lines)
                
                # 检查是否包含关键字
                if 'No.U' in header and any(param in header for param in self.target_params):
                    return True
                    
        except Exception as e:
            print(f"警告: 无法读取文件 {file_path}: {e}")
            
        return False
    
    def parse_file(self, file_path):
        """
        解析单个CP测试日志文件
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            tuple: (DataFrame, dict) 解析后的数据和参数限制
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # 提取元数据
            metadata = self._extract_metadata(lines)
            
            # 提取表头
            header_idx, headers = self._extract_headers(lines)
            if header_idx is None or headers is None:
                print(f"错误: 无法在文件 {file_path} 中找到表头")
                return None, None
                
            # 提取限制
            limits = self._extract_limits(lines, header_idx, headers)
            
            # 提取数据
            data = self._extract_data(lines, header_idx, headers, metadata)
            
            return data, limits
            
        except Exception as e:
            print(f"错误: 解析文件 {file_path} 时出错: {e}")
            return None, None
    
    def _extract_metadata(self, lines):
        """
        提取元数据
        
        Args:
            lines (list): 文件行列表
            
        Returns:
            dict: 元数据字典
        """
        metadata = {}
        
        # 提取批次号
        for line in lines[:10]:
            if 'Lot number' in line:
                parts = line.strip().split('\t')
                if len(parts) > 1:
                    metadata['Lot'] = parts[1]
                    break
                    
        # 提取晶圆片号
        for line in lines[:10]:
            if 'Wafer number' in line:
                parts = line.strip().split('\t')
                if len(parts) > 1:
                    metadata['Wafer'] = parts[1]
                    break
                    
        return metadata
    
    def _extract_headers(self, lines):
        """
        提取表头
        
        Args:
            lines (list): 文件行列表
            
        Returns:
            tuple: (int, list) 表头行索引和表头列表
        """
        for i, line in enumerate(lines):
            if 'No.U' in line:
                headers = line.strip().split('\t')
                return i, headers
                
        return None, None
    
    def _extract_limits(self, lines, header_idx, headers):
        """
        提取参数限制
        
        Args:
            lines (list): 文件行列表
            header_idx (int): 表头行索引
            headers (list): 表头列表
            
        Returns:
            dict: 参数限制字典
        """
        limits = {}
        
        # 提取上限
        if header_idx + 1 < len(lines) and 'LimitU' in lines[header_idx + 1]:
            limit_u_parts = lines[header_idx + 1].strip().split('\t')
            if len(limit_u_parts) >= len(headers):
                for i, header in enumerate(headers):
                    if header in self.target_params:
                        if i < len(limit_u_parts):
                            limits.setdefault(header, {})
                            limits[header]['upper'] = self._parse_limit_value(limit_u_parts[i])
                            
        # 提取下限
        if header_idx + 2 < len(lines) and 'LimitL' in lines[header_idx + 2]:
            limit_l_parts = lines[header_idx + 2].strip().split('\t')
            if len(limit_l_parts) >= len(headers):
                for i, header in enumerate(headers):
                    if header in self.target_params:
                        if i < len(limit_l_parts):
                            limits.setdefault(header, {})
                            limits[header]['lower'] = self._parse_limit_value(limit_l_parts[i])
                            
        return limits
    
    def _parse_limit_value(self, limit_str):
        """
        解析限制值
        
        Args:
            limit_str (str): 限制值字符串
            
        Returns:
            float: 限制值
        """
        if not limit_str or limit_str == '':
            return None
            
        # 移除单位
        value_str = re.sub(r'[A-Za-z]', '', limit_str)
        
        # 处理特殊格式
        if '-' in value_str:
            value_str = value_str.replace('-', '')
            
        try:
            # 转换为浮点数
            value = float(value_str)
            
            # 处理单位
            if 'n' in limit_str.lower():
                value *= 1e-9
            elif 'u' in limit_str.lower():
                value *= 1e-6
            elif 'm' in limit_str.lower() and 'ohm' not in limit_str.lower():
                value *= 1e-3
                
            return value
            
        except ValueError:
            return None
    
    def _extract_data(self, lines, header_idx, headers, metadata):
        """
        提取数据
        
        Args:
            lines (list): 文件行列表
            header_idx (int): 表头行索引
            headers (list): 表头列表
            metadata (dict): 元数据字典
            
        Returns:
            DataFrame: 解析后的数据
        """
        # 跳过表头和限制行
        data_start_idx = header_idx + 7  # 表头 + 上限 + 下限 + 4行偏置
        
        # 创建数据列表
        data_list = []
        
        # 遍历数据行
        for i in range(data_start_idx, len(lines)):
            line = lines[i].strip()
            if not line:
                continue
                
            parts = line.split('\t')
            if len(parts) < len(headers):
                continue
                
            # 创建数据字典
            data_dict = {}
            
            # 添加元数据
            for key, value in metadata.items():
                data_dict[key] = value
                
            # 添加数据
            for j, header in enumerate(headers):
                if j < len(parts):
                    data_dict[header] = parts[j]
                    
            # 添加器件编号
            if 'No.U' in data_dict:
                data_dict['Device'] = data_dict['No.U']
                
            data_list.append(data_dict)
            
        # 创建DataFrame
        df = pd.DataFrame(data_list)
        
        return df
    
    def parse_all_files(self):
        """
        解析所有CP测试日志文件
        
        Returns:
            tuple: (DataFrame, dict) 解析后的数据和参数限制
        """
        # 查找日志文件
        log_files = self.find_log_files()
        if not log_files:
            return None, None
            
        # 创建数据列表和限制字典
        all_data = []
        all_limits = {}
        
        # 遍历日志文件
        for file_path in log_files:
            print(f"正在解析文件: {os.path.basename(file_path)}")
            
            # 解析文件
            data, limits = self.parse_file(file_path)
            
            if data is not None:
                all_data.append(data)
                
            if limits is not None:
                for param, limit in limits.items():
                    if param not in all_limits:
                        all_limits[param] = limit
                        
        # 合并数据
        if all_data:
            df = pd.concat(all_data, ignore_index=True)
            return df, all_limits
        else:
            return None, None
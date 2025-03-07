#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
晶圆厂CP测试数据分析模块
"""

import pandas as pd
import numpy as np

class CPDataAnalyzer:
    """
    CP测试数据分析类
    
    用于清洗、分析CP测试数据，并提供各种数据分析功能
    """
    
    def __init__(self, df=None, target_params=None, limits=None):
        """
        初始化数据分析器
        
        Args:
            df (DataFrame): 原始数据
            target_params (list): 目标参数列表
            limits (dict): 参数限制字典，格式为 {参数名: {'upper': 上限值, 'lower': 下限值}}
        """
        self.df = df
        self.df_clean = None
        self.target_params = target_params or []
        self.limits = limits or {}
    
    def clean_data(self):
        """
        数据清洗
        
        Returns:
            DataFrame: 清洗后的数据
        """
        if self.df is None or self.df.empty:
            print("错误: 数据为空，无法进行清洗")
            return None
            
        # 复制数据，避免修改原始数据
        df_clean = self.df.copy()
        
        # 检查Lot列是否存在
        if 'Lot' not in df_clean.columns:
            print("警告: 数据中缺少Lot列，将使用默认值")
            df_clean['Lot'] = 'LOT01'
            
        # 检查Wafer列是否存在
        if 'Wafer' not in df_clean.columns:
            print("警告: 数据中缺少Wafer列，将使用默认值")
            df_clean['Wafer'] = '01'
        
        # 处理特殊值
        for param in self.target_params:
            if param in df_clean.columns:
                # 将字符串转换为数值类型，错误值设为NaN
                df_clean[param] = pd.to_numeric(df_clean[param], errors='coerce')
                
                # 获取参数的上下限
                upper = None
                lower = None
                if param in self.limits:
                    upper = self.limits[param].get('upper')
                    lower = self.limits[param].get('lower')
                
                # 根据上下限过滤异常值
                if upper is not None:
                    # 标记超出上限的值
                    df_clean.loc[df_clean[param] > upper * 1.5, f"{param}_outlier_high"] = True
                    # 不移除异常值，只标记
                
                if lower is not None:
                    # 标记低于下限的值
                    df_clean.loc[df_clean[param] < lower * 0.5, f"{param}_outlier_low"] = True
                    # 不移除异常值，只标记
        
        # 保存清洗后的数据
        self.df_clean = df_clean
        
        return df_clean

    def get_parameter_info(self, param):
        """
        获取参数信息
        
        Args:
            param (str): 参数名称
            
        Returns:
            dict: 参数信息字典
        """
        info = {
            'name': param,
            'limits': {}
        }
        
        # 获取参数限制
        if param in self.limits:
            info['limits'] = self.limits[param]
        else:
            # 如果没有找到限制，设置默认值
            info['limits'] = {'upper': None, 'lower': None}
            print(f"警告: 未找到参数 {param} 的限制信息，将使用默认值")
        
        return info

    def get_data_for_boxplot(self, param):
        """
        获取箱型图数据
        
        Args:
            param (str): 参数名称
            
        Returns:
            dict: 箱型图数据字典
        """
        if self.df_clean is None or param not in self.df_clean.columns:
            return None
        
        # 确保Wafer列存在
        if 'Wafer' not in self.df_clean.columns:
            print(f"警告: 数据中缺少Wafer列，将使用默认值")
            self.df_clean['Wafer'] = '01'
        
        # 按晶圆片分组
        wafers = sorted(self.df_clean['Wafer'].unique())
        
        # 创建箱型图数据
        x = []
        y = []
        
        for wafer in wafers:
            # 获取该晶圆片的数据
            wafer_data = self.df_clean[self.df_clean['Wafer'] == wafer][param].dropna()
            
            # 添加数据
            x.extend([wafer] * len(wafer_data))
            y.extend(wafer_data.tolist())
        
        return {'x': x, 'y': y}

    def get_data_for_scatter(self, param):
        """
        获取散点图数据
        
        Args:
            param (str): 参数名称
            
        Returns:
            dict: 散点图数据字典
        """
        if self.df_clean is None or param not in self.df_clean.columns:
            return None
        
        # 确保必要的列存在
        if 'Lot' not in self.df_clean.columns:
            print(f"警告: 数据中缺少Lot列，将使用默认值")
            self.df_clean['Lot'] = 'LOT01'
        
        if 'Wafer' not in self.df_clean.columns:
            print(f"警告: 数据中缺少Wafer列，将使用默认值")
            self.df_clean['Wafer'] = '01'
        
        # 创建散点图数据
        data = {
            'x': self.df_clean['Wafer'].tolist(),  # 使用晶圆片号作为X轴
            'y': self.df_clean[param].tolist(),
            'lot': self.df_clean['Lot'].tolist()
        }
        
        return data
    
    def calculate_statistics(self, param):
        """
        计算参数的统计信息
        
        Args:
            param (str): 参数名称
            
        Returns:
            dict: 统计信息字典
        """
        if self.df_clean is None or param not in self.df_clean.columns:
            return None
        
        # 获取参数数据
        data = self.df_clean[param].dropna()
        
        if len(data) == 0:
            return None
        
        # 计算整体统计信息
        overall_stats = {
            'mean': float(data.mean()),
            'median': float(data.median()),
            'std': float(data.std()),
            'min': float(data.min()),
            'max': float(data.max()),
            'count': int(len(data)),
            'range': float(data.max() - data.min())
        }
        
        # 创建统计信息字典
        stats = {
            'overall': overall_stats
        }
        
        # 计算分位数
        for q in [0.1, 0.25, 0.5, 0.75, 0.9]:
            stats['overall'][f'q{int(q*100)}'] = float(data.quantile(q))
        
        # 获取参数限制
        if param in self.limits:
            stats['overall']['upper_limit'] = self.limits[param].get('upper')
            stats['overall']['lower_limit'] = self.limits[param].get('lower')
        else:
            stats['overall']['upper_limit'] = None
            stats['overall']['lower_limit'] = None
        
        # 按晶圆片计算统计信息
        stats['by_lot'] = {}
        
        # 确保Wafer列存在
        if 'Wafer' not in self.df_clean.columns:
            print(f"警告: 数据中缺少Wafer列，将使用默认值")
            self.df_clean['Wafer'] = '01'
        
        # 按晶圆片分组计算统计信息
        for wafer in sorted(self.df_clean['Wafer'].unique()):
            wafer_data = self.df_clean[self.df_clean['Wafer'] == wafer][param].dropna()
            
            if len(wafer_data) == 0:
                continue
            
            lot_stats = {
                'mean': float(wafer_data.mean()),
                'median': float(wafer_data.median()),
                'std': float(wafer_data.std()) if len(wafer_data) > 1 else 0.0,
                'min': float(wafer_data.min()),
                'max': float(wafer_data.max()),
                'count': int(len(wafer_data)),
                'range': float(wafer_data.max() - wafer_data.min())
            }
            
            stats['by_lot'][wafer] = lot_stats
        
        return stats
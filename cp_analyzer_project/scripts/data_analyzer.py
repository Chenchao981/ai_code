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
    
    # 确保Lot列存在
    if 'Lot' not in self.df_clean.columns:
        print(f"警告: 数据中缺少Lot列，将使用默认值")
        self.df_clean['Lot'] = 'LOT01'
    
    # 按批次分组
    lots = sorted(self.df_clean['Lot'].unique())
    
    # 创建箱型图数据
    x = []
    y = []
    
    for lot in lots:
        # 获取该批次的数据
        lot_data = self.df_clean[self.df_clean['Lot'] == lot][param].dropna()
        
        # 添加数据
        x.extend([lot] * len(lot_data))
        y.extend(lot_data.tolist())
    
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
        self.df_clean['Wafer'] = self.df_clean.index.astype(str)
    
    if 'Device' not in self.df_clean.columns:
        print(f"警告: 数据中缺少Device列，将使用默认值")
        self.df_clean['Device'] = self.df_clean.index.astype(str)
    
    # 创建散点图数据
    data = {
        'x': self.df_clean['Lot'].tolist(),
        'y': self.df_clean[param].tolist(),
        'wafer': self.df_clean['Wafer'].tolist(),
        'device': self.df_clean['Device'].tolist()
    }
    
    return data
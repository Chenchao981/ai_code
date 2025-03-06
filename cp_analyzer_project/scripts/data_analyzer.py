import pandas as pd
import numpy as np

class CPDataAnalyzer:
    """
    CP测试数据分析类
    """
    def __init__(self, dataframe, limits):
        """
        初始化数据分析器
        
        Args:
            dataframe (pd.DataFrame): 包含CP测试数据的DataFrame
            limits (dict): 参数上下限字典
        """
        self.df = dataframe
        self.limits = limits
        self.df_clean = None
        self.target_params = ["BVDSS1"]  # 简化为只分析BVDSS1参数
    
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
                
                # 处理异常值
                # 计算四分位数
                q1 = df_clean[param].quantile(0.25)
                q3 = df_clean[param].quantile(0.75)
                iqr = q3 - q1
                
                # 定义异常值范围
                lower_bound = q1 - 3 * iqr
                upper_bound = q3 + 3 * iqr
                
                # 标记异常值
                df_clean.loc[(df_clean[param] < lower_bound) | (df_clean[param] > upper_bound), f"{param}_outlier"] = True
                
                # 不移除异常值，只标记，以便在图表中显示
        
        # 保存清洗后的数据
        self.df_clean = df_clean
        
        return df_clean
    
    def calculate_statistics(self, param):
        """
        计算指定参数的统计信息
        
        Args:
            param (str): 参数名称
            
        Returns:
            dict: 统计信息字典
        """
        if param not in self.df.columns:
            return {}
            
        # 按Lot分组计算统计量
        stats = self.df.groupby('Lot')[param].agg(['mean', 'std', 'median', 'count']).reset_index()
        stats.columns = ['Lot', 'Average', 'StdDev', 'Median', 'Count']
        
        # 计算整体统计量
        overall_stats = {
            'mean': self.df[param].mean(),
            'std': self.df[param].std(),
            'median': self.df[param].median(),
            'min': self.df[param].min(),
            'max': self.df[param].max(),
            'count': self.df[param].count()
        }
        
        # 获取参数的上下限
        limits = {}
        if param in self.limits:
            limits = self.limits[param]
        
        return {
            'by_lot': stats.to_dict('records'),
            'overall': overall_stats,
            'limits': limits
        }
    
    def get_boxplot_data(self, param):
        """
        获取箱型图所需的数据
        
        Args:
            param (str): 参数名称
            
        Returns:
            dict: 箱型图数据
        """
        if param not in self.df.columns:
            return {}
            
        # 清洗数据
        df_clean = self.clean_data()
        
        # 按Lot分组获取箱型图数据
        boxplot_data = []
        
        for lot, group in df_clean.groupby('Lot'):
            if param in group.columns:
                values = group[param].dropna().tolist()
                
                if values:
                    q1 = np.percentile(values, 25)
                    median = np.percentile(values, 50)
                    q3 = np.percentile(values, 75)
                    iqr = q3 - q1
                    
                    # 计算须线范围
                    whisker_low = max(min(values), q1 - 1.5 * iqr)
                    whisker_high = min(max(values), q3 + 1.5 * iqr)
                    
                    # 识别异常值
                    outliers = [v for v in values if v < whisker_low or v > whisker_high]
                    
                    boxplot_data
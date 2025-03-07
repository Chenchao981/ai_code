#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CP Test Data Analyzer
-------------------
This module analyzes CP test data.
"""

import pandas as pd
import numpy as np


class CPDataAnalyzer:
    """Analyzer for CP test data."""
    
    def __init__(self, data=None):
        """
        Initialize the data analyzer with the specified data.
        
        Args:
            data (pandas.DataFrame, optional): CP test data.
        """
        self.data = data
        
    def set_data(self, data):
        """
        Set the data to analyze.
        
        Args:
            data (pandas.DataFrame): CP test data.
        """
        self.data = data
    
    def get_parameter_stats(self, parameter, group_by=None):
        """
        Get statistics for a parameter.
        
        Args:
            parameter (str): Parameter name.
            group_by (str, optional): Column to group by. Defaults to None.
            
        Returns:
            pandas.DataFrame: DataFrame containing statistics.
        """
        if self.data is None or parameter not in self.data.columns:
            return pd.DataFrame()
            
        if group_by is not None and group_by in self.data.columns:
            # Group by the specified column
            stats = self.data.groupby(group_by)[parameter].agg([
                ('count', 'count'),
                ('mean', 'mean'),
                ('std', lambda x: x.std() if len(x) > 1 else 0),
                ('min', 'min'),
                ('max', 'max')
            ]).reset_index()
        else:
            # Calculate overall statistics
            stats = pd.DataFrame({
                'count': [len(self.data)],
                'mean': [self.data[parameter].mean()],
                'std': [self.data[parameter].std() if len(self.data) > 1 else 0],
                'min': [self.data[parameter].min()],
                'max': [self.data[parameter].max()]
            })
            
            if group_by is not None:
                stats[group_by] = ['All']
                
        return stats
    
    def calculate_yield(self, parameter, lower=None, upper=None, group_by=None):
        """
        Calculate yield statistics for a parameter.
        
        Args:
            parameter (str): Parameter name.
            lower (float, optional): Lower limit. Defaults to None.
            upper (float, optional): Upper limit. Defaults to None.
            group_by (str, optional): Column to group by. Defaults to None.
            
        Returns:
            pandas.DataFrame: DataFrame containing yield statistics.
        """
        if self.data is None or parameter not in self.data.columns:
            return pd.DataFrame()
            
        data = self.data.copy()
        
        # Add a pass/fail column based on limits
        if lower is not None and upper is not None:
            data['pass'] = (data[parameter] >= lower) & (data[parameter] <= upper)
        elif lower is not None:
            data['pass'] = data[parameter] >= lower
        elif upper is not None:
            data['pass'] = data[parameter] <= upper
        else:
            # No limits, all pass
            data['pass'] = True
            
        if group_by is not None and group_by in data.columns:
            # Group by the specified column
            yield_data = data.groupby(group_by).agg({
                'pass': ['count', 'sum']
            }).reset_index()
            
            # Rename columns
            yield_data.columns = [group_by, 'total', 'passed']
            
            # Calculate fail count and yield percentage
            yield_data['failed'] = yield_data['total'] - yield_data['passed']
            yield_data['yield_pct'] = (yield_data['passed'] / yield_data['total'] * 100)
            
        else:
            # Calculate overall yield
            total = len(data)
            passed = data['pass'].sum()
            failed = total - passed
            yield_pct = passed / total * 100 if total > 0 else 0
            
            yield_data = pd.DataFrame({
                'total': [total],
                'passed': [passed],
                'failed': [failed],
                'yield_pct': [yield_pct]
            })
            
            if group_by is not None:
                yield_data[group_by] = ['All']
                
        return yield_data
    
    def calculate_cp_capability(self, parameter, lower=None, upper=None, group_by=None):
        """
        Calculate process capability indices (Cp, Cpk) for a parameter.
        
        Args:
            parameter (str): Parameter name.
            lower (float, optional): Lower limit. Defaults to None.
            upper (float, optional): Upper limit. Defaults to None.
            group_by (str, optional): Column to group by. Defaults to None.
            
        Returns:
            pandas.DataFrame: DataFrame containing process capability indices.
        """
        if self.data is None or parameter not in self.data.columns:
            return pd.DataFrame()
            
        if lower is None and upper is None:
            return pd.DataFrame()
            
        data = self.data.copy()
        
        if group_by is not None and group_by in data.columns:
            groups = data.groupby(group_by)
            group_names = data[group_by].unique()
        else:
            # Treat all data as one group
            data['_all'] = 'All'
            groups = data.groupby('_all')
            group_names = ['All']
            group_by = '_all'
            
        results = []
        
        for name, group in zip(group_names, groups):
            if isinstance(name, tuple):
                name = name[0]
                
            group_data = group[1][parameter].dropna()
            
            if len(group_data) < 2:
                continue
                
            mean = group_data.mean()
            std = group_data.std()
            
            # Calculate process capability indices
            if std > 0:
                # Calculate Cp if both limits are provided
                if lower is not None and upper is not None:
                    cp = (upper - lower) / (6 * std)
                else:
                    cp = float('nan')
                    
                # Calculate Cpk
                if upper is not None:
                    cpu = (upper - mean) / (3 * std)
                else:
                    cpu = float('nan')
                    
                if lower is not None:
                    cpl = (mean - lower) / (3 * std)
                else:
                    cpl = float('nan')
                    
                if not np.isnan(cpu) and not np.isnan(cpl):
                    cpk = min(cpu, cpl)
                elif not np.isnan(cpu):
                    cpk = cpu
                elif not np.isnan(cpl):
                    cpk = cpl
                else:
                    cpk = float('nan')
            else:
                cp = float('nan')
                cpk = float('nan')
                
            result = {
                group_by: name,
                'count': len(group_data),
                'mean': mean,
                'std': std,
                'cp': cp,
                'cpk': cpk
            }
            
            results.append(result)
            
        if not results:
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=[group_by, 'count', 'mean', 'std', 'cp', 'cpk'])
            
        return pd.DataFrame(results)
        
    def filter_data(self, conditions):
        """
        Filter data based on conditions.
        
        Args:
            conditions (dict): Dictionary containing column-value pairs to filter on.
            
        Returns:
            pandas.DataFrame: Filtered data.
        """
        if self.data is None:
            return pd.DataFrame()
            
        filtered_data = self.data.copy()
        
        for column, value in conditions.items():
            if column in filtered_data.columns:
                if isinstance(value, (list, tuple)):
                    filtered_data = filtered_data[filtered_data[column].isin(value)]
                else:
                    filtered_data = filtered_data[filtered_data[column] == value]
                    
        return filtered_data
        
    def get_parameter_data(self, parameter, group_by=None):
        """
        Get data for a specific parameter, optionally grouped.
        
        Args:
            parameter (str): Parameter name.
            group_by (str, optional): Column to group by. Defaults to None.
            
        Returns:
            dict: Dictionary containing data for the parameter.
        """
        if self.data is None or parameter not in self.data.columns:
            return {}
            
        result = {}
        
        if group_by is not None and group_by in self.data.columns:
            for group, group_data in self.data.groupby(group_by):
                result[group] = group_data[parameter].tolist()
        else:
            result['all'] = self.data[parameter].tolist()
            
        return result


if __name__ == "__main__":
    # Example usage
    from log_parser import CPLogParser
    
    parser = CPLogParser("./data/data2/rawdata")
    df = parser.parse_all_logs()
    
    analyzer = CPDataAnalyzer(df)
    
    # Calculate statistics for BVDSS1 parameter
    stats = analyzer.get_parameter_stats("BVDSS1", group_by="wafer_number")
    print(stats)
    
    # Calculate yield for BVDSS1 parameter with limits
    limits = parser.get_limits("BVDSS1")
    yield_data = analyzer.calculate_yield("BVDSS1", limits['lower'], limits['upper'], group_by="wafer_number")
    print(yield_data)

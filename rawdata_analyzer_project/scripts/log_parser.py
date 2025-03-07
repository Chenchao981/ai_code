#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CP Test Log Parser
-------------------
This module parses CP test log files.
"""

import os
import re
import pandas as pd
import numpy as np
from pathlib import Path


class CPLogParser:
    """Parser for CP test log files."""
    
    def __init__(self, log_dir=None):
        """
        Initialize the log parser.
        
        Args:
            log_dir (str, optional): Directory containing CP test log files.
        """
        self.log_dir = log_dir if log_dir else './data/data2/rawdata'
        self.parameter_limits = {}  # Dictionary to store parameter limits
        
    def set_log_dir(self, log_dir):
        """
        Set the directory containing CP test log files.
        
        Args:
            log_dir (str): Directory containing CP test log files.
        """
        self.log_dir = log_dir
        
    def get_log_files(self):
        """
        Get a list of CP test log files in the specified directory.
        
        Returns:
            list: List of CP test log file paths.
        """
        log_files = []
        
        if not os.path.exists(self.log_dir):
            return log_files
            
        for file in os.listdir(self.log_dir):
            file_path = os.path.join(self.log_dir, file)
            
            if os.path.isfile(file_path) and file.endswith('.TXT'):
                log_files.append(file_path)
                
        return log_files
        
    def parse_log_file(self, file_path):
        """
        Parse a CP test log file.
        
        Args:
            file_path (str): Path to the CP test log file.
            
        Returns:
            pandas.DataFrame: Parsed data.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # Extract header information
            header_info = self._extract_header_info(lines)
            
            # Extract parameter data
            data_df = self._extract_parameter_data(lines)
            
            # Add header information to each row
            for key, value in header_info.items():
                data_df[key] = value
                
            # Add file information
            data_df['file_name'] = os.path.basename(file_path)
            
            return data_df
            
        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")
            return pd.DataFrame()
            
    def parse_all_logs(self):
        """
        Parse all CP test log files in the specified directory.
        
        Returns:
            pandas.DataFrame: Combined data from all log files.
        """
        log_files = self.get_log_files()
        
        if not log_files:
            print(f"No log files found in {self.log_dir}")
            return pd.DataFrame()
            
        all_data = []
        
        for file_path in log_files:
            data_df = self.parse_log_file(file_path)
            
            if not data_df.empty:
                all_data.append(data_df)
                
        if not all_data:
            return pd.DataFrame()
            
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        
        return combined_df
        
    def _extract_header_info(self, lines):
        """
        Extract header information from log file lines.
        
        Args:
            lines (list): Lines from the log file.
            
        Returns:
            dict: Dictionary containing header information.
        """
        header_info = {}
        
        # Patterns to match header information
        patterns = {
            'program_name': r'Program name\s+(.*)',
            'lot_number': r'Lot number\s+(.*)',
            'wafer_number': r'Wafer number\s+(.*)',
            'test_date': r'Date\s+(.*)',
            'test_time': r'Time\s+(.*)'
        }
        
        for i, line in enumerate(lines[:20]):  # Check first 20 lines for header info
            for key, pattern in patterns.items():
                match = re.search(pattern, line)
                
                if match:
                    header_info[key] = match.group(1).strip()
        
        return header_info
        
    def _extract_parameter_data(self, lines):
        """
        Extract parameter data from log file lines.
        
        Args:
            lines (list): Lines from the log file.
            
        Returns:
            pandas.DataFrame: DataFrame containing parameter data.
        """
        # Find the "No.U" line which contains parameter names
        param_line_idx = -1
        limit_u_line_idx = -1
        limit_l_line_idx = -1
        data_start_idx = -1
        
        for i, line in enumerate(lines):
            if line.startswith('No.U'):
                param_line_idx = i
            elif line.startswith('LimitU'):
                limit_u_line_idx = i
            elif line.startswith('LimitL'):
                limit_l_line_idx = i
            elif param_line_idx != -1 and limit_u_line_idx != -1 and limit_l_line_idx != -1 and line[0].isdigit():
                data_start_idx = i
                break
                
        if param_line_idx == -1 or data_start_idx == -1:
            return pd.DataFrame()
            
        # Extract parameter names
        param_names = lines[param_line_idx].strip().split('\t')
        
        # Extract upper and lower limits
        upper_limits = self._parse_limits(lines[limit_u_line_idx], param_names)
        lower_limits = self._parse_limits(lines[limit_l_line_idx], param_names)
        
        # Store limits for each parameter
        for param, upper_limit in upper_limits.items():
            lower_limit = lower_limits.get(param)
            
            if param not in self.parameter_limits:
                self.parameter_limits[param] = {}
                
            self.parameter_limits[param]['upper'] = upper_limit
            self.parameter_limits[param]['lower'] = lower_limit
            
        # Extract data
        data_lines = []
        
        for i in range(data_start_idx, len(lines)):
            line = lines[i].strip()
            
            if not line:
                continue
                
            parts = line.split('\t')
            
            if len(parts) >= len(param_names) and parts[0].isdigit():
                data_lines.append(parts)
            else:
                # Stop when we reach a non-data line
                break
                
        # Create DataFrame
        df = pd.DataFrame(data_lines, columns=param_names)
        
        # Convert numeric columns to appropriate types
        for col in df.columns:
            if col in ['No.U', 'X', 'Y', 'Bin']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                # Handle scientific notation (e.g., 1.20E-08)
                df[col] = df[col].apply(lambda x: self._parse_scientific_notation(x))
                
        return df
        
    def _parse_limits(self, limit_line, param_names):
        """
        Parse limit values from a limit line.
        
        Args:
            limit_line (str): Line containing limit values.
            param_names (list): List of parameter names.
            
        Returns:
            dict: Dictionary mapping parameter names to limit values.
        """
        limits = {}
        parts = limit_line.strip().split('\t')
        
        for i, param in enumerate(param_names):
            if i < len(parts):
                limit_value = self._parse_scientific_notation(parts[i])
                limits[param] = limit_value
                
        return limits
        
    def _parse_scientific_notation(self, value_str):
        """
        Parse a string that may contain scientific notation or unit suffixes.
        
        Args:
            value_str (str): String to parse.
            
        Returns:
            float or None: Parsed value.
        """
        if not isinstance(value_str, str):
            return value_str
            
        value_str = value_str.strip()
        
        if not value_str or value_str == '999.9':
            return None
            
        # Handle common unit suffixes
        unit_multipliers = {
            'u': 1e-6,  # micro
            'n': 1e-9,  # nano
            'm': 1e-3,  # milli
            'k': 1e3,   # kilo
            'M': 1e6,   # mega
            'G': 1e9    # giga
        }
        
        # Regular expression to match number with optional scientific notation and/or unit suffix
        match = re.match(r'([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*([a-zA-Z]*)([a-zA-Z]*)?', value_str)
        
        if match:
            value = float(match.group(1))
            
            # Apply unit multiplier if present
            if match.group(2) in unit_multipliers:
                value *= unit_multipliers[match.group(2)]
                
            # Check if there's a secondary unit (e.g., "mOHM" would have "m" as group 2 and "OHM" as group 3)
            # We just apply the first unit multiplier
                
            return value
            
        # Handle special notations like "-" (meaning zero or infinity)
        if value_str == '-':
            return 0
            
        return None
        
    def get_limits(self, parameter):
        """
        Get the upper and lower limits for a parameter.
        
        Args:
            parameter (str): Parameter name.
            
        Returns:
            dict: Dictionary containing upper and lower limits.
        """
        if parameter in self.parameter_limits:
            return self.parameter_limits[parameter]
            
        return {'upper': None, 'lower': None}
        
    def set_limits(self, parameter, lower=None, upper=None):
        """
        Set the upper and lower limits for a parameter.
        
        Args:
            parameter (str): Parameter name.
            lower (float, optional): Lower limit. Defaults to None.
            upper (float, optional): Upper limit. Defaults to None.
        """
        if parameter not in self.parameter_limits:
            self.parameter_limits[parameter] = {}
            
        if lower is not None:
            self.parameter_limits[parameter]['lower'] = lower
            
        if upper is not None:
            self.parameter_limits[parameter]['upper'] = upper


if __name__ == "__main__":
    # Example usage
    parser = CPLogParser("./data/data2/rawdata")
    log_files = parser.get_log_files()
    
    print(f"Found {len(log_files)} log files.")
    
    if log_files:
        # Parse first log file
        first_log = log_files[0]
        df = parser.parse_log_file(first_log)
        
        print(f"Parsed data from {first_log}:")
        print(df.head())
        
        # Get parameter limits
        for param in ['BVDSS1', 'BVDSS2', 'DELTABV']:
            limits = parser.get_limits(param)
            print(f"{param} limits: lower={limits['lower']}, upper={limits['upper']}")
            
        # Parse all log files
        all_data = parser.parse_all_logs()
        
        print(f"Parsed data from all log files: {len(all_data)} rows")

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
晶圆厂CP测试数据分析工具主程序
"""

import os
import sys
import argparse
from log_parser import CPLogParser
from data_analyzer import CPDataAnalyzer
from chart_generator import CPChartGenerator
from html_report import CPHTMLReport

def parse_args():
    """
    解析命令行参数
    
    Returns:
        Namespace: 参数命名空间
    """
    parser = argparse.ArgumentParser(description='晶圆厂CP测试数据分析工具')
    
    parser.add_argument('--data-dir', type=str, default='./data/data2/rawdata',
                        help='数据目录路径 (默认: ./data/data2/rawdata)')
    
    parser.add_argument('--output-dir', type=str, default='./output',
                        help='输出目录路径 (默认: ./output)')
    
    parser.add_argument('--params', type=str, nargs='+',
                        default=["BVDSS1", "BVDSS2", "DELTABV", "IDSS1", "VTH", 
                                "RDSON1", "VFSDS", "IGSS2", "IGSSR2", "IDSS2"],
                        help='要分析的参数列表')
    
    return parser.parse_args()

def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_args()
    
    # 获取数据目录的绝对路径
    data_dir = os.path.abspath(args.data_dir)
    
    # 获取输出目录的绝对路径
    output_dir = os.path.abspath(args.output_dir)
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"数据目录: {data_dir}")
    print(f"输出目录: {output_dir}")
    print(f"目标参数: {args.params}")
    
    # 初始化日志解析器
    print("\n步骤1: 解析CP测试数据文件...")
    parser = CPLogParser(data_dir)
    parser.target_params = args.params
    
    # 解析所有文件
    df, limits = parser.parse_all_files()
    
    if df is None or limits is None:
        print("错误: 未能成功解析CP测试数据文件")
        return 1
        
    print(f"成功解析 {len(df)} 条数据记录")
    
    # 初始化数据分析器
    print("\n步骤2: 数据清洗与分析...")
    analyzer = CPDataAnalyzer(df, limits)
    analyzer.target_params = args.params
    
    # 数据清洗
    df_clean = analyzer.clean_data()
    
    if df_clean is None:
        print("错误: 数据清洗失败")
        return 1
        
    print(f"清洗后的数据记录数: {len(df_clean)}")
    
    # 初始化图表生成器
    print("\n步骤3: 生成图表...")
    chart_generator = CPChartGenerator(analyzer)
    chart_generator.output_dir = output_dir
    
    # 初始化HTML报告生成器
    print("\n步骤4: 生成HTML报告...")
    report_generator = CPHTMLReport(chart_generator)
    
    # 生成所有报告
    index_path = report_generator.generate_all_reports()
    
    if index_path is None:
        print("错误: 生成HTML报告失败")
        return 1
        
    print(f"\n分析完成! HTML报告已生成: {index_path}")
    print(f"请在浏览器中打开以下链接查看报告:")
    print(f"file://{index_path}")
    
    # 尝试自动打开浏览器
    try:
        import webbrowser
        webbrowser.open(f"file://{index_path}")
    except:
        pass
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
import os
import sys
import argparse
from log_parser import CPLogParser
from data_analyzer import CPDataAnalyzer
from chart_generator import CPChartGenerator
from html_report import CPHTMLReport

def main():
    """
    主程序入口
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='晶圆厂CP测试数据分析工具')
    parser.add_argument('--data-dir', type=str, default='E:/data/data2/rawdata',
                        help='CP测试数据目录路径 (默认: E:/data/data2/rawdata)')
    parser.add_argument('--output-dir', type=str, default='./output',
                        help='输出目录路径 (默认: ./output)')
    parser.add_argument('--interactive', action='store_true',
                        help='生成交互式HTML报告 (默认: True)')
    args = parser.parse_args()
    
    # 获取数据目录的绝对路径
    if os.path.isabs(args.data_dir):
        data_dir = args.data_dir
    else:
        data_dir = os.path.abspath(args.data_dir)
        
    # 检查数据目录是否存在
    if not os.path.exists(data_dir):
        print(f"错误: 数据目录 {data_dir} 不存在")
        return 1
        
    # 获取输出目录的绝对路径
    if os.path.isabs(args.output_dir):
        output_dir = args.output_dir
    else:
        output_dir = os.path.abspath(args.output_dir)
        
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 解析CP测试日志文件
    print(f"正在解析CP测试日志文件...")
    parser = CPLogParser(data_dir)
    df, limits = parser.parse_all_files()
    
    if df is None or df.empty:
        print("错误: 未找到有效的CP测试数据")
        return 1
        
    print(f"成功解析 {len(df)} 条数据记录")
    
    # 数据分析
    print("正在进行数据分析...")
    analyzer = CPDataAnalyzer(df, limits)
    df_clean = analyzer.clean_data()
    
    # 生成图表
    print("正在生成图表...")
    chart_generator = CPChartGenerator(analyzer)
    
    # 生成HTML报告
    print("正在生成HTML报告...")
    report_generator = CPHTMLReport(chart_generator)
    index_path = report_generator.generate_all_reports()
    
    if index_path:
        print(f"HTML报告已生成: {index_path}")
        print(f"请在浏览器中打开上述文件查看报告")
    else:
        print("错误: 生成HTML报告失败")
        return 1
        
    return 0

if __name__ == '__main__':
    sys.exit(main())
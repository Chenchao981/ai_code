#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
晶圆厂CP测试数据HTML报告生成模块
生成交互式HTML报告
"""

import os
import shutil
import jinja2
import plotly.io as pio
from datetime import datetime

class CPHTMLReport:
    """
    CP测试数据HTML报告生成类
    """
    def __init__(self, chart_generator):
        """
        初始化HTML报告生成器
        
        Args:
            chart_generator (CPChartGenerator): 图表生成器对象
        """
        self.chart_generator = chart_generator
        self.analyzer = chart_generator.analyzer
        self.output_dir = chart_generator.output_dir
        self.template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
        self.static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
        
        # 确保模板目录存在
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
            
        # 确保静态资源目录存在
        if not os.path.exists(self.static_dir):
            os.makedirs(self.static_dir)
            
        # 确保CSS目录存在
        css_dir = os.path.join(self.static_dir, 'css')
        if not os.path.exists(css_dir):
            os.makedirs(css_dir)
            
        # 确保JS目录存在
        js_dir = os.path.join(self.static_dir, 'js')
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
            
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # 复制静态资源文件到输出目录
        self._copy_static_files()
        
    def _copy_static_files(self):
        """
        复制静态资源文件到输出目录
        """
        # 创建输出目录中的静态资源目录
        output_static_dir = os.path.join(self.output_dir, 'static')
        if not os.path.exists(output_static_dir):
            os.makedirs(output_static_dir)
            
        # 创建输出目录中的CSS目录
        output_css_dir = os.path.join(output_static_dir, 'css')
        if not os.path.exists(output_css_dir):
            os.makedirs(output_css_dir)
            
        # 创建输出目录中的JS目录
        output_js_dir = os.path.join(output_static_dir, 'js')
        if not os.path.exists(output_js_dir):
            os.makedirs(output_js_dir)
            
        # 复制CSS文件
        css_files = [f for f in os.listdir(os.path.join(self.static_dir, 'css')) if f.endswith('.css')]
        for css_file in css_files:
            src = os.path.join(self.static_dir, 'css', css_file)
            dst = os.path.join(output_css_dir, css_file)
            shutil.copy2(src, dst)
            
        # 复制JS文件
        js_files = [f for f in os.listdir(os.path.join(self.static_dir, 'js')) if f.endswith('.js')]
        for js_file in js_files:
            src = os.path.join(self.static_dir, 'js', js_file)
            dst = os.path.join(output_js_dir, js_file)
            shutil.copy2(src, dst)
            
    def create_template(self):
        """
        创建HTML模板
        
        Returns:
            str: 模板文件路径
        """
        # 创建模板文件路径
        template_path = os.path.join(self.template_dir, 'report_template.html')
        
        # 创建模板内容
        template_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>晶圆厂CP测试数据分析报告 - {{ param }}</title>
    <link rel="stylesheet" href="static/css/style.css">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="static/js/script.js"></script>
</head>
<body>
    <div class="container">
        <h1>晶圆厂CP测试数据分析报告</h1>
        
        <div class="parameter-selector">
            <label for="param-select">选择参数：</label>
            <select id="param-select">
                {% for p in params %}
                <option value="{{ p }}" {% if p == param %}selected{% endif %}>{{ p }}</option>
                {% endfor %}
            </select>
        </div>
        
        <h2>参数：{{ param }}</h2>
        
        <div class="chart-container">
            {{ chart_html|safe }}
        </div>
        
        <div class="stats-container">
            <h3>统计信息</h3>
            <table class="stats-table">
                <tr>
                    <th>批次</th>
                    <th>平均值</th>
                    <th>标准差</th>
                    <th>中位数</th>
                    <th>最小值</th>
                    <th>最大值</th>
                    <th>数据点数</th>
                </tr>
                {% for lot, stat in stats.by_lot.items() %}
                <tr>
                    <td>{{ lot }}</td>
                    <td class="blue-text">{{ "%.4f"|format(stat.mean) }}</td>
                    <td class="brown-text">{{ "%.4f"|format(stat.std) }}</td>
                    <td>{{ "%.4f"|format(stat.median) }}</td>
                    <td>{{ "%.4f"|format(stat.min) }}</td>
                    <td>{{ "%.4f"|format(stat.max) }}</td>
                    <td>{{ stat.count }}</td>
                </tr>
                {% endfor %}
                <tr>
                    <td><strong>总体</strong></td>
                    <td class="blue-text"><strong>{{ "%.4f"|format(stats.overall.mean) }}</strong></td>
                    <td class="brown-text"><strong>{{ "%.4f"|format(stats.overall.std) }}</strong></td>
                    <td><strong>{{ "%.4f"|format(stats.overall.median) }}</strong></td>
                    <td><strong>{{ "%.4f"|format(stats.overall.min) }}</strong></td>
                    <td><strong>{{ "%.4f"|format(stats.overall.max) }}</strong></td>
                    <td><strong>{{ stats.overall.count }}</strong></td>
                </tr>
            </table>
        </div>
        
        <div class="footer">
            <p>生成时间：{{ timestamp }}</p>
            <p>晶圆厂CP测试数据分析工具</p>
        </div>
    </div>
</body>
</html>
"""
        
        # 写入模板文件
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
            
        return template_path
    
    def generate_report(self, param):
        """
        生成HTML报告
        
        Args:
            param (str): 参数名称
            
        Returns:
            str: HTML报告文件路径
        """
        # 创建模板
        template_path = self.create_template()
        
        # 生成图表
        fig = self.chart_generator.generate_boxplot_with_scatter(param)
        if fig is None:
            print(f"错误: 无法生成参数 {param} 的图表")
            return None
            
        # 获取图表HTML
        chart_html = pio.to_html(fig, include_plotlyjs=False, full_html=False)
        
        # 获取统计信息
        stats = self.analyzer.calculate_statistics(param)
        if stats is None:
            print(f"错误: 无法获取参数 {param} 的统计信息")
            return None
            
        # 获取所有参数
        params = [p for p in self.analyzer.target_params if p in self.analyzer.df.columns]
        
        # 创建模板环境
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_dir))
        template = env.get_template('report_template.html')
        
        # 渲染模板
        html_content = template.render(
            param=param,
            params=params,
            chart_html=chart_html,
            stats=stats,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # 创建HTML报告文件路径
        report_path = os.path.join(self.output_dir, f"{param}_report.html")
        
        # 写入HTML报告文件
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"HTML报告已生成: {report_path}")
        
        return report_path
    
    def generate_index(self, report_files):
        """
        生成索引页面
        
        Args:
            report_files (list): HTML报告文件路径列表
            
        Returns:
            str: 索引页面文件路径
        """
        # 创建索引页面文件路径
        index_path = os.path.join(self.output_dir, "index.html")
        
        # 创建索引页面内容
        index_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>晶圆厂CP测试数据分析报告</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <div class="container">
        <h1>晶圆厂CP测试数据分析报告</h1>
        
        <h2>参数列表</h2>
        
        <ul class="param-list">
            {% for file in report_files %}
            <li><a href="{{ file }}">{{ file|replace('_report.html', '') }}</a></li>
            {% endfor %}
        </ul>
        
        <div class="footer">
            <p>生成时间：{{ timestamp }}</p>
            <p>晶圆厂CP测试数据分析工具</p>
        </div>
    </div>
</body>
</html>
"""
        
        # 创建模板环境
        env = jinja2.Environment(loader=jinja2.BaseLoader())
        template = env.from_string(index_content)
        
        # 获取报告文件名
        report_file_names = [os.path.basename(f) for f in report_files]
        
        # 渲染模板
        html_content = template.render(
            report_files=report_file_names,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # 写入索引页面文件
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"索引页面已生成: {index_path}")
        
        return index_path
    
    def generate_all_reports(self):
        """
        生成所有参数的HTML报告
        
        Returns:
            str: 索引页面文件路径
        """
        # 创建报告文件路径列表
        report_files = []
        
        # 遍历目标参数
        for param in self.analyzer.target_params:
            if param in self.analyzer.df.columns:
                print(f"正在生成参数 {param} 的HTML报告...")
                
                # 生成HTML报告
                report_path = self.generate_report(param)
                
                if report_path is not None:
                    report_files.append(report_path)
                    
        # 生成索引页面
        index_path = self.generate_index(report_files)
        
        return index_path
import os
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
            chart_generator (CPChartGenerator): 图表生成器实例
        """
        self.chart_generator = chart_generator
        self.analyzer = chart_generator.analyzer
        self.output_dir = chart_generator.output_dir
        
        # 模板目录
        self.template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
        
        # 确保模板目录存在
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
            
        # 创建Jinja2环境
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def create_template(self):
        """
        创建HTML模板文件
        
        Returns:
            str: 模板文件路径
        """
        template_path = os.path.join(self.template_dir, 'report_template.html')
        
        # 如果模板文件不存在，则创建
        if not os.path.exists(template_path):
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>晶圆厂CP测试数据分析报告</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1, h2 {
            color: #333;
            text-align: center;
        }
        .parameter-selector {
            margin: 20px 0;
            text-align: center;
        }
        select {
            padding: 8px 15px;
            font-size: 16px;
            border-radius: 4px;
            border: 1px solid #ccc;
        }
        .chart-container {
            margin: 20px 0;
            height: 800px;
        }
        .stats-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .stats-table th, .stats-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        .stats-table th {
            background-color: #f2f2f2;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
        .blue-text {
            color: blue;
        }
        .brown-text {
            color: brown;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>晶圆厂CP测试数据分析报告</h1>
        
        <div class="parameter-selector">
            <label for="param-select">选择参数：</label>
            <select id="param-select" onchange="changeParameter()">
                {% for param in parameters %}
                <option value="{{ param }}" {% if param == current_param %}selected{% endif %}>{{ param }}</option>
                {% endfor %}
            </select>
        </div>
        
        <div class="chart-container">
            {{ chart_div|safe }}
        </div>
        
        <h2>统计信息</h2>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>参数</th>
                    <th>平均值</th>
                    <th>标准差</th>
                    <th>中位数</th>
                    <th>最小值</th>
                    <th>最大值</th>
                    <th>数据点数</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{{ current_param }}</td>
                    <td class="blue-text">{{ stats.overall.mean|round(4) }}</td>
                    <td class="brown-text">{{ stats.overall.std|round(4) }}</td>
                    <td>{{ stats.overall.median|round(4) }}</td>
                    <td>{{ stats.overall.min|round(4) }}</td>
                    <td>{{ stats.overall.max|round(4) }}</td>
                    <td>{{ stats.overall.count }}</td>
                </tr>
            </tbody>
        </table>
        
        <h2>批次统计</h2>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>批次</th>
                    <th>平均值</th>
                    <th>标准差</th>
                    <th>中位数</th>
                    <th>数据点数</th>
                </tr>
            </thead>
            <tbody>
                {% for lot_stat in stats.by_lot %}
                <tr>
                    <td>{{ lot_stat.Lot }}</td>
                    <td class="blue-text">{{ lot_stat.Average|round(4) }}</td>
                    <td class="brown-text">{{ lot_stat.StdDev|round(4) }}</td>
                    <td>{{ lot_stat.Median|round(4) }}</td>
                    <td>{{ lot_stat.Count }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="footer">
            <p>生成时间: {{ generation_time }}</p>
            <p>数据来源: {{ data_source }}</p>
        </div>
    </div>
    
    <script>
        function changeParameter() {
            const param = document.getElementById('param-select').value;
            window.location.href = `${param}_report.html`;
        }
    </script>
</body>
</html>''')
        
        return template_path
    
    def generate_report(self, param):
        """
        生成指定参数的HTML报告
        
        Args:
            param (str): 参数名称
            
        Returns:
            str: HTML报告文件路径
        """
        # 创建模板
        template_path = self.create_template()
        template = self.jinja_env.get_template('report_template.html')
        
        # 生成图表
        fig = self.chart_generator.generate_boxplot_with_scatter(param)
        
        if fig is None:
            print(f"参数 {param} 没有有效数据，无法生成报告")
            return None
            
        # 获取图表的HTML代码
        chart_div = pio.to_html(
            fig,
            include_plotlyjs='cdn',
            full_html=False,
            config={
                'displayModeBar': True,
                'scrollZoom': True,
                'responsive': True
            }
        )
        
        # 获取统计信息
        stats = self.analyzer.calculate_statistics(param)
        
        # 渲染模板
        html_content = template.render(
            parameters=self.analyzer.target_params,
            current_param=param,
            chart_div=chart_div,
            stats=stats,
            generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data_source='晶圆厂CP测试数据'
        )
        
        # 保存HTML报告
        report_path = os.path.join(self.output_dir, f"{param}_report.html")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return report_path
    
    def generate_index(self, report_files):
        """
        生成索引页面
        
        Args:
            report_files (list): 报告文件路径列表
            
        Returns:
            str: 索引页面文件路径
        """
        # 提取参数名称
        params = []
        for file_path in report_files:
            param = os.path.basename(file_path).replace('_report.html', '')
            params.append({
                'name': param,
                'path': os.path.basename(file_path)
            })
            
        # 创建索引页面
        index_path = os.path.join(self.output_dir, 'index.html')
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>晶圆厂CP测试数据分析报告索引</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .param-list {
            list-style-type: none;
            padding: 0;
        }
        .param-list li {
            margin: 10px 0;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .param-list li a {
            display: block;
            color: #0066cc;
            text-decoration: none;
            font-size: 18px;
        }
        .param-list li a:hover {
            color: #004080;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>晶圆厂CP测试数据分析报告索引</h1>
        
        <ul class="param-list">
''')
            
            # 添加参数链接
            for param in params:
                f.write(f'            <li><a href="{param["path"]}">{param["name"]} 参数分析报告</a></li>\n')
                
            f.write('''        </ul>
        
        <div class="footer">
            <p>生成时间: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
        </div>
    </div>
</body>
</html>''')
            
        return index_path
    
    def generate_all_reports(self):
        """
        生成所有参数的HTML报告
        
        Returns:
            str: 索引页面文件路径
        """
        report_files = []
        
        for param in self.analyzer.target_params:
            print(f"正在生成 {param} 的HTML报告...")
            report_path = self.generate_report(param)
            
            if report_path:
                report_files.append(report_path)
                print(f"已保存 {report_path}")
                
        # 生成索引页面
        if report_files:
            index_path = self.generate_index(report_files)
            print(f"已生成索引页面: {index_path}")
            return index_path
            
        return None
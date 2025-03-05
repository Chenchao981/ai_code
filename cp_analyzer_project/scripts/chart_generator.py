import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os

class CPChartGenerator:
    """
    CP测试数据图表生成类
    """
    def __init__(self, analyzer):
        """
        初始化图表生成器
        
        Args:
            analyzer (CPDataAnalyzer): 数据分析器实例
        """
        self.analyzer = analyzer
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_boxplot_with_scatter(self, param):
        """
        生成箱型图和散点图的组合图
        
        Args:
            param (str): 参数名称
            
        Returns:
            go.Figure: Plotly图表对象
        """
        # 获取箱型图数据
        boxplot_data = self.analyzer.get_boxplot_data(param)
        
        if not boxplot_data:
            print(f"参数 {param} 没有有效数据")
            return None
            
        # 获取散点图数据
        scatter_data = self.analyzer.get_scatter_data(param)
        
        # 获取统计信息
        stats = self.analyzer.calculate_statistics(param)
        
        # 获取参数上下限
        limits = {}
        if param in self.analyzer.limits:
            limits = self.analyzer.limits[param]
        
        # 创建图表
        fig = go.Figure()
        
        # 添加箱型图
        lots = [data['lot'] for data in boxplot_data]
        
        # 添加箱型图 - 蓝色箱体
        fig.add_trace(go.Box(
            x=lots,
            q1=[data['q1'] for data in boxplot_data],
            median=[data['median'] for data in boxplot_data],
            q3=[data['q3'] for data in boxplot_data],
            lowerfence=[data['whisker_low'] for data in boxplot_data],
            upperfence=[data['whisker_high'] for data in boxplot_data],
            boxmean='sd',  # 显示均值和标准差
            boxpoints=False,  # 不显示异常值点
            name='Box Plot',
            marker_color='blue',
            line=dict(color='blue'),
            showlegend=True
        ))
        
        # 添加散点图 - 棕色点
        for lot in lots:
            lot_points = [point for point in scatter_data if point['lot'] == lot]
            
            if lot_points:
                fig.add_trace(go.Scatter(
                    x=[lot] * len(lot_points),
                    y=[point['value'] for point in lot_points],
                    mode='markers',
                    name=f'Lot {lot}',
                    marker=dict(
                        color='brown',
                        size=6,
                        opacity=0.7
                    ),
                    hovertemplate='Lot: %{x}<br>Value: %{y:.4f}<br>Wafer: %{customdata[0]}<br>No.U: %{customdata[1]}',
                    customdata=[[point['wafer'], point['no_u']] for point in lot_points],
                    showlegend=False
                ))
        
        # 添加上下限线 - 红色虚线
        if limits and 'upper' in limits and 'lower' in limits:
            upper = limits['upper']
            lower = limits['lower']
            
            if not np.isnan(upper):
                fig.add_shape(
                    type='line',
                    x0=-0.5,
                    y0=upper,
                    x1=len(lots) - 0.5,
                    y1=upper,
                    line=dict(
                        color='red',
                        width=2,
                        dash='dash'
                    ),
                    name='USL'
                )
                
                fig.add_annotation(
                    x=len(lots) - 0.5,
                    y=upper,
                    text=f'USL: {upper:.2f}',
                    showarrow=False,
                    xanchor='right',
                    yanchor='bottom',
                    font=dict(color='red')
                )
            
            if not np.isnan(lower):
                fig.add_shape(
                    type='line',
                    x0=-0.5,
                    y0=lower,
                    x1=len(lots) - 0.5,
                    y1=lower,
                    line=dict(
                        color='red',
                        width=2,
                        dash='dash'
                    ),
                    name='LSL'
                )
                
                fig.add_annotation(
                    x=len(lots) - 0.5,
                    y=lower,
                    text=f'LSL: {lower:.2f}',
                    showarrow=False,
                    xanchor='right',
                    yanchor='top',
                    font=dict(color='red')
                )
        
        # 设置图表布局
        fig.update_layout(
            title={
                'text': f'Box Plot / VALUE<br><sub>Parameter: {param}</sub>',
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title='LOT',
            yaxis_title='VALUE',
            height=800,
            width=1200,
            margin=dict(l=50, r=50, t=100, b=200),  # 底部留出空间放置表格
            template='plotly_white',
            hovermode='closest',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            )
        )
        
        # 创建表格数据
        table_data = []
        
        # 平均值行 - 蓝色数值
        averages = ['Average']
        for data in boxplot_data:
            averages.append(f'{data["mean"]:.2f}')
        table_data.append(averages)
        
        # 标准差行 - 棕色数值
        stds = ['StdDev']
        for data in boxplot_data:
            stds.append(f'{data["std"]:.2f}')
        table_data.append(stds)
        
        # Wafer LOT行
        wafers = ['WAFER LOT']
        for data in boxplot_data:
            wafers.append(data['lot'])
        table_data.append(wafers)
        
        # 批次号行
        lot_numbers = ['Lot Number']
        for _ in range(len(boxplot_data)):
            lot_numbers.append('')
        table_data.append(lot_numbers)
        
        # 添加表格
        fig.add_trace(go.Table(
            header=dict(
                values=[''] + [f'LOT {i+1:02d}' for i in range(len(boxplot_data))],
                align='center',
                font=dict(size=12),
                height=30
            ),
            cells=dict(
                values=table_data,
                align='center',
                font=dict(
                    size=11,
                    color=[
                        ['black'] * (len(boxplot_data) + 1),
                        ['blue'] * (len(boxplot_data) + 1),
                        ['brown'] * (len(boxplot_data) + 1),
                        ['black'] * (len(boxplot_data) + 1),
                        ['black'] * (len(boxplot_data) + 1)
                    ]
                ),
                height=25
            ),
            domain=dict(x=[0, 1], y=[0, 0.2])
        ))
        
        # 添加图例
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color='blue'),
            name='VALUE',
            showlegend=True
        ))
        
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color='red', symbol='triangle-up'),
            name='Average',
            showlegend=True
        ))
        
        return fig
    
    def save_html(self, fig, param, interactive=True):
        """
        将图表保存为HTML文件
        
        Args:
            fig (go.Figure): Plotly图表对象
            param (str): 参数名称
            interactive (bool): 是否生成交互式HTML
            
        Returns:
            str: HTML文件路径
        """
        if fig is None:
            return None
            
        # 生成文件名
        file_name = f"{param}_boxplot.html"
        file_path = os.path.join(self.output_dir, file_name)
        
        # 保存HTML文件
        if interactive:
            fig.write_html(
                file_path,
                include_plotlyjs=True,
                full_html=True,
                config={
                    'displayModeBar': True,
                    'scrollZoom': True,
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': f'{param}_boxplot',
                        'height': 800,
                        'width': 1200,
                        'scale': 2
                    }
                }
            )
        else:
            fig.write_image(file_path.replace('.html', '.png'))
            
        return file_path
    
    def generate_all_charts(self, interactive=True):
        """
        为所有目标参数生成图表
        
        Args:
            interactive (bool): 是否生成交互式HTML
            
        Returns:
            list: 生成的HTML文件路径列表
        """
        html_files = []
        
        for param in self.analyzer.target_params:
            print(f"正在生成 {param} 的图表...")
            fig = self.generate_boxplot_with_scatter(param)
            
            if fig:
                file_path = self.save_html(fig, param, interactive)
                if file_path:
                    html_files.append(file_path)
                    print(f"已保存 {file_path}")
        
        return html_files
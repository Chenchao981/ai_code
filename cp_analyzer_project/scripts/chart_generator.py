#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
晶圆厂CP测试数据图表生成模块
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

class CPChartGenerator:
    """
    CP测试数据图表生成类
    
    用于生成各种数据可视化图表
    """
    
    def __init__(self, analyzer=None):
        """
        初始化图表生成器
        
        Args:
            analyzer (CPDataAnalyzer): 数据分析器对象
        """
        self.analyzer = analyzer
        self.charts = {}
    
    def generate_boxplot_with_scatter(self, param):
        """
        生成箱型图和散点图的组合图表
        
        Args:
            param (str): 参数名称
            
        Returns:
            Figure: Plotly图表对象
        """
        # 获取参数信息
        param_info = self.analyzer.get_parameter_info(param)
        
        # 获取箱型图数据
        boxplot_data = self.analyzer.get_data_for_boxplot(param)
        if boxplot_data is None or len(boxplot_data['y']) == 0:
            print(f"错误: 无法获取参数 {param} 的箱型图数据或数据为空")
            return None
        
        # 获取散点图数据
        scatter_data = self.analyzer.get_data_for_scatter(param)
        if scatter_data is None or len(scatter_data['y']) == 0:
            print(f"错误: 无法获取参数 {param} 的散点图数据或数据为空")
            return None
        
        # 获取统计信息
        stats = self.analyzer.calculate_statistics(param)
        if stats is None:
            print(f"错误: 无法获取参数 {param} 的统计信息")
            return None
        
        # 获取参数限制
        limits = param_info['limits']
        
        # 获取晶圆片列表并排序
        wafers = sorted(set(boxplot_data['x']))
        
        # 设置Y轴范围
        y_min = min(boxplot_data['y']) * 0.95 if boxplot_data['y'] else 0
        y_max = max(boxplot_data['y']) * 1.05 if boxplot_data['y'] else 1000
        
        # 如果有上下限，则考虑上下限
        if limits.get('upper') is not None:
            y_max = max(y_max, limits['upper'] * 1.1)
        if limits.get('lower') is not None:
            y_min = min(y_min, limits['lower'] * 0.9)
        
        # 创建图表
        fig = go.Figure()
        
        # 添加箱型图
        fig.add_trace(go.Box(
            x=boxplot_data['x'],
            y=boxplot_data['y'],
            name='VALUE',
            boxpoints='all',  # 显示所有点
            jitter=0.3,  # 点的抖动程度
            pointpos=0,  # 点的位置
            marker=dict(
                color='brown',
                size=3
            ),
            line=dict(
                color='blue',
                width=2
            ),
            fillcolor='rgba(0, 0, 255, 0.1)',
            whiskerwidth=0.6,
            boxmean='sd',  # 显示均值和标准差
            showlegend=True
        ))
        
        # 计算每个晶圆片的平均值，用于添加平均值标记
        wafer_means = {}
        for wafer in wafers:
            wafer_means[wafer] = stats['by_lot'][wafer]['mean'] if wafer in stats['by_lot'] else None
        
        # 添加平均值标记
        avg_x = []
        avg_y = []
        
        for wafer in wafers:
            if wafer in wafer_means and wafer_means[wafer] is not None:
                avg_x.append(wafer)
                avg_y.append(wafer_means[wafer])
        
        fig.add_trace(go.Scatter(
            x=avg_x,
            y=avg_y,
            mode='markers',
            name='Average',
            marker=dict(
                symbol='triangle-up',
                color='red',
                size=10,
                line=dict(
                    color='darkred',
                    width=1
                )
            ),
            showlegend=True
        ))
        
        # 设置图表布局
        fig.update_layout(
            title=dict(
                text=f"Box Plot<br><span style='font-size:14px;'>VALUE<br>PARAMETER:{param}</span>",
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top'
            ),
            xaxis=dict(
                title='WAFER',
                tickmode='array',
                tickvals=list(range(len(wafers))),
                ticktext=wafers
            ),
            yaxis=dict(
                title='VALUE',
                zeroline=False,
                range=[y_min, y_max]  # 设置Y轴范围
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.3,
                xanchor='center',
                x=0.5
            ),
            margin=dict(
                l=50,
                r=50,
                t=100,
                b=150
            ),
            height=800,
            width=1200,
            hovermode='closest',
            template='plotly_white'
        )
        
        # 如果有限制，则添加水平线
        if limits.get('upper') is not None:
            fig.add_shape(
                type="line",
                x0=-0.5,
                y0=limits['upper'],
                x1=len(wafers) - 0.5,
                y1=limits['upper'],
                line=dict(
                    color="red",
                    width=2,
                    dash="dash",
                ),
                name="USL"
            )
            # 添加USL标签
            fig.add_annotation(
                x=-0.4,
                y=limits['upper'],
                text=f"USL:{limits['upper']}",
                showarrow=False,
                font=dict(
                    color="red",
                    size=12
                ),
                xanchor="left"
            )
            
        if limits.get('lower') is not None:
            fig.add_shape(
                type="line",
                x0=-0.5,
                y0=limits['lower'],
                x1=len(wafers) - 0.5,
                y1=limits['lower'],
                line=dict(
                    color="red",
                    width=2,
                    dash="dash",
                ),
                name="LSL"
            )
            # 添加LSL标签
            fig.add_annotation(
                x=-0.4,
                y=limits['lower'],
                text=f"LSL:{limits['lower']}",
                showarrow=False,
                font=dict(
                    color="red",
                    size=12
                ),
                xanchor="left"
            )
        
        # 添加统计信息表格
        self._add_stats_table(fig, param, stats)
        
        # 添加数据表格，显示每个Wafer的平均值和标准差
        self._add_wafer_stats_table(fig, param, stats)
        
        # 添加批次信息
        lot_number = self.analyzer.df_clean['Lot'].iloc[0] if not self.analyzer.df_clean.empty else "Unknown"
        fig.add_annotation(
            x=0.5,
            y=-0.25,
            xref="paper",
            yref="paper",
            text=f"{lot_number}",
            showarrow=False,
            font=dict(
                color="black",
                size=14
            ),
            align="center"
        )
        
        # 保存图表
        self.charts[param] = fig
        
        return fig
    
    def _add_stats_table(self, fig, param, stats):
        """
        向图表添加统计信息表格
        
        Args:
            fig (Figure): Plotly图表对象
            param (str): 参数名称
            stats (dict): 统计信息字典
        """
        # 获取整体统计信息
        overall_stats = stats['overall']
        
        # 创建表格数据
        table_data = [
            ["统计指标", "数值"],
            ["样本数", f"{overall_stats['count']}"],
            ["平均值", f"{overall_stats['mean']:.6f}"],
            ["中位数", f"{overall_stats['median']:.6f}"],
            ["标准差", f"{overall_stats['std']:.6f}"],
            ["最小值", f"{overall_stats['min']:.6f}"],
            ["最大值", f"{overall_stats['max']:.6f}"],
            ["范围", f"{overall_stats['range']:.6f}"],
            ["10%分位数", f"{overall_stats['q10']:.6f}"],
            ["25%分位数", f"{overall_stats['q25']:.6f}"],
            ["75%分位数", f"{overall_stats['q75']:.6f}"],
            ["90%分位数", f"{overall_stats['q90']:.6f}"]
        ]
        
        # 如果有限制，则添加到表格
        if overall_stats['upper_limit'] is not None:
            table_data.append(["上限", f"{overall_stats['upper_limit']:.6f}"])
        if overall_stats['lower_limit'] is not None:
            table_data.append(["下限", f"{overall_stats['lower_limit']:.6f}"])
        
        # 添加表格到图表
        fig.add_trace(go.Table(
            domain=dict(x=[0.7, 1.0], y=[0.5, 1.0]),
            header=dict(
                values=["<b>统计指标</b>", "<b>数值</b>"],
                line_color='darkslategray',
                fill_color='lightgrey',
                align='center',
                font=dict(color='black', size=12)
            ),
            cells=dict(
                values=list(zip(*table_data))[1:],
                line_color='darkslategray',
                fill_color='white',
                align='left',
                font=dict(color='black', size=11)
            )
        ))
    
    def _add_wafer_stats_table(self, fig, param, stats):
        """
        向图表添加Wafer统计信息表格
        
        Args:
            fig (Figure): Plotly图表对象
            param (str): 参数名称
            stats (dict): 统计信息字典
        """
        # 获取所有晶圆片并排序
        wafers = sorted(stats['by_lot'].keys())
        
        # 提取每个晶圆片的平均值和标准差
        avg_values = []
        std_values = []
        
        for wafer in wafers:
            wafer_stats = stats['by_lot'][wafer]
            avg_values.append(f"{wafer_stats['mean']:.1f}")
            std_values.append(f"{wafer_stats['std']:.2f}")
        
        # 创建表格数据
        table_headers = ["Average"] + wafers
        table_rows = [
            avg_values,
            ["StdDev"] + std_values,
            ["WAFER"] + wafers,
            ["LOT"] + [""] * len(wafers)
        ]
        
        # 添加表格到图表
        fig.add_trace(go.Table(
            domain=dict(x=[0.0, 1.0], y=[0.0, 0.15]),
            header=dict(
                values=table_headers,
                line_color='darkslategray',
                fill_color='white',
                align='center',
                font=dict(color='black', size=10)
            ),
            cells=dict(
                values=table_rows,
                line_color='darkslategray',
                fill_color=[
                    ['white', 'white', 'white', 'white'],  # 行颜色
                    ['lightblue'] * len(wafers),  # 平均值颜色
                    ['brown'] * len(wafers),  # 标准差颜色
                    ['white'] * len(wafers),  # WAFER颜色
                    ['white'] * len(wafers)   # LOT颜色
                ],
                align='center',
                font=dict(
                    color=['black', 'blue', 'brown', 'black', 'black'],
                    size=10
                ),
                height=25
            )
        ))
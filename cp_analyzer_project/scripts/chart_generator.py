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
    
    # 创建图表
    fig = go.Figure()
    
    # 添加箱型图
    fig.add_trace(go.Box(
        x=boxplot_data['x'],
        y=boxplot_data['y'],
        name='VALUE',
        boxpoints=False,  # 不显示箱型图中的点
        marker_color='blue',
        line_color='blue',
        whiskerwidth=0.5,
        boxmean=False,  # 不显示均值
        hoverinfo='none'  # 禁用悬停信息
    ))
    
    # 添加散点图
    fig.add_trace(go.Scatter(
        x=scatter_data['x'],
        y=scatter_data['y'],
        mode='markers',
        name='Wafer',
        marker=dict(
            color='brown',
            size=6,
            opacity=0.7
        ),
        hovertemplate='<b>LOT:</b> %{x}<br><b>Wafer:</b> %{customdata[0]}<br><b>Value:</b> %{y:.4f}<extra></extra>',
        customdata=list(zip(scatter_data['wafer'], scatter_data['device']))
    ))
    
    # 添加上限规格线
    if limits['upper'] is not None:
        fig.add_shape(
            type='line',
            x0=-0.5,
            y0=limits['upper'],
            x1=len(set(boxplot_data['x'])) - 0.5,
            y1=limits['upper'],
            line=dict(
                color='red',
                width=2,
                dash='dash'
            )
        )
        
        # 添加上限规格标签
        fig.add_annotation(
            x=len(set(boxplot_data['x'])) - 0.5,
            y=limits['upper'],
            text=f"USL: {limits['upper']}",
            showarrow=False,
            xanchor='right',
            yanchor='bottom',
            font=dict(
                color='red'
            )
        )
        
    # 添加下限规格线
    if limits['lower'] is not None:
        fig.add_shape(
            type='line',
            x0=-0.5,
            y0=limits['lower'],
            x1=len(set(boxplot_data['x'])) - 0.5,
            y1=limits['lower'],
            line=dict(
                color='red',
                width=2,
                dash='dash'
            )
        )
        
        # 添加下限规格标签
        fig.add_annotation(
            x=len(set(boxplot_data['x'])) - 0.5,
            y=limits['lower'],
            text=f"LSL: {limits['lower']}",
            showarrow=False,
            xanchor='right',
            yanchor='top',
            font=dict(
                color='red'
            )
        )
    
    # 设置Y轴范围，确保能够显示所有数据点
    y_values = boxplot_data['y']
    y_min = min(y_values) * 0.9 if min(y_values) > 0 else min(y_values) * 1.1
    y_max = max(y_values) * 1.1 if max(y_values) > 0 else max(y_values) * 0.9
    
    # 考虑上下限
    if limits['lower'] is not None:
        y_min = min(y_min, limits['lower'] * 0.9)
    if limits['upper'] is not None:
        y_max = max(y_max, limits['upper'] * 1.1)
        
    # 设置图表布局
    fig.update_layout(
        title=dict(
            text=f"Box Plot / VALUE<br><span style='font-size:14px;'>Parameter: {param}</span>",
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top'
        ),
        xaxis=dict(
            title='LOT',
            tickmode='array',
            tickvals=list(range(len(set(boxplot_data['x'])))),
            ticktext=sorted(list(set(boxplot_data['x'])))
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
    
    # 添加统计信息表格
    self._add_stats_table(fig, param, stats)
    
    return fig
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CP Test Chart Generator
-------------------
This module generates charts for CP test data.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


class CPChartGenerator:
    """Generator for CP test charts."""
    
    def __init__(self, analyzer=None):
        """
        Initialize the chart generator with a data analyzer.
        
        Args:
            analyzer (CPDataAnalyzer, optional): Data analyzer.
        """
        self.analyzer = analyzer
        self.colors = {
            'box': 'blue',
            'scatter': 'red',
            'limit_line': 'green',
            'mean_line': 'orange'
        }
        
    def set_analyzer(self, analyzer):
        """
        Set the data analyzer.
        
        Args:
            analyzer (CPDataAnalyzer): Data analyzer.
        """
        self.analyzer = analyzer
        
    def generate_box_plot(self, parameter, limits=None, group_by='lot_number'):
        """
        Generate a box plot for a parameter.
        
        Args:
            parameter (str): Parameter name.
            limits (dict, optional): Dictionary containing upper and lower limits.
            group_by (str, optional): Column to group by. Defaults to 'lot_number'.
            
        Returns:
            plotly.graph_objects.Figure: Box plot figure.
        """
        if self.analyzer is None or self.analyzer.data is None:
            return go.Figure()
            
        data = self.analyzer.data
        
        if parameter not in data.columns:
            return go.Figure()
            
        if group_by not in data.columns:
            group_by = None
            
        # Create figure
        fig = go.Figure()
        
        if group_by:
            # Add box plot for each group
            for group in data[group_by].unique():
                group_data = data[data[group_by] == group]
                
                fig.add_trace(go.Box(
                    y=group_data[parameter],
                    name=str(group),
                    boxmean=True,
                    marker_color=self.colors['box'],
                    line=dict(color=self.colors['box']),
                    boxpoints='outliers'
                ))
        else:
            # Add overall box plot
            fig.add_trace(go.Box(
                y=data[parameter],
                name=parameter,
                boxmean=True,
                marker_color=self.colors['box'],
                line=dict(color=self.colors['box']),
                boxpoints='outliers'
            ))
            
        # Add limit lines if provided
        if limits:
            if limits.get('lower') is not None:
                fig.add_shape(
                    type='line',
                    x0=-0.5,
                    x1=len(data[group_by].unique()) - 0.5 if group_by else 0.5,
                    y0=limits['lower'],
                    y1=limits['lower'],
                    line=dict(
                        color=self.colors['limit_line'],
                        width=2,
                        dash='dash'
                    )
                )
                
            if limits.get('upper') is not None:
                fig.add_shape(
                    type='line',
                    x0=-0.5,
                    x1=len(data[group_by].unique()) - 0.5 if group_by else 0.5,
                    y0=limits['upper'],
                    y1=limits['upper'],
                    line=dict(
                        color=self.colors['limit_line'],
                        width=2,
                        dash='dash'
                    )
                )
                
        # Update layout
        fig.update_layout(
            title=f'Box Plot - {parameter}',
            xaxis_title=group_by if group_by else '',
            yaxis_title=parameter,
            showlegend=False,
            height=600,
            width=800,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    
    def generate_scatter_plot(self, parameter, limits=None, group_by='lot_number'):
        """
        Generate a scatter plot for a parameter.
        
        Args:
            parameter (str): Parameter name.
            limits (dict, optional): Dictionary containing upper and lower limits.
            group_by (str, optional): Column to group by. Defaults to 'lot_number'.
            
        Returns:
            plotly.graph_objects.Figure: Scatter plot figure.
        """
        if self.analyzer is None or self.analyzer.data is None:
            return go.Figure()
            
        data = self.analyzer.data
        
        if parameter not in data.columns:
            return go.Figure()
            
        if group_by not in data.columns:
            group_by = None
            
        # Create figure
        fig = go.Figure()
        
        if group_by:
            # Add scatter plot for each group
            for i, group in enumerate(data[group_by].unique()):
                group_data = data[data[group_by] == group]
                
                fig.add_trace(go.Scatter(
                    x=[i] * len(group_data),
                    y=group_data[parameter],
                    mode='markers',
                    name=str(group),
                    marker=dict(
                        color=self.colors['scatter'],
                        size=8,
                        opacity=0.7
                    ),
                    hovertemplate=f'{parameter}: %{{y}}<br>{group_by}: {group}<extra></extra>'
                ))
                
            # Set x-axis labels
            fig.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(len(data[group_by].unique()))),
                    ticktext=data[group_by].unique()
                )
            )
        else:
            # Add overall scatter plot
            fig.add_trace(go.Scatter(
                x=list(range(len(data))),
                y=data[parameter],
                mode='markers',
                name=parameter,
                marker=dict(
                    color=self.colors['scatter'],
                    size=8,
                    opacity=0.7
                ),
                hovertemplate=f'{parameter}: %{{y}}<extra></extra>'
            ))
            
        # Add limit lines if provided
        if limits:
            if limits.get('lower') is not None:
                fig.add_shape(
                    type='line',
                    x0=-0.5,
                    x1=len(data[group_by].unique()) - 0.5 if group_by else len(data) - 0.5,
                    y0=limits['lower'],
                    y1=limits['lower'],
                    line=dict(
                        color=self.colors['limit_line'],
                        width=2,
                        dash='dash'
                    )
                )
                
            if limits.get('upper') is not None:
                fig.add_shape(
                    type='line',
                    x0=-0.5,
                    x1=len(data[group_by].unique()) - 0.5 if group_by else len(data) - 0.5,
                    y0=limits['upper'],
                    y1=limits['upper'],
                    line=dict(
                        color=self.colors['limit_line'],
                        width=2,
                        dash='dash'
                    )
                )
                
        # Update layout
        fig.update_layout(
            title=f'Scatter Plot - {parameter}',
            xaxis_title=group_by if group_by else 'Index',
            yaxis_title=parameter,
            showlegend=False,
            height=600,
            width=800,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    
    def generate_combined_chart(self, parameter, limits=None, group_by='lot_number'):
        """
        Generate a combined chart with box plot and scatter plot.
        
        Args:
            parameter (str): Parameter name.
            limits (dict, optional): Dictionary containing upper and lower limits.
            group_by (str, optional): Column to group by. Defaults to 'lot_number'.
            
        Returns:
            plotly.graph_objects.Figure: Combined chart figure.
        """
        if self.analyzer is None or self.analyzer.data is None:
            return go.Figure()
            
        data = self.analyzer.data
        
        if parameter not in data.columns:
            return go.Figure()
            
        if group_by not in data.columns:
            group_by = None
            
        # Create figure with subplots
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=(f'Box Plot - {parameter}', f'Scatter Plot - {parameter}'),
            shared_xaxes=True,
            vertical_spacing=0.1
        )
        
        if group_by:
            # Add box plot for each group
            for i, group in enumerate(data[group_by].unique()):
                group_data = data[data[group_by] == group]
                
                fig.add_trace(
                    go.Box(
                        y=group_data[parameter],
                        name=str(group),
                        boxmean=True,
                        marker_color=self.colors['box'],
                        line=dict(color=self.colors['box']),
                        boxpoints='outliers'
                    ),
                    row=1,
                    col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=[i] * len(group_data),
                        y=group_data[parameter],
                        mode='markers',
                        name=str(group),
                        marker=dict(
                            color=self.colors['scatter'],
                            size=8,
                            opacity=0.7
                        ),
                        hovertemplate=f'{parameter}: %{{y}}<br>{group_by}: {group}<extra></extra>'
                    ),
                    row=2,
                    col=1
                )
                
            # Set x-axis labels
            fig.update_xaxes(
                tickmode='array',
                tickvals=list(range(len(data[group_by].unique()))),
                ticktext=data[group_by].unique(),
                row=2,
                col=1
            )
        else:
            # Add overall box plot
            fig.add_trace(
                go.Box(
                    y=data[parameter],
                    name=parameter,
                    boxmean=True,
                    marker_color=self.colors['box'],
                    line=dict(color=self.colors['box']),
                    boxpoints='outliers'
                ),
                row=1,
                col=1
            )
            
            # Add overall scatter plot
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(data))),
                    y=data[parameter],
                    mode='markers',
                    name=parameter,
                    marker=dict(
                        color=self.colors['scatter'],
                        size=8,
                        opacity=0.7
                    ),
                    hovertemplate=f'{parameter}: %{{y}}<extra></extra>'
                ),
                row=2,
                col=1
            )
            
        # Add limit lines if provided
        if limits:
            if limits.get('lower') is not None:
                fig.add_shape(
                    type='line',
                    x0=-0.5,
                    x1=len(data[group_by].unique()) - 0.5 if group_by else 0.5,
                    y0=limits['lower'],
                    y1=limits['lower'],
                    line=dict(
                        color=self.colors['limit_line'],
                        width=2,
                        dash='dash'
                    ),
                    row=1,
                    col=1
                )
                
                fig.add_shape(
                    type='line',
                    x0=-0.5,
                    x1=len(data[group_by].unique()) - 0.5 if group_by else len(data) - 0.5,
                    y0=limits['lower'],
                    y1=limits['lower'],
                    line=dict(
                        color=self.colors['limit_line'],
                        width=2,
                        dash='dash'
                    ),
                    row=2,
                    col=1
                )
                
            if limits.get('upper') is not None:
                fig.add_shape(
                    type='line',
                    x0=-0.5,
                    x1=len(data[group_by].unique()) - 0.5 if group_by else 0.5,
                    y0=limits['upper'],
                    y1=limits['upper'],
                    line=dict(
                        color=self.colors['limit_line'],
                        width=2,
                        dash='dash'
                    ),
                    row=1,
                    col=1
                )
                
                fig.add_shape(
                    type='line',
                    x0=-0.5,
                    x1=len(data[group_by].unique()) - 0.5 if group_by else len(data) - 0.5,
                    y0=limits['upper'],
                    y1=limits['upper'],
                    line=dict(
                        color=self.colors['limit_line'],
                        width=2,
                        dash='dash'
                    ),
                    row=2,
                    col=1
                )
                
        # Add statistics table
        stats = self.analyzer.get_parameter_stats(parameter, group_by)
        
        if not stats.empty:
            # Create table trace
            table_data = [stats.columns.tolist()]
            table_data.extend(stats.values.tolist())
            
            table = go.Table(
                header=dict(
                    values=stats.columns.tolist(),
                    fill_color='paleturquoise',
                    align='center'
                ),
                cells=dict(
                    values=[stats[col] for col in stats.columns],
                    fill_color='lavender',
                    align='center'
                )
            )
            
            # Add table as annotation
            table_html = f"""
            <table style="width:100%; border-collapse: collapse; margin-top: 20px;">
                <tr style="background-color: #f2f2f2;">
                    <th style="padding: 8px; text-align: center; border: 1px solid #ddd;">{group_by if group_by else ''}</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid #ddd;">Count</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid #ddd;">Mean</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid #ddd;">Std</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid #ddd;">Min</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid #ddd;">Max</th>
                </tr>
            """
            
            for _, row in stats.iterrows():
                table_html += f"""
                <tr>
                    <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{row[group_by] if group_by else 'All'}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{int(row['count'])}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{row['mean']:.4f}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{row['std']:.4f}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{row['min']:.4f}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{row['max']:.4f}</td>
                </tr>
                """
            
            table_html += "</table>"
            
        # Update layout
        fig.update_layout(
            title=f'Parameter Analysis - {parameter}',
            xaxis_title=group_by if group_by else '',
            yaxis_title=parameter,
            showlegend=False,
            height=900,
            width=800,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig


if __name__ == "__main__":
    # Example usage
    from log_parser import CPLogParser
    from data_analyzer import CPDataAnalyzer
    
    parser = CPLogParser("./data/data2/rawdata")
    df = parser.parse_all_logs()
    
    analyzer = CPDataAnalyzer(df)
    
    generator = CPChartGenerator(analyzer)
    
    # Generate combined chart for BVDSS1 parameter
    limits = parser.get_limits("BVDSS1")
    fig = generator.generate_combined_chart("BVDSS1", limits, group_by="lot_number")
    
    # Show figure
    fig.show()

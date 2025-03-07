#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CP Test HTML Report Generator
------------------------
This module generates HTML reports for CP test data.
"""

import os
import datetime
import pandas as pd
import numpy as np
from jinja2 import Environment, FileSystemLoader
import plotly.io as pio


class CPHTMLReporter:
    """Generator for CP test HTML reports."""
    
    def __init__(self, chart_generator=None, template_dir=None):
        """
        Initialize the HTML report generator.
        
        Args:
            chart_generator (CPChartGenerator, optional): Chart generator.
            template_dir (str, optional): Directory containing templates.
        """
        self.chart_generator = chart_generator
        self.template_dir = template_dir if template_dir else os.path.join(os.path.dirname(__file__), '../templates')
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
    def set_chart_generator(self, chart_generator):
        """
        Set the chart generator.
        
        Args:
            chart_generator (CPChartGenerator): Chart generator.
        """
        self.chart_generator = chart_generator
        
    def set_template_dir(self, template_dir):
        """
        Set the template directory.
        
        Args:
            template_dir (str): Directory containing templates.
        """
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
    def generate_parameter_report(self, parameter, limits=None, group_by='lot_number', output_file=None):
        """
        Generate an HTML report for a parameter.
        
        Args:
            parameter (str): Parameter name.
            limits (dict, optional): Dictionary containing upper and lower limits.
            group_by (str, optional): Column to group by. Defaults to 'lot_number'.
            output_file (str, optional): Output file path.
            
        Returns:
            str: HTML report content.
        """
        if not self.chart_generator or not self.chart_generator.analyzer:
            return ""
            
        analyzer = self.chart_generator.analyzer
        data = analyzer.data
        
        if parameter not in data.columns:
            return ""
            
        # Get template
        template = self.env.get_template('report_template.html')
        
        # Generate chart
        chart = self.chart_generator.generate_combined_chart(parameter, limits, group_by)
        
        # Convert chart to HTML div
        plot_div = pio.to_html(chart, full_html=False)
        
        # Generate statistics table
        stats = analyzer.get_parameter_stats(parameter, group_by)
        
        stats_table = stats.to_html(
            index=False,
            float_format='%.4f',
            classes='table table-striped',
            border=0
        )
        
        # Generate yield data
        if limits:
            yield_data = analyzer.calculate_yield(
                parameter,
                lower=limits.get('lower'),
                upper=limits.get('upper'),
                group_by=group_by
            )
            
            yield_table = yield_data.to_html(
                index=False,
                float_format='%.2f',
                classes='table table-striped',
                border=0
            )
        else:
            yield_table = ""
        
        # Render template
        html = template.render(
            parameter=parameter,
            plot_div=plot_div,
            stats_table=stats_table,
            yield_table=yield_table,
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Save to file if output_file is provided
        if output_file:
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
        return html
    
    def generate_multi_parameter_report(self, parameters, limits=None, group_by='lot_number', output_file=None):
        """
        Generate an HTML report for multiple parameters.
        
        Args:
            parameters (list): List of parameter names.
            limits (dict, optional): Dictionary containing upper and lower limits.
            group_by (str, optional): Column to group by. Defaults to 'lot_number'.
            output_file (str, optional): Output file path.
            
        Returns:
            str: HTML report content.
        """
        if not self.chart_generator or not self.chart_generator.analyzer:
            return ""
            
        analyzer = self.chart_generator.analyzer
        data = analyzer.data
        
        # Check if parameters exist in data
        parameters = [p for p in parameters if p in data.columns]
        
        if not parameters:
            return ""
            
        # Get template
        template = self.env.get_template('multi_parameter_template.html')
        
        # Generate charts and statistics
        charts = {}
        stats_tables = {}
        yield_tables = {}
        
        for param in parameters:
            # Generate chart
            chart = self.chart_generator.generate_combined_chart(param, limits.get(param) if limits else None, group_by)
            
            # Convert chart to HTML div
            charts[param] = pio.to_html(chart, full_html=False)
            
            # Generate statistics table
            stats = analyzer.get_parameter_stats(param, group_by)
            
            stats_tables[param] = stats.to_html(
                index=False,
                float_format='%.4f',
                classes='table table-striped',
                border=0
            )
            
            # Generate yield data
            if limits and param in limits:
                yield_data = analyzer.calculate_yield(
                    param,
                    lower=limits[param].get('lower'),
                    upper=limits[param].get('upper'),
                    group_by=group_by
                )
                
                yield_tables[param] = yield_data.to_html(
                    index=False,
                    float_format='%.2f',
                    classes='table table-striped',
                    border=0
                )
            else:
                yield_tables[param] = ""
        
        # Render template
        html = template.render(
            parameters=parameters,
            charts=charts,
            stats_tables=stats_tables,
            yield_tables=yield_tables,
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Save to file if output_file is provided
        if output_file:
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
        return html


if __name__ == "__main__":
    # Example usage
    from log_parser import CPLogParser
    from data_analyzer import CPDataAnalyzer
    from chart_generator import CPChartGenerator
    
    parser = CPLogParser("./data/data2/rawdata")
    df = parser.parse_all_logs()
    
    analyzer = CPDataAnalyzer(df)
    
    generator = CPChartGenerator(analyzer)
    
    reporter = CPHTMLReporter(generator)
    
    # Generate report for BVDSS1 parameter
    limits = parser.get_limits("BVDSS1")
    html = reporter.generate_parameter_report("BVDSS1", limits, group_by="lot_number", output_file="./output/bvdss1_report.html")
    
    print(f"Report generated to ./output/bvdss1_report.html")

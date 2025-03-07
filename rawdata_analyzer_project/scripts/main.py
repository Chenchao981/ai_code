#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CP Test Analyzer - Main Application
--------------------------
Main entry point for the CP Test Analyzer application.
"""

import os
import sys
import argparse
import pandas as pd
from pathlib import Path

from log_parser import CPLogParser
from data_analyzer import CPDataAnalyzer
from chart_generator import CPChartGenerator
from html_report import CPHTMLReporter


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Analyze CP test data and generate reports.')
    
    # Input/output paths
    parser.add_argument('-i', '--input', dest='input_dir', required=True,
                        help='Input directory containing CP test log files')
    parser.add_argument('-o', '--output', dest='output_dir', default='./output',
                        help='Output directory for generated reports')
    
    # Parameter selection
    parser.add_argument('-p', '--param', dest='parameter', default='BVDSS1',
                        help='Parameter to analyze (default: BVDSS1)')
    parser.add_argument('--params', dest='parameters', nargs='+',
                        help='Multiple parameters to analyze')
    
    # Grouping option
    parser.add_argument('-g', '--group', dest='group_by', default='lot_number',
                        help='Column to group by (default: lot_number)')
    
    # Limits
    parser.add_argument('--lower', dest='lower_limit', type=float,
                        help='Lower limit for parameter')
    parser.add_argument('--upper', dest='upper_limit', type=float,
                        help='Upper limit for parameter')
    
    # Output format
    parser.add_argument('-f', '--format', dest='output_format', default='html',
                        choices=['html', 'csv', 'excel'],
                        help='Output format (default: html)')
    
    # Other options
    parser.add_argument('--no-charts', dest='no_charts', action='store_true',
                        help='Do not generate charts')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug output')
    
    return parser.parse_args()


def main():
    """
    Main entry point for the application.
    """
    args = parse_arguments()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize parser
    parser = CPLogParser(args.input_dir)
    
    # Set limits if provided
    if args.lower_limit is not None or args.upper_limit is not None:
        parser.set_limits(args.parameter, args.lower_limit, args.upper_limit)
    
    # Parse log files
    print(f"Parsing log files from {args.input_dir}...")
    df = parser.parse_all_logs()
    
    if df.empty:
        print(f"No data found in {args.input_dir}")
        return 1
    
    print(f"Found data for {len(df)} test runs.")
    
    # Initialize analyzer and chart generator
    analyzer = CPDataAnalyzer(df)
    chart_gen = CPChartGenerator(analyzer)
    
    # Process single parameter
    if not args.parameters:
        parameter = args.parameter
        limits = parser.get_limits(parameter)
        
        print(f"Analyzing parameter: {parameter}")
        
        # Generate statistics
        stats = analyzer.get_parameter_stats(parameter, args.group_by)
        
        # Calculate yield
        yield_data = analyzer.calculate_yield(parameter, limits['lower'], limits['upper'], args.group_by)
        
        # Output results based on format
        if args.output_format == 'csv':
            # Save statistics to CSV
            stats_file = os.path.join(args.output_dir, f"{parameter}_stats.csv")
            stats.to_csv(stats_file, index=False)
            
            # Save yield data to CSV
            yield_file = os.path.join(args.output_dir, f"{parameter}_yield.csv")
            yield_data.to_csv(yield_file, index=False)
            
            print(f"Results saved to {stats_file} and {yield_file}")
            
        elif args.output_format == 'excel':
            # Save to Excel
            excel_file = os.path.join(args.output_dir, f"{parameter}_analysis.xlsx")
            
            with pd.ExcelWriter(excel_file) as writer:
                stats.to_excel(writer, sheet_name='Statistics', index=False)
                yield_data.to_excel(writer, sheet_name='Yield', index=False)
                df.to_excel(writer, sheet_name='Raw Data', index=False)
            
            print(f"Results saved to {excel_file}")
            
        elif args.output_format == 'html':
            # Generate HTML report
            reporter = CPHTMLReporter(chart_gen)
            
            report_file = os.path.join(args.output_dir, f"{parameter}_report.html")
            html = reporter.generate_parameter_report(parameter, limits, args.group_by, report_file)
            
            print(f"Report generated at {report_file}")
            
    # Process multiple parameters
    else:
        parameters = args.parameters
        
        # Get limits for each parameter
        limits = {}
        for param in parameters:
            limits[param] = parser.get_limits(param)
        
        print(f"Analyzing parameters: {', '.join(parameters)}")
        
        # Output results based on format
        if args.output_format == 'csv':
            for param in parameters:
                # Generate statistics
                stats = analyzer.get_parameter_stats(param, args.group_by)
                
                # Calculate yield
                yield_data = analyzer.calculate_yield(
                    param,
                    limits[param]['lower'],
                    limits[param]['upper'],
                    args.group_by
                )
                
                # Save statistics to CSV
                stats_file = os.path.join(args.output_dir, f"{param}_stats.csv")
                stats.to_csv(stats_file, index=False)
                
                # Save yield data to CSV
                yield_file = os.path.join(args.output_dir, f"{param}_yield.csv")
                yield_data.to_csv(yield_file, index=False)
            
            print(f"Results saved to {args.output_dir}")
            
        elif args.output_format == 'excel':
            # Save to Excel
            excel_file = os.path.join(args.output_dir, "cp_test_analysis.xlsx")
            
            with pd.ExcelWriter(excel_file) as writer:
                # Add raw data sheet
                df.to_excel(writer, sheet_name='Raw Data', index=False)
                
                # Add sheets for each parameter
                for param in parameters:
                    # Generate statistics
                    stats = analyzer.get_parameter_stats(param, args.group_by)
                    
                    # Calculate yield
                    yield_data = analyzer.calculate_yield(
                        param,
                        limits[param]['lower'],
                        limits[param]['upper'],
                        args.group_by
                    )
                    
                    # Save to sheets
                    stats.to_excel(writer, sheet_name=f'{param} Stats', index=False)
                    yield_data.to_excel(writer, sheet_name=f'{param} Yield', index=False)
            
            print(f"Results saved to {excel_file}")
            
        elif args.output_format == 'html':
            # Generate HTML report
            reporter = CPHTMLReporter(chart_gen)
            
            report_file = os.path.join(args.output_dir, "multi_parameter_report.html")
            html = reporter.generate_multi_parameter_report(parameters, limits, args.group_by, report_file)
            
            print(f"Report generated at {report_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

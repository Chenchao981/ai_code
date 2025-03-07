# CP Test Data Analyzer

This project analyzes CP (Circuit Probe) test data from semiconductor wafer testing and generates interactive HTML reports with box plots and scatter plots.

## Features

- Parse CP test log files
- Extract and analyze test parameters (BVDSS1, BVDSS2, DELTABV, IDSS1, VTH, RDSON1, VFSDS, IGSS2, IGSSR2, IDSS2)
- Generate interactive box plots and scatter plots
- Create HTML reports with parameter statistics
- Support for multiple parameters and batch analysis

## Project Structure

```
rawdata_analyzer_project/
├── data/                    # Store CP test log files
├── scripts/                 # Python scripts
│   ├── log_parser.py        # Parse CP test log files
│   ├── data_analyzer.py     # Analyze data and calculate statistics
│   ├── chart_generator.py   # Generate charts using Plotly
│   ├── html_report.py       # Generate HTML reports
│   ├── main.py              # Main entry point
├── templates/               # HTML templates
├── static/                  # Static resources (CSS, JS)
│   ├── css/
│   ├── js/
├── output/                  # Generated HTML reports
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/rawdata_analyzer_project.git
cd rawdata_analyzer_project
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

To analyze a specific parameter (default is BVDSS1):

```bash
python scripts/main.py
```

### Command Line Options

- `--data-dir`: Directory containing CP test log files (default: ./data/data2/rawdata)
- `--output-dir`: Directory for output HTML reports (default: ./output)
- `--parameter`: Parameter to analyze (default: BVDSS1)
- `--all-parameters`: Analyze all parameters
- `--group-by`: Column to group by (default: lot_number)

### Examples

Analyze BVDSS1 parameter:

```bash
python scripts/main.py --parameter BVDSS1
```

Analyze all parameters:

```bash
python scripts/main.py --all-parameters
```

Specify custom data and output directories:

```bash
python scripts/main.py --data-dir /path/to/data --output-dir /path/to/output
```

## Output

The generated HTML reports include:

- Box plots showing the distribution of parameter values
- Scatter plots showing individual wafer values
- Statistical tables with average and standard deviation values
- Interactive elements for exploring the data

## Requirements

- Python 3.6+
- pandas
- numpy
- plotly
- pathlib

## License

This project is licensed under the MIT License - see the LICENSE file for details.

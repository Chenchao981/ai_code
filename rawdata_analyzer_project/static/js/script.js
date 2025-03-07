/**
 * CP Test Analyzer JavaScript
 * Provides interactive functionality for the HTML reports
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Parameter selector functionality
    const parameterSelect = document.getElementById('parameter-select');
    if (parameterSelect) {
        parameterSelect.addEventListener('change', function() {
            // Hide all parameter plots
            const plots = document.getElementsByClassName('parameter-plot');
            for (let i = 0; i < plots.length; i++) {
                plots[i].classList.remove('active');
            }
            
            // Show selected parameter plot
            const selectedParameter = this.value;
            const selectedPlot = document.getElementById(selectedParameter + '-plot');
            if (selectedPlot) {
                selectedPlot.classList.add('active');
            }
        });
    }
    
    // Add hover effects to data points
    const dataPoints = document.querySelectorAll('.scatter .points path');
    if (dataPoints) {
        dataPoints.forEach(point => {
            point.addEventListener('mouseenter', function() {
                this.style.opacity = '1';
                this.style.stroke = '#000';
                this.style.strokeWidth = '2px';
            });
            
            point.addEventListener('mouseleave', function() {
                this.style.opacity = '0.7';
                this.style.stroke = 'none';
                this.style.strokeWidth = '0';
            });
        });
    }
    
    // Add export functionality if available
    const exportButton = document.getElementById('export-button');
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            const plotContainer = document.querySelector('.js-plotly-plot');
            if (plotContainer && window.Plotly) {
                Plotly.downloadImage(plotContainer, {
                    format: 'png',
                    width: 1200,
                    height: 800,
                    filename: 'cp_test_chart'
                });
            }
        });
    }
    
    // Add toggle functionality for statistics table
    const toggleStatsButton = document.getElementById('toggle-stats');
    const statsTable = document.getElementById('stats-table');
    if (toggleStatsButton && statsTable) {
        toggleStatsButton.addEventListener('click', function() {
            if (statsTable.style.display === 'none') {
                statsTable.style.display = 'table';
                this.textContent = 'Hide Statistics';
            } else {
                statsTable.style.display = 'none';
                this.textContent = 'Show Statistics';
            }
        });
    }
});

/**
 * Updates the chart title with the selected parameter
 * @param {string} parameter - The selected parameter name
 */
function updateChartTitle(parameter) {
    const chartTitle = document.getElementById('chart-title');
    if (chartTitle) {
        chartTitle.textContent = `Box Plot / VALUE - ${parameter}`;
    }
}

/**
 * Formats a number with the specified precision
 * @param {number} value - The number to format
 * @param {number} precision - The number of decimal places
 * @returns {string} The formatted number
 */
function formatNumber(value, precision = 2) {
    if (isNaN(value)) {
        return 'N/A';
    }
    return value.toFixed(precision);
}

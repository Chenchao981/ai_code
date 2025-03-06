/**
 * 晶圆厂CP测试数据分析工具JavaScript脚本
 */

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 获取参数选择器
    const paramSelect = document.getElementById('param-select');
    
    // 如果存在参数选择器，添加事件监听器
    if (paramSelect) {
        paramSelect.addEventListener('change', function() {
            // 获取选中的参数
            const selectedParam = this.value;
            
            // 跳转到对应的报告页面
            window.location.href = `${selectedParam}_report.html`;
        });
    }
    
    // 添加表格行悬停效果
    const tableRows = document.querySelectorAll('.stats-table tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseover', function() {
            this.style.backgroundColor = '#e9f7fe';
        });
        
        row.addEventListener('mouseout', function() {
            // 恢复原来的背景色
            if (this.rowIndex % 2 === 0) {
                this.style.backgroundColor = '#f2f2f2';
            } else {
                this.style.backgroundColor = '';
            }
        });
    });
});

/**
 * 格式化数值，添加单位
 * @param {number} value - 数值
 * @param {string} unit - 单位
 * @returns {string} 格式化后的字符串
 */
function formatValue(value, unit) {
    if (value === null || value === undefined) {
        return 'N/A';
    }
    
    // 处理不同量级
    if (Math.abs(value) < 1e-9) {
        return (value * 1e12).toFixed(2) + ' p' + unit;
    } else if (Math.abs(value) < 1e-6) {
        return (value * 1e9).toFixed(2) + ' n' + unit;
    } else if (Math.abs(value) < 1e-3) {
        return (value * 1e6).toFixed(2) + ' μ' + unit;
    } else if (Math.abs(value) < 1) {
        return (value * 1e3).toFixed(2) + ' m' + unit;
    } else {
        return value.toFixed(2) + ' ' + unit;
    }
}
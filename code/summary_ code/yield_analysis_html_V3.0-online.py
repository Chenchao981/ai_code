import re  # 新增正则模块导入
import pandas as pd
import plotly.graph_objects as go
import os
import csv
from plotly.subplots import make_subplots

# 新增辅助函数（移动到文件顶部）
def _has_separator(file_path):
    """ 检测CSV文件是否包含分隔线 """
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            next(reader)  # 跳过标题行
            second_line = next(reader)
            return all(not re.search(r'\d', cell) for cell in second_line)
        except StopIteration:
            return False
def plot_yield_chart_html(data_file, output_html=None):
    # 如果没有指定输出路径，则在数据文件所在目录下创建HTML文件
    if output_html is None:
        data_dir = os.path.dirname(data_file)
        data_filename = os.path.basename(data_file)
        base_name = os.path.splitext(data_filename)[0]
        output_html = os.path.join(data_dir, f'{base_name}_yield_chart.html')

    # 读取数据文件（支持CSV和Excel格式）
    file_ext = os.path.splitext(data_file)[1].lower()
    if file_ext == '.csv':
        # 修改skiprows参数为动态判断
        df = pd.read_csv(
            data_file,
            dtype={'WAFER_ID': str},
            skipinitialspace=True,
            parse_dates=False,
            engine='python',
            skip_blank_lines=True,
            header=0,
            skiprows=lambda x: x == 1 if _has_separator(data_file) else False  # 新增判断逻辑
        )
        
        # 新增列名清洗逻辑
        df.columns = df.columns.str.strip()
        print("\n清洗后列名:", list(df.columns))
        
        # 新增数据格式验证（移动到单次读取后）
        print("\n原始数据格式验证:")
        print(df.dtypes.to_string())
        
    elif file_ext in ['.xls', '.xlsx']:
        df = pd.read_excel(data_file)
    else:
        raise ValueError(f'不支持的文件格式：{file_ext}')

    # 加强列名匹配逻辑（新增精确匹配优先）
    wafer_id_col = next((col for col in df.columns if col.strip().upper() == 'WAFER_ID'), None)
    if not wafer_id_col:
        wafer_id_col = next((col for col in df.columns if 'WAFER' in col.upper() and 'ID' in col.upper()), None)
    
    # 同样的逻辑应用到良率列
    yield_col = next((col for col in df.columns if col.strip().upper() == 'YIELD(%)'), None)
    if not yield_col:
        yield_col = next((col for col in df.columns if 'YIELD' in col.upper() and '%' in col), None)

    # 打印列名，帮助调试
    print(f"文件 {os.path.basename(data_file)} 的列名: {list(df.columns)}")

    # 智能识别WAFER_ID和YIELD(%)列
    wafer_id_col = None
    yield_col = None

    # 尝试查找WAFER_ID列
    wafer_id_candidates = ['WAFER_ID', 'WAFER ID', 'WAFERID', 'WAFER', '晶圆片号', '片号']
    for candidate in wafer_id_candidates:
        if candidate in df.columns:
            wafer_id_col = candidate
            break

    # 尝试查找YIELD(%)列
    yield_candidates = ['YIELD(%)', 'YIELD', 'YIELD PERCENT', 'YIELD%', '良率', '良率(%)']
    for candidate in yield_candidates:
        if candidate in df.columns:
            yield_col = candidate
            break

    # 如果仍然没有找到，抛出错误 -  **修改点： 移除内容推断逻辑后，找不到列名直接报错**
    if wafer_id_col is None:
        raise ValueError(f'无法识别晶圆片号列，请检查数据文件中是否包含 "WAFER_ID", "WAFER ID", "WAFERID", "WAFER", "晶圆片号", 或 "片号" 列名')
    if yield_col is None:
        raise ValueError(f'无法识别良率列，请检查数据文件中是否包含 "YIELD(%)", "YIELD", "YIELD PERCENT", "YIELD%", "良率", 或 "良率(%)" 列名')

    print(f"使用 '{wafer_id_col}' 作为晶圆片号列，'{yield_col}' 作为良率列")

    # 提取WAFER_ID和YIELD(%)列，并确保数据类型正确
    try:
        # 对于晶圆片号，进行严格验证
        wafer_ids = pd.to_numeric(df[wafer_id_col], errors='coerce')
        
        # 验证1：数值有效性
        invalid_numeric = wafer_ids.isna()
        # 验证2：范围有效性 (1-25)
        out_of_range = (wafer_ids < 1) | (wafer_ids > 25)
        
        # 合并所有无效条件
        invalid_conditions = invalid_numeric | out_of_range
        valid_indices = ~invalid_conditions
        
        # 处理无效数据
        if invalid_conditions.any():
            invalid_df = df[invalid_conditions]
            print(f"发现 {len(invalid_df)} 条无效晶圆片数据:")
            print("无效原因分布:")
            print(f"  - 非数字值: {invalid_numeric.sum()} 条")
            print(f"  - 超出范围(1-25): {out_of_range.sum()} 条")
            print("样例数据:")
            print(invalid_df[[wafer_id_col, yield_col]].head(3))
            
            # 过滤无效数据
            wafer_ids = wafer_ids[valid_indices].astype(int)
            df = df[valid_indices]
        else:
            wafer_ids = wafer_ids.astype(int)

        # 对于良率，进行严格验证
        yields = pd.to_numeric(df[yield_col], errors='coerce')
        
        # 验证良率范围 (80-100)
        invalid_yield = (yields < 80) | (yields > 100)
        valid_yield_indices = ~invalid_yield
        
        # 处理无效良率
        if invalid_yield.any():
            invalid_yield_df = df[invalid_yield]
            print(f"发现 {len(invalid_yield_df)} 条无效良率数据:")
            print(f"最小良率值: {yields.min():.2f}")
            print(f"最大良率值: {yields.max():.2f}")
            print("样例数据:")
            print(invalid_yield_df[[wafer_id_col, yield_col]].head(3))
            
            # 过滤无效良率
            yields = yields[valid_yield_indices]
            wafer_ids = wafer_ids[valid_yield_indices]
        
    except Exception as e:
        raise ValueError(f'数据处理失败: {str(e)}')

    # 打印预览数据，用于调试（修改为使用原始DataFrame）
    print(f"找到 {len(wafer_ids)} 条数据记录")
    print("数据预览:")
    for i, row in df[:5].iterrows():  # 修改点：直接使用原始DataFrame的前5行
        print(f"  行 {i+1}: 晶圆片号={row[wafer_id_col]}, 良率={row[yield_col]}")
    if len(df) > 5:
        print("  ...")

    # 创建Plotly图表 - 移除表格，只保留散点图
    fig = go.Figure()

    # 添加折线图
    fig.add_trace(
        go.Scatter(
            x=wafer_ids,
            y=yields,
            mode='lines+markers+text',
            name='良率',
            line=dict(color='royalblue', width=2),
            marker=dict(size=10),
            text=[f'{y:.2f}' for y in yields],
            textposition='top center',
            hovertemplate='晶圆片号: %{x}<br>良率: %{y:.2f}%'
        )
    )

    # 在x轴下方添加良率值标签
    annotations = []

    # 添加晶圆片号下方的良率值
    for i, (wafer_id, yield_value) in enumerate(zip(wafer_ids, yields)):
        annotations.append(
            dict(
                x=wafer_id,
                y=-0.15,  # 位置在x轴下方
                text=f'{yield_value:.2f}',
                showarrow=False,
                xref='x',
                yref='paper',
                font=dict(size=10)
            )
        )

    # 添加"良率"标签在纵坐标80下方
    annotations.append(
        dict(
            x=-0.05,  # 位置在y轴左侧
            y=0,  # 对应于y轴的80位置
            text="良率",
            showarrow=False,
            xref='paper',
            yref='paper',
            font=dict(size=12),
            xanchor='right'
        )
    )

    # 设置y轴范围为80-102，间隔为2
    fig.update_yaxes(
        range=[80, 102],
        dtick=2,
        tickvals=list(range(80, 101, 2))  # 仅显示80-100的刻度
    )

    # 设置x轴刻度为实际的晶圆片号
    fig.update_xaxes(
        tickmode='array',
        tickvals=wafer_ids,
        ticktext=wafer_ids
    )

    # 添加网格线
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

    # 更新布局
    fig.update_layout(
        title={
            'text': 'YIELD',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20)
        },
        yaxis_title='YIELD(%)',
        showlegend=False,
        height=600,
        margin=dict(l=50, r=50, t=120, b=100),  # 增加上边距到120（原为80）
        plot_bgcolor='white',
        hovermode='closest',
        annotations=annotations
    )

    # 保存为HTML文件（修改include_plotlyjs参数为CDN模式）
    fig.write_html(
        output_html,
        include_plotlyjs='cdn',  # 改为CDN加载
        full_html=True,
        config={'displayModeBar': True, 'responsive': True}
    )

    return output_html

def main():
    # 数据文件路径
    data_dir = r"E:\data\data2\summary"

    # 遍历目录下的所有CSV和Excel文件
    for file_name in os.listdir(data_dir):
        if file_name.lower().endswith(('.csv', '.xls', '.xlsx')):
            data_file = os.path.join(data_dir, file_name)
            try:
                print(f"正在处理文件: {file_name}")
                output_file = plot_yield_chart_html(data_file)  # 不再指定输出路径，使用默认值
                print(f'交互式良率图表已生成：{output_file} (数据来源：{file_name})')
            except Exception as e:
                print(f'处理文件 {file_name} 时出错：{str(e)}')

if __name__ == '__main__':
    main()


# 新增辅助函数（添加到文件末尾）
def _has_separator(file_path):
    """ 检测CSV文件是否包含分隔线 """
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            next(reader)  # 跳过标题行
            second_line = next(reader)
            # 检测分隔线特征：包含非字母数字字符且无数字
            return all(not re.search(r'\d', cell) for cell in second_line)
        except StopIteration:
            return False
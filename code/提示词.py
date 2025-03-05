“C:\Users\wgs03\Desktop\zhulr-ansys\data\data1\dataSummary\”这个路径下的文件是晶圆厂CP数据的汇总表。现在要解析这个表的数据，根据生成图片中的表格。
表格内容：
    1.表格纵坐标是80~100的良率数值
    2.表格最下面的横坐标是字段“YIELD(%)”的值（浮点型），也就是良率值。
    3.在良率值上面一行是片号WAFER_ID的值（正整数）
    4.表格的折线图是每一片晶圆片的良率值的取值
    5.表格标题YIELD


数据源从“C:\Users\wgs03\Desktop\zhulr-ansys\data\data1\dataSummary”文件夹下的文件中读取。这个文件类型是*.CSV或者excel文件类型。请先解析这个文件，读取文件中的实际数据，然后塞入图标中进行展示。横坐标以实际的WAFER_ID进行标注。比如这个例子是14开始到25，横坐标就应该用14片的良率作为起点。 根据逻辑进行代码调整

对齐有问题。可以渲染成html格式，用合适的前端技术帮助我绘制这个图形。

然后通过Plotly、Bokeh或ECharts等JavaScript库在HTML中展示交互式图表。 --要研究下哪个比较好用
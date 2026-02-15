"""
图表相关 Schema 定义
用于数据可视化功能的 API
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChartTypeEnum(str, Enum):
    """图表类型枚举"""

    BAR = "bar"  # 柱状图
    LINE = "line"  # 折线图
    PIE = "pie"  # 饼图
    SCATTER = "scatter"  # 散点图
    AREA = "area"  # 面积图
    RADAR = "radar"  # 雷达图
    FUNNEL = "funnel"  # 漏斗图
    GAUGE = "gauge"  # 仪表盘
    TREEMAP = "treemap"  # 矩形树图
    SUNBURST = "sunburst"  # 旭日图


class FieldTypeEnum(str, Enum):
    """字段类型枚举"""

    DIMENSION = "dimension"  # 维度字段（分类、时间等）
    MEASURE = "measure"  # 度量字段（数值、金额等）


class DataFieldType(str, Enum):
    """数据字段数据类型"""

    STRING = "string"  # 字符串类型
    NUMBER = "number"  # 数值类型
    DATE = "date"  # 日期类型
    BOOLEAN = "boolean"  # 布尔类型


class DataFieldInfo(BaseModel):
    """数据字段信息"""

    name: str = Field(..., description="字段名称")
    field_type: FieldTypeEnum = Field(
        ..., alias="fieldType", description="字段类型: dimension/measure"
    )
    data_type: DataFieldType = Field(
        ..., alias="dataType", description="数据类型: string/number/date/boolean"
    )
    unique_count: int = Field(..., alias="uniqueCount", description="唯一值数量")
    null_count: int = Field(..., alias="nullCount", description="空值数量")
    sample_values: List[Any] = Field(
        default_factory=list, alias="sampleValues", description="样本值列表"
    )
    min_value: Optional[float] = Field(None, alias="minValue", description="最小值（数值字段）")
    max_value: Optional[float] = Field(None, alias="maxValue", description="最大值（数值字段）")
    avg_value: Optional[float] = Field(None, alias="avgValue", description="平均值（数值字段）")

    model_config = ConfigDict(populate_by_name=True)


class DataAnalyzeRequest(BaseModel):
    """数据分析请求"""

    data: List[Dict[str, Any]] = Field(..., min_length=1, description="数据列表")
    sample_size: int = Field(default=100, alias="sampleSize", description="采样大小")

    model_config = ConfigDict(populate_by_name=True)


class DataAnalyzeResponse(BaseModel):
    """数据分析响应"""

    total_rows: int = Field(..., alias="totalRows", description="总行数")
    total_columns: int = Field(..., alias="totalColumns", description="总列数")
    fields: List[DataFieldInfo] = Field(..., description="字段信息列表")
    suggestions: List[str] = Field(default_factory=list, description="数据建议列表")

    model_config = ConfigDict(populate_by_name=True)


class FieldMapping(BaseModel):
    """字段映射配置"""

    x_field: Optional[str] = Field(None, alias="xField", description="X 轴字段")
    y_field: Optional[str] = Field(None, alias="yField", description="Y 轴字段")
    series_field: Optional[str] = Field(None, alias="seriesField", description="系列字段")
    value_field: Optional[str] = Field(None, alias="valueField", description="值字段（饼图等）")
    name_field: Optional[str] = Field(None, alias="nameField", description="名称字段")
    size_field: Optional[str] = Field(None, alias="sizeField", description="大小字段（散点图）")

    model_config = ConfigDict(populate_by_name=True)


class ChartStyleConfig(BaseModel):
    """图表样式配置"""

    title: Optional[str] = Field(None, description="图表标题")
    subtitle: Optional[str] = Field(None, description="图表副标题")
    width: Optional[int] = Field(None, description="图表宽度")
    height: Optional[int] = Field(None, description="图表高度")
    color_palette: Optional[List[str]] = Field(
        None, alias="colorPalette", description="颜色调色板"
    )
    show_legend: bool = Field(default=True, alias="showLegend", description="是否显示图例")
    show_tooltip: bool = Field(default=True, alias="showTooltip", description="是否显示提示框")
    show_grid: bool = Field(default=True, alias="showGrid", description="是否显示网格")
    animation: bool = Field(default=True, description="是否启用动画")
    theme: str = Field(default="default", description="主题名称")

    model_config = ConfigDict(populate_by_name=True)


class ChartGenerateRequest(BaseModel):
    """图表生成请求"""

    chart_type: ChartTypeEnum = Field(..., alias="chartType", description="图表类型")
    data: List[Dict[str, Any]] = Field(..., min_length=1, description="数据列表")
    field_mapping: FieldMapping = Field(..., alias="fieldMapping", description="字段映射配置")
    style_config: Optional[ChartStyleConfig] = Field(
        None, alias="styleConfig", description="样式配置"
    )

    model_config = ConfigDict(populate_by_name=True)


class ChartGenerateResponse(BaseModel):
    """图表生成响应"""

    chart_type: ChartTypeEnum = Field(..., alias="chartType", description="图表类型")
    echarts_option: Dict[str, Any] = Field(..., alias="echartsOption", description="ECharts 配置")
    data_count: int = Field(..., alias="dataCount", description="数据条数")
    generated_at: str = Field(..., alias="generatedAt", description="生成时间")

    model_config = ConfigDict(populate_by_name=True)


class RecommendedChart(BaseModel):
    """推荐图表"""

    chart_type: ChartTypeEnum = Field(..., alias="chartType", description="推荐图表类型")
    confidence: float = Field(..., ge=0.0, le=1.0, description="推荐置信度")
    reason: str = Field(..., description="推荐理由")
    field_mapping: FieldMapping = Field(..., alias="fieldMapping", description="建议的字段映射")
    preview_option: Optional[Dict[str, Any]] = Field(
        None, alias="previewOption", description="预览配置（可选）"
    )

    model_config = ConfigDict(populate_by_name=True)


class ChartRecommendRequest(BaseModel):
    """图表推荐请求"""

    data: List[Dict[str, Any]] = Field(..., min_length=1, description="数据列表")
    context: Optional[str] = Field(None, description="上下文描述（可选）")
    max_recommendations: int = Field(
        default=3, alias="maxRecommendations", ge=1, le=5, description="最大推荐数量"
    )

    model_config = ConfigDict(populate_by_name=True)


class ChartRecommendResponse(BaseModel):
    """图表推荐响应"""

    recommendations: List[RecommendedChart] = Field(..., description="推荐图表列表")
    data_summary: str = Field(..., alias="dataSummary", description="数据摘要")
    analyzed_at: str = Field(..., alias="analyzedAt", description="分析时间")

    model_config = ConfigDict(populate_by_name=True)

"""
图表服务模块
处理数据分析和图表生成的核心逻辑
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from ai_ppt.api.v1.schemas.chart import (
    ChartGenerateResponse,
    ChartRecommendRequest,
    ChartRecommendResponse,
    ChartStyleConfig,
    ChartTypeEnum,
    DataAnalyzeRequest,
    DataAnalyzeResponse,
    DataFieldInfo,
    DataFieldType,
    FieldMapping,
    FieldTypeEnum,
    RecommendedChart,
)


class ChartService:
    """
    图表服务类

    提供数据分析、图表生成和图表推荐功能
    """

    # 默认颜色调色板
    DEFAULT_COLORS = [
        "#5470c6",  # 蓝色
        "#91cc75",  # 绿色
        "#fac858",  # 黄色
        "#ee6666",  # 红色
        "#73c0de",  # 浅蓝
        "#3ba272",  # 深绿
        "#fc8452",  # 橙色
        "#9a60b4",  # 紫色
        "#ea7ccc",  # 粉色
    ]

    # 图表类型中文名称映射
    CHART_TYPE_NAMES = {
        ChartTypeEnum.BAR: "柱状图",
        ChartTypeEnum.LINE: "折线图",
        ChartTypeEnum.PIE: "饼图",
        ChartTypeEnum.SCATTER: "散点图",
        ChartTypeEnum.AREA: "面积图",
        ChartTypeEnum.RADAR: "雷达图",
        ChartTypeEnum.FUNNEL: "漏斗图",
        ChartTypeEnum.GAUGE: "仪表盘",
        ChartTypeEnum.TREEMAP: "矩形树图",
        ChartTypeEnum.SUNBURST: "旭日图",
    }

    def __init__(self) -> None:
        """初始化图表服务"""
        pass

    def analyze_data(self, request: DataAnalyzeRequest) -> DataAnalyzeResponse:
        """
        分析数据，返回字段信息和数据建议

        Args:
            request: 数据分析请求

        Returns:
            DataAnalyzeResponse: 数据分析响应
        """
        data = request.data
        total_rows = len(data)

        # 如果数据为空，返回空响应
        if total_rows == 0:
            return DataAnalyzeResponse(
                total_rows=0,
                total_columns=0,
                fields=[],
                suggestions=["数据为空，请提供有效数据"],
            )

        # 获取所有字段名
        all_fields = set()
        for row in data:
            all_fields.update(row.keys())

        total_columns = len(all_fields)
        fields: List[DataFieldInfo] = []

        # 分析每个字段
        for field_name in all_fields:
            field_info = self._analyze_field(
                data, field_name, request.sample_size
            )
            fields.append(field_info)

        # 生成数据建议
        suggestions = self._generate_data_suggestions(fields, total_rows)

        return DataAnalyzeResponse(
            total_rows=total_rows,
            total_columns=total_columns,
            fields=fields,
            suggestions=suggestions,
        )

    def _analyze_field(
        self, data: List[Dict[str, Any]], field_name: str, sample_size: int
    ) -> DataFieldInfo:
        """
        分析单个字段

        Args:
            data: 数据列表
            field_name: 字段名称
            sample_size: 采样大小

        Returns:
            DataFieldInfo: 字段信息
        """
        # 提取字段值
        values = []
        null_count = 0

        for row in data:
            value = row.get(field_name)
            if value is None or value == "":
                null_count += 1
            else:
                values.append(value)

        # 计算唯一值数量
        unique_values = set(str(v) for v in values)
        unique_count = len(unique_values)

        # 推断数据类型
        data_type = self._infer_data_type(values)

        # 推断字段类型（维度/度量）
        field_type = self._infer_field_type(
            values, data_type, unique_count, len(data)
        )

        # 获取样本值
        sample_values = list(unique_values)[
            : min(sample_size, len(unique_values))
        ]

        # 计算数值统计
        min_value = None
        max_value = None
        avg_value = None

        if data_type == DataFieldType.NUMBER:
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            if numeric_values:
                min_value = min(numeric_values)
                max_value = max(numeric_values)
                avg_value = sum(numeric_values) / len(numeric_values)

        return DataFieldInfo(
            name=field_name,
            field_type=field_type,
            data_type=data_type,
            unique_count=unique_count,
            null_count=null_count,
            sample_values=sample_values,
            min_value=min_value,
            max_value=max_value,
            avg_value=avg_value,
        )

    def _infer_data_type(self, values: List[Any]) -> DataFieldType:
        """
        推断数据类型

        Args:
            values: 值列表

        Returns:
            DataFieldType: 数据类型
        """
        if not values:
            return DataFieldType.STRING

        # 统计各类型数量
        number_count = 0
        date_count = 0
        bool_count = 0

        for value in values:
            if isinstance(value, bool):
                bool_count += 1
            elif isinstance(value, (int, float)):
                number_count += 1
            elif isinstance(value, str):
                # 尝试解析日期
                if self._is_date_string(value):
                    date_count += 1

        total = len(values)

        # 根据占比判断类型
        if bool_count / total > 0.8:
            return DataFieldType.BOOLEAN
        if number_count / total > 0.8:
            return DataFieldType.NUMBER
        if date_count / total > 0.8:
            return DataFieldType.DATE

        return DataFieldType.STRING

    def _is_date_string(self, value: str) -> bool:
        """
        判断字符串是否为日期格式

        Args:
            value: 字符串值

        Returns:
            bool: 是否为日期格式
        """
        import re

        # 常见日期格式正则
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{4}/\d{2}/\d{2}",  # YYYY/MM/DD
            r"\d{2}-\d{2}-\d{4}",  # MM-DD-YYYY
            r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
            r"\d{4}年\d{1,2}月\d{1,2}日",  # 中文日期
        ]

        for pattern in date_patterns:
            if re.match(pattern, value):
                return True

        return False

    def _infer_field_type(
        self,
        values: List[Any],
        data_type: DataFieldType,
        unique_count: int,
        total_count: int,
    ) -> FieldTypeEnum:
        """
        推断字段类型（维度/度量）

        Args:
            values: 值列表
            data_type: 数据类型
            unique_count: 唯一值数量
            total_count: 总数量

        Returns:
            FieldTypeEnum: 字段类型
        """
        # 数值类型且唯一值较多，倾向于度量
        if data_type == DataFieldType.NUMBER:
            # 如果唯一值占比超过 50%，更可能是度量
            if unique_count / max(total_count, 1) > 0.5:
                return FieldTypeEnum.MEASURE
            # 如果唯一值较少（如性别、等级），可能是维度
            if unique_count <= 10:
                return FieldTypeEnum.DIMENSION
            return FieldTypeEnum.MEASURE

        # 日期类型通常是维度
        if data_type == DataFieldType.DATE:
            return FieldTypeEnum.DIMENSION

        # 布尔类型是维度
        if data_type == DataFieldType.BOOLEAN:
            return FieldTypeEnum.DIMENSION

        # 字符串类型，根据唯一值占比判断
        if unique_count / max(total_count, 1) > 0.8:
            # 唯一值太多，可能是 ID，不适合作为维度
            return FieldTypeEnum.DIMENSION

        return FieldTypeEnum.DIMENSION

    def _generate_data_suggestions(
        self, fields: List[DataFieldInfo], total_rows: int
    ) -> List[str]:
        """
        生成数据建议

        Args:
            fields: 字段信息列表
            total_rows: 总行数

        Returns:
            List[str]: 建议列表
        """
        suggestions = []

        # 检查数据量
        if total_rows < 10:
            suggestions.append(
                "数据量较少，建议增加更多数据以获得更好的可视化效果"
            )

        # 检查空值
        high_null_fields = [
            f.name for f in fields if f.null_count / max(total_rows, 1) > 0.3
        ]
        if high_null_fields:
            suggestions.append(
                f"字段 {', '.join(high_null_fields)} 空值较多，建议进行数据清洗"
            )

        # 检查维度和度量
        dimensions = [
            f for f in fields if f.field_type == FieldTypeEnum.DIMENSION
        ]
        measures = [f for f in fields if f.field_type == FieldTypeEnum.MEASURE]

        if not dimensions:
            suggestions.append("未检测到维度字段，建议添加分类或时间字段")

        if not measures:
            suggestions.append("未检测到度量字段，建议添加数值字段")

        # 根据字段数量推荐图表类型
        if len(dimensions) >= 1 and len(measures) >= 1:
            suggestions.append("数据适合生成柱状图、折线图或饼图")

        if len(measures) >= 2:
            suggestions.append("数据适合生成散点图，展示两个度量之间的关系")

        return suggestions

    def generate_chart(
        self,
        chart_type: ChartTypeEnum,
        data: List[Dict[str, Any]],
        field_mapping: FieldMapping,
        style_config: Optional[ChartStyleConfig] = None,
    ) -> ChartGenerateResponse:
        """
        生成图表配置

        Args:
            chart_type: 图表类型
            data: 数据列表
            field_mapping: 字段映射
            style_config: 样式配置

        Returns:
            ChartGenerateResponse: 图表生成响应
        """
        # 根据图表类型生成对应的 ECharts 配置
        if chart_type == ChartTypeEnum.BAR:
            echarts_option = self._generate_bar_chart(
                data, field_mapping, style_config
            )
        elif chart_type == ChartTypeEnum.LINE:
            echarts_option = self._generate_line_chart(
                data, field_mapping, style_config
            )
        elif chart_type == ChartTypeEnum.PIE:
            echarts_option = self._generate_pie_chart(
                data, field_mapping, style_config
            )
        elif chart_type == ChartTypeEnum.SCATTER:
            echarts_option = self._generate_scatter_chart(
                data, field_mapping, style_config
            )
        elif chart_type == ChartTypeEnum.AREA:
            echarts_option = self._generate_area_chart(
                data, field_mapping, style_config
            )
        elif chart_type == ChartTypeEnum.RADAR:
            echarts_option = self._generate_radar_chart(
                data, field_mapping, style_config
            )
        elif chart_type == ChartTypeEnum.FUNNEL:
            echarts_option = self._generate_funnel_chart(
                data, field_mapping, style_config
            )
        else:
            # 默认使用柱状图
            echarts_option = self._generate_bar_chart(
                data, field_mapping, style_config
            )

        return ChartGenerateResponse(
            chart_type=chart_type,
            echarts_option=echarts_option,
            data_count=len(data),
            generated_at=datetime.now().isoformat(),
        )

    def _get_base_option(
        self, style_config: Optional[ChartStyleConfig]
    ) -> Dict[str, Any]:
        """
        获取基础配置

        Args:
            style_config: 样式配置

        Returns:
            Dict: 基础配置字典
        """
        option: Dict[str, Any] = {
            "title": {
                "text": style_config.title if style_config else "",
                "subtext": style_config.subtitle if style_config else "",
                "left": "center",
            },
            "tooltip": {
                "trigger": "item",
                "confine": True,
            },
            "legend": {
                "orient": "horizontal",
                "bottom": 10,
            },
            "color": (
                style_config.color_palette
                if style_config and style_config.color_palette
                else self.DEFAULT_COLORS
            ),
            "animation": style_config.animation if style_config else True,
        }

        # 根据配置调整显示
        if style_config:
            if not style_config.show_legend:
                option.pop("legend", None)
            if not style_config.show_tooltip:
                option.pop("tooltip", None)

        return option

    def _generate_bar_chart(
        self,
        data: List[Dict[str, Any]],
        field_mapping: FieldMapping,
        style_config: Optional[ChartStyleConfig],
    ) -> Dict[str, Any]:
        """
        生成柱状图配置

        Args:
            data: 数据列表
            field_mapping: 字段映射
            style_config: 样式配置

        Returns:
            Dict: ECharts 配置
        """
        option = self._get_base_option(style_config)
        option["tooltip"]["trigger"] = "axis"

        # 提取 X 轴数据
        x_field = field_mapping.x_field
        y_field = field_mapping.y_field
        series_field = field_mapping.series_field

        if not x_field or not y_field:
            return option

        # 获取 X 轴唯一值
        x_values = list(set(row.get(x_field, "") for row in data))
        x_values.sort()

        # 构建系列数据
        if series_field:
            # 有系列字段，生成多系列
            series_values = list(
                set(row.get(series_field, "") for row in data)
            )
            series_list = []

            for series_name in series_values:
                series_data = []
                for x_val in x_values:
                    # 查找对应的数据
                    value = 0
                    for row in data:
                        if (
                            row.get(x_field) == x_val
                            and row.get(series_field) == series_name
                        ):
                            value = row.get(y_field, 0)
                            break
                    series_data.append(value)

                series_list.append(
                    {
                        "name": series_name,
                        "type": "bar",
                        "data": series_data,
                    }
                )
        else:
            # 无系列字段，生成单系列
            series_data = []
            for x_val in x_values:
                # 查找对应的数据
                value = 0
                for row in data:
                    if row.get(x_field) == x_val:
                        value = row.get(y_field, 0)
                        break
                series_data.append(value)

            series_list = [
                {
                    "name": y_field,
                    "type": "bar",
                    "data": series_data,
                }
            ]

        # 设置 X 轴和 Y 轴
        option["xAxis"] = {
            "type": "category",
            "data": x_values,
            "axisLabel": {"interval": 0, "rotate": 30},
        }
        option["yAxis"] = {"type": "value"}
        option["series"] = series_list

        # 网格配置
        if style_config and style_config.show_grid:
            option["grid"] = {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "containLabel": True,
            }

        return option

    def _generate_line_chart(
        self,
        data: List[Dict[str, Any]],
        field_mapping: FieldMapping,
        style_config: Optional[ChartStyleConfig],
    ) -> Dict[str, Any]:
        """
        生成折线图配置

        Args:
            data: 数据列表
            field_mapping: 字段映射
            style_config: 样式配置

        Returns:
            Dict: ECharts 配置
        """
        option = self._get_base_option(style_config)
        option["tooltip"]["trigger"] = "axis"

        x_field = field_mapping.x_field
        y_field = field_mapping.y_field
        series_field = field_mapping.series_field

        if not x_field or not y_field:
            return option

        # 获取 X 轴唯一值
        x_values = list(set(row.get(x_field, "") for row in data))
        x_values.sort()

        # 构建系列数据
        if series_field:
            series_values = list(
                set(row.get(series_field, "") for row in data)
            )
            series_list = []

            for series_name in series_values:
                series_data = []
                for x_val in x_values:
                    value = 0
                    for row in data:
                        if (
                            row.get(x_field) == x_val
                            and row.get(series_field) == series_name
                        ):
                            value = row.get(y_field, 0)
                            break
                    series_data.append(value)

                series_list.append(
                    {
                        "name": series_name,
                        "type": "line",
                        "data": series_data,
                        "smooth": True,
                    }
                )
        else:
            series_data = []
            for x_val in x_values:
                value = 0
                for row in data:
                    if row.get(x_field) == x_val:
                        value = row.get(y_field, 0)
                        break
                series_data.append(value)

            series_list = [
                {
                    "name": y_field,
                    "type": "line",
                    "data": series_data,
                    "smooth": True,
                }
            ]

        option["xAxis"] = {
            "type": "category",
            "data": x_values,
            "boundaryGap": False,
        }
        option["yAxis"] = {"type": "value"}
        option["series"] = series_list

        if style_config and style_config.show_grid:
            option["grid"] = {
                "left": "3%",
                "right": "4%",
                "bottom": "3%",
                "containLabel": True,
            }

        return option

    def _generate_pie_chart(
        self,
        data: List[Dict[str, Any]],
        field_mapping: FieldMapping,
        style_config: Optional[ChartStyleConfig],
    ) -> Dict[str, Any]:
        """
        生成饼图配置

        Args:
            data: 数据列表
            field_mapping: 字段映射
            style_config: 样式配置

        Returns:
            Dict: ECharts 配置
        """
        option = self._get_base_option(style_config)

        name_field = field_mapping.name_field or field_mapping.x_field
        value_field = field_mapping.value_field or field_mapping.y_field

        if not name_field or not value_field:
            return option

        # 构建饼图数据
        pie_data = []
        for row in data:
            name = row.get(name_field, "")
            value = row.get(value_field, 0)
            if name:
                pie_data.append({"name": str(name), "value": value})

        option["series"] = [
            {
                "name": value_field,
                "type": "pie",
                "radius": ["40%", "70%"],
                "center": ["50%", "50%"],
                "data": pie_data,
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    }
                },
                "label": {
                    "show": True,
                    "formatter": "{b}: {d}%",
                },
            }
        ]

        return option

    def _generate_scatter_chart(
        self,
        data: List[Dict[str, Any]],
        field_mapping: FieldMapping,
        style_config: Optional[ChartStyleConfig],
    ) -> Dict[str, Any]:
        """
        生成散点图配置

        Args:
            data: 数据列表
            field_mapping: 字段映射
            style_config: 样式配置

        Returns:
            Dict: ECharts 配置
        """
        option = self._get_base_option(style_config)
        option["tooltip"]["trigger"] = "item"
        option["tooltip"]["formatter"] = "{c}"

        x_field = field_mapping.x_field
        y_field = field_mapping.y_field
        size_field = field_mapping.size_field

        if not x_field or not y_field:
            return option

        # 构建散点数据
        scatter_data = []
        for row in data:
            x_val = row.get(x_field, 0)
            y_val = row.get(y_field, 0)

            if size_field:
                size_val = row.get(size_field, 10)
                scatter_data.append([x_val, y_val, size_val])
            else:
                scatter_data.append([x_val, y_val])

        option["xAxis"] = {"type": "value"}
        option["yAxis"] = {"type": "value"}
        option["series"] = [
            {
                "name": "散点",
                "type": "scatter",
                "data": scatter_data,
                "symbolSize": lambda data: data[2] if len(data) > 2 else 10,
            }
        ]

        if style_config and style_config.show_grid:
            option["grid"] = {
                "left": "3%",
                "right": "7%",
                "bottom": "7%",
                "containLabel": True,
            }

        return option

    def _generate_area_chart(
        self,
        data: List[Dict[str, Any]],
        field_mapping: FieldMapping,
        style_config: Optional[ChartStyleConfig],
    ) -> Dict[str, Any]:
        """
        生成面积图配置

        Args:
            data: 数据列表
            field_mapping: 字段映射
            style_config: 样式配置

        Returns:
            Dict: ECharts 配置
        """
        # 面积图基于折线图
        option = self._generate_line_chart(data, field_mapping, style_config)

        # 添加面积样式
        for series in option.get("series", []):
            series["areaStyle"] = {"opacity": 0.3}

        return option

    def _generate_radar_chart(
        self,
        data: List[Dict[str, Any]],
        field_mapping: FieldMapping,
        style_config: Optional[ChartStyleConfig],
    ) -> Dict[str, Any]:
        """
        生成雷达图配置

        Args:
            data: 数据列表
            field_mapping: 字段映射
            style_config: 样式配置

        Returns:
            Dict: ECharts 配置
        """
        option = self._get_base_option(style_config)

        # 获取所有数值字段作为指标
        indicators = []
        for key in data[0].keys() if data else []:
            values = [
                row.get(key, 0)
                for row in data
                if isinstance(row.get(key), (int, float))
            ]
            if values:
                indicators.append(
                    {
                        "name": key,
                        "max": max(values) * 1.2 if values else 100,
                    }
                )

        # 构建雷达数据
        radar_data = []
        for row in data[:5]:  # 最多显示 5 条数据
            values = [row.get(ind["name"], 0) for ind in indicators]
            radar_data.append(
                {
                    "value": values,
                    "name": str(row.get(field_mapping.name_field, "系列")),
                }
            )

        option["radar"] = {
            "indicator": indicators,
            "shape": "polygon",
            "splitNumber": 5,
        }
        option["series"] = [
            {
                "name": "雷达图",
                "type": "radar",
                "data": radar_data,
            }
        ]

        return option

    def _generate_funnel_chart(
        self,
        data: List[Dict[str, Any]],
        field_mapping: FieldMapping,
        style_config: Optional[ChartStyleConfig],
    ) -> Dict[str, Any]:
        """
        生成漏斗图配置

        Args:
            data: 数据列表
            field_mapping: 字段映射
            style_config: 样式配置

        Returns:
            Dict: ECharts 配置
        """
        option = self._get_base_option(style_config)

        name_field = field_mapping.name_field or field_mapping.x_field
        value_field = field_mapping.value_field or field_mapping.y_field

        if not name_field or not value_field:
            return option

        # 构建漏斗数据
        funnel_data = []
        for row in data:
            name = row.get(name_field, "")
            value = row.get(value_field, 0)
            if name:
                funnel_data.append({"name": str(name), "value": value})

        # 按值排序
        funnel_data.sort(key=lambda x: x["value"], reverse=True)

        option["series"] = [
            {
                "name": "漏斗图",
                "type": "funnel",
                "left": "10%",
                "top": 60,
                "bottom": 60,
                "width": "80%",
                "min": 0,
                "max": (
                    max(d["value"] for d in funnel_data)
                    if funnel_data
                    else 100
                ),
                "minSize": "0%",
                "maxSize": "100%",
                "sort": "descending",
                "gap": 2,
                "data": funnel_data,
            }
        ]

        return option

    def recommend_charts(
        self, request: ChartRecommendRequest
    ) -> ChartRecommendResponse:
        """
        推荐图表类型

        Args:
            request: 图表推荐请求

        Returns:
            ChartRecommendResponse: 图表推荐响应
        """
        data = request.data
        max_recommendations = request.max_recommendations

        # 分析数据
        analyze_request = DataAnalyzeRequest(data=data)
        analyze_result = self.analyze_data(analyze_request)

        fields = analyze_result.fields
        dimensions = [
            f for f in fields if f.field_type == FieldTypeEnum.DIMENSION
        ]
        measures = [f for f in fields if f.field_type == FieldTypeEnum.MEASURE]

        recommendations: List[RecommendedChart] = []

        # 规则 1: 有维度和度量，推荐柱状图
        if dimensions and measures:
            recommendations.append(
                RecommendedChart(
                    chart_type=ChartTypeEnum.BAR,
                    confidence=0.9,
                    reason=f"数据包含维度字段（{dimensions[0].name}）和度量字段（{measures[0].name}），适合使用柱状图展示对比关系",
                    field_mapping=FieldMapping(
                        x_field=dimensions[0].name,
                        y_field=measures[0].name,
                    ),
                )
            )

        # 规则 2: 维度唯一值较少，推荐饼图
        if dimensions and measures:
            dim = dimensions[0]
            if dim.unique_count <= 10 and dim.unique_count >= 2:
                recommendations.append(
                    RecommendedChart(
                        chart_type=ChartTypeEnum.PIE,
                        confidence=0.85,
                        reason=f"维度字段（{dim.name}）有 {dim.unique_count} 个唯一值，适合使用饼图展示占比分布",
                        field_mapping=FieldMapping(
                            name_field=dim.name,
                            value_field=measures[0].name,
                        ),
                    )
                )

        # 规则 3: 有时间维度，推荐折线图
        date_dimensions = [
            f for f in dimensions if f.data_type == DataFieldType.DATE
        ]
        if date_dimensions and measures:
            recommendations.append(
                RecommendedChart(
                    chart_type=ChartTypeEnum.LINE,
                    confidence=0.88,
                    reason=f"数据包含时间维度（{date_dimensions[0].name}），适合使用折线图展示趋势变化",
                    field_mapping=FieldMapping(
                        x_field=date_dimensions[0].name,
                        y_field=measures[0].name,
                    ),
                )
            )

        # 规则 4: 有两个度量字段，推荐散点图
        if len(measures) >= 2:
            recommendations.append(
                RecommendedChart(
                    chart_type=ChartTypeEnum.SCATTER,
                    confidence=0.75,
                    reason=f"数据包含多个度量字段（{measures[0].name}, {measures[1].name}），适合使用散点图展示相关性",
                    field_mapping=FieldMapping(
                        x_field=measures[0].name,
                        y_field=measures[1].name,
                    ),
                )
            )

        # 规则 5: 维度有序且度量递减，推荐漏斗图
        if dimensions and measures and len(data) >= 3:
            recommendations.append(
                RecommendedChart(
                    chart_type=ChartTypeEnum.FUNNEL,
                    confidence=0.7,
                    reason="数据适合使用漏斗图展示转化或递减过程",
                    field_mapping=FieldMapping(
                        name_field=dimensions[0].name,
                        value_field=measures[0].name,
                    ),
                )
            )

        # 规则 6: 多个度量字段，推荐雷达图
        if len(measures) >= 3:
            recommendations.append(
                RecommendedChart(
                    chart_type=ChartTypeEnum.RADAR,
                    confidence=0.72,
                    reason=f"数据包含 {len(measures)} 个度量字段，适合使用雷达图进行多维对比",
                    field_mapping=FieldMapping(
                        name_field=dimensions[0].name if dimensions else None,
                    ),
                )
            )

        # 按置信度排序，取前 N 个
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        recommendations = recommendations[:max_recommendations]

        # 生成数据摘要
        data_summary = self._generate_data_summary(analyze_result)

        return ChartRecommendResponse(
            recommendations=recommendations,
            data_summary=data_summary,
            analyzed_at=datetime.now().isoformat(),
        )

    def _generate_data_summary(
        self, analyze_result: DataAnalyzeResponse
    ) -> str:
        """
        生成数据摘要

        Args:
            analyze_result: 数据分析结果

        Returns:
            str: 数据摘要
        """
        dimensions = [
            f
            for f in analyze_result.fields
            if f.field_type == FieldTypeEnum.DIMENSION
        ]
        measures = [
            f
            for f in analyze_result.fields
            if f.field_type == FieldTypeEnum.MEASURE
        ]

        summary_parts = [
            f"共 {analyze_result.total_rows} 行数据",
            f"{analyze_result.total_columns} 个字段",
            f"{len(dimensions)} 个维度字段",
            f"{len(measures)} 个度量字段",
        ]

        return "，".join(summary_parts)


# 创建全局服务实例
chart_service = ChartService()

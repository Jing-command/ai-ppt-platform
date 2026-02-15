"""
图表服务单元测试
直接测试 chart_service 的核心逻辑，不依赖数据库

测试范围：
- 数据分析功能
- 图表生成功能
- 图表推荐功能
"""

import pytest
from datetime import datetime

from ai_ppt.api.v1.schemas.chart import (
    ChartTypeEnum,
    FieldTypeEnum,
    DataFieldType,
    DataAnalyzeRequest,
    ChartGenerateRequest,
    ChartRecommendRequest,
    FieldMapping,
    ChartStyleConfig,
)
from ai_ppt.services.chart_service import chart_service

# ==================== 测试数据 ====================


@pytest.fixture
def sample_data_basic():
    """基础测试数据"""
    return [
        {"category": "A", "value": 100, "date": "2024-01-01"},
        {"category": "B", "value": 200, "date": "2024-01-02"},
        {"category": "C", "value": 150, "date": "2024-01-03"},
        {"category": "A", "value": 120, "date": "2024-01-04"},
        {"category": "B", "value": 180, "date": "2024-01-05"},
    ]


@pytest.fixture
def sample_data_with_nulls():
    """包含空值的测试数据"""
    return [
        {"category": "A", "value": 100, "description": "产品A"},
        {"category": "B", "value": None, "description": None},
        {"category": None, "value": 150, "description": "产品C"},
        {"category": "D", "value": 200, "description": ""},
    ]


@pytest.fixture
def sample_data_numeric_only():
    """仅包含数值字段的测试数据"""
    return [
        {"value1": 100, "value2": 50, "value3": 25},
        {"value1": 200, "value2": 75, "value3": 30},
        {"value1": 150, "value2": 60, "value3": 28},
    ]


@pytest.fixture
def sample_data_string_only():
    """仅包含字符串字段的测试数据"""
    return [
        {"name": "Alice", "city": "Beijing"},
        {"name": "Bob", "city": "Shanghai"},
        {"name": "Charlie", "city": "Guangzhou"},
    ]


@pytest.fixture
def sample_data_date_fields():
    """包含日期字段的测试数据"""
    return [
        {"date": "2024-01-01", "value": 100},
        {"date": "2024-01-02", "value": 150},
        {"date": "2024-01-03", "value": 200},
    ]


# ==================== 数据分析测试 ====================


class TestAnalyzeData:
    """数据分析功能测试类"""

    def test_analyze_basic_data(self, sample_data_basic):
        """
        UNIT-001: 测试基础数据分析

        验证点：
        - 正确识别总行数和总列数
        - 正确识别字段名称
        - 正确推断字段类型
        """
        # 创建请求
        request = DataAnalyzeRequest(data=sample_data_basic, sample_size=100)

        # 执行分析
        result = chart_service.analyze_data(request)

        # 验证基本字段
        assert result.total_rows == 5
        assert result.total_columns == 3

        # 验证字段列表
        assert len(result.fields) == 3

        # 验证字段名称
        field_names = [f.name for f in result.fields]
        assert "category" in field_names
        assert "value" in field_names
        assert "date" in field_names

        # 验证字段类型推断
        for field in result.fields:
            if field.name == "category":
                assert field.field_type == FieldTypeEnum.DIMENSION
                assert field.data_type == DataFieldType.STRING
            elif field.name == "value":
                assert field.field_type == FieldTypeEnum.MEASURE
                assert field.data_type == DataFieldType.NUMBER

    def test_analyze_data_with_nulls(self, sample_data_with_nulls):
        """
        UNIT-002: 测试包含空值的数据分析

        验证点：
        - 正确统计空值数量
        """
        # 创建请求
        request = DataAnalyzeRequest(
            data=sample_data_with_nulls, sample_size=100
        )

        # 执行分析
        result = chart_service.analyze_data(request)

        # 验证空值计数
        for field in result.fields:
            if field.name == "value":
                assert field.null_count == 1
            elif field.name == "category":
                assert field.null_count == 1

    def test_analyze_numeric_only_data(self, sample_data_numeric_only):
        """
        UNIT-003: 测试仅包含数值字段的数据分析

        验证点：
        - 所有字段被识别为度量字段
        - 建议中包含维度字段缺失警告
        """
        # 创建请求
        request = DataAnalyzeRequest(
            data=sample_data_numeric_only, sample_size=100
        )

        # 执行分析
        result = chart_service.analyze_data(request)

        # 验证所有字段都是度量字段
        for field in result.fields:
            assert field.field_type == FieldTypeEnum.MEASURE

        # 验证建议中包含维度字段缺失警告
        suggestions_text = " ".join(result.suggestions)
        assert "维度" in suggestions_text

    def test_analyze_string_only_data(self, sample_data_string_only):
        """
        UNIT-004: 测试仅包含字符串字段的数据分析

        验证点：
        - 所有字段被识别为维度字段
        - 建议中包含度量字段缺失警告
        """
        # 创建请求
        request = DataAnalyzeRequest(
            data=sample_data_string_only, sample_size=100
        )

        # 执行分析
        result = chart_service.analyze_data(request)

        # 验证所有字段都是维度字段
        for field in result.fields:
            assert field.field_type == FieldTypeEnum.DIMENSION

        # 验证建议中包含度量字段缺失警告
        suggestions_text = " ".join(result.suggestions)
        assert "度量" in suggestions_text

    def test_analyze_date_field_recognition(self, sample_data_date_fields):
        """
        UNIT-005: 测试日期字段识别

        验证点：
        - 日期字段被正确识别
        - 日期字段被识别为维度字段
        """
        # 创建请求
        request = DataAnalyzeRequest(
            data=sample_data_date_fields, sample_size=100
        )

        # 执行分析
        result = chart_service.analyze_data(request)

        # 查找日期字段
        date_field = None
        for field in result.fields:
            if field.name == "date":
                date_field = field
                break

        # 验证日期字段存在且类型正确
        assert date_field is not None
        assert date_field.data_type == DataFieldType.DATE
        assert date_field.field_type == FieldTypeEnum.DIMENSION

    def test_analyze_empty_data(self):
        """
        UNIT-006: 测试空数据分析

        验证点：
        - Pydantic 验证不允许空数据列表
        - 这是预期的验证行为
        """
        # 创建空数据请求应该抛出验证错误
        # 这是正确的行为，因为 API 层面会返回 422 错误
        with pytest.raises(Exception):  # Pydantic ValidationError
            DataAnalyzeRequest(data=[], sample_size=100)


# ==================== 图表生成测试 ====================


class TestGenerateChart:
    """图表生成功能测试类"""

    def test_generate_bar_chart(self, sample_data_basic):
        """
        UNIT-007: 测试柱状图生成

        验证点：
        - 返回正确的图表类型
        - ECharts 配置包含必要字段
        - 数据条数正确
        """
        # 创建字段映射
        field_mapping = FieldMapping(x_field="category", y_field="value")

        # 生成图表
        result = chart_service.generate_chart(
            chart_type=ChartTypeEnum.BAR,
            data=sample_data_basic,
            field_mapping=field_mapping,
        )

        # 验证基本字段
        assert result.chart_type == ChartTypeEnum.BAR
        assert result.data_count == 5

        # 验证 ECharts 配置
        assert "xAxis" in result.echarts_option
        assert "yAxis" in result.echarts_option
        assert "series" in result.echarts_option

        # 验证系列类型
        assert result.echarts_option["series"][0]["type"] == "bar"

    def test_generate_line_chart(self, sample_data_basic):
        """
        UNIT-008: 测试折线图生成

        验证点：
        - 返回正确的图表类型
        - ECharts 配置正确
        """
        # 创建字段映射
        field_mapping = FieldMapping(x_field="date", y_field="value")

        # 生成图表
        result = chart_service.generate_chart(
            chart_type=ChartTypeEnum.LINE,
            data=sample_data_basic,
            field_mapping=field_mapping,
        )

        # 验证图表类型
        assert result.chart_type == ChartTypeEnum.LINE

        # 验证系列类型
        assert result.echarts_option["series"][0]["type"] == "line"

    def test_generate_pie_chart(self, sample_data_basic):
        """
        UNIT-009: 测试饼图生成

        验证点：
        - 返回正确的图表类型
        - ECharts 配置正确
        """
        # 创建字段映射 - 饼图使用 name_field 和 value_field
        field_mapping = FieldMapping(
            name_field="category", value_field="value"
        )

        # 生成图表
        result = chart_service.generate_chart(
            chart_type=ChartTypeEnum.PIE,
            data=sample_data_basic,
            field_mapping=field_mapping,
        )

        # 验证图表类型
        assert result.chart_type == ChartTypeEnum.PIE

        # 验证系列类型
        assert result.echarts_option["series"][0]["type"] == "pie"

    def test_generate_scatter_chart(self):
        """
        UNIT-010: 测试散点图生成

        验证点：
        - 返回正确的图表类型
        - ECharts 配置正确
        """
        # 构造散点图数据
        scatter_data = [
            {"x": 10, "y": 20},
            {"x": 30, "y": 40},
            {"x": 50, "y": 60},
        ]

        # 创建字段映射
        field_mapping = FieldMapping(x_field="x", y_field="y")

        # 生成图表
        result = chart_service.generate_chart(
            chart_type=ChartTypeEnum.SCATTER,
            data=scatter_data,
            field_mapping=field_mapping,
        )

        # 验证图表类型
        assert result.chart_type == ChartTypeEnum.SCATTER

        # 验证系列类型
        assert result.echarts_option["series"][0]["type"] == "scatter"

    def test_generate_area_chart(self, sample_data_basic):
        """
        UNIT-011: 测试面积图生成

        验证点：
        - 返回正确的图表类型
        - ECharts 配置包含面积样式
        """
        # 创建字段映射
        field_mapping = FieldMapping(x_field="date", y_field="value")

        # 生成图表
        result = chart_service.generate_chart(
            chart_type=ChartTypeEnum.AREA,
            data=sample_data_basic,
            field_mapping=field_mapping,
        )

        # 验证图表类型
        assert result.chart_type == ChartTypeEnum.AREA

        # 验证面积样式
        series = result.echarts_option["series"][0]
        assert "areaStyle" in series

    def test_generate_radar_chart(self):
        """
        UNIT-012: 测试雷达图生成

        验证点：
        - 返回正确的图表类型
        - ECharts 配置正确
        """
        # 构造雷达图数据
        radar_data = [
            {"name": "指标A", "value": 80},
            {"name": "指标B", "value": 90},
            {"name": "指标C", "value": 70},
        ]

        # 创建字段映射
        field_mapping = FieldMapping(name_field="name", value_field="value")

        # 生成图表
        result = chart_service.generate_chart(
            chart_type=ChartTypeEnum.RADAR,
            data=radar_data,
            field_mapping=field_mapping,
        )

        # 验证图表类型
        assert result.chart_type == ChartTypeEnum.RADAR

    def test_generate_funnel_chart(self):
        """
        UNIT-013: 测试漏斗图生成

        验证点：
        - 返回正确的图表类型
        - ECharts 配置正确
        """
        # 构造漏斗图数据
        funnel_data = [
            {"stage": "访问", "value": 1000},
            {"stage": "浏览", "value": 800},
            {"stage": "下单", "value": 500},
            {"stage": "支付", "value": 300},
        ]

        # 创建字段映射
        field_mapping = FieldMapping(name_field="stage", value_field="value")

        # 生成图表
        result = chart_service.generate_chart(
            chart_type=ChartTypeEnum.FUNNEL,
            data=funnel_data,
            field_mapping=field_mapping,
        )

        # 验证图表类型
        assert result.chart_type == ChartTypeEnum.FUNNEL

        # 验证系列类型
        assert result.echarts_option["series"][0]["type"] == "funnel"

    def test_generate_chart_with_style_config(self, sample_data_basic):
        """
        UNIT-014: 测试带样式配置的图表生成

        验证点：
        - 样式配置被正确应用
        """
        # 创建字段映射
        field_mapping = FieldMapping(x_field="category", y_field="value")

        # 创建样式配置
        style_config = ChartStyleConfig(
            title="自定义标题",
            subtitle="自定义副标题",
            show_legend=True,
            show_tooltip=True,
            show_grid=True,
            animation=True,
            color_palette=["#5470c6", "#91cc75", "#fac858"],
        )

        # 生成图表
        result = chart_service.generate_chart(
            chart_type=ChartTypeEnum.BAR,
            data=sample_data_basic,
            field_mapping=field_mapping,
            style_config=style_config,
        )

        # 验证标题配置
        assert "title" in result.echarts_option
        assert result.echarts_option["title"]["text"] == "自定义标题"


# ==================== 图表推荐测试 ====================


class TestRecommendCharts:
    """图表推荐功能测试类"""

    def test_recommend_basic_data(self, sample_data_basic):
        """
        UNIT-015: 测试基础数据图表推荐

        验证点：
        - 返回推荐列表不为空
        - 推荐项结构正确
        - 置信度范围正确
        """
        # 创建请求
        request = ChartRecommendRequest(
            data=sample_data_basic,
            context="销售数据分析",
            max_recommendations=3,
        )

        # 执行推荐
        result = chart_service.recommend_charts(request)

        # 验证推荐列表
        assert len(result.recommendations) > 0
        assert len(result.recommendations) <= 3

        # 验证推荐项结构
        for rec in result.recommendations:
            assert rec.chart_type is not None
            assert 0.0 <= rec.confidence <= 1.0
            assert rec.reason is not None
            assert rec.field_mapping is not None

        # 验证数据摘要
        assert result.data_summary != ""

    def test_recommend_with_dimension_and_measure(self, sample_data_basic):
        """
        UNIT-016: 测试包含维度和度量字段的数据推荐

        验证点：
        - 推荐包含柱状图
        """
        # 创建请求
        request = ChartRecommendRequest(
            data=sample_data_basic, max_recommendations=5
        )

        # 执行推荐
        result = chart_service.recommend_charts(request)

        # 获取推荐的图表类型
        recommended_types = [rec.chart_type for rec in result.recommendations]

        # 验证包含柱状图推荐
        assert ChartTypeEnum.BAR in recommended_types

    def test_recommend_with_date_field(self, sample_data_date_fields):
        """
        UNIT-017: 测试包含日期字段的数据推荐

        验证点：
        - 推荐包含折线图
        """
        # 创建请求
        request = ChartRecommendRequest(
            data=sample_data_date_fields, max_recommendations=5
        )

        # 执行推荐
        result = chart_service.recommend_charts(request)

        # 获取推荐的图表类型
        recommended_types = [rec.chart_type for rec in result.recommendations]

        # 验证包含折线图推荐
        assert ChartTypeEnum.LINE in recommended_types

    def test_recommend_with_multiple_measures(self, sample_data_numeric_only):
        """
        UNIT-018: 测试包含多个度量字段的数据推荐

        验证点：
        - 推荐包含散点图
        """
        # 创建请求
        request = ChartRecommendRequest(
            data=sample_data_numeric_only, max_recommendations=5
        )

        # 执行推荐
        result = chart_service.recommend_charts(request)

        # 获取推荐的图表类型
        recommended_types = [rec.chart_type for rec in result.recommendations]

        # 验证包含散点图推荐
        assert ChartTypeEnum.SCATTER in recommended_types

    def test_recommend_max_recommendations_limit(self, sample_data_basic):
        """
        UNIT-019: 测试最大推荐数量限制

        验证点：
        - 返回的推荐数量不超过限制
        """
        # 创建请求 - 限制为 2 个推荐
        request = ChartRecommendRequest(
            data=sample_data_basic, max_recommendations=2
        )

        # 执行推荐
        result = chart_service.recommend_charts(request)

        # 验证推荐数量不超过限制
        assert len(result.recommendations) <= 2

    def test_recommend_confidence_ordering(self, sample_data_basic):
        """
        UNIT-020: 测试推荐置信度排序

        验证点：
        - 推荐按置信度降序排列
        """
        # 创建请求
        request = ChartRecommendRequest(
            data=sample_data_basic, max_recommendations=5
        )

        # 执行推荐
        result = chart_service.recommend_charts(request)

        # 获取置信度列表
        confidences = [rec.confidence for rec in result.recommendations]

        # 验证按置信度降序排列
        assert confidences == sorted(confidences, reverse=True)

    def test_recommend_field_mapping_suggestion(self, sample_data_basic):
        """
        UNIT-021: 测试字段映射建议

        验证点：
        - 每个推荐包含字段映射建议
        """
        # 创建请求
        request = ChartRecommendRequest(
            data=sample_data_basic, max_recommendations=3
        )

        # 执行推荐
        result = chart_service.recommend_charts(request)

        # 验证字段映射
        for rec in result.recommendations:
            field_mapping = rec.field_mapping
            # 至少有一个字段被映射
            has_mapping = any(
                [
                    field_mapping.x_field,
                    field_mapping.y_field,
                    field_mapping.name_field,
                    field_mapping.value_field,
                ]
            )
            assert has_mapping, f"推荐 {rec.chart_type} 缺少字段映射"


# ==================== 边界情况测试 ====================


class TestEdgeCases:
    """边界情况测试类"""

    def test_analyze_single_row_data(self):
        """
        UNIT-022: 测试单行数据分析

        验证点：
        - 正确处理单行数据
        """
        # 创建请求
        request = DataAnalyzeRequest(
            data=[{"category": "A", "value": 100}],
            sample_size=100,
        )

        # 执行分析
        result = chart_service.analyze_data(request)

        # 验证基本字段
        assert result.total_rows == 1
        assert result.total_columns == 2

    def test_analyze_inconsistent_schema(self):
        """
        UNIT-023: 测试不一致的数据结构

        验证点：
        - 所有字段都被识别
        """
        # 创建请求 - 字段不一致
        request = DataAnalyzeRequest(
            data=[
                {"category": "A", "value": 100},
                {"category": "B", "value": 200, "extra": "extra_value"},
                {"category": "C"},
            ],
            sample_size=100,
        )

        # 执行分析
        result = chart_service.analyze_data(request)

        # 验证所有字段都被识别
        field_names = [f.name for f in result.fields]
        assert "category" in field_names
        assert "value" in field_names
        assert "extra" in field_names

    def test_generate_chart_with_special_characters(self):
        """
        UNIT-024: 测试包含特殊字符的数据

        验证点：
        - 图表正确生成
        """
        # 构造包含特殊字符的数据
        special_data = [
            {"category": "类别<特殊>", "value": 100},
            {"category": "类别&符号", "value": 200},
            {"category": '类别"引号', "value": 150},
        ]

        # 创建字段映射
        field_mapping = FieldMapping(x_field="category", y_field="value")

        # 生成图表
        result = chart_service.generate_chart(
            chart_type=ChartTypeEnum.BAR,
            data=special_data,
            field_mapping=field_mapping,
        )

        # 验证图表生成成功
        assert result.data_count == 3

    def test_analyze_boolean_fields(self):
        """
        UNIT-025: 测试布尔类型字段识别

        验证点：
        - 布尔字段被正确识别
        """
        # 构造包含布尔字段的数据
        bool_data = [
            {"name": "A", "active": True, "value": 100},
            {"name": "B", "active": False, "value": 200},
            {"name": "C", "active": True, "value": 150},
        ]

        # 创建请求
        request = DataAnalyzeRequest(data=bool_data, sample_size=100)

        # 执行分析
        result = chart_service.analyze_data(request)

        # 查找布尔字段
        active_field = None
        for field in result.fields:
            if field.name == "active":
                active_field = field
                break

        # 验证布尔字段被正确识别
        assert active_field is not None
        assert active_field.data_type == DataFieldType.BOOLEAN

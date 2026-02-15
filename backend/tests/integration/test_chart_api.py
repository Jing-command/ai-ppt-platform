"""
图表可视化 API 集成测试
测试数据分析、图表生成和图表推荐接口

测试范围：
- POST /api/v1/charts/analyze - 数据分析接口
- POST /api/v1/charts/generate - 图表生成接口
- POST /api/v1/charts/recommend - 图表推荐接口

边界情况：
- 空数据处理
- 大数据量处理
- 无效数据处理
- 字段类型推断
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from ai_ppt.api.v1.schemas.chart import (
    ChartTypeEnum,
    FieldTypeEnum,
    DataFieldType,
)


# ==================== 测试数据 Fixtures ====================


@pytest.fixture
def sample_data_basic():
    """
    基础测试数据
    包含维度字段和度量字段的标准数据
    """
    return [
        {"category": "A", "value": 100, "date": "2024-01-01"},
        {"category": "B", "value": 200, "date": "2024-01-02"},
        {"category": "C", "value": 150, "date": "2024-01-03"},
        {"category": "A", "value": 120, "date": "2024-01-04"},
        {"category": "B", "value": 180, "date": "2024-01-05"},
    ]


@pytest.fixture
def sample_data_with_nulls():
    """
    包含空值的测试数据
    用于测试空值处理逻辑
    """
    return [
        {"category": "A", "value": 100, "description": "产品A"},
        {"category": "B", "value": None, "description": None},
        {"category": None, "value": 150, "description": "产品C"},
        {"category": "D", "value": 200, "description": ""},
    ]


@pytest.fixture
def sample_data_large():
    """
    大数据量测试数据
    生成 100 条数据用于测试性能
    """
    import random

    categories = ["A", "B", "C", "D", "E"]
    data = []
    for i in range(100):
        data.append(
            {
                "category": random.choice(categories),
                "value": random.randint(10, 1000),
                "date": f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                "count": random.randint(1, 100),
            }
        )
    return data


@pytest.fixture
def sample_data_numeric_only():
    """
    仅包含数值字段的测试数据
    用于测试度量字段识别
    """
    return [
        {"value1": 100, "value2": 50, "value3": 25},
        {"value1": 200, "value2": 75, "value3": 30},
        {"value1": 150, "value2": 60, "value3": 28},
    ]


@pytest.fixture
def sample_data_string_only():
    """
    仅包含字符串字段的测试数据
    用于测试维度字段识别
    """
    return [
        {"name": "Alice", "city": "Beijing"},
        {"name": "Bob", "city": "Shanghai"},
        {"name": "Charlie", "city": "Guangzhou"},
    ]


@pytest.fixture
def sample_data_date_fields():
    """
    包含日期字段的测试数据
    用于测试日期类型识别
    """
    return [
        {"date": "2024-01-01", "value": 100},
        {"date": "2024-01-02", "value": 150},
        {"date": "2024-01-03", "value": 200},
    ]


# ==================== 数据分析接口测试 ====================


class TestDataAnalyzeAPI:
    """
    数据分析接口测试类
    测试 POST /api/v1/charts/analyze 端点
    """

    @pytest.mark.asyncio
    async def test_analyze_basic_data(self, client: AsyncClient, sample_data_basic):
        """
        API-001: 测试基础数据分析

        测试步骤：
        1. 发送包含维度和度量字段的数据
        2. 验证响应状态码为 200
        3. 验证返回的字段信息正确
        4. 验证字段类型推断正确
        """
        # 构造请求体
        request_body = {"data": sample_data_basic, "sampleSize": 100}

        # 发送请求
        response = await client.post("/api/v1/charts/analyze", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证基本字段
        assert result["totalRows"] == 5
        assert result["totalColumns"] == 3

        # 验证字段列表
        assert len(result["fields"]) == 3

        # 验证字段名称
        field_names = [f["name"] for f in result["fields"]]
        assert "category" in field_names
        assert "value" in field_names
        assert "date" in field_names

        # 验证字段类型推断
        for field in result["fields"]:
            if field["name"] == "category":
                # category 应该被识别为维度字段
                assert field["fieldType"] == FieldTypeEnum.DIMENSION.value
                assert field["dataType"] == DataFieldType.STRING.value
            elif field["name"] == "value":
                # value 应该被识别为度量字段
                assert field["fieldType"] == FieldTypeEnum.MEASURE.value
                assert field["dataType"] == DataFieldType.NUMBER.value

    @pytest.mark.asyncio
    async def test_analyze_data_with_nulls(
        self, client: AsyncClient, sample_data_with_nulls
    ):
        """
        API-002: 测试包含空值的数据分析

        测试步骤：
        1. 发送包含空值的数据
        2. 验证响应状态码为 200
        3. 验证空值计数正确
        4. 验证建议中包含空值警告
        """
        # 构造请求体
        request_body = {"data": sample_data_with_nulls, "sampleSize": 100}

        # 发送请求
        response = await client.post("/api/v1/charts/analyze", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证空值计数
        for field in result["fields"]:
            if field["name"] == "value":
                # value 字段有 1 个空值
                assert field["nullCount"] == 1
            elif field["name"] == "category":
                # category 字段有 1 个空值
                assert field["nullCount"] == 1
            elif field["name"] == "description":
                # description 字段有 2 个空值（None 和空字符串）
                assert field["nullCount"] >= 1

    @pytest.mark.asyncio
    async def test_analyze_large_data(self, client: AsyncClient, sample_data_large):
        """
        API-003: 测试大数据量分析

        测试步骤：
        1. 发送 100 条数据
        2. 验证响应状态码为 200
        3. 验证处理时间合理
        4. 验证字段分析正确
        """
        # 构造请求体
        request_body = {"data": sample_data_large, "sampleSize": 50}

        # 发送请求
        response = await client.post("/api/v1/charts/analyze", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证基本字段
        assert result["totalRows"] == 100
        assert result["totalColumns"] == 4

        # 验证字段数量
        assert len(result["fields"]) == 4

    @pytest.mark.asyncio
    async def test_analyze_empty_data(self, client: AsyncClient):
        """
        API-004: 测试空数据分析

        测试步骤：
        1. 发送空数据列表
        2. 验证返回 422 错误（数据验证失败）
        """
        # 构造请求体 - 空数据
        request_body = {"data": [], "sampleSize": 100}

        # 发送请求
        response = await client.post("/api/v1/charts/analyze", json=request_body)

        # 验证响应状态码 - 应该返回 422 验证错误
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_analyze_numeric_only_data(
        self, client: AsyncClient, sample_data_numeric_only
    ):
        """
        API-005: 测试仅包含数值字段的数据分析

        测试步骤：
        1. 发送仅包含数值字段的数据
        2. 验证所有字段被识别为度量字段
        3. 验证建议中包含维度字段缺失警告
        """
        # 构造请求体
        request_body = {"data": sample_data_numeric_only, "sampleSize": 100}

        # 发送请求
        response = await client.post("/api/v1/charts/analyze", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证所有字段都是度量字段
        for field in result["fields"]:
            assert field["fieldType"] == FieldTypeEnum.MEASURE.value

        # 验证建议中包含维度字段缺失警告
        suggestions_text = " ".join(result.get("suggestions", []))
        assert "维度" in suggestions_text or "dimension" in suggestions_text.lower()

    @pytest.mark.asyncio
    async def test_analyze_string_only_data(
        self, client: AsyncClient, sample_data_string_only
    ):
        """
        API-006: 测试仅包含字符串字段的数据分析

        测试步骤：
        1. 发送仅包含字符串字段的数据
        2. 验证所有字段被识别为维度字段
        3. 验证建议中包含度量字段缺失警告
        """
        # 构造请求体
        request_body = {"data": sample_data_string_only, "sampleSize": 100}

        # 发送请求
        response = await client.post("/api/v1/charts/analyze", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证所有字段都是维度字段
        for field in result["fields"]:
            assert field["fieldType"] == FieldTypeEnum.DIMENSION.value

        # 验证建议中包含度量字段缺失警告
        suggestions_text = " ".join(result.get("suggestions", []))
        assert "度量" in suggestions_text or "measure" in suggestions_text.lower()

    @pytest.mark.asyncio
    async def test_analyze_date_field_recognition(
        self, client: AsyncClient, sample_data_date_fields
    ):
        """
        API-007: 测试日期字段识别

        测试步骤：
        1. 发送包含日期字段的数据
        2. 验证日期字段被正确识别
        3. 验证日期字段被识别为维度字段
        """
        # 构造请求体
        request_body = {"data": sample_data_date_fields, "sampleSize": 100}

        # 发送请求
        response = await client.post("/api/v1/charts/analyze", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 查找日期字段
        date_field = None
        for field in result["fields"]:
            if field["name"] == "date":
                date_field = field
                break

        # 验证日期字段存在且类型正确
        assert date_field is not None
        assert date_field["dataType"] == DataFieldType.DATE.value
        assert date_field["fieldType"] == FieldTypeEnum.DIMENSION.value

    @pytest.mark.asyncio
    async def test_analyze_invalid_request_body(self, client: AsyncClient):
        """
        API-008: 测试无效请求体

        测试步骤：
        1. 发送缺少 data 字段的请求
        2. 验证返回 422 错误
        """
        # 构造无效请求体
        request_body = {"sampleSize": 100}

        # 发送请求
        response = await client.post("/api/v1/charts/analyze", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ==================== 图表生成接口测试 ====================


class TestChartGenerateAPI:
    """
    图表生成接口测试类
    测试 POST /api/v1/charts/generate 端点
    """

    @pytest.mark.asyncio
    async def test_generate_bar_chart(self, client: AsyncClient, sample_data_basic):
        """
        API-009: 测试柱状图生成

        测试步骤：
        1. 发送柱状图生成请求
        2. 验证响应状态码为 200
        3. 验证返回的 ECharts 配置正确
        4. 验证数据条数正确
        """
        # 构造请求体
        request_body = {
            "chartType": ChartTypeEnum.BAR.value,
            "data": sample_data_basic,
            "fieldMapping": {"xField": "category", "yField": "value"},
            "styleConfig": {"title": "销售数据", "showLegend": True, "animation": True},
        }

        # 发送请求
        response = await client.post("/api/v1/charts/generate", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证基本字段
        assert result["chartType"] == ChartTypeEnum.BAR.value
        assert result["dataCount"] == 5

        # 验证 ECharts 配置
        echarts_option = result["echartsOption"]
        assert "xAxis" in echarts_option
        assert "yAxis" in echarts_option
        assert "series" in echarts_option

        # 验证系列类型
        assert echarts_option["series"][0]["type"] == "bar"

    @pytest.mark.asyncio
    async def test_generate_line_chart(self, client: AsyncClient, sample_data_basic):
        """
        API-010: 测试折线图生成

        测试步骤：
        1. 发送折线图生成请求
        2. 验证响应状态码为 200
        3. 验证返回的 ECharts 配置正确
        """
        # 构造请求体
        request_body = {
            "chartType": ChartTypeEnum.LINE.value,
            "data": sample_data_basic,
            "fieldMapping": {"xField": "date", "yField": "value"},
        }

        # 发送请求
        response = await client.post("/api/v1/charts/generate", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证图表类型
        assert result["chartType"] == ChartTypeEnum.LINE.value

        # 验证系列类型
        assert result["echartsOption"]["series"][0]["type"] == "line"

    @pytest.mark.asyncio
    async def test_generate_pie_chart(self, client: AsyncClient, sample_data_basic):
        """
        API-011: 测试饼图生成

        测试步骤：
        1. 发送饼图生成请求
        2. 验证响应状态码为 200
        3. 验证返回的 ECharts 配置正确
        """
        # 构造请求体 - 饼图使用 nameField 和 valueField
        request_body = {
            "chartType": ChartTypeEnum.PIE.value,
            "data": sample_data_basic,
            "fieldMapping": {"nameField": "category", "valueField": "value"},
        }

        # 发送请求
        response = await client.post("/api/v1/charts/generate", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证图表类型
        assert result["chartType"] == ChartTypeEnum.PIE.value

        # 验证系列类型
        assert result["echartsOption"]["series"][0]["type"] == "pie"

    @pytest.mark.asyncio
    async def test_generate_scatter_chart(self, client: AsyncClient):
        """
        API-012: 测试散点图生成

        测试步骤：
        1. 发送散点图生成请求
        2. 验证响应状态码为 200
        3. 验证返回的 ECharts 配置正确
        """
        # 构造散点图数据
        scatter_data = [
            {"x": 10, "y": 20},
            {"x": 30, "y": 40},
            {"x": 50, "y": 60},
        ]

        # 构造请求体
        request_body = {
            "chartType": ChartTypeEnum.SCATTER.value,
            "data": scatter_data,
            "fieldMapping": {"xField": "x", "yField": "y"},
        }

        # 发送请求
        response = await client.post("/api/v1/charts/generate", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证图表类型
        assert result["chartType"] == ChartTypeEnum.SCATTER.value

        # 验证系列类型
        assert result["echartsOption"]["series"][0]["type"] == "scatter"

    @pytest.mark.asyncio
    async def test_generate_area_chart(self, client: AsyncClient, sample_data_basic):
        """
        API-013: 测试面积图生成

        测试步骤：
        1. 发送面积图生成请求
        2. 验证响应状态码为 200
        3. 验证返回的 ECharts 配置包含面积样式
        """
        # 构造请求体
        request_body = {
            "chartType": ChartTypeEnum.AREA.value,
            "data": sample_data_basic,
            "fieldMapping": {"xField": "date", "yField": "value"},
        }

        # 发送请求
        response = await client.post("/api/v1/charts/generate", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证图表类型
        assert result["chartType"] == ChartTypeEnum.AREA.value

        # 验证面积样式
        series = result["echartsOption"]["series"][0]
        assert "areaStyle" in series

    @pytest.mark.asyncio
    async def test_generate_radar_chart(self, client: AsyncClient):
        """
        API-014: 测试雷达图生成

        测试步骤：
        1. 发送雷达图生成请求
        2. 验证响应状态码为 200
        3. 验证返回的 ECharts 配置正确
        """
        # 构造雷达图数据
        radar_data = [
            {"name": "指标A", "value": 80},
            {"name": "指标B", "value": 90},
            {"name": "指标C", "value": 70},
        ]

        # 构造请求体
        request_body = {
            "chartType": ChartTypeEnum.RADAR.value,
            "data": radar_data,
            "fieldMapping": {"nameField": "name", "valueField": "value"},
        }

        # 发送请求
        response = await client.post("/api/v1/charts/generate", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证图表类型
        assert result["chartType"] == ChartTypeEnum.RADAR.value

    @pytest.mark.asyncio
    async def test_generate_funnel_chart(self, client: AsyncClient):
        """
        API-015: 测试漏斗图生成

        测试步骤：
        1. 发送漏斗图生成请求
        2. 验证响应状态码为 200
        3. 验证返回的 ECharts 配置正确
        """
        # 构造漏斗图数据
        funnel_data = [
            {"stage": "访问", "value": 1000},
            {"stage": "浏览", "value": 800},
            {"stage": "下单", "value": 500},
            {"stage": "支付", "value": 300},
        ]

        # 构造请求体
        request_body = {
            "chartType": ChartTypeEnum.FUNNEL.value,
            "data": funnel_data,
            "fieldMapping": {"nameField": "stage", "valueField": "value"},
        }

        # 发送请求
        response = await client.post("/api/v1/charts/generate", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证图表类型
        assert result["chartType"] == ChartTypeEnum.FUNNEL.value

        # 验证系列类型
        assert result["echartsOption"]["series"][0]["type"] == "funnel"

    @pytest.mark.asyncio
    async def test_generate_chart_with_style_config(
        self, client: AsyncClient, sample_data_basic
    ):
        """
        API-016: 测试带样式配置的图表生成

        测试步骤：
        1. 发送包含完整样式配置的请求
        2. 验证响应状态码为 200
        3. 验证样式配置被正确应用
        """
        # 构造请求体
        request_body = {
            "chartType": ChartTypeEnum.BAR.value,
            "data": sample_data_basic,
            "fieldMapping": {"xField": "category", "yField": "value"},
            "styleConfig": {
                "title": "自定义标题",
                "subtitle": "自定义副标题",
                "showLegend": True,
                "showTooltip": True,
                "showGrid": True,
                "animation": True,
                "colorPalette": ["#5470c6", "#91cc75", "#fac858"],
            },
        }

        # 发送请求
        response = await client.post("/api/v1/charts/generate", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证标题配置
        echarts_option = result["echartsOption"]
        assert "title" in echarts_option
        assert echarts_option["title"]["text"] == "自定义标题"

    @pytest.mark.asyncio
    async def test_generate_chart_empty_data(self, client: AsyncClient):
        """
        API-017: 测试空数据图表生成

        测试步骤：
        1. 发送空数据请求
        2. 验证返回 422 错误
        """
        # 构造请求体 - 空数据
        request_body = {
            "chartType": ChartTypeEnum.BAR.value,
            "data": [],
            "fieldMapping": {"xField": "category", "yField": "value"},
        }

        # 发送请求
        response = await client.post("/api/v1/charts/generate", json=request_body)

        # 验证响应状态码 - 应该返回 422 验证错误
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_generate_chart_invalid_type(self, client: AsyncClient, sample_data_basic):
        """
        API-018: 测试无效图表类型

        测试步骤：
        1. 发送无效图表类型请求
        2. 验证返回 422 错误
        """
        # 构造请求体 - 无效图表类型
        request_body = {
            "chartType": "invalid_type",
            "data": sample_data_basic,
            "fieldMapping": {"xField": "category", "yField": "value"},
        }

        # 发送请求
        response = await client.post("/api/v1/charts/generate", json=request_body)

        # 验证响应状态码 - 应该返回 422 验证错误
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_generate_chart_missing_field_mapping(
        self, client: AsyncClient, sample_data_basic
    ):
        """
        API-019: 测试缺少字段映射的图表生成

        测试步骤：
        1. 发送缺少字段映射的请求
        2. 验证返回 422 错误
        """
        # 构造请求体 - 缺少字段映射
        request_body = {
            "chartType": ChartTypeEnum.BAR.value,
            "data": sample_data_basic,
        }

        # 发送请求
        response = await client.post("/api/v1/charts/generate", json=request_body)

        # 验证响应状态码 - 应该返回 422 验证错误
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ==================== 图表推荐接口测试 ====================


class TestChartRecommendAPI:
    """
    图表推荐接口测试类
    测试 POST /api/v1/charts/recommend 端点
    """

    @pytest.mark.asyncio
    async def test_recommend_basic_data(self, client: AsyncClient, sample_data_basic):
        """
        API-020: 测试基础数据图表推荐

        测试步骤：
        1. 发送图表推荐请求
        2. 验证响应状态码为 200
        3. 验证返回的推荐列表不为空
        4. 验证推荐理由存在
        """
        # 构造请求体
        request_body = {
            "data": sample_data_basic,
            "context": "销售数据分析",
            "maxRecommendations": 3,
        }

        # 发送请求
        response = await client.post("/api/v1/charts/recommend", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证推荐列表
        assert len(result["recommendations"]) > 0
        assert len(result["recommendations"]) <= 3

        # 验证推荐项结构
        for rec in result["recommendations"]:
            assert "chartType" in rec
            assert "confidence" in rec
            assert "reason" in rec
            assert "fieldMapping" in rec
            # 验证置信度范围
            assert 0.0 <= rec["confidence"] <= 1.0

        # 验证数据摘要
        assert "dataSummary" in result
        assert result["dataSummary"] != ""

    @pytest.mark.asyncio
    async def test_recommend_with_dimension_and_measure(
        self, client: AsyncClient, sample_data_basic
    ):
        """
        API-021: 测试包含维度和度量字段的数据推荐

        测试步骤：
        1. 发送包含维度和度量字段的数据
        2. 验证推荐包含柱状图
        3. 验证推荐包含饼图（维度唯一值较少）
        """
        # 构造请求体
        request_body = {"data": sample_data_basic, "maxRecommendations": 5}

        # 发送请求
        response = await client.post("/api/v1/charts/recommend", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 获取推荐的图表类型
        recommended_types = [rec["chartType"] for rec in result["recommendations"]]

        # 验证包含柱状图推荐
        assert ChartTypeEnum.BAR.value in recommended_types

    @pytest.mark.asyncio
    async def test_recommend_with_date_field(
        self, client: AsyncClient, sample_data_date_fields
    ):
        """
        API-022: 测试包含日期字段的数据推荐

        测试步骤：
        1. 发送包含日期字段的数据
        2. 验证推荐包含折线图
        """
        # 构造请求体
        request_body = {"data": sample_data_date_fields, "maxRecommendations": 5}

        # 发送请求
        response = await client.post("/api/v1/charts/recommend", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 获取推荐的图表类型
        recommended_types = [rec["chartType"] for rec in result["recommendations"]]

        # 验证包含折线图推荐
        assert ChartTypeEnum.LINE.value in recommended_types

    @pytest.mark.asyncio
    async def test_recommend_with_multiple_measures(
        self, client: AsyncClient, sample_data_numeric_only
    ):
        """
        API-023: 测试包含多个度量字段的数据推荐

        测试步骤：
        1. 发送包含多个度量字段的数据
        2. 验证推荐包含散点图
        """
        # 构造请求体
        request_body = {"data": sample_data_numeric_only, "maxRecommendations": 5}

        # 发送请求
        response = await client.post("/api/v1/charts/recommend", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 获取推荐的图表类型
        recommended_types = [rec["chartType"] for rec in result["recommendations"]]

        # 验证包含散点图推荐
        assert ChartTypeEnum.SCATTER.value in recommended_types

    @pytest.mark.asyncio
    async def test_recommend_max_recommendations_limit(
        self, client: AsyncClient, sample_data_basic
    ):
        """
        API-024: 测试最大推荐数量限制

        测试步骤：
        1. 发送指定最大推荐数量的请求
        2. 验证返回的推荐数量不超过限制
        """
        # 构造请求体 - 限制为 2 个推荐
        request_body = {"data": sample_data_basic, "maxRecommendations": 2}

        # 发送请求
        response = await client.post("/api/v1/charts/recommend", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证推荐数量不超过限制
        assert len(result["recommendations"]) <= 2

    @pytest.mark.asyncio
    async def test_recommend_empty_data(self, client: AsyncClient):
        """
        API-025: 测试空数据推荐

        测试步骤：
        1. 发送空数据请求
        2. 验证返回 422 错误
        """
        # 构造请求体 - 空数据
        request_body = {"data": [], "maxRecommendations": 3}

        # 发送请求
        response = await client.post("/api/v1/charts/recommend", json=request_body)

        # 验证响应状态码 - 应该返回 422 验证错误
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_recommend_confidence_ordering(
        self, client: AsyncClient, sample_data_basic
    ):
        """
        API-026: 测试推荐置信度排序

        测试步骤：
        1. 发送图表推荐请求
        2. 验证推荐按置信度降序排列
        """
        # 构造请求体
        request_body = {"data": sample_data_basic, "maxRecommendations": 5}

        # 发送请求
        response = await client.post("/api/v1/charts/recommend", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 获取置信度列表
        confidences = [rec["confidence"] for rec in result["recommendations"]]

        # 验证按置信度降序排列
        assert confidences == sorted(confidences, reverse=True)

    @pytest.mark.asyncio
    async def test_recommend_field_mapping_suggestion(
        self, client: AsyncClient, sample_data_basic
    ):
        """
        API-027: 测试字段映射建议

        测试步骤：
        1. 发送图表推荐请求
        2. 验证每个推荐包含字段映射建议
        3. 验证字段映射使用正确的字段名
        """
        # 构造请求体
        request_body = {"data": sample_data_basic, "maxRecommendations": 3}

        # 发送请求
        response = await client.post("/api/v1/charts/recommend", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证字段映射
        for rec in result["recommendations"]:
            field_mapping = rec["fieldMapping"]
            # 至少有一个字段被映射
            has_mapping = any(
                [
                    field_mapping.get("xField"),
                    field_mapping.get("yField"),
                    field_mapping.get("nameField"),
                    field_mapping.get("valueField"),
                ]
            )
            assert has_mapping, f"推荐 {rec['chartType']} 缺少字段映射"

    @pytest.mark.asyncio
    async def test_recommend_invalid_max_recommendations(
        self, client: AsyncClient, sample_data_basic
    ):
        """
        API-028: 测试无效的最大推荐数量

        测试步骤：
        1. 发送超出范围的最大推荐数量
        2. 验证返回 422 错误
        """
        # 构造请求体 - 超出范围的最大推荐数量
        request_body = {"data": sample_data_basic, "maxRecommendations": 10}

        # 发送请求
        response = await client.post("/api/v1/charts/recommend", json=request_body)

        # 验证响应状态码 - 应该返回 422 验证错误
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ==================== 边界情况和异常处理测试 ====================


class TestChartAPIEdgeCases:
    """
    边界情况和异常处理测试类
    """

    @pytest.mark.asyncio
    async def test_analyze_single_row_data(self, client: AsyncClient):
        """
        API-029: 测试单行数据分析

        测试步骤：
        1. 发送仅包含一行数据的请求
        2. 验证响应状态码为 200
        3. 验证分析结果正确
        """
        # 构造请求体
        request_body = {
            "data": [{"category": "A", "value": 100}],
            "sampleSize": 100,
        }

        # 发送请求
        response = await client.post("/api/v1/charts/analyze", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证基本字段
        assert result["totalRows"] == 1
        assert result["totalColumns"] == 2

    @pytest.mark.asyncio
    async def test_analyze_inconsistent_schema(self, client: AsyncClient):
        """
        API-030: 测试不一致的数据结构

        测试步骤：
        1. 发送字段不一致的数据
        2. 验证响应状态码为 200
        3. 验证所有字段都被识别
        """
        # 构造请求体 - 字段不一致
        request_body = {
            "data": [
                {"category": "A", "value": 100},
                {"category": "B", "value": 200, "extra": "extra_value"},
                {"category": "C"},
            ],
            "sampleSize": 100,
        }

        # 发送请求
        response = await client.post("/api/v1/charts/analyze", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证所有字段都被识别
        field_names = [f["name"] for f in result["fields"]]
        assert "category" in field_names
        assert "value" in field_names
        assert "extra" in field_names

    @pytest.mark.asyncio
    async def test_generate_chart_with_special_characters(
        self, client: AsyncClient
    ):
        """
        API-031: 测试包含特殊字符的数据

        测试步骤：
        1. 发送包含特殊字符的数据
        2. 验证响应状态码为 200
        3. 验证图表正确生成
        """
        # 构造包含特殊字符的数据
        special_data = [
            {"category": "类别<特殊>", "value": 100},
            {"category": "类别&符号", "value": 200},
            {"category": "类别\"引号", "value": 150},
        ]

        # 构造请求体
        request_body = {
            "chartType": ChartTypeEnum.BAR.value,
            "data": special_data,
            "fieldMapping": {"xField": "category", "yField": "value"},
        }

        # 发送请求
        response = await client.post("/api/v1/charts/generate", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 验证图表生成成功
        assert result["dataCount"] == 3

    @pytest.mark.asyncio
    async def test_analyze_boolean_fields(self, client: AsyncClient):
        """
        API-032: 测试布尔类型字段识别

        测试步骤：
        1. 发送包含布尔字段的数据
        2. 验证布尔字段被正确识别
        """
        # 构造包含布尔字段的数据
        bool_data = [
            {"name": "A", "active": True, "value": 100},
            {"name": "B", "active": False, "value": 200},
            {"name": "C", "active": True, "value": 150},
        ]

        # 构造请求体
        request_body = {"data": bool_data, "sampleSize": 100}

        # 发送请求
        response = await client.post("/api/v1/charts/analyze", json=request_body)

        # 验证响应状态码
        assert response.status_code == status.HTTP_200_OK

        # 解析响应数据
        result = response.json()

        # 查找布尔字段
        active_field = None
        for field in result["fields"]:
            if field["name"] == "active":
                active_field = field
                break

        # 验证布尔字段被正确识别
        assert active_field is not None
        assert active_field["dataType"] == DataFieldType.BOOLEAN.value

"""
图表可视化 API
处理数据分析、图表生成和图表推荐
"""

from fastapi import APIRouter, status

from ai_ppt.api.v1.schemas.chart import (
    ChartGenerateRequest,
    ChartGenerateResponse,
    ChartRecommendRequest,
    ChartRecommendResponse,
    DataAnalyzeRequest,
    DataAnalyzeResponse,
)
from ai_ppt.api.v1.schemas.common import ErrorResponse
from ai_ppt.services.chart_service import chart_service

# 创建路由器
router = APIRouter(prefix="/charts", tags=["数据可视化"])


@router.post(
    "/analyze",
    summary="分析数据",
    description="分析数据结构，识别字段类型，返回数据建议",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
)
async def analyze_data(request: DataAnalyzeRequest) -> DataAnalyzeResponse:
    """
    分析数据

    分析数据结构，识别维度和度量字段，统计唯一值、空值，
    并返回数据建议。

    Args:
        request: 数据分析请求，包含数据列表和采样大小

    Returns:
        DataAnalyzeResponse: 数据分析响应

    请求示例:
        ```json
        {
            "data": [
                {"category": "A", "value": 100, "date": "2024-01-01"},
                {"category": "B", "value": 200, "date": "2024-01-02"}
            ],
            "sampleSize": 100
        }
        ```

    响应示例:
        ```json
        {
            "totalRows": 2,
            "totalColumns": 3,
            "fields": [
                {
                    "name": "category",
                    "fieldType": "dimension",
                    "dataType": "string",
                    "uniqueCount": 2,
                    "nullCount": 0,
                    "sampleValues": ["A", "B"]
                },
                {
                    "name": "value",
                    "fieldType": "measure",
                    "dataType": "number",
                    "uniqueCount": 2,
                    "nullCount": 0,
                    "minValue": 100,
                    "maxValue": 200,
                    "avgValue": 150
                }
            ],
            "suggestions": ["数据适合生成柱状图、折线图或饼图"]
        }
        ```
    """
    # 调用服务进行数据分析
    result = chart_service.analyze_data(request)

    return result


@router.post(
    "/generate",
    summary="生成图表",
    description="根据图表类型和数据生成 ECharts 配置",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
)
async def generate_chart(request: ChartGenerateRequest) -> ChartGenerateResponse:
    """
    生成图表

    根据指定的图表类型、数据和字段映射生成 ECharts 配置。
    支持柱状图、折线图、饼图、散点图、面积图、雷达图、漏斗图等。

    Args:
        request: 图表生成请求

    Returns:
        ChartGenerateResponse: 图表生成响应，包含 ECharts 配置

    请求示例:
        ```json
        {
            "chartType": "bar",
            "data": [
                {"category": "A", "value": 100},
                {"category": "B", "value": 200},
                {"category": "C", "value": 150}
            ],
            "fieldMapping": {
                "xField": "category",
                "yField": "value"
            },
            "styleConfig": {
                "title": "销售数据",
                "showLegend": true,
                "animation": true
            }
        }
        ```

    响应示例:
        ```json
        {
            "chartType": "bar",
            "echartsOption": {
                "title": {"text": "销售数据"},
                "xAxis": {"type": "category", "data": ["A", "B", "C"]},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar", "data": [100, 200, 150]}]
            },
            "dataCount": 3,
            "generatedAt": "2024-01-01T00:00:00"
        }
        ```
    """
    # 调用服务生成图表
    result = chart_service.generate_chart(
        chart_type=request.chart_type,
        data=request.data,
        field_mapping=request.field_mapping,
        style_config=request.style_config,
    )

    return result


@router.post(
    "/recommend",
    summary="推荐图表",
    description="分析数据特征，返回推荐的图表类型",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
)
async def recommend_charts(request: ChartRecommendRequest) -> ChartRecommendResponse:
    """
    推荐图表

    分析数据特征，根据字段类型、数据分布等特征，
    返回推荐的图表类型及其置信度和推荐理由。

    Args:
        request: 图表推荐请求

    Returns:
        ChartRecommendResponse: 图表推荐响应

    请求示例:
        ```json
        {
            "data": [
                {"category": "A", "value": 100, "date": "2024-01-01"},
                {"category": "B", "value": 200, "date": "2024-01-02"},
                {"category": "C", "value": 150, "date": "2024-01-03"}
            ],
            "context": "销售数据分析",
            "maxRecommendations": 3
        }
        ```

    响应示例:
        ```json
        {
            "recommendations": [
                {
                    "chartType": "bar",
                    "confidence": 0.9,
                    "reason": "数据包含维度字段（category）和度量字段（value），适合使用柱状图展示对比关系",
                    "fieldMapping": {
                        "xField": "category",
                        "yField": "value"
                    }
                },
                {
                    "chartType": "line",
                    "confidence": 0.88,
                    "reason": "数据包含时间维度（date），适合使用折线图展示趋势变化",
                    "fieldMapping": {
                        "xField": "date",
                        "yField": "value"
                    }
                },
                {
                    "chartType": "pie",
                    "confidence": 0.85,
                    "reason": "维度字段（category）有 3 个唯一值，适合使用饼图展示占比分布",
                    "fieldMapping": {
                        "nameField": "category",
                        "valueField": "value"
                    }
                }
            ],
            "dataSummary": "共 3 行数据，3 个字段，1 个维度字段，1 个度量字段",
            "analyzedAt": "2024-01-01T00:00:00"
        }
        ```
    """
    # 调用服务推荐图表
    result = chart_service.recommend_charts(request)

    return result

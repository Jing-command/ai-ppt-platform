"""
连接器 Schema 定义
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConnectorBase(BaseModel):
    """连接器基础模型"""

    name: str = Field(..., min_length=1, max_length=100, description="连接器名称")
    type: str = Field(
        ..., description="连接类型: mysql, postgresql, mongodb, csv, api, etc."
    )
    description: Optional[str] = Field(None, max_length=500, description="描述")


class ConnectorCreate(ConnectorBase):
    """创建连接器请求"""

    config: Dict[str, Any] = Field(..., description="连接配置参数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "销售数据库",
                "type": "mysql",
                "description": "连接销售数据MySQL数据库",
                "config": {
                    "host": "localhost",
                    "port": 3306,
                    "database": "sales",
                    "username": "readonly",
                    "password": "***",
                },
            }
        }
    )


class ConnectorUpdate(BaseModel):
    """更新连接器请求"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = Field(None, alias="isActive")

    model_config = ConfigDict(populate_by_name=True)


class ConnectorResponse(ConnectorBase):
    """连接器响应"""

    id: UUID
    user_id: UUID = Field(..., alias="userId")
    config: Dict[str, Any] = Field(
        default_factory=dict, description="配置(敏感信息脱敏)"
    )
    is_active: bool = Field(default=True, alias="isActive")
    last_tested_at: Optional[datetime] = Field(None, alias="lastTestedAt")
    last_test_status: Optional[str] = Field(
        None, alias="lastTestStatus", description="last_test_status: success, failed"
    )
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(populate_by_name=True)


class ConnectorDetailResponse(ConnectorResponse):
    """连接器详情响应"""


class ConnectorTestRequest(BaseModel):
    """测试连接请求"""

    config: Optional[Dict[str, Any]] = None


class ConnectorTestResponse(BaseModel):
    """测试连接响应"""

    success: bool
    message: str
    latency_ms: Optional[int] = Field(
        None, alias="latencyMs", description="连接延迟毫秒"
    )
    server_version: Optional[str] = Field(None, alias="serverVersion")
    error_details: Optional[str] = Field(None, alias="errorDetails")

    model_config = ConfigDict(populate_by_name=True)


class DatabaseColumn(BaseModel):
    """数据库列信息"""

    name: str
    type: str
    is_nullable: bool = Field(default=True, alias="isNullable")
    is_primary_key: bool = Field(default=False, alias="isPrimaryKey")
    default_value: Optional[str] = Field(None, alias="defaultValue")
    comment: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class DatabaseTable(BaseModel):
    """数据库表信息"""

    name: str
    schema_: Optional[str] = Field(default=None, alias="schema")
    comment: Optional[str] = None
    columns: List[DatabaseColumn] = Field(default_factory=list)
    row_count: Optional[int] = Field(None, alias="rowCount")

    model_config = ConfigDict(populate_by_name=True)


class ConnectorSchemaResponse(BaseModel):
    """连接器数据结构响应"""

    connector_id: UUID = Field(..., alias="connectorId")
    tables: List[DatabaseTable]
    views: Optional[List[DatabaseTable]] = None

    model_config = ConfigDict(populate_by_name=True)


class ConnectorQueryRequest(BaseModel):
    """执行查询请求"""

    query: str = Field(..., min_length=1, description="SQL 查询或查询语句")
    params: Optional[Dict[str, Any]] = Field(None, description="查询参数")
    limit: int = Field(default=100, ge=1, le=10000, description="结果行数限制")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "SELECT * FROM sales WHERE date >= :start_date LIMIT 100",
                "params": {"start_date": "2024-01-01"},
                "limit": 100,
            }
        }
    )


class QueryResultColumn(BaseModel):
    """查询结果列信息"""

    name: str
    type: str


class ConnectorQueryResponse(BaseModel):
    """查询执行响应"""

    success: bool
    columns: List[QueryResultColumn]
    rows: List[Dict[str, Any]]
    row_count: int = Field(..., alias="rowCount")
    execution_time_ms: int = Field(..., alias="executionTimeMs")
    query: str

    model_config = ConfigDict(populate_by_name=True)

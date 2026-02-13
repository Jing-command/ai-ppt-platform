"""
连接器管理 API
处理数据源连接器的 CRUD 操作
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.api.deps import get_current_user
from ai_ppt.api.v1.schemas.common import ErrorResponse, PaginatedResponse, PaginationParams
from ai_ppt.api.v1.schemas.connector import (
    ConnectorCreate,
    ConnectorDetailResponse,
    ConnectorQueryRequest,
    ConnectorQueryResponse,
    ConnectorResponse,
    ConnectorSchemaResponse,
    ConnectorTestRequest,
    ConnectorTestResponse,
    ConnectorUpdate,
)
from ai_ppt.database import get_db
from ai_ppt.models.user import User
from ai_ppt.application.services.connector_service import (
    ConnectorService,
    ConnectorNotFoundError,
    ConnectorNameExistsError,
)

router = APIRouter(prefix="/connectors", tags=["连接器管理"])


def get_connector_service(db: AsyncSession = Depends(get_db)) -> ConnectorService:
    """获取连接器服务实例"""
    return ConnectorService(db)


@router.get(
    "",
    response_model=PaginatedResponse[ConnectorResponse],
    summary="获取连接器列表",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        500: {"model": ErrorResponse, "description": "服务器错误"}
    }
)
async def list_connectors(
    pagination: PaginationParams = Depends(),
    connector_type: str = None,
    current_user: User = Depends(get_current_user),
    service: ConnectorService = Depends(get_connector_service),
):
    """
    获取当前用户的连接器列表
    
    - **page**: 页码，默认 1
    - **pageSize**: 每页数量，默认 20
    - **connector_type**: 可选，按类型过滤 (mysql, postgresql, mongodb 等)
    """
    skip = (pagination.page - 1) * pagination.page_size
    connectors, total = await service.get_connectors(
        user_id=current_user.id,
        skip=skip,
        limit=pagination.page_size,
        connector_type=connector_type,
    )
    
    total_pages = (total + pagination.page_size - 1) // pagination.page_size
    
    return {
        "data": connectors,
        "meta": {
            "page": pagination.page,
            "pageSize": pagination.page_size,
            "total": total,
            "totalPages": total_pages,
        }
    }


@router.post(
    "",
    response_model=ConnectorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建连接器",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        409: {"model": ErrorResponse, "description": "名称已存在"}
    }
)
async def create_connector(
    data: ConnectorCreate,
    current_user: User = Depends(get_current_user),
    service: ConnectorService = Depends(get_connector_service),
):
    """
    创建新的数据源连接器
    
    - **name**: 连接器名称
    - **type**: 连接类型 (mysql, postgresql, mongodb, csv, api)
    - **config**: 连接配置（主机、端口、认证信息等）
    - **description**: 可选，描述信息
    """
    try:
        connector = await service.create_connector(
            data=data,
            user_id=current_user.id,
        )
        return connector
    except ConnectorNameExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "NAME_EXISTS", "message": "连接器名称已存在"}
        )


@router.get(
    "/{connector_id}",
    response_model=ConnectorDetailResponse,
    summary="获取连接器详情",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "连接器不存在"}
    }
)
async def get_connector(
    connector_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ConnectorService = Depends(get_connector_service),
):
    """
    获取指定连接器的详细信息
    
    - **connector_id**: 连接器 UUID
    """
    try:
        connector = await service.get_connector(
            connector_id=connector_id,
            user_id=current_user.id,
        )
        return connector
    except ConnectorNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "连接器不存在"}
        )


@router.put(
    "/{connector_id}",
    response_model=ConnectorResponse,
    summary="更新连接器",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "连接器不存在"},
        409: {"model": ErrorResponse, "description": "名称已存在"}
    }
)
async def update_connector(
    connector_id: UUID,
    data: ConnectorUpdate,
    current_user: User = Depends(get_current_user),
    service: ConnectorService = Depends(get_connector_service),
):
    """
    更新连接器配置
    
    - **connector_id**: 连接器 UUID
    - **name**: 可选，新名称
    - **config**: 可选，新的连接配置
    - **is_active**: 可选，是否激活
    """
    try:
        connector = await service.update_connector(
            connector_id=connector_id,
            data=data,
            user_id=current_user.id,
        )
        return connector
    except ConnectorNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "连接器不存在"}
        )
    except ConnectorNameExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "NAME_EXISTS", "message": "连接器名称已存在"}
        )


@router.delete(
    "/{connector_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除连接器",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "连接器不存在"}
    }
)
async def delete_connector(
    connector_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ConnectorService = Depends(get_connector_service),
):
    """
    删除指定的连接器
    
    - **connector_id**: 连接器 UUID
    """
    try:
        await service.delete_connector(
            connector_id=connector_id,
            user_id=current_user.id,
        )
    except ConnectorNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "连接器不存在"}
        )


@router.post(
    "/{connector_id}/test",
    response_model=ConnectorTestResponse,
    summary="测试连接",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "连接器不存在"}
    }
)
async def test_connector(
    connector_id: UUID,
    data: ConnectorTestRequest | None = None,
    current_user: User = Depends(get_current_user),
    service: ConnectorService = Depends(get_connector_service),
):
    """
    测试数据源连接
    
    - **connector_id**: 连接器 UUID
    - **config**: 可选，临时配置用于测试（不提供则使用保存的配置）
    
    返回连接延迟、服务器版本等信息
    """
    try:
        result = await service.test_connector(
            connector_id=connector_id,
            user_id=current_user.id,
            test_config=data.config if data else None,
        )
        return result
    except ConnectorNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "连接器不存在"}
        )


@router.get(
    "/{connector_id}/schema",
    response_model=ConnectorSchemaResponse,
    summary="获取数据源结构",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "连接器不存在"},
        502: {"model": ErrorResponse, "description": "连接失败"}
    }
)
async def get_connector_schema(
    connector_id: UUID,
    refresh: bool = False,
    current_user: User = Depends(get_current_user),
    service: ConnectorService = Depends(get_connector_service),
):
    """
    获取数据源的表结构和字段信息
    
    - **connector_id**: 连接器 UUID
    - **refresh**: 是否刷新缓存的结构信息
    
    返回表列表、列信息、数据类型等
    """
    # TODO: 实现获取数据源结构
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={"code": "NOT_IMPLEMENTED", "message": "获取数据源结构待实现"}
    )


@router.post(
    "/{connector_id}/query",
    response_model=ConnectorQueryResponse,
    summary="执行查询",
    responses={
        400: {"model": ErrorResponse, "description": "查询语法错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "连接器不存在"},
        502: {"model": ErrorResponse, "description": "查询执行失败"}
    }
)
async def execute_query(
    connector_id: UUID,
    data: ConnectorQueryRequest,
    current_user: User = Depends(get_current_user),
    service: ConnectorService = Depends(get_connector_service),
):
    """
    在数据源上执行查询
    
    - **connector_id**: 连接器 UUID
    - **query**: SQL 查询语句或查询表达式
    - **params**: 可选，查询参数
    - **limit**: 结果行数限制，默认 100
    
    支持参数化查询，如 `SELECT * FROM table WHERE id = :id`
    """
    # TODO: 实现执行查询
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={"code": "NOT_IMPLEMENTED", "message": "执行查询待实现"}
    )

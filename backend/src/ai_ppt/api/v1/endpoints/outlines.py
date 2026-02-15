"""
大纲管理 API - 完整实现版
处理 PPT 大纲的 CRUD 和 AI 生成
"""

from typing import Any, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.api.deps import get_current_user
from ai_ppt.api.v1.schemas.common import (
    ErrorResponse,
    PaginatedResponse,
    PaginationParams,
)
from ai_ppt.api.v1.schemas.outline import (
    OutlineCreate,
    OutlineDetailResponse,
    OutlineGenerateRequest,
    OutlineGenerateResponse,
    OutlineResponse,
    OutlineToPresentationRequest,
    OutlineToPresentationResponse,
    OutlineUpdate,
)
from ai_ppt.database import get_db
from ai_ppt.models.user import User
from ai_ppt.services.outline_service import OutlineService

router = APIRouter(prefix="/outlines", tags=["大纲管理"])


def _outline_to_response(outline: Any) -> dict:
    """将 Outline 模型转换为响应字典"""
    return {
        "id": outline.id,
        "userId": outline.user_id,
        "title": outline.title,
        "description": outline.description,
        "pages": outline.pages or [],
        "background": outline.background,
        "totalSlides": outline.total_slides,
        "status": outline.status,
        "aiPrompt": outline.ai_prompt,
        "aiParameters": outline.ai_parameters,
        "createdAt": outline.created_at,
        "updatedAt": outline.updated_at,
        "generatedAt": outline.generated_at,
    }


@router.get(
    "",
    response_model=PaginatedResponse[OutlineResponse],
    summary="获取大纲列表",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
)
async def list_outlines(
    pagination: PaginationParams = Depends(),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    获取当前用户的大纲列表

    - **page**: 页码，默认 1
    - **pageSize**: 每页数量，默认 20
    - **status**: 可选，按状态过滤 (draft, generating, completed, archived)
    """
    service = OutlineService(db)
    outlines, total = await service.get_by_user(
        user_id=current_user.id,
        page=pagination.page,
        page_size=pagination.page_size,
        status=status,
    )

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return {
        "data": [_outline_to_response(o) for o in outlines],
        "meta": {
            "page": pagination.page,
            "pageSize": pagination.page_size,
            "total": total,
            "totalPages": total_pages,
        },
    }


@router.post(
    "",
    response_model=OutlineResponse,
    status_code=status.HTTP_201_CREATED,
    summary="手动创建大纲",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
    },
)
async def create_outline(
    data: OutlineCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    手动创建 PPT 大纲

    - **title**: 大纲标题
    - **description**: 可选，描述信息
    - **pages**: 页面列表，包含标题、内容、页面类型、插图提示词
    - **background**: 可选，背景设置
    """
    service = OutlineService(db)

    outline = await service.create_from_schema(
        user_id=current_user.id,
        data=data.model_dump(by_alias=True),
    )

    return _outline_to_response(outline)


@router.post(
    "/generate",
    response_model=OutlineGenerateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="AI 生成大纲",
    responses={
        400: {"model": ErrorResponse, "description": "提示词过短或参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        429: {"model": ErrorResponse, "description": "请求过于频繁"},
    },
)
async def generate_outline(
    data: OutlineGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    使用 AI 自动生成 PPT 大纲

    - **prompt**: 主题描述（10-2000 字符）
    - **numSlides**: PPT总页数，默认 10，范围 3-50
    - **language**: 语言，zh 或 en
    - **style**: 风格 (business, education, creative, technical)
    - **contextData**: 可选，上下文数据
    - **connectorId**: 可选，关联数据源 ID

    返回生成的结果（同步生成，直接返回完整大纲）
    """
    service = OutlineService(db)

    try:
        outline = await service.generate(
            user_id=current_user.id,
            prompt=data.prompt,
            num_slides=data.num_slides,
            language=data.language,
            style=data.style,
            context_data=data.context_data,
            connector_id=data.connector_id,
        )

        return OutlineGenerateResponse(
            taskId=outline.id,
            status="completed",
            estimatedTime=0,
            message="大纲生成成功",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "GENERATION_FAILED",
                "message": f"生成大纲失败: {str(e)}",
            },
        )


@router.get(
    "/{outline_id}",
    response_model=OutlineDetailResponse,
    summary="获取大纲详情",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "大纲不存在"},
    },
)
async def get_outline(
    outline_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    获取大纲详情

    - **outline_id**: 大纲 UUID
    """
    service = OutlineService(db)

    try:
        outline = await service.get_by_id_or_raise(outline_id, current_user.id)
        return _outline_to_response(outline)
    except Exception as e:
        if "无权访问" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "无权访问此大纲"},
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "大纲不存在"},
        )


@router.put(
    "/{outline_id}",
    response_model=OutlineResponse,
    summary="更新大纲",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "大纲不存在"},
    },
)
async def update_outline(
    outline_id: UUID,
    data: OutlineUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    更新大纲内容

    - **outline_id**: 大纲 UUID
    - **title**: 可选，新标题
    - **description**: 可选，新描述
    - **pages**: 可选，新的页面列表
    - **background**: 可选，新的背景设置
    - **status**: 可选，新状态
    """
    service = OutlineService(db)

    try:
        outline = await service.update(
            outline_id=outline_id,
            user_id=current_user.id,
            data=data.model_dump(by_alias=True, exclude_none=True),
        )
        return _outline_to_response(outline)
    except Exception as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "大纲不存在"},
            )
        if "无权访问" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "无权访问此大纲"},
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "UPDATE_FAILED", "message": f"更新失败: {str(e)}"},
        )


@router.delete(
    "/{outline_id}",
    summary="删除大纲",
    responses={
        200: {"description": "删除成功"},
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "大纲不存在"},
    },
)
async def delete_outline(
    outline_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    删除指定大纲

    - **outline_id**: 大纲 UUID
    """
    service = OutlineService(db)

    try:
        await service.delete(outline_id, current_user.id)
    except Exception as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "大纲不存在"},
            )
        if "无权访问" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "无权访问此大纲"},
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "DELETE_FAILED", "message": f"删除失败: {str(e)}"},
        )


@router.post(
    "/{outline_id}/presentations",
    response_model=OutlineToPresentationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="基于大纲创建 PPT",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "大纲不存在"},
    },
)
async def create_presentation_from_outline(
    outline_id: UUID,
    data: OutlineToPresentationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    基于大纲创建完整的 PPT

    - **outline_id**: 大纲 UUID
    - **title**: 可选，自定义 PPT 标题（默认使用大纲标题）
    - **templateId**: 可选，模板 ID
    - **theme**: 可选，主题风格
    - **slideLayout**: 幻灯片布局 (auto, detailed, minimal)
    - **generateContent**: 是否使用 AI 生成详细内容
    - **provider**: 可选，指定 AI 提供商

    返回 PPT ID 和生成任务信息
    """
    service = OutlineService(db)

    # 验证大纲存在
    try:
        _ = await service.get_by_id_or_raise(outline_id, current_user.id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "大纲不存在"},
        )

    # TODO: 实现基于大纲创建 PPT 的功能
    # 这里返回模拟响应
    presentation_id = uuid4()
    task_id = uuid4()

    return OutlineToPresentationResponse(
        presentationId=presentation_id,
        taskId=task_id,
        status="pending",
        message="PPT 生成任务已提交",
        estimatedTime=60,
    )

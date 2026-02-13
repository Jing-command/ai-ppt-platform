"""
PPT 管理 API
处理 PPT 演示文稿的 CRUD 操作
"""

from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.api.deps import get_current_user
from ai_ppt.api.v1.schemas.common import (
    ErrorResponse,
    PaginatedResponse,
    PaginationParams,
)
from ai_ppt.api.v1.schemas.presentation import (
    GenerateRequest,
    GenerateResponse,
    PresentationCreate,
    PresentationDetailResponse,
    PresentationResponse,
    PresentationUpdate,
    SlideCreate,
    SlideUpdate,
)
from ai_ppt.api.v1.schemas.slide import UndoRedoResponse
from ai_ppt.application.services.presentation_service import (
    PresentationNotFoundError,
    PresentationService,
)
from ai_ppt.application.services.slide_service import SlideService, UndoRedoError
from ai_ppt.database import get_db
from ai_ppt.models.user import User

router = APIRouter(prefix="/presentations", tags=["PPT 管理"])


def get_presentation_service(db: AsyncSession = Depends(get_db)) -> PresentationService:
    """获取演示文稿服务"""
    return PresentationService(db)


def get_slide_service(db: AsyncSession = Depends(get_db)) -> SlideService:
    """获取幻灯片服务"""
    return SlideService(db)


@router.get(
    "",
    response_model=PaginatedResponse[PresentationResponse],
    summary="获取 PPT 列表",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
)
async def list_presentations(
    pagination: PaginationParams = Depends(),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: PresentationService = Depends(get_presentation_service),
) -> Any:
    """
    获取当前用户的 PPT 列表

    - **page**: 页码，默认 1
    - **pageSize**: 每页数量，默认 20
    - **status**: 可选，按状态过滤 (draft, published, archived)
    """
    presentations, total = await service.get_by_user(
        user_id=current_user.id,
        page=pagination.page,
        page_size=pagination.page_size,
        status=status,
    )

    # 计算总页数
    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return {
        "data": presentations,
        "meta": {
            "page": pagination.page,
            "pageSize": pagination.page_size,
            "total": total,
            "totalPages": total_pages,
        },
    }


@router.post(
    "",
    response_model=PresentationDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建 PPT",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
    },
)
async def create_presentation(
    data: PresentationCreate,
    current_user: User = Depends(get_current_user),
    service: PresentationService = Depends(get_presentation_service),
) -> Any:
    """
    创建新的 PPT 演示文稿

    - **title**: PPT 标题
    - **description**: 可选，描述信息
    - **templateId**: 可选，模板 ID
    - **outlineId**: 可选，关联的大纲 ID
    - **slides**: 可选，初始幻灯片列表
    """
    presentation = await service.create(
        data=data,
        user_id=current_user.id,
    )

    return presentation


@router.get(
    "/{presentation_id}",
    response_model=PresentationDetailResponse,
    summary="获取 PPT 详情",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "PPT 不存在"},
    },
)
async def get_presentation(
    presentation_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PresentationService = Depends(get_presentation_service),
) -> Any:
    """
    获取 PPT 详情（包含所有幻灯片）

    - **presentation_id**: PPT UUID
    """
    presentation = await service.get_by_id(presentation_id, current_user.id)

    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"},
        )

    return presentation


@router.put(
    "/{presentation_id}",
    response_model=PresentationDetailResponse,
    summary="更新 PPT",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "PPT 不存在"},
    },
)
async def update_presentation(
    presentation_id: UUID,
    data: PresentationUpdate,
    current_user: User = Depends(get_current_user),
    service: PresentationService = Depends(get_presentation_service),
) -> Any:
    """
    更新 PPT 信息

    - **presentation_id**: PPT UUID
    - **title**: 可选，新标题
    - **description**: 可选，新描述
    - **slides**: 可选，完整幻灯片列表（替换现有）
    - **status**: 可选，新状态
    - **templateId**: 可选，新模板
    """
    try:
        presentation = await service.update(
            presentation_id=presentation_id,
            user_id=current_user.id,
            data=data,
        )
        return presentation
    except PresentationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"},
        )


@router.delete(
    "/{presentation_id}",
    summary="删除 PPT",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "PPT 不存在"},
    },
)
async def delete_presentation(
    presentation_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PresentationService = Depends(get_presentation_service),
) -> Any:
    """
    删除指定 PPT

    - **presentation_id**: PPT UUID
    """
    success = await service.delete(presentation_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"},
        )

    return None


# ==================== 幻灯片操作 ====================


@router.post(
    "/{presentation_id}/slides",
    response_model=PresentationDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="添加幻灯片",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "PPT 不存在"},
    },
)
async def add_slide(
    presentation_id: UUID,
    data: SlideCreate,
    current_user: User = Depends(get_current_user),
    service: PresentationService = Depends(get_presentation_service),
) -> Any:
    """
    向 PPT 添加新幻灯片

    - **presentation_id**: PPT UUID
    - **type**: 幻灯片类型
    - **content**: 幻灯片内容
    - **layout**: 可选，布局配置
    - **position**: 可选，插入位置（默认末尾）

    返回更新后的完整 PPT
    """
    try:
        presentation = await service.add_slide(
            presentation_id=presentation_id,
            user_id=current_user.id,
            slide_data=data,
        )
        return presentation
    except PresentationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"},
        )


@router.put(
    "/{presentation_id}/slides/{slide_id}",
    response_model=PresentationDetailResponse,
    summary="更新幻灯片",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "幻灯片不存在"},
    },
)
async def update_slide(
    presentation_id: UUID,
    slide_id: UUID,
    data: SlideUpdate,
    current_user: User = Depends(get_current_user),
    service: PresentationService = Depends(get_presentation_service),
    slide_service: SlideService = Depends(get_slide_service),
) -> Any:
    """
    更新幻灯片内容（支持撤销/重做）

    - **presentation_id**: PPT UUID
    - **slide_id**: 幻灯片 ID
    - **type**: 可选，幻灯片类型
    - **content**: 可选，内容更新
    - **layout**: 可选，布局更新
    - **notes**: 可选，备注

    使用 Command 模式自动记录操作历史
    """
    try:
        # 使用 SlideService 更新并记录 Command
        await slide_service.update_slide(
            presentation_id=presentation_id,
            slide_id=slide_id,
            user_id=current_user.id,
            updates=data.model_dump(exclude_unset=True),
        )

        # 返回更新后的完整 PPT
        presentation = await service.get_by_id(presentation_id, current_user.id)
        return presentation
    except PresentationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"},
        )


@router.delete(
    "/{presentation_id}/slides/{slide_id}",
    response_model=PresentationDetailResponse,
    summary="删除幻灯片",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "幻灯片不存在"},
    },
)
async def delete_slide(
    presentation_id: UUID,
    slide_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PresentationService = Depends(get_presentation_service),
) -> Any:
    """
    删除幻灯片

    - **presentation_id**: PPT UUID
    - **slide_id**: 幻灯片 ID

    返回更新后的完整 PPT
    """
    success = await service.delete_slide(
        presentation_id=presentation_id,
        slide_id=slide_id,
        user_id=current_user.id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "幻灯片不存在"},
        )

    # 返回更新后的完整 PPT
    presentation = await service.get_by_id(presentation_id, current_user.id)
    return presentation


@router.post(
    "/{presentation_id}/slides/{slide_id}/undo",
    response_model=UndoRedoResponse,
    summary="撤销操作",
    responses={
        400: {"model": ErrorResponse, "description": "无可撤销的操作"},
        401: {"model": ErrorResponse, "description": "未认证"},
    },
)
async def undo_slide_operation(
    presentation_id: UUID,
    slide_id: UUID,
    current_user: User = Depends(get_current_user),
    slide_service: SlideService = Depends(get_slide_service),
) -> Any:
    """
    撤销对幻灯片的上一操作

    - **presentation_id**: PPT UUID
    - **slide_id**: 幻灯片 ID

    使用 Command 模式实现撤销功能
    """
    try:
        result = await slide_service.undo(
            presentation_id=presentation_id,
            slide_id=slide_id,
            user_id=current_user.id,
        )

        return UndoRedoResponse(
            success=result["success"],
            description=result["description"],
            state=result.get("state"),
            slideId=result["slide_id"],
        )
    except UndoRedoError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "CANNOT_UNDO", "message": str(e)},
        )


@router.post(
    "/{presentation_id}/slides/{slide_id}/redo",
    response_model=UndoRedoResponse,
    summary="重做操作",
    responses={
        400: {"model": ErrorResponse, "description": "无可重做的操作"},
        401: {"model": ErrorResponse, "description": "未认证"},
    },
)
async def redo_slide_operation(
    presentation_id: UUID,
    slide_id: UUID,
    current_user: User = Depends(get_current_user),
    slide_service: SlideService = Depends(get_slide_service),
) -> Any:
    """
    重做被撤销的操作

    - **presentation_id**: PPT UUID
    - **slide_id**: 幻灯片 ID

    使用 Command 模式实现重做功能
    """
    try:
        result = await slide_service.redo(
            presentation_id=presentation_id,
            slide_id=slide_id,
            user_id=current_user.id,
        )

        return UndoRedoResponse(
            success=result["success"],
            description=result["description"],
            state=result.get("state"),
            slideId=result["slide_id"],
        )
    except UndoRedoError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "CANNOT_REDO", "message": str(e)},
        )


# ==================== 直接生成 PPT（无大纲）====================


@router.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="AI 生成 PPT",
    responses={
        400: {"model": ErrorResponse, "description": "提示词过短或参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        429: {"model": ErrorResponse, "description": "请求过于频繁"},
    },
)
async def generate_presentation(
    data: GenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    直接使用 AI 生成 PPT（无需先创建大纲）

    - **prompt**: 生成提示词（10-2000 字符）
    - **templateId**: 可选，模板 ID
    - **numSlides**: 幻灯片数量，默认 10
    - **language**: 语言，zh 或 en
    - **style**: 风格 (business, education, creative, minimal)
    - **provider**: 可选，指定 AI 提供商

    返回异步任务 ID，使用 /generation/{task_id} 查询进度
    """
    # TODO: 实现服务层调用
    # service = get_ppt_generation_service(db)
    # task = await service.generate(
    #     user_id=current_user.id,
    #     prompt=data.prompt,
    #     template_id=data.template_id,
    #     num_slides=data.num_slides,
    #     language=data.language,
    #     style=data.style,
    #     provider=data.provider
    # )
    # return GenerateResponse(
    #     taskId=task.id,
    #     status=task.status,
    #     estimatedTime=task.estimated_seconds,
    #     message="PPT 生成任务已提交"
    # )

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={"code": "NOT_IMPLEMENTED", "message": "AI 生成功能待实现"},
    )

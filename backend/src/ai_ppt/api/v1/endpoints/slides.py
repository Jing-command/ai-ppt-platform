"""
幻灯片管理 API
处理单张幻灯片的编辑和撤销/重做操作
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.api.deps import get_current_user
from ai_ppt.api.v1.schemas.common import ErrorResponse
from ai_ppt.api.v1.schemas.presentation import SlideResponse, SlideUpdate
from ai_ppt.api.v1.schemas.slide import UndoRedoResponse
from ai_ppt.application.services.presentation_service import (
    PresentationNotFoundError,
    PresentationService,
    SlideNotFoundError,
)
from ai_ppt.application.services.slide_service import SlideService, UndoRedoError
from ai_ppt.database import get_db
from ai_ppt.models.user import User

router = APIRouter(prefix="/presentations/{ppt_id}/slides", tags=["幻灯片管理"])


def get_presentation_service(db: AsyncSession = Depends(get_db)) -> PresentationService:
    """获取演示文稿服务"""
    return PresentationService(db)


def get_slide_service(db: AsyncSession = Depends(get_db)) -> SlideService:
    """获取幻灯片服务"""
    return SlideService(db)


@router.get(
    "",
    response_model=List[SlideResponse],
    summary="获取幻灯片列表",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "PPT 不存在"},
    },
)
async def list_slides(
    ppt_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PresentationService = Depends(get_presentation_service),
) -> Any:
    """
    获取 PPT 的所有幻灯片

    - **ppt_id**: PPT UUID

    返回按顺序排列的幻灯片列表
    """
    slides = await service.get_slides(ppt_id, current_user.id)

    if slides is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"},
        )

    return slides


@router.get(
    "/{slide_id}",
    response_model=SlideResponse,
    summary="获取单个幻灯片",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "幻灯片不存在"},
    },
)
async def get_slide(
    ppt_id: UUID,
    slide_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PresentationService = Depends(get_presentation_service),
) -> Any:
    """
    获取指定幻灯片的详细信息

    - **ppt_id**: PPT UUID
    - **slide_id**: 幻灯片 ID
    """
    slide = await service.get_slide(ppt_id, slide_id, current_user.id)

    if not slide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "幻灯片不存在"},
        )

    return slide


@router.put(
    "/{slide_id}",
    response_model=SlideResponse,
    summary="更新幻灯片",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "幻灯片不存在"},
    },
)
async def update_slide(
    ppt_id: UUID,
    slide_id: UUID,
    data: SlideUpdate,
    current_user: User = Depends(get_current_user),
    service: PresentationService = Depends(get_presentation_service),
    slide_service: SlideService = Depends(get_slide_service),
) -> Any:
    """
    更新指定幻灯片（支持部分更新）

    - **ppt_id**: PPT UUID
    - **slide_id**: 幻灯片 ID
    - **type**: 可选，幻灯片类型
    - **content**: 可选，内容更新
    - **layout**: 可选，布局更新
    - **style**: 可选，样式更新
    - **notes**: 可选，备注

    支持增量更新，只更新提供的字段。
    使用 Command 模式自动记录操作历史用于撤销。
    """
    try:
        # 使用 SlideService 更新（包含 Command 记录）
        _ = await slide_service.update_slide(
            presentation_id=ppt_id,
            slide_id=slide_id,
            user_id=current_user.id,
            updates=data.model_dump(exclude_unset=True),
        )

        # 重新获取完整的 slide 对象返回
        slide = await service.get_slide(ppt_id, slide_id, current_user.id)
        return slide
    except PresentationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"},
        )
    except SlideNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "幻灯片不存在"},
        )


@router.delete(
    "/{slide_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除幻灯片",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "幻灯片不存在"},
    },
)
async def delete_slide(
    ppt_id: UUID,
    slide_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PresentationService = Depends(get_presentation_service),
) -> None:
    """
    删除指定幻灯片

    - **ppt_id**: PPT UUID
    - **slide_id**: 幻灯片 ID
    """
    success = await service.delete_slide(ppt_id, slide_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "幻灯片不存在"},
        )

    return None


# ==================== 撤销/重做 ====================


@router.post(
    "/{slide_id}/undo",
    response_model=UndoRedoResponse,
    summary="撤销操作",
    responses={
        400: {"model": ErrorResponse, "description": "无可撤销的操作"},
        401: {"model": ErrorResponse, "description": "未认证"},
    },
)
async def undo_slide_operation(
    ppt_id: UUID,
    slide_id: UUID,
    current_user: User = Depends(get_current_user),
    slide_service: SlideService = Depends(get_slide_service),
) -> UndoRedoResponse:
    """
    撤销对幻灯片的上一操作

    - **ppt_id**: PPT UUID
    - **slide_id**: 幻灯片 ID

    返回撤销后的幻灯片状态
    """
    try:
        result = await slide_service.undo(
            presentation_id=ppt_id,
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
    "/{slide_id}/redo",
    response_model=UndoRedoResponse,
    summary="重做操作",
    responses={
        400: {"model": ErrorResponse, "description": "无可重做的操作"},
        401: {"model": ErrorResponse, "description": "未认证"},
    },
)
async def redo_slide_operation(
    ppt_id: UUID,
    slide_id: UUID,
    current_user: User = Depends(get_current_user),
    slide_service: SlideService = Depends(get_slide_service),
) -> UndoRedoResponse:
    """
    重做被撤销的操作

    - **ppt_id**: PPT UUID
    - **slide_id**: 幻灯片 ID

    返回重做后的幻灯片状态
    """
    try:
        result = await slide_service.redo(
            presentation_id=ppt_id,
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

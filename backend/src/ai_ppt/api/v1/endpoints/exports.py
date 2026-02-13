"""
导出 API
处理 PPT 导出为各种格式的异步任务
"""
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.api.deps import get_current_user
from ai_ppt.api.v1.schemas.common import ErrorResponse
from ai_ppt.api.v1.schemas.export import ExportResponse, ExportStatusResponse
from ai_ppt.database import get_db
from ai_ppt.models.user import User
from ai_ppt.services.export_service import (
    ExportFormat,
    ExportService,
    process_export_task,
)

router = APIRouter(prefix="/exports", tags=["导出管理"])


def get_export_service(db: AsyncSession = Depends(get_db)) -> ExportService:
    """获取导出服务"""
    return ExportService(db)


@router.post(
    "/pptx",
    response_model=ExportResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="导出 PPTX",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "PPT 不存在"},
    },
)
async def export_pptx(
    presentation_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: ExportService = Depends(get_export_service),
    quality: str = "standard",
    slide_range: str = "all",
    include_notes: bool = False,
) -> Any:
    """
    提交 PPTX 导出任务

    - **presentation_id**: PPT ID
    - **quality**: 导出质量 (standard, high)
    - **slide_range**: 可选，页面范围如 "1-5" 或 "all"
    - **include_notes**: 是否包含演讲者备注

    返回任务 ID，使用 /exports/{task_id}/status 查询进度
    """
    # 验证 PPT 存在
    from ai_ppt.application.services.presentation_service import PresentationService

    ppt_service = PresentationService(db)
    presentation = await ppt_service.get_by_id(presentation_id, current_user.id)

    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"},
        )

    # 创建导出任务
    task = await service.create_task(
        user_id=current_user.id,
        presentation_id=presentation_id,
        format=ExportFormat.PPTX,
        quality=quality,
        slide_range=slide_range,
        include_notes=include_notes,
    )

    # 启动后台任务
    background_tasks.add_task(process_export_task, task.id)

    return ExportResponse(
        taskId=task.id,
        status=task.status.value,
        downloadUrl=None,
        fileSize=None,
        expiresAt=None,
        createdAt=task.created_at,
    )


@router.post(
    "/pdf",
    response_model=ExportResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="导出 PDF",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "PPT 不存在"},
    },
)
async def export_pdf(
    presentation_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: ExportService = Depends(get_export_service),
    quality: str = "standard",
    slide_range: str = "all",
    include_notes: bool = False,
) -> Any:
    """
    提交 PDF 导出任务

    - **presentation_id**: PPT ID
    - **quality**: 导出质量 (standard, high)
    - **slide_range**: 可选，页面范围
    - **include_notes**: 是否包含演讲者备注

    返回任务 ID，使用 /exports/{task_id}/status 查询进度
    """
    # 验证 PPT 存在
    from ai_ppt.application.services.presentation_service import PresentationService

    ppt_service = PresentationService(db)
    presentation = await ppt_service.get_by_id(presentation_id, current_user.id)

    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"},
        )

    # 创建导出任务
    task = await service.create_task(
        user_id=current_user.id,
        presentation_id=presentation_id,
        format=ExportFormat.PDF,
        quality=quality,
        slide_range=slide_range,
        include_notes=include_notes,
    )

    # 启动后台任务
    background_tasks.add_task(process_export_task, task.id)

    return ExportResponse(
        taskId=task.id,
        status=task.status.value,
        downloadUrl=None,
        fileSize=None,
        expiresAt=None,
        createdAt=task.created_at,
    )


@router.post(
    "/images",
    response_model=ExportResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="导出图片",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "PPT 不存在"},
    },
)
async def export_images(
    presentation_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: ExportService = Depends(get_export_service),
    format: str = "png",
    quality: str = "standard",
    slide_range: str = "all",
) -> Any:
    """
    提交图片导出任务（每页一张图片，打包为 zip）

    - **presentation_id**: PPT ID
    - **format**: 图片格式 (png, jpg)
    - **quality**: 导出质量 (standard, high)
    - **slide_range**: 可选，页面范围

    返回任务 ID，使用 /exports/{task_id}/status 查询进度
    """
    # 验证格式
    if format not in ("png", "jpg"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_FORMAT", "message": "格式必须是 png 或 jpg"},
        )

    # 验证 PPT 存在
    from ai_ppt.application.services.presentation_service import PresentationService

    ppt_service = PresentationService(db)
    presentation = await ppt_service.get_by_id(presentation_id, current_user.id)

    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"},
        )

    # 创建导出任务
    export_format = ExportFormat.PNG if format == "png" else ExportFormat.JPG
    task = await service.create_task(
        user_id=current_user.id,
        presentation_id=presentation_id,
        format=export_format,
        quality=quality,
        slide_range=slide_range,
        include_notes=False,
    )

    # 启动后台任务
    background_tasks.add_task(process_export_task, task.id)

    return ExportResponse(
        taskId=task.id,
        status=task.status.value,
        downloadUrl=None,
        fileSize=None,
        expiresAt=None,
        createdAt=task.created_at,
    )


@router.get(
    "/{task_id}/status",
    response_model=ExportStatusResponse,
    summary="查询导出状态",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "任务不存在"},
    },
)
async def get_export_status(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> Any:
    """
    查询导出任务状态

    - **task_id**: 导出任务 UUID

    状态包括：pending, processing, completed, failed
    completed 时返回 downloadUrl
    """
    task = await service.get_task(task_id, current_user.id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "导出任务不存在"},
        )

    # 构建下载 URL（如果已完成）
    download_url = None
    if task.status.value == "completed" and task.file_path:
        download_url = f"/api/v1/exports/{task_id}/download"

    return ExportStatusResponse(
        taskId=task.id,
        presentationId=task.presentation_id,
        format=task.format.value,
        status=task.status.value,
        progress=task.progress,
        filePath=task.file_path,
        fileSize=task.file_size,
        errorMessage=task.error_message,
        downloadUrl=download_url,
        expiresAt=task.expires_at,
        createdAt=task.created_at,
        completedAt=task.completed_at,
    )


@router.get(
    "/{task_id}/download",
    summary="下载导出文件",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "文件不存在"},
        410: {"model": ErrorResponse, "description": "文件已过期"},
    },
)
async def download_export(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> Any:
    """
    下载导出的文件

    - **task_id**: 导出任务 UUID

    文件完成且未过期时返回文件内容
    支持流式下载大文件
    """
    task = await service.get_task(task_id, current_user.id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "导出任务不存在"},
        )

    if task.status.value != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "NOT_COMPLETED", "message": "导出任务尚未完成"},
        )

    # 检查文件是否过期
    if task.expires_at and task.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={"code": "EXPIRED", "message": "文件下载链接已过期"},
        )

    # 检查文件路径是否存在
    if not task.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "FILE_NOT_FOUND", "message": "导出文件不存在"},
        )

    file_path = service.get_full_path(task.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "FILE_NOT_FOUND", "message": "导出文件不存在"},
        )

    # 确定 MIME 类型和文件名
    mime_types = {
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # noqa: E501
        "pdf": "application/pdf",
        "png": "application/zip",
        "jpg": "application/zip",
    }

    mime_type = mime_types.get(task.format.value, "application/octet-stream")

    # 构建友好的文件名
    extensions = {
        "pptx": "pptx",
        "pdf": "pdf",
        "png": "zip",
        "jpg": "zip",
    }
    filename = f"presentation.{extensions.get(task.format.value, task.format.value)}"

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=mime_type,
    )

"""
大纲应用服务 - 更新版
协调数据查询、AI 生成和持久化
"""

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.domain.models.outline import Outline, OutlineStatus
from ai_ppt.services.outline_generation import OutlineGenerationService


class OutlineServiceError(Exception):
    """大纲服务错误基类"""


class OutlineNotFoundError(OutlineServiceError):
    """大纲不存在错误"""


class OutlinePermissionError(OutlineServiceError):
    """权限错误"""


class OutlineService:
    """
    大纲应用服务

    提供大纲的 CRUD 操作和 AI 生成功能
    """

    def __init__(
        self,
        db_session: AsyncSession,
        generation_service: Optional[OutlineGenerationService] = None,
    ) -> None:
        """
        初始化服务

        Args:
            db_session: 数据库会话
            generation_service: 生成服务，如未提供则自动创建
        """
        self._db = db_session
        self._generation_service = generation_service

    async def get_by_id(
        self, outline_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[Outline]:
        """
        根据 ID 获取大纲

        Args:
            outline_id: 大纲ID
            user_id: 可选，验证用户权限

        Returns:
            Outline 或 None
        """
        result = await self._db.execute(select(Outline).where(Outline.id == outline_id))
        outline = result.scalar_one_or_none()

        if outline and user_id and outline.user_id != user_id:
            raise OutlinePermissionError("无权访问此大纲")

        return outline

    async def get_by_id_or_raise(
        self, outline_id: UUID, user_id: Optional[UUID] = None
    ) -> Outline:
        """
        根据 ID 获取大纲，不存在则抛出异常

        Args:
            outline_id: 大纲ID
            user_id: 可选，验证用户权限

        Returns:
            Outline

        Raises:
            OutlineNotFoundError: 大纲不存在
            OutlinePermissionError: 无权访问
        """
        outline = await self.get_by_id(outline_id, user_id)
        if not outline:
            raise OutlineNotFoundError(f"大纲 {outline_id} 不存在")
        return outline

    async def get_by_user(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
    ) -> tuple[list[Outline], int]:
        """
        获取用户的大纲列表

        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            status: 可选，状态过滤

        Returns:
            (大纲列表, 总数)
        """
        # 构建查询
        query = select(Outline).where(Outline.user_id == user_id)
        count_query = (
            select(func.count()).select_from(Outline).where(Outline.user_id == user_id)
        )

        if status:
            query = query.where(Outline.status == status)
            count_query = count_query.where(Outline.status == status)

        # 获取总数
        count_result = await self._db.execute(count_query)
        total = count_result.scalar() or 0

        # 分页获取数据
        query = query.order_by(Outline.updated_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self._db.execute(query)
        outlines = list(result.scalars().all())

        return outlines, total

    async def create(
        self,
        user_id: UUID,
        title: str,
        description: Optional[str] = None,
        pages: Optional[list[dict[str, Any]]] = None,
        background: Optional[dict[str, Any]] = None,
    ) -> Outline:
        """
        手动创建大纲

        Args:
            user_id: 用户ID
            title: 标题
            description: 描述
            pages: 页面列表
            background: 背景设置

        Returns:
            创建的 Outline
        """
        outline = Outline(
            title=title,
            description=description,
            user_id=user_id,
            pages=pages or [],
            background=background,
            status=OutlineStatus.DRAFT.value,
        )

        if pages:
            outline.total_slides = len(pages)

        self._db.add(outline)
        await self._db.flush()
        await self._db.refresh(outline)

        return outline

    async def create_from_schema(self, user_id: UUID, data: dict[str, Any]) -> Outline:
        """
        从 Schema 数据创建大纲

        Args:
            user_id: 用户ID
            data: 包含 title, description, pages, background 的数据

        Returns:
            创建的 Outline
        """
        # 处理 pages，可能是 dict 列表或 Pydantic 模型列表
        pages_data = data.get("pages", [])
        processed_pages = []
        for p in pages_data:
            if hasattr(p, "model_dump"):
                processed_pages.append(p.model_dump(by_alias=True))
            else:
                processed_pages.append(p)

        # 处理 background
        bg_data = data.get("background")
        processed_bg = None
        if bg_data is not None:
            if hasattr(bg_data, "model_dump"):
                processed_bg = bg_data.model_dump()
            else:
                processed_bg = bg_data

        return await self.create(
            user_id=user_id,
            title=data["title"],
            description=data.get("description"),
            pages=processed_pages,
            background=processed_bg,
        )

    async def update(
        self,
        outline_id: UUID,
        user_id: UUID,
        data: dict[str, Any],
    ) -> Outline:
        """
        更新大纲

        Args:
            outline_id: 大纲ID
            user_id: 用户ID（权限验证）
            data: 更新数据

        Returns:
            更新后的 Outline

        Raises:
            OutlineNotFoundError: 大纲不存在
            OutlinePermissionError: 无权访问
        """
        outline = await self.get_by_id_or_raise(outline_id, user_id)

        # 更新字段
        if "title" in data and data["title"] is not None:
            outline.title = data["title"]

        if "description" in data:
            outline.description = data["description"]

        if "pages" in data and data["pages"] is not None:
            pages = data["pages"]
            if isinstance(pages, list):
                # 如果是 Pydantic 模型列表，转换为字典
                if pages and hasattr(pages[0], "model_dump"):
                    pages = [p.model_dump(by_alias=True) for p in pages]
                outline.pages = pages
                outline.total_slides = len(pages)

        if "background" in data:
            bg = data["background"]
            if bg is None:
                outline.background = None
            elif hasattr(bg, "model_dump"):
                outline.background = bg.model_dump()
            else:
                outline.background = bg

        if "status" in data and data["status"] is not None:
            outline.status = data["status"]

        await self._db.flush()
        await self._db.refresh(outline)

        return outline

    async def delete(self, outline_id: UUID, user_id: UUID) -> bool:
        """
        删除大纲

        Args:
            outline_id: 大纲ID
            user_id: 用户ID（权限验证）

        Returns:
            是否删除成功

        Raises:
            OutlineNotFoundError: 大纲不存在
            OutlinePermissionError: 无权访问
        """
        outline = await self.get_by_id_or_raise(outline_id, user_id)

        await self._db.delete(outline)
        await self._db.flush()

        return True

    async def generate(
        self,
        user_id: UUID,
        prompt: str,
        num_slides: int = 10,
        language: str = "zh",
        style: str = "business",
        context_data: Optional[dict[str, Any]] = None,
        connector_id: Optional[UUID] = None,
    ) -> Outline:
        """
        AI 生成大纲

        Args:
            user_id: 用户ID
            prompt: 主题描述
            num_slides: 幻灯片数量
            language: 语言
            style: 风格
            context_data: 上下文数据
            connector_id: 连接器ID

        Returns:
            生成的 Outline
        """
        # 创建生成中的大纲记录
        outline = Outline(
            title=prompt[:50] + "..." if len(prompt) > 50 else prompt,
            description=prompt,
            user_id=user_id,
            status=OutlineStatus.GENERATING.value,
            ai_prompt=prompt,
            ai_parameters={
                "num_slides": num_slides,
                "language": language,
                "style": style,
                "context_data": context_data,
                "connector_id": str(connector_id) if connector_id else None,
            },
        )

        self._db.add(outline)
        await self._db.flush()
        await self._db.refresh(outline)

        # 使用生成服务生成大纲内容
        if not self._generation_service:
            self._generation_service = OutlineGenerationService()

        try:
            # 生成内容
            result = await self._generation_service.generate_outline(
                topic=prompt,
                num_slides=num_slides,
                language=language,
                style=style,
                context_data=context_data,
            )

            # 更新大纲
            outline.title = result.get("title", outline.title)
            outline.description = result.get("description", outline.description)
            outline.pages = result.get("pages", [])
            outline.total_slides = len(result.get("pages", []))

            # 处理背景
            background_data = result.get("background")
            if background_data:
                outline.background = background_data

            outline.mark_as_completed()

            await self._db.flush()
            await self._db.refresh(outline)

        except Exception:
            # 生成失败，保持 generating 状态或标记为失败
            # 这里可以选择删除失败的记录或保留用于调试
            raise
        finally:
            await self._generation_service.close()

        return outline


# 依赖注入函数
async def get_outline_service(db: AsyncSession) -> OutlineService:
    """获取大纲服务实例（用于依赖注入）"""
    return OutlineService(db)

"""
演示文稿应用服务
处理 PPT 的 CRUD 操作和幻灯片管理
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.api.v1.schemas.presentation import (
    PresentationCreate,
    PresentationUpdate,
    SlideCreate,
    SlideUpdate,
)
from ai_ppt.domain.models.presentation import Presentation, PresentationStatus
from ai_ppt.domain.models.slide import Slide, SlideLayoutType
from ai_ppt.infrastructure.repositories.slide import SlideRepository


class PresentationServiceError(Exception):
    """演示文稿服务错误基类"""


class PresentationNotFoundError(PresentationServiceError):
    """演示文稿不存在错误"""


class SlideNotFoundError(PresentationServiceError):
    """幻灯片不存在错误"""


class PermissionDeniedError(PresentationServiceError):
    """权限不足错误"""


class PresentationService:
    """
    演示文稿应用服务

    协调 PPT 的 CRUD 操作：
    1. 创建 PPT
    2. 获取 PPT 列表和详情
    3. 更新 PPT 信息
    4. 删除 PPT
    5. 管理幻灯片

    使用示例:
        >>> service = PresentationService(db_session)
        >>> presentation = await service.create(
        ...     data=PresentationCreate(title="My PPT"),
        ...     user_id=user_id,
        ... )
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        初始化演示文稿服务

        Args:
            session: SQLAlchemy 异步会话
        """
        self._session = session
        self._slide_repo = SlideRepository(session)

    async def create(
        self,
        data: PresentationCreate,
        user_id: UUID,
    ) -> Presentation:
        """
        创建演示文稿

        Args:
            data: 创建数据
            user_id: 用户 ID

        Returns:
            创建的演示文稿实体
        """
        # 创建演示文稿
        presentation = Presentation(
            title=data.title,
            owner_id=user_id,
            description=data.description,
            theme=data.template_id or "default",
        )

        if data.outline_id:
            presentation.outline_id = data.outline_id

        self._session.add(presentation)
        await self._session.flush()
        await self._session.refresh(presentation)

        # 如果有初始幻灯片，创建它们
        if data.slides:
            for idx, slide_data in enumerate(data.slides):
                slide = self._create_slide_from_schema(
                    presentation_id=presentation.id,
                    slide_data=slide_data,
                    order_index=idx,
                )
                self._session.add(slide)

            await self._session.flush()
            await self._session.refresh(presentation)

        return presentation

    async def get_by_id(
        self,
        presentation_id: UUID,
        user_id: UUID,
    ) -> Optional[Presentation]:
        """
        获取演示文稿详情

        Args:
            presentation_id: PPT ID
            user_id: 用户 ID

        Returns:
            演示文稿实体，不存在则返回 None
        """
        stmt = select(Presentation).where(
            Presentation.id == presentation_id,
            Presentation.owner_id == user_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(
        self,
        presentation_id: UUID,
        user_id: UUID,
    ) -> Presentation:
        """
        获取演示文稿详情，不存在则抛出异常

        Args:
            presentation_id: PPT ID
            user_id: 用户 ID

        Returns:
            演示文稿实体

        Raises:
            PresentationNotFoundError: PPT 不存在
        """
        presentation = await self.get_by_id(presentation_id, user_id)
        if not presentation:
            raise PresentationNotFoundError(f"Presentation {presentation_id} not found")
        return presentation

    async def get_by_user(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
    ) -> tuple[list[Presentation], int]:
        """
        获取用户的 PPT 列表

        Args:
            user_id: 用户 ID
            page: 页码
            page_size: 每页数量
            status: 可选的状态过滤

        Returns:
            (PPT 列表, 总数量)
        """
        # 构建基础查询
        where_clause = Presentation.owner_id == user_id

        # 状态过滤
        if status:
            where_clause = where_clause & (Presentation.status == status)

        # 获取总数
        count_stmt = select(func.count()).select_from(Presentation).where(where_clause)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        # 获取分页数据
        stmt = (
            select(Presentation)
            .where(where_clause)
            .order_by(Presentation.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(stmt)
        presentations = list(result.scalars().all())

        return presentations, total

    async def update(
        self,
        presentation_id: UUID,
        user_id: UUID,
        data: PresentationUpdate,
    ) -> Presentation:
        """
        更新演示文稿

        Args:
            presentation_id: PPT ID
            user_id: 用户 ID
            data: 更新数据

        Returns:
            更新后的演示文稿实体

        Raises:
            PresentationNotFoundError: PPT 不存在
        """
        presentation = await self.get_by_id_or_raise(presentation_id, user_id)

        # 更新字段
        if data.title is not None:
            presentation.title = data.title

        if data.description is not None:
            presentation.description = data.description

        if data.status is not None:
            presentation.status = PresentationStatus(data.status)

        if data.template_id is not None:
            presentation.theme = data.template_id

        # 如果提供了完整的 slides 数组，替换现有幻灯片
        if data.slides is not None:
            # 删除现有幻灯片
            await self._slide_repo.delete_by_presentation(presentation_id)

            # 创建新幻灯片
            for idx, slide_data in enumerate(data.slides):
                slide = self._create_slide_from_schema(
                    presentation_id=presentation_id,
                    slide_data=slide_data,
                    order_index=idx,
                )
                self._session.add(slide)

        await self._session.flush()
        await self._session.refresh(presentation)

        return presentation

    async def delete(
        self,
        presentation_id: UUID,
        user_id: UUID,
    ) -> bool:
        """
        删除演示文稿

        Args:
            presentation_id: PPT ID
            user_id: 用户 ID

        Returns:
            是否成功删除
        """
        presentation = await self.get_by_id(presentation_id, user_id)
        if not presentation:
            return False

        await self._session.delete(presentation)
        await self._session.flush()

        return True

    async def add_slide(
        self,
        presentation_id: UUID,
        user_id: UUID,
        slide_data: SlideCreate,
    ) -> Presentation:
        """
        添加幻灯片到 PPT

        Args:
            presentation_id: PPT ID
            user_id: 用户 ID
            slide_data: 幻灯片数据

        Returns:
            更新后的演示文稿实体

        Raises:
            PresentationNotFoundError: PPT 不存在
        """
        presentation = await self.get_by_id_or_raise(presentation_id, user_id)

        # 计算 order_index
        if slide_data.position is not None:
            order_index = slide_data.position
        else:
            max_order = await self._slide_repo.get_max_order(presentation_id)
            order_index = max_order + 1

        # 创建幻灯片
        content_dict = slide_data.content.model_dump(by_alias=True, exclude_none=True)

        # 确定布局类型
        layout_type = SlideLayoutType.TITLE_CONTENT
        if slide_data.layout and slide_data.layout.type:
            try:
                layout_type = SlideLayoutType(slide_data.layout.type)
            except ValueError:
                pass  # 使用默认布局

        slide = Slide(
            title=content_dict.get("title", "Untitled"),
            presentation_id=presentation_id,
            layout_type=layout_type,
            order_index=order_index,
            content=content_dict,
            notes=slide_data.notes,
        )

        self._session.add(slide)
        await self._session.flush()
        await self._session.refresh(presentation)

        return presentation

    async def get_slides(
        self,
        presentation_id: UUID,
        user_id: UUID,
    ) -> Optional[list[Slide]]:
        """
        获取 PPT 的所有幻灯片

        Args:
            presentation_id: PPT ID
            user_id: 用户 ID

        Returns:
            幻灯片列表，如果 PPT 不存在则返回 None
        """
        # 先检查 PPT 是否存在且属于该用户
        presentation = await self.get_by_id(presentation_id, user_id)
        if not presentation:
            return None

        return await self._slide_repo.get_by_presentation(presentation_id)

    async def get_slide(
        self,
        presentation_id: UUID,
        slide_id: UUID,
        user_id: UUID,
    ) -> Optional[Slide]:
        """
        获取单个幻灯片

        Args:
            presentation_id: PPT ID
            slide_id: 幻灯片 ID
            user_id: 用户 ID

        Returns:
            幻灯片实体，不存在则返回 None
        """
        # 先检查 PPT 是否存在
        presentation = await self.get_by_id(presentation_id, user_id)
        if not presentation:
            return None

        slide = await self._slide_repo.get_by_id(slide_id)
        if not slide or slide.presentation_id != presentation_id:
            return None

        return slide

    async def update_slide(
        self,
        presentation_id: UUID,
        slide_id: UUID,
        user_id: UUID,
        data: SlideUpdate,
    ) -> Slide:
        """
        更新幻灯片

        Args:
            presentation_id: PPT ID
            slide_id: 幻灯片 ID
            user_id: 用户 ID
            data: 更新数据

        Returns:
            更新后的幻灯片实体

        Raises:
            PresentationNotFoundError: PPT 不存在
            SlideNotFoundError: 幻灯片不存在
        """
        # 检查 PPT 存在
        await self.get_by_id_or_raise(presentation_id, user_id)

        # 获取幻灯片
        slide = await self._slide_repo.get_by_id(slide_id)
        if not slide or slide.presentation_id != presentation_id:
            raise SlideNotFoundError(f"Slide {slide_id} not found")

        # 更新字段
        if data.type is not None:
            try:
                slide.layout_type = SlideLayoutType(data.type)
            except ValueError:
                pass

        if data.content is not None:
            content_dict = data.content.model_dump(by_alias=True, exclude_none=True)
            slide.update_content(content_dict)

            # 同步更新 title
            if content_dict.get("title"):
                slide.title = content_dict["title"]

        if data.notes is not None:
            slide.notes = data.notes

        if data.order_index is not None:
            slide.order_index = data.order_index

        await self._session.flush()
        await self._session.refresh(slide)

        return slide

    async def delete_slide(
        self,
        presentation_id: UUID,
        slide_id: UUID,
        user_id: UUID,
    ) -> bool:
        """
        删除幻灯片

        Args:
            presentation_id: PPT ID
            slide_id: 幻灯片 ID
            user_id: 用户 ID

        Returns:
            是否成功删除
        """
        # 检查 PPT 存在
        presentation = await self.get_by_id(presentation_id, user_id)
        if not presentation:
            return False

        # 获取幻灯片
        slide = await self._slide_repo.get_by_id(slide_id)
        if not slide or slide.presentation_id != presentation_id:
            return False

        await self._slide_repo.delete(slide_id)

        return True

    def _create_slide_from_schema(
        self,
        presentation_id: UUID,
        slide_data,
        order_index: int,
    ) -> Slide:
        """
        从 Schema 创建 Slide 实体

        Args:
            presentation_id: PPT ID
            slide_data: 幻灯片数据
            order_index: 排序索引

        Returns:
            Slide 实体
        """
        content_dict = {}
        if hasattr(slide_data, "content") and slide_data.content:
            content_dict = slide_data.content.model_dump(
                by_alias=True, exclude_none=True
            )

        # 确定布局类型
        layout_type = SlideLayoutType.TITLE_CONTENT
        if (
            hasattr(slide_data, "layout")
            and slide_data.layout
            and slide_data.layout.type
        ):
            try:
                layout_type = SlideLayoutType(slide_data.layout.type)
            except ValueError:
                pass

        title = content_dict.get("title", f"Slide {order_index + 1}")

        return Slide(
            title=title,
            presentation_id=presentation_id,
            layout_type=layout_type,
            order_index=order_index,
            content=content_dict,
            notes=getattr(slide_data, "notes", None),
        )

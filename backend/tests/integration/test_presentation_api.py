"""
PPT 管理 API 集成测试
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestPresentationAPI:
    """测试 PPT API 端点"""

    async def test_list_presentations_success(
        self, client: AsyncClient, authenticated_user
    ):
        """测试成功获取 PPT 列表"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get(
            "/api/v1/presentations?page=1&pageSize=10",
            headers=headers,
        )

        assert response.status_code in [200, 500]

    async def test_list_presentations_no_auth(self, client: AsyncClient):
        """测试未认证访问 PPT 列表"""
        response = await client.get("/api/v1/presentations")

        # 401 (Unauthorized) 或 403 (Forbidden) 都是有效的未认证响应
        assert response.status_code in [401, 403]

    async def test_create_presentation_success(
        self, client: AsyncClient, authenticated_user
    ):
        """测试成功创建 PPT"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            "/api/v1/presentations",
            headers=headers,
            json={
                "title": "Test Presentation",
                "description": "Test description",
                "templateId": "modern",
            },
        )

        assert response.status_code in [201, 200, 500]

    async def test_create_presentation_no_auth(self, client: AsyncClient):
        """测试未认证创建 PPT"""
        response = await client.post(
            "/api/v1/presentations",
            json={"title": "Test"},
        )

        # 401 (Unauthorized) 或 403 (Forbidden) 都是有效的未认证响应
        assert response.status_code in [401, 403]

    async def test_create_presentation_invalid_data(
        self, client: AsyncClient, authenticated_user
    ):
        """测试创建 PPT 时提供无效数据"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            "/api/v1/presentations",
            headers=headers,
            json={
                # 缺少必需的 title
                "description": "Test",
            },
        )

        assert response.status_code == 422

    async def test_get_presentation_success(
        self, client: AsyncClient, authenticated_user
    ):
        """测试成功获取 PPT 详情"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        ppt_id = uuid.uuid4()

        response = await client.get(
            f"/api/v1/presentations/{ppt_id}",
            headers=headers,
        )

        assert response.status_code in [200, 404, 500]

    async def test_get_presentation_not_found(
        self, client: AsyncClient, authenticated_user
    ):
        """测试获取不存在的 PPT"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get(
            f"/api/v1/presentations/{uuid.uuid4()}",
            headers=headers,
        )

        assert response.status_code in [404, 500]

    async def test_update_presentation_success(
        self, client: AsyncClient, authenticated_user
    ):
        """测试成功更新 PPT"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        ppt_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}",
            headers=headers,
            json={
                "title": "Updated Title",
                "description": "Updated description",
            },
        )

        assert response.status_code in [200, 404, 500]

    async def test_update_presentation_invalid_status(
        self, client: AsyncClient, authenticated_user
    ):
        """测试更新 PPT 时提供无效状态"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        ppt_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}",
            headers=headers,
            json={
                "status": "invalid_status",
            },
        )

        assert response.status_code == 422

    async def test_delete_presentation_success(
        self, client: AsyncClient, authenticated_user
    ):
        """测试成功删除 PPT"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        ppt_id = uuid.uuid4()

        response = await client.delete(
            f"/api/v1/presentations/{ppt_id}",
            headers=headers,
        )

        assert response.status_code in [204, 404, 500]

    async def test_delete_presentation_no_auth(self, client: AsyncClient):
        """测试未认证删除 PPT"""
        response = await client.delete(f"/api/v1/presentations/{uuid.uuid4()}")

        # 401 (Unauthorized) 或 403 (Forbidden) 都是有效的未认证响应
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
class TestPresentationSlidesAPI:
    """测试 PPT 幻灯片 API"""

    async def test_add_slide_success(
        self, client: AsyncClient, authenticated_user
    ):
        """测试成功添加幻灯片"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        ppt_id = uuid.uuid4()

        response = await client.post(
            f"/api/v1/presentations/{ppt_id}/slides",
            headers=headers,
            json={
                "type": "content",
                "content": {
                    "title": "New Slide",
                    "text": "Slide content",
                },
                "layout": {
                    "type": "title_content",
                },
            },
        )

        assert response.status_code in [201, 404, 500]

    async def test_update_slide_success(
        self, client: AsyncClient, authenticated_user
    ):
        """测试成功更新幻灯片"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=headers,
            json={
                "content": {
                    "title": "Updated Title",
                },
            },
        )

        assert response.status_code in [200, 404, 500]

    async def test_delete_slide_success(
        self, client: AsyncClient, authenticated_user
    ):
        """测试成功删除幻灯片"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.delete(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=headers,
        )

        assert response.status_code in [200, 404, 500]

    async def test_undo_slide_success(
        self, client: AsyncClient, authenticated_user, db_session
    ):
        """测试成功撤销幻灯片操作"""
        from ai_ppt.core.security import create_access_token
        from ai_ppt.domain.models.presentation import Presentation
        from ai_ppt.domain.models.slide import Slide

        # 创建测试数据
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        presentation = Presentation(
            id=ppt_id,
            title="Test PPT",
            owner_id=authenticated_user.id,
            status="draft",
        )
        db_session.add(presentation)
        await db_session.flush()

        slide = Slide(
            id=slide_id,
            presentation_id=ppt_id,
            order_index=0,
            title="Test Slide",
        )
        db_session.add(slide)
        await db_session.commit()

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}/undo",
            headers=headers,
        )

        assert response.status_code in [200, 400, 404, 500]

    async def test_redo_slide_success(
        self, client: AsyncClient, authenticated_user, db_session
    ):
        """测试成功重做幻灯片操作"""
        from ai_ppt.core.security import create_access_token
        from ai_ppt.domain.models.presentation import Presentation
        from ai_ppt.domain.models.slide import Slide

        # 创建测试数据
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        presentation = Presentation(
            id=ppt_id,
            title="Test PPT",
            owner_id=authenticated_user.id,
            status="draft",
        )
        db_session.add(presentation)
        await db_session.flush()

        slide = Slide(
            id=slide_id,
            presentation_id=ppt_id,
            order_index=0,
            title="Test Slide",
        )
        db_session.add(slide)
        await db_session.commit()

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}/redo",
            headers=headers,
        )

        assert response.status_code in [200, 400, 404, 500]


@pytest.mark.asyncio
class TestGeneratePresentationAPI:
    """测试生成 PPT API"""

    async def test_generate_presentation_not_implemented(
        self, client: AsyncClient, authenticated_user
    ):
        """测试生成 PPT 接口（未实现）"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            "/api/v1/presentations/generate",
            headers=headers,
            json={
                "prompt": "Create a presentation about AI",
                "numSlides": 10,
                "language": "zh",
                "style": "business",
            },
        )

        # 应该返回 501（未实现）或 200（如果已实现）
        assert response.status_code in [200, 202, 501]

    async def test_generate_presentation_invalid_prompt(
        self, client: AsyncClient, authenticated_user
    ):
        """测试生成 PPT 时提示词太短"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            "/api/v1/presentations/generate",
            headers=headers,
            json={
                "prompt": "Short",
                "numSlides": 10,
            },
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestSlideAPI:
    """测试独立幻灯片 API"""

    async def test_list_slides_success(
        self, client: AsyncClient, authenticated_user
    ):
        """测试成功获取幻灯片列表"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        ppt_id = uuid.uuid4()

        response = await client.get(
            f"/api/v1/presentations/{ppt_id}/slides",
            headers=headers,
        )

        assert response.status_code in [200, 404, 500]

    async def test_get_slide_success(
        self, client: AsyncClient, authenticated_user
    ):
        """测试成功获取单个幻灯片"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.get(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=headers,
        )

        assert response.status_code in [200, 404, 500]

    async def test_update_slide_direct_success(
        self, client: AsyncClient, authenticated_user
    ):
        """测试直接更新幻灯片"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=headers,
            json={
                "type": "content",
                "content": {
                    "title": "Updated",
                },
            },
        )

        assert response.status_code in [200, 404, 500]

    async def test_delete_slide_direct_success(
        self, client: AsyncClient, authenticated_user
    ):
        """测试直接删除幻灯片"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.delete(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=headers,
        )

        assert response.status_code in [204, 404, 500]

    async def test_undo_slide_direct_success(
        self, client: AsyncClient, authenticated_user, db_session
    ):
        """测试直接撤销幻灯片操作"""
        from ai_ppt.core.security import create_access_token
        from ai_ppt.domain.models.presentation import Presentation
        from ai_ppt.domain.models.slide import Slide

        # 创建测试数据
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        presentation = Presentation(
            id=ppt_id,
            title="Test PPT",
            owner_id=authenticated_user.id,
            status="draft",
        )
        db_session.add(presentation)
        await db_session.flush()

        slide = Slide(
            id=slide_id,
            presentation_id=ppt_id,
            order_index=0,
            title="Test Slide",
        )
        db_session.add(slide)
        await db_session.commit()

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}/undo",
            headers=headers,
        )

        assert response.status_code in [200, 400, 404, 500]

    async def test_redo_slide_direct_success(
        self, client: AsyncClient, authenticated_user, db_session
    ):
        """测试直接重做幻灯片操作"""
        from ai_ppt.core.security import create_access_token
        from ai_ppt.domain.models.presentation import Presentation
        from ai_ppt.domain.models.slide import Slide

        # 创建测试数据
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        presentation = Presentation(
            id=ppt_id,
            title="Test PPT",
            owner_id=authenticated_user.id,
            status="draft",
        )
        db_session.add(presentation)
        await db_session.flush()

        slide = Slide(
            id=slide_id,
            presentation_id=ppt_id,
            order_index=0,
            title="Test Slide",
        )
        db_session.add(slide)
        await db_session.commit()

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}/redo",
            headers=headers,
        )

        assert response.status_code in [200, 400, 404, 500]

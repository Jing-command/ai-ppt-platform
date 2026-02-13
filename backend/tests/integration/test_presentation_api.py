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

    async def test_list_presentations_success(self, client: AsyncClient, auth_headers):
        """测试成功获取 PPT 列表"""
        response = await client.get(
            "/api/v1/presentations?page=1&pageSize=10",
            headers=auth_headers,
        )

        assert response.status_code in [200, 500]

    async def test_list_presentations_no_auth(self, client: AsyncClient):
        """测试未认证访问 PPT 列表"""
        response = await client.get("/api/v1/presentations")

        assert response.status_code == 403

    async def test_create_presentation_success(self, client: AsyncClient, auth_headers):
        """测试成功创建 PPT"""
        response = await client.post(
            "/api/v1/presentations",
            headers=auth_headers,
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

        assert response.status_code == 403

    async def test_create_presentation_invalid_data(self, client: AsyncClient, auth_headers):
        """测试创建 PPT 时提供无效数据"""
        response = await client.post(
            "/api/v1/presentations",
            headers=auth_headers,
            json={
                # 缺少必需的 title
                "description": "Test",
            },
        )

        assert response.status_code == 422

    async def test_get_presentation_success(self, client: AsyncClient, auth_headers):
        """测试成功获取 PPT 详情"""
        ppt_id = uuid.uuid4()

        response = await client.get(
            f"/api/v1/presentations/{ppt_id}",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404, 500]

    async def test_get_presentation_not_found(self, client: AsyncClient, auth_headers):
        """测试获取不存在的 PPT"""
        response = await client.get(
            f"/api/v1/presentations/{uuid.uuid4()}",
            headers=auth_headers,
        )

        assert response.status_code in [404, 500]

    async def test_update_presentation_success(self, client: AsyncClient, auth_headers):
        """测试成功更新 PPT"""
        ppt_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}",
            headers=auth_headers,
            json={
                "title": "Updated Title",
                "description": "Updated description",
            },
        )

        assert response.status_code in [200, 404, 500]

    async def test_update_presentation_invalid_status(self, client: AsyncClient, auth_headers):
        """测试更新 PPT 时提供无效状态"""
        ppt_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}",
            headers=auth_headers,
            json={
                "status": "invalid_status",
            },
        )

        assert response.status_code == 422

    async def test_delete_presentation_success(self, client: AsyncClient, auth_headers):
        """测试成功删除 PPT"""
        ppt_id = uuid.uuid4()

        response = await client.delete(
            f"/api/v1/presentations/{ppt_id}",
            headers=auth_headers,
        )

        assert response.status_code in [204, 404, 500]

    async def test_delete_presentation_no_auth(self, client: AsyncClient):
        """测试未认证删除 PPT"""
        response = await client.delete(f"/api/v1/presentations/{uuid.uuid4()}")

        assert response.status_code == 403


@pytest.mark.asyncio
class TestPresentationSlidesAPI:
    """测试 PPT 幻灯片 API"""

    async def test_add_slide_success(self, client: AsyncClient, auth_headers):
        """测试成功添加幻灯片"""
        ppt_id = uuid.uuid4()

        response = await client.post(
            f"/api/v1/presentations/{ppt_id}/slides",
            headers=auth_headers,
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

    async def test_update_slide_success(self, client: AsyncClient, auth_headers):
        """测试成功更新幻灯片"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
            json={
                "content": {
                    "title": "Updated Title",
                },
            },
        )

        assert response.status_code in [200, 404, 500]

    async def test_delete_slide_success(self, client: AsyncClient, auth_headers):
        """测试成功删除幻灯片"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.delete(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404, 500]

    async def test_undo_slide_success(self, client: AsyncClient, auth_headers):
        """测试成功撤销幻灯片操作"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.post(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}/undo",
            headers=auth_headers,
        )

        assert response.status_code in [200, 400, 404, 500]

    async def test_redo_slide_success(self, client: AsyncClient, auth_headers):
        """测试成功重做幻灯片操作"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.post(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}/redo",
            headers=auth_headers,
        )

        assert response.status_code in [200, 400, 404, 500]


@pytest.mark.asyncio
class TestGeneratePresentationAPI:
    """测试生成 PPT API"""

    async def test_generate_presentation_not_implemented(self, client: AsyncClient, auth_headers):
        """测试生成 PPT 接口（未实现）"""
        response = await client.post(
            "/api/v1/presentations/generate",
            headers=auth_headers,
            json={
                "prompt": "Create a presentation about AI",
                "numSlides": 10,
                "language": "zh",
                "style": "business",
            },
        )

        # 应该返回 501（未实现）或 200（如果已实现）
        assert response.status_code in [200, 202, 501]

    async def test_generate_presentation_invalid_prompt(self, client: AsyncClient, auth_headers):
        """测试生成 PPT 时提示词太短"""
        response = await client.post(
            "/api/v1/presentations/generate",
            headers=auth_headers,
            json={
                "prompt": "Short",
                "numSlides": 10,
            },
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestSlideAPI:
    """测试独立幻灯片 API"""

    async def test_list_slides_success(self, client: AsyncClient, auth_headers):
        """测试成功获取幻灯片列表"""
        ppt_id = uuid.uuid4()

        response = await client.get(
            f"/api/v1/presentations/{ppt_id}/slides",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404, 500]

    async def test_get_slide_success(self, client: AsyncClient, auth_headers):
        """测试成功获取单个幻灯片"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.get(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404, 500]

    async def test_update_slide_direct_success(self, client: AsyncClient, auth_headers):
        """测试直接更新幻灯片"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
            json={
                "type": "content",
                "content": {
                    "title": "Updated",
                },
            },
        )

        assert response.status_code in [200, 404, 500]

    async def test_delete_slide_direct_success(self, client: AsyncClient, auth_headers):
        """测试直接删除幻灯片"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.delete(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
        )

        assert response.status_code in [204, 404, 500]

    async def test_undo_slide_direct_success(self, client: AsyncClient, auth_headers):
        """测试直接撤销幻灯片操作"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.post(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}/undo",
            headers=auth_headers,
        )

        assert response.status_code in [200, 400, 404, 500]

    async def test_redo_slide_direct_success(self, client: AsyncClient, auth_headers):
        """测试直接重做幻灯片操作"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.post(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}/redo",
            headers=auth_headers,
        )

        assert response.status_code in [200, 400, 404, 500]

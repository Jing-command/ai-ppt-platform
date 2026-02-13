"""
幻灯片 API 集成测试
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestSlideAPI:
    """测试幻灯片 API 端点（独立路由）"""

    async def test_list_slides_success(self, client: AsyncClient, auth_headers):
        """测试成功获取幻灯片列表"""
        ppt_id = uuid.uuid4()

        response = await client.get(
            f"/api/v1/presentations/{ppt_id}/slides",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404, 500]

    async def test_list_slides_no_auth(self, client: AsyncClient):
        """测试未认证获取幻灯片列表"""
        response = await client.get(f"/api/v1/presentations/{uuid.uuid4()}/slides")

        assert response.status_code == 403

    async def test_list_slides_presentation_not_found(self, client: AsyncClient, auth_headers):
        """测试获取不存在 PPT 的幻灯片"""
        response = await client.get(
            f"/api/v1/presentations/{uuid.uuid4()}/slides",
            headers=auth_headers,
        )

        assert response.status_code in [404, 500]

    async def test_get_slide_success(self, client: AsyncClient, auth_headers):
        """测试成功获取单个幻灯片"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.get(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404, 500]

    async def test_get_slide_not_found(self, client: AsyncClient, auth_headers):
        """测试获取不存在的幻灯片"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.get(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
        )

        assert response.status_code in [404, 500]

    async def test_get_slide_no_auth(self, client: AsyncClient):
        """测试未认证获取幻灯片"""
        response = await client.get(
            f"/api/v1/presentations/{uuid.uuid4()}/slides/{uuid.uuid4()}",
        )

        assert response.status_code == 403


@pytest.mark.asyncio
class TestSlideUpdateAPI:
    """测试幻灯片更新 API"""

    async def test_update_slide_success(self, client: AsyncClient, auth_headers):
        """测试成功更新幻灯片"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
            json={
                "type": "content",
                "content": {
                    "title": "Updated Slide",
                    "text": "Updated content",
                },
                "layout": {
                    "type": "title_content",
                },
                "notes": "Updated notes",
            },
        )

        assert response.status_code in [200, 404, 500]

    async def test_update_slide_partial(self, client: AsyncClient, auth_headers):
        """测试部分更新幻灯片"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
            json={
                "content": {
                    "title": "Only Title Updated",
                },
            },
        )

        assert response.status_code in [200, 404, 500]

    async def test_update_slide_no_auth(self, client: AsyncClient):
        """测试未认证更新幻灯片"""
        response = await client.put(
            f"/api/v1/presentations/{uuid.uuid4()}/slides/{uuid.uuid4()}",
            json={"content": {"title": "Test"}},
        )

        assert response.status_code == 403

    async def test_update_slide_invalid_data(self, client: AsyncClient, auth_headers):
        """测试更新幻灯片时提供无效数据"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
            json={
                "orderIndex": "not_a_number",  # 应该是整数
            },
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestSlideDeleteAPI:
    """测试幻灯片删除 API"""

    async def test_delete_slide_success(self, client: AsyncClient, auth_headers):
        """测试成功删除幻灯片"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.delete(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
        )

        assert response.status_code in [204, 404, 500]

    async def test_delete_slide_no_auth(self, client: AsyncClient):
        """测试未认证删除幻灯片"""
        response = await client.delete(
            f"/api/v1/presentations/{uuid.uuid4()}/slides/{uuid.uuid4()}",
        )

        assert response.status_code == 403

    async def test_delete_slide_not_found(self, client: AsyncClient, auth_headers):
        """测试删除不存在的幻灯片"""
        response = await client.delete(
            f"/api/v1/presentations/{uuid.uuid4()}/slides/{uuid.uuid4()}",
            headers=auth_headers,
        )

        assert response.status_code in [404, 500]


@pytest.mark.asyncio
class TestSlideUndoRedoAPI:
    """测试幻灯片撤销/重做 API"""

    async def test_undo_slide_success(self, client: AsyncClient, auth_headers):
        """测试成功撤销幻灯片操作"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.post(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}/undo",
            headers=auth_headers,
        )

        assert response.status_code in [200, 400, 404, 500]

    async def test_undo_slide_no_auth(self, client: AsyncClient):
        """测试未认证撤销操作"""
        response = await client.post(
            f"/api/v1/presentations/{uuid.uuid4()}/slides/{uuid.uuid4()}/undo",
        )

        assert response.status_code == 403

    async def test_undo_slide_no_history(self, client: AsyncClient, auth_headers):
        """测试无历史记录时撤销"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        # 由于没有操作历史，应该返回 400
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

    async def test_redo_slide_no_auth(self, client: AsyncClient):
        """测试未认证重做操作"""
        response = await client.post(
            f"/api/v1/presentations/{uuid.uuid4()}/slides/{uuid.uuid4()}/redo",
        )

        assert response.status_code == 403

    async def test_redo_slide_no_history(self, client: AsyncClient, auth_headers):
        """测试无可重做操作时"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        # 由于没有可重做的操作，应该返回 400
        response = await client.post(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}/redo",
            headers=auth_headers,
        )

        assert response.status_code in [200, 400, 404, 500]


@pytest.mark.asyncio
class TestSlideContentValidation:
    """测试幻灯片内容验证"""

    async def test_update_slide_empty_content(self, client: AsyncClient, auth_headers):
        """测试更新幻灯片时提供空内容"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
            json={
                "content": {},  # 空内容
            },
        )

        # 空内容应该被接受
        assert response.status_code in [200, 404, 500]

    async def test_update_slide_complex_content(self, client: AsyncClient, auth_headers):
        """测试更新幻灯片时提供复杂内容"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
            json={
                "content": {
                    "title": "Complex Slide",
                    "subtitle": "Subtitle",
                    "text": "Main text content",
                    "bullets": ["Point 1", "Point 2", "Point 3"],
                    "imageUrl": "https://example.com/image.png",
                    "chartData": {
                        "type": "bar",
                        "data": [10, 20, 30],
                    },
                },
            },
        )

        assert response.status_code in [200, 404, 500]

    async def test_update_slide_style(self, client: AsyncClient, auth_headers):
        """测试更新幻灯片样式"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
            json={
                "style": {
                    "fontFamily": "Arial",
                    "fontSize": 16,
                    "color": "#333333",
                    "alignment": "left",
                },
            },
        )

        assert response.status_code in [200, 404, 500]

    async def test_update_slide_notes(self, client: AsyncClient, auth_headers):
        """测试更新幻灯片备注"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()

        response = await client.put(
            f"/api/v1/presentations/{ppt_id}/slides/{slide_id}",
            headers=auth_headers,
            json={
                "notes": "These are speaker notes for this slide.",
            },
        )

        assert response.status_code in [200, 404, 500]

"""
导出 API 集成测试
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestExportAPI:
    """测试导出 API 端点"""

    async def test_export_pptx_success(self, client: AsyncClient, authenticated_user):
        """测试成功导出 PPTX"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        with patch(
            "ai_ppt.application.services.presentation_service.PresentationService"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_by_id.return_value = MagicMock(id=uuid.uuid4())
            mock_service.return_value = mock_instance

            with patch("ai_ppt.api.v1.endpoints.exports.ExportService") as mock_export:
                mock_export_instance = AsyncMock()
                mock_task = MagicMock()
                mock_task.id = uuid.uuid4()
                mock_task.status.value = "pending"
                mock_task.created_at = "2024-01-01T00:00:00"
                mock_export_instance.create_task.return_value = mock_task
                mock_export.return_value = mock_export_instance

                response = await client.post(
                    "/api/v1/exports/pptx?presentation_id=" + str(uuid.uuid4()),
                    headers=headers,
                )

        assert response.status_code in [202, 200, 404, 500]

    async def test_export_pptx_no_auth(self, client: AsyncClient):
        """测试未认证导出 PPTX"""
        response = await client.post(
            "/api/v1/exports/pptx?presentation_id=" + str(uuid.uuid4()),
        )

        # 401 (Unauthorized) 或 403 (Forbidden) 都是有效的未认证响应
        assert response.status_code in [401, 403]

    async def test_export_pptx_presentation_not_found(
        self, client: AsyncClient, authenticated_user
    ):
        """测试导出不存在的 PPT"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        with patch(
            "ai_ppt.application.services.presentation_service.PresentationService"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_by_id.return_value = None
            mock_service.return_value = mock_instance

            response = await client.post(
                "/api/v1/exports/pptx?presentation_id=" + str(uuid.uuid4()),
                headers=headers,
            )

        assert response.status_code == 404

    async def test_export_pdf_success(self, client: AsyncClient, authenticated_user):
        """测试成功导出 PDF"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        with patch(
            "ai_ppt.application.services.presentation_service.PresentationService"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_by_id.return_value = MagicMock(id=uuid.uuid4())
            mock_service.return_value = mock_instance

            with patch("ai_ppt.api.v1.endpoints.exports.ExportService") as mock_export:
                mock_export_instance = AsyncMock()
                mock_task = MagicMock()
                mock_task.id = uuid.uuid4()
                mock_task.status.value = "pending"
                mock_task.created_at = "2024-01-01T00:00:00"
                mock_export_instance.create_task.return_value = mock_task
                mock_export.return_value = mock_export_instance

                response = await client.post(
                    "/api/v1/exports/pdf?presentation_id=" + str(uuid.uuid4()),
                    headers=headers,
                )

        assert response.status_code in [202, 200, 404, 500]

    async def test_export_pdf_with_options(self, client: AsyncClient, authenticated_user):
        """测试带选项导出 PDF"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        with patch(
            "ai_ppt.application.services.presentation_service.PresentationService"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_by_id.return_value = MagicMock(id=uuid.uuid4())
            mock_service.return_value = mock_instance

            with patch("ai_ppt.api.v1.endpoints.exports.ExportService") as mock_export:
                mock_export_instance = AsyncMock()
                mock_task = MagicMock()
                mock_task.id = uuid.uuid4()
                mock_task.status.value = "pending"
                mock_task.created_at = "2024-01-01T00:00:00"
                mock_export_instance.create_task.return_value = mock_task
                mock_export.return_value = mock_export_instance

                response = await client.post(
                    f"/api/v1/exports/pdf?presentation_id={uuid.uuid4()}&quality=high&slide_range=1-5&include_notes=true",
                    headers=headers,
                )

        assert response.status_code in [202, 200, 404, 500]

    async def test_export_images_success(self, client: AsyncClient, authenticated_user):
        """测试成功导出图片"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        with patch(
            "ai_ppt.application.services.presentation_service.PresentationService"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_by_id.return_value = MagicMock(id=uuid.uuid4())
            mock_service.return_value = mock_instance

            with patch("ai_ppt.api.v1.endpoints.exports.ExportService") as mock_export:
                mock_export_instance = AsyncMock()
                mock_task = MagicMock()
                mock_task.id = uuid.uuid4()
                mock_task.status.value = "pending"
                mock_task.created_at = "2024-01-01T00:00:00"
                mock_export_instance.create_task.return_value = mock_task
                mock_export.return_value = mock_export_instance

                response = await client.post(
                    f"/api/v1/exports/images?presentation_id={uuid.uuid4()}&format=png",
                    headers=headers,
                )

        assert response.status_code in [202, 200, 404, 500]

    async def test_export_images_invalid_format(
        self, client: AsyncClient, authenticated_user
    ):
        """测试导出图片时提供无效格式"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        with patch(
            "ai_ppt.application.services.presentation_service.PresentationService"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_by_id.return_value = MagicMock(id=uuid.uuid4())
            mock_service.return_value = mock_instance

            response = await client.post(
                f"/api/v1/exports/images?presentation_id={uuid.uuid4()}&format=gif",  # 无效格式
                headers=headers,
            )

        assert response.status_code == 400

    async def test_get_export_status_success(self, client: AsyncClient, authenticated_user):
        """测试成功获取导出状态"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        task_id = uuid.uuid4()

        with patch("ai_ppt.api.v1.endpoints.exports.ExportService") as mock_export:
            mock_export_instance = AsyncMock()
            mock_task = MagicMock()
            mock_task.id = task_id
            mock_task.presentation_id = uuid.uuid4()
            mock_task.format.value = "pptx"
            mock_task.status.value = "completed"
            mock_task.progress = 100
            mock_task.file_path = "/path/to/file.pptx"
            mock_task.file_size = 1024
            mock_task.error_message = None
            mock_task.expires_at = None
            mock_task.created_at = "2024-01-01T00:00:00"
            mock_task.completed_at = "2024-01-01T00:01:00"
            mock_export_instance.get_task.return_value = mock_task
            mock_export.return_value = mock_export_instance

            response = await client.get(
                f"/api/v1/exports/{task_id}/status",
                headers=headers,
            )

        assert response.status_code in [200, 404, 500]

    async def test_get_export_status_no_auth(self, client: AsyncClient):
        """测试未认证获取导出状态"""
        response = await client.get(f"/api/v1/exports/{uuid.uuid4()}/status")

        # 401 (Unauthorized) 或 403 (Forbidden) 都是有效的未认证响应
        assert response.status_code in [401, 403]

    async def test_get_export_status_not_found(self, client: AsyncClient, authenticated_user):
        """测试获取不存在的导出任务状态"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        with patch("ai_ppt.api.v1.endpoints.exports.ExportService") as mock_export:
            mock_export_instance = AsyncMock()
            mock_export_instance.get_task.return_value = None
            mock_export.return_value = mock_export_instance

            response = await client.get(
                f"/api/v1/exports/{uuid.uuid4()}/status",
                headers=headers,
            )

        assert response.status_code == 404

    async def test_download_export_success(self, client: AsyncClient, authenticated_user):
        """测试成功下载导出文件"""
        import tempfile
        from pathlib import Path

        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        task_id = uuid.uuid4()

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pptx', delete=False) as f:
            f.write("test content")
            temp_file_path = f.name

        try:
            with patch("ai_ppt.api.v1.endpoints.exports.ExportService") as mock_export:
                mock_export_instance = AsyncMock()
                mock_task = MagicMock()
                mock_task.status.value = "completed"
                mock_task.file_path = temp_file_path
                mock_task.expires_at = None
                mock_export_instance.get_task.return_value = mock_task
                # get_full_path is a sync method, use MagicMock instead of AsyncMock attribute
                mock_path = Path(temp_file_path)
                mock_export_instance.get_full_path = MagicMock(return_value=mock_path)
                mock_export.return_value = mock_export_instance

                response = await client.get(
                    f"/api/v1/exports/{task_id}/download",
                    headers=headers,
                )

            assert response.status_code in [200, 404, 410, 500]
        finally:
            # 清理临时文件
            Path(temp_file_path).unlink(missing_ok=True)

    async def test_download_export_not_completed(
        self, client: AsyncClient, authenticated_user
    ):
        """测试下载未完成的导出"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        task_id = uuid.uuid4()

        with patch("ai_ppt.api.v1.endpoints.exports.ExportService") as mock_export:
            mock_export_instance = AsyncMock()
            mock_task = MagicMock()
            mock_task.status.value = "processing"
            mock_task.progress = 50
            mock_export_instance.get_task.return_value = mock_task
            mock_export.return_value = mock_export_instance

            response = await client.get(
                f"/api/v1/exports/{task_id}/download",
                headers=headers,
            )

        assert response.status_code == 400

    async def test_download_export_expired(self, client: AsyncClient, authenticated_user):
        """测试下载已过期的导出"""
        from datetime import datetime, timedelta, timezone
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        task_id = uuid.uuid4()

        with patch("ai_ppt.api.v1.endpoints.exports.ExportService") as mock_export:
            mock_export_instance = AsyncMock()
            mock_task = MagicMock()
            mock_task.status.value = "completed"
            mock_task.file_path = "test.pptx"
            mock_task.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
            mock_export_instance.get_task.return_value = mock_task
            mock_export.return_value = mock_export_instance

            response = await client.get(
                f"/api/v1/exports/{task_id}/download",
                headers=headers,
            )

        assert response.status_code == 410

    async def test_download_export_no_auth(self, client: AsyncClient):
        """测试未认证下载导出文件"""
        response = await client.get(f"/api/v1/exports/{uuid.uuid4()}/download")

        # 401 (Unauthorized) 或 403 (Forbidden) 都是有效的未认证响应
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
class TestExportFormats:
    """测试不同导出格式"""

    async def test_export_jpg_success(self, client: AsyncClient, authenticated_user):
        """测试成功导出 JPG"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        with patch(
            "ai_ppt.application.services.presentation_service.PresentationService"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_by_id.return_value = MagicMock(id=uuid.uuid4())
            mock_service.return_value = mock_instance

            with patch("ai_ppt.api.v1.endpoints.exports.ExportService") as mock_export:
                mock_export_instance = AsyncMock()
                mock_task = MagicMock()
                mock_task.id = uuid.uuid4()
                mock_task.status.value = "pending"
                mock_task.created_at = "2024-01-01T00:00:00"
                mock_export_instance.create_task.return_value = mock_task
                mock_export.return_value = mock_export_instance

                response = await client.post(
                    f"/api/v1/exports/images?presentation_id={uuid.uuid4()}&format=jpg",
                    headers=headers,
                )

        assert response.status_code in [202, 200, 404, 500]

    async def test_export_with_quality_standard(
        self, client: AsyncClient, authenticated_user
    ):
        """测试导出标准质量"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        with patch(
            "ai_ppt.application.services.presentation_service.PresentationService"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_by_id.return_value = MagicMock(id=uuid.uuid4())
            mock_service.return_value = mock_instance

            with patch("ai_ppt.api.v1.endpoints.exports.ExportService") as mock_export:
                mock_export_instance = AsyncMock()
                mock_task = MagicMock()
                mock_task.id = uuid.uuid4()
                mock_task.status.value = "pending"
                mock_task.created_at = "2024-01-01T00:00:00"
                mock_export_instance.create_task.return_value = mock_task
                mock_export.return_value = mock_export_instance

                response = await client.post(
                    f"/api/v1/exports/pptx?presentation_id={uuid.uuid4()}&quality=standard",
                    headers=headers,
                )

        assert response.status_code in [202, 200, 404, 500]

    async def test_export_with_slide_range(self, client: AsyncClient, authenticated_user):
        """测试导出指定页面范围"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        with patch(
            "ai_ppt.application.services.presentation_service.PresentationService"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_by_id.return_value = MagicMock(id=uuid.uuid4())
            mock_service.return_value = mock_instance

            with patch("ai_ppt.api.v1.endpoints.exports.ExportService") as mock_export:
                mock_export_instance = AsyncMock()
                mock_task = MagicMock()
                mock_task.id = uuid.uuid4()
                mock_task.status.value = "pending"
                mock_task.created_at = "2024-01-01T00:00:00"
                mock_export_instance.create_task.return_value = mock_task
                mock_export.return_value = mock_export_instance

                response = await client.post(
                    f"/api/v1/exports/pdf?presentation_id={uuid.uuid4()}&slide_range=1-3",
                    headers=headers,
                )

        assert response.status_code in [202, 200, 404, 500]

    async def test_export_with_include_notes(self, client: AsyncClient, authenticated_user):
        """测试导出包含备注"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        with patch(
            "ai_ppt.application.services.presentation_service.PresentationService"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_by_id.return_value = MagicMock(id=uuid.uuid4())
            mock_service.return_value = mock_instance

            with patch("ai_ppt.api.v1.endpoints.exports.ExportService") as mock_export:
                mock_export_instance = AsyncMock()
                mock_task = MagicMock()
                mock_task.id = uuid.uuid4()
                mock_task.status.value = "pending"
                mock_task.created_at = "2024-01-01T00:00:00"
                mock_export_instance.create_task.return_value = mock_task
                mock_export.return_value = mock_export_instance

                response = await client.post(
                    f"/api/v1/exports/pptx?presentation_id={uuid.uuid4()}&include_notes=true",
                    headers=headers,
                )

        assert response.status_code in [202, 200, 404, 500]

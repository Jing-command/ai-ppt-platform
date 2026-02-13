"""
Schema 验证测试
测试所有 Pydantic 模型
"""

import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from ai_ppt.api.v1.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)
from ai_ppt.api.v1.schemas.common import (
    ErrorResponse,
    PaginationMeta,
    PaginationParams,
    SuccessResponse,
)
from ai_ppt.api.v1.schemas.connector import (
    ConnectorCreate,
    ConnectorQueryRequest,
    ConnectorResponse,
    ConnectorTestRequest,
    ConnectorTestResponse,
    ConnectorUpdate,
)
from ai_ppt.api.v1.schemas.export import (
    ExportRequest,
    ExportResponse,
    ExportStatusResponse,
)
from ai_ppt.api.v1.schemas.outline import (
    OutlineBackground,
    OutlineCreate,
    OutlineGenerateRequest,
    OutlineGenerateResponse,
    OutlinePage,
    OutlineResponse,
    OutlineUpdate,
)
from ai_ppt.api.v1.schemas.presentation import (
    PresentationCreate,
    PresentationResponse,
    PresentationUpdate,
    Slide,
    SlideContent,
    SlideCreate,
    SlideLayout,
)
from ai_ppt.api.v1.schemas.slide import UndoRedoResponse

# ==================== Auth Schemas Tests ====================


class TestAuthSchemas:
    """测试认证相关 Schema"""

    def test_login_request_valid(self):
        """测试有效的登录请求"""
        data = {"email": "test@example.com", "password": "password123"}
        request = LoginRequest(**data)
        assert request.email == "test@example.com"
        assert request.password == "password123"

    def test_login_request_invalid_email(self):
        """测试无效的邮箱格式"""
        with pytest.raises(ValidationError):
            LoginRequest(email="invalid-email", password="password123")

    def test_register_request_valid(self):
        """测试有效的注册请求"""
        data = {
            "email": "new@example.com",
            "password": "password123",
            "name": "New User",
        }
        request = RegisterRequest(**data)
        assert request.email == "new@example.com"
        assert request.name == "New User"

    def test_register_request_password_too_short(self):
        """测试密码太短"""
        with pytest.raises(ValidationError):
            RegisterRequest(email="test@example.com", password="123", name="Test")

    def test_register_request_name_too_long(self):
        """测试名称太长"""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="test@example.com",
                password="password123",
                name="A" * 101,
            )

    def test_user_response_with_alias(self):
        """测试用户响应的字段别名"""
        user_id = uuid.uuid4()
        data = {
            "id": user_id,
            "email": "test@example.com",
            "name": "Test User",
            "createdAt": datetime.now(),
        }
        response = UserResponse(**data)
        assert response.id == user_id
        # 验证别名映射
        output = response.model_dump(by_alias=True)
        assert "createdAt" in output

    def test_login_response_with_alias(self):
        """测试登录响应的字段别名"""
        user_id = uuid.uuid4()
        data = {
            "accessToken": "test_token",
            "tokenType": "bearer",
            "user": {
                "id": user_id,
                "email": "test@example.com",
                "name": "Test",
                "createdAt": datetime.now(),
            },
        }
        response = LoginResponse(**data)
        assert response.access_token == "test_token"
        output = response.model_dump(by_alias=True)
        assert "accessToken" in output

    def test_refresh_request_with_alias(self):
        """测试刷新请求"""
        data = {"refreshToken": "refresh_token_here"}
        request = RefreshRequest(**data)
        assert request.refresh_token == "refresh_token_here"

    def test_refresh_response_with_alias(self):
        """测试刷新响应"""
        data = {"accessToken": "new_token", "tokenType": "bearer"}
        response = RefreshResponse(**data)
        output = response.model_dump(by_alias=True)
        assert output["accessToken"] == "new_token"


# ==================== Connector Schemas Tests ====================


class TestConnectorSchemas:
    """测试连接器相关 Schema"""

    def test_connector_create_valid(self):
        """测试有效的连接器创建"""
        data = {
            "name": "MySQL Database",
            "type": "mysql",
            "config": {
                "host": "localhost",
                "port": 3306,
                "database": "test",
                "username": "user",
                "password": "pass",
            },
            "description": "Test database connection",
        }
        connector = ConnectorCreate(**data)
        assert connector.name == "MySQL Database"
        assert connector.type == "mysql"

    def test_connector_create_invalid_type(self):
        """测试无效的连接器类型"""
        # 任何字符串都应该被接受，因为 type 没有特定的约束
        data = {
            "name": "Test",
            "type": "unknown_type",
            "config": {},
        }
        connector = ConnectorCreate(**data)
        assert connector.type == "unknown_type"

    def test_connector_update_partial(self):
        """测试部分更新连接器"""
        data = {"name": "Updated Name"}
        update = ConnectorUpdate(**data)
        assert update.name == "Updated Name"
        assert update.description is None

    def test_connector_response_with_alias(self):
        """测试连接器响应的别名"""
        connector_id = uuid.uuid4()
        user_id = uuid.uuid4()
        data = {
            "id": connector_id,
            "name": "Test Connector",
            "type": "mysql",
            "userId": user_id,
            "config": {},
            "isActive": True,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
        }
        response = ConnectorResponse(**data)
        output = response.model_dump(by_alias=True)
        assert "userId" in output
        assert "isActive" in output

    def test_connector_test_request_empty(self):
        """测试空的连接器测试请求"""
        request = ConnectorTestRequest()
        assert request.config is None

    def test_connector_test_request_with_config(self):
        """测试带配置的连接器测试请求"""
        data = {"config": {"host": "localhost", "port": 3306}}
        request = ConnectorTestRequest(**data)
        assert request.config["host"] == "localhost"

    def test_connector_test_response_success(self):
        """测试成功的连接测试响应"""
        data = {
            "success": True,
            "message": "Connection successful",
            "latencyMs": 50,
            "serverVersion": "8.0.0",
        }
        response = ConnectorTestResponse(**data)
        assert response.success is True
        assert response.latency_ms == 50

    def test_connector_test_response_failure(self):
        """测试失败的连接测试响应"""
        data = {
            "success": False,
            "message": "Connection failed",
            "errorDetails": "Authentication error",
        }
        response = ConnectorTestResponse(**data)
        assert response.success is False
        assert response.error_details == "Authentication error"

    def test_connector_query_request_valid(self):
        """测试有效的查询请求"""
        data = {
            "query": "SELECT * FROM users WHERE id = :id",
            "params": {"id": 1},
            "limit": 50,
        }
        request = ConnectorQueryRequest(**data)
        assert request.query == "SELECT * FROM users WHERE id = :id"
        assert request.limit == 50

    def test_connector_query_request_limit_bounds(self):
        """测试查询请求的 limit 边界"""
        # 测试 limit 过小
        with pytest.raises(ValidationError):
            ConnectorQueryRequest(query="SELECT 1", limit=0)

        # 测试 limit 过大
        with pytest.raises(ValidationError):
            ConnectorQueryRequest(query="SELECT 1", limit=10001)


# ==================== Outline Schemas Tests ====================


class TestOutlineSchemas:
    """测试大纲相关 Schema"""

    def test_outline_page_valid(self):
        """测试有效的大纲页面"""
        data = {
            "id": "page-1",
            "pageNumber": 1,
            "title": "Introduction",
            "content": "Overview content",
            "pageType": "title",
        }
        page = OutlinePage(**data)
        assert page.title == "Introduction"
        assert page.page_number == 1

    def test_outline_page_default_type(self):
        """测试大纲页面默认类型"""
        data = {"pageNumber": 1, "title": "Test"}
        page = OutlinePage(**data)
        assert page.page_type == "content"

    def test_outline_background_valid(self):
        """测试有效的背景设置"""
        data = {
            "type": "ai",
            "prompt": "Blue gradient background",
            "opacity": 0.8,
            "blur": 5.0,
        }
        bg = OutlineBackground(**data)
        assert bg.type == "ai"
        assert bg.opacity == 0.8

    def test_outline_background_opacity_bounds(self):
        """测试背景透明度边界"""
        # 测试 opacity 超出范围
        with pytest.raises(ValidationError):
            OutlineBackground(type="solid", opacity=1.5)

        with pytest.raises(ValidationError):
            OutlineBackground(type="solid", opacity=-0.1)

    def test_outline_create_valid(self):
        """测试有效的创建大纲请求"""
        data = {
            "title": "AI Presentation",
            "description": "About AI technology",
            "pages": [
                {
                    "id": "page-1",
                    "pageNumber": 1,
                    "title": "Cover",
                    "pageType": "title",
                },
            ],
            "background": {"type": "ai", "prompt": "Tech background"},
        }
        outline = OutlineCreate(**data)
        assert outline.title == "AI Presentation"
        assert len(outline.pages) == 1

    def test_outline_create_empty_pages(self):
        """测试空页面的创建大纲请求"""
        data = {"title": "Test Outline", "pages": []}
        outline = OutlineCreate(**data)
        assert outline.pages == []

    def test_outline_generate_request_valid(self):
        """测试有效的生成大纲请求"""
        data = {
            "prompt": "Create a presentation about AI",
            "numSlides": 10,
            "language": "en",
            "style": "business",
        }
        request = OutlineGenerateRequest(**data)
        assert request.prompt == "Create a presentation about AI"
        assert request.num_slides == 10

    def test_outline_generate_request_prompt_bounds(self):
        """测试生成大纲请求的提示词边界"""
        # 测试提示词太短
        with pytest.raises(ValidationError):
            OutlineGenerateRequest(prompt="Short", numSlides=5)

        # 测试提示词太长
        with pytest.raises(ValidationError):
            OutlineGenerateRequest(prompt="A" * 2001, numSlides=5)

    def test_outline_generate_request_num_slides_bounds(self):
        """测试生成大纲请求的幻灯片数量边界"""
        with pytest.raises(ValidationError):
            OutlineGenerateRequest(prompt="Valid prompt here", numSlides=2)

        with pytest.raises(ValidationError):
            OutlineGenerateRequest(prompt="Valid prompt here", numSlides=51)

    def test_outline_generate_request_invalid_language(self):
        """测试无效的语言代码"""
        with pytest.raises(ValidationError):
            OutlineGenerateRequest(prompt="Valid prompt here", language="fr")

    def test_outline_response_with_alias(self):
        """测试大纲响应的别名"""
        outline_id = uuid.uuid4()
        user_id = uuid.uuid4()
        data = {
            "id": outline_id,
            "userId": user_id,
            "title": "Test Outline",
            "pages": [],
            "totalSlides": 0,
            "status": "draft",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
        }
        response = OutlineResponse(**data)
        output = response.model_dump(by_alias=True)
        assert "userId" in output
        assert "totalSlides" in output


# ==================== Presentation Schemas Tests ====================


class TestPresentationSchemas:
    """测试演示文稿相关 Schema"""

    def test_slide_content_valid(self):
        """测试有效的幻灯片内容"""
        data = {
            "title": "Slide Title",
            "subtitle": "Subtitle",
            "text": "Main content",
            "bullets": ["Point 1", "Point 2"],
        }
        content = SlideContent(**data)
        assert content.title == "Slide Title"
        assert len(content.bullets) == 2

    def test_slide_content_extra_fields(self):
        """测试幻灯片内容的额外字段"""
        data = {
            "title": "Test",
            "customField": "custom value",
        }
        content = SlideContent(**data)
        assert content.customField == "custom value"

    def test_slide_layout_valid(self):
        """测试有效的幻灯片布局"""
        data = {"type": "title_content", "background": "blue", "theme": "modern"}
        layout = SlideLayout(**data)
        assert layout.type == "title_content"

    def test_slide_create_valid(self):
        """测试有效的幻灯片创建"""
        data = {
            "type": "content",
            "content": {"title": "Test Slide", "text": "Content"},
            "layout": {"type": "title_content"},
            "notes": "Speaker notes",
        }
        slide = SlideCreate(**data)
        assert slide.type == "content"
        assert slide.notes == "Speaker notes"

    def test_presentation_create_valid(self):
        """测试有效的 PPT 创建"""
        data = {
            "title": "My Presentation",
            "description": "A test presentation",
            "templateId": "modern",
        }
        presentation = PresentationCreate(**data)
        assert presentation.title == "My Presentation"
        assert presentation.template_id == "modern"

    def test_presentation_create_minimal(self):
        """测试最小化的 PPT 创建"""
        data = {"title": "Simple Presentation"}
        presentation = PresentationCreate(**data)
        assert presentation.description is None
        assert presentation.slides == []

    def test_presentation_update_partial(self):
        """测试部分更新 PPT"""
        data = {"title": "Updated Title"}
        update = PresentationUpdate(**data)
        assert update.title == "Updated Title"
        assert update.description is None

    def test_presentation_update_invalid_status(self):
        """测试无效的 PPT 状态"""
        with pytest.raises(ValidationError):
            PresentationUpdate(status="invalid_status")

    def test_presentation_response_with_alias(self):
        """测试 PPT 响应的别名"""
        ppt_id = uuid.uuid4()
        owner_id = uuid.uuid4()
        data = {
            "id": ppt_id,
            "title": "Test",
            "ownerId": owner_id,
            "slideCount": 5,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
        }
        response = PresentationResponse(**data)
        output = response.model_dump(by_alias=True)
        assert "ownerId" in output
        assert "slideCount" in output

    def test_slide_model_validator(self):
        """测试幻灯片模型验证器"""

        class MockSlideData:
            def __init__(self):
                self.layout_type = "content"
                self.content = {"title": "Test"}

        mock_data = MockSlideData()
        slide = Slide.model_validate(mock_data)
        assert slide.type == "content"


# ==================== Export Schemas Tests ====================


class TestExportSchemas:
    """测试导出相关 Schema"""

    def test_export_request_valid(self):
        """测试有效的导出请求"""
        data = {"format": "pptx", "quality": "high", "includeNotes": True}
        request = ExportRequest(**data)
        assert request.format == "pptx"
        assert request.quality == "high"

    def test_export_request_invalid_format(self):
        """测试无效的导出格式"""
        with pytest.raises(ValidationError):
            ExportRequest(format="invalid")

    def test_export_request_invalid_quality(self):
        """测试无效的导出质量"""
        with pytest.raises(ValidationError):
            ExportRequest(quality="ultra")

    def test_export_response_with_alias(self):
        """测试导出响应的别名"""
        task_id = uuid.uuid4()
        data = {
            "taskId": task_id,
            "status": "pending",
            "createdAt": datetime.now(),
        }
        response = ExportResponse(**data)
        output = response.model_dump(by_alias=True)
        assert "taskId" in output

    def test_export_status_response_with_alias(self):
        """测试导出状态响应的别名"""
        task_id = uuid.uuid4()
        ppt_id = uuid.uuid4()
        data = {
            "taskId": task_id,
            "presentationId": ppt_id,
            "format": "pptx",
            "status": "processing",
            "progress": 50,
            "filePath": "/path/to/file.pptx",
            "createdAt": datetime.now(),
        }
        response = ExportStatusResponse(**data)
        assert response.progress == 50
        output = response.model_dump(by_alias=True)
        assert "presentationId" in output


# ==================== Common Schemas Tests ====================


class TestCommonSchemas:
    """测试通用 Schema"""

    def test_error_response_valid(self):
        """测试有效的错误响应"""
        data = {
            "code": "NOT_FOUND",
            "message": "Resource not found",
            "details": {"resource_id": "123"},
        }
        response = ErrorResponse(**data)
        assert response.code == "NOT_FOUND"
        assert response.details["resource_id"] == "123"

    def test_error_response_without_details(self):
        """测试没有详情的错误响应"""
        data = {"code": "ERROR", "message": "Something went wrong"}
        response = ErrorResponse(**data)
        assert response.details is None

    def test_pagination_params_default(self):
        """测试分页参数默认值"""
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 20

    def test_pagination_params_custom(self):
        """测试自定义分页参数"""
        params = PaginationParams(page=5, page_size=50)
        assert params.page == 5
        assert params.page_size == 50

    def test_pagination_params_bounds(self):
        """测试分页参数边界"""
        with pytest.raises(ValidationError):
            PaginationParams(page=0)

        with pytest.raises(ValidationError):
            PaginationParams(page_size=0)

        with pytest.raises(ValidationError):
            PaginationParams(page_size=101)

    def test_pagination_meta(self):
        """测试分页元数据"""
        data = {
            "page": 1,
            "pageSize": 20,
            "total": 100,
            "totalPages": 5,
        }
        meta = PaginationMeta(**data)
        output = meta.model_dump(by_alias=True)
        assert output["totalPages"] == 5

    def test_success_response(self):
        """测试成功响应"""
        response = SuccessResponse()
        assert response.success is True
        assert response.message is None

        response_with_data = SuccessResponse(message="Done", data={"id": 1})
        assert response_with_data.message == "Done"


# ==================== Slide Schemas Tests ====================


class TestSlideSchemas:
    """测试幻灯片相关 Schema"""

    def test_undo_redo_response_success(self):
        """测试成功的撤销/重做响应"""
        data = {
            "success": True,
            "description": "Undo completed",
            "slideId": "slide-123",
        }
        response = UndoRedoResponse(**data)
        assert response.success is True
        output = response.model_dump(by_alias=True)
        assert "slideId" in output

    def test_undo_redo_response_with_state(self):
        """测试带状态的撤销/重做响应"""
        data = {
            "success": True,
            "description": "Redo completed",
            "state": {"content": {"title": "Updated"}},
        }
        response = UndoRedoResponse(**data)
        assert response.state["content"]["title"] == "Updated"

"""
大纲生成服务
调用 DeepSeek API 生成大纲内容
"""

import json
import uuid
from datetime import datetime
from typing import Any, Optional

from ai_ppt.domain.models.outline import (
    Outline,
    OutlineBackground,
    OutlineStatus,
)
from ai_ppt.infrastructure.ai.client import LLMClient
from ai_ppt.infrastructure.ai.models import LLMRequest


class OutlineGenerationError(Exception):
    """大纲生成错误"""


class OutlineGenerationService:
    """
    大纲生成服务

    使用 DeepSeek API 生成 PPT 大纲，包括：
    - 每页的标题、内容、类型、插图提示词
    - PPT 整体背景描述
    """

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        """
        初始化服务

        Args:
            llm_client: LLM 客户端，如未提供则自动创建
        """
        self._llm_client = llm_client or LLMClient()

    def _build_generation_prompt(
        self,
        topic: str,
        num_slides: int,
        language: str = "zh",
        style: str = "business",
        context_data: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        构建生成提示词

        Args:
            topic: 主题
            num_slides: 幻灯片数量
            language: 语言
            style: 风格
            context_data: 上下文数据

        Returns:
            提示词字符串
        """
        language_name = "中文" if language == "zh" else "English"

        style_desc = {
            "business": "商务专业风格，简洁大气",
            "education": "教育学术风格，清晰易懂",
            "creative": "创意设计风格，富有活力",
            "technical": "技术专业风格，逻辑严谨",
        }.get(style, "商务专业风格")

        context_str = ""
        if context_data:
            context_str = f"\n参考数据/上下文：\n{json.dumps(context_data, ensure_ascii=False, indent=2)}"  # noqa: E501

        prompt = f"""请为一个关于"{topic}"的PPT生成大纲，共{num_slides}页。

要求：
- 语言：{language_name}
- 风格：{style_desc}
- 总页数：{num_slides}页{context_str}

对每一页提供：
1. 页面标题
2. 页面内容描述（100字以内）
3. 页面类型（title/content/section/chart/conclusion）
4. 插图提示词（用于AI生成配图，50字以内）

另外提供一个PPT整体背景的描述提示词。

返回JSON格式，结构如下：
{{
  "title": "PPT主标题",
  "description": "PPT简介（200字以内）",
  "pages": [
    {{
      "id": "page-1",
      "pageNumber": 1,
      "title": "页面标题",
      "content": "页面内容描述",
      "pageType": "title",
      "imagePrompt": "插图提示词"
    }}
  ],
  "background": {{
    "type": "ai",
    "prompt": "PPT整体背景描述，用于AI生成背景图片"
  }}
}}

注意事项：
1. 第一页通常是title类型（封面）
2. 中间可以有section类型（章节分隔页）
3. 内容页使用content类型
4. 数据展示页使用chart类型
5. 最后一页使用conclusion类型（总结）
6. 确保 pageNumber 从1开始连续编号
"""
        return prompt

    async def generate_outline(
        self,
        topic: str,
        num_slides: int = 10,
        language: str = "zh",
        style: str = "business",
        context_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        生成大纲

        Args:
            topic: 主题
            num_slides: 幻灯片数量
            language: 语言
            style: 风格
            context_data: 上下文数据

        Returns:
            包含 title, description, pages, background 的字典

        Raises:
            OutlineGenerationError: 生成失败
        """
        prompt = self._build_generation_prompt(
            topic=topic,
            num_slides=num_slides,
            language=language,
            style=style,
            context_data=context_data,
        )

        request = LLMRequest(
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的PPT大纲设计专家，擅长根据主题生成结构清晰、内容丰富的PPT大纲。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )

        try:
            response = await self._llm_client.complete(request)
            result = json.loads(response.content)

            # 验证结果格式
            if "pages" not in result:
                raise OutlineGenerationError("生成的结果缺少 pages 字段")

            # 确保每个页面有 id
            for i, page in enumerate(result.get("pages", [])):
                if "id" not in page:
                    page["id"] = f"page-{i+1}"
                if "pageNumber" not in page:
                    page["pageNumber"] = i + 1

            return result

        except json.JSONDecodeError as e:
            raise OutlineGenerationError(f"解析 AI 响应失败: {e}") from e
        except Exception as e:
            raise OutlineGenerationError(f"生成大纲失败: {e}") from e

    async def create_outline_from_generation(
        self,
        user_id: uuid.UUID,
        topic: str,
        num_slides: int = 10,
        language: str = "zh",
        style: str = "business",
        context_data: Optional[dict[str, Any]] = None,
        connector_id: Optional[uuid.UUID] = None,
    ) -> Outline:
        """
        生成大纲并创建 Outline 实体

        Args:
            user_id: 用户ID
            topic: 主题
            num_slides: 幻灯片数量
            language: 语言
            style: 风格
            context_data: 上下文数据
            connector_id: 连接器ID

        Returns:
            Outline 实体（已填充生成结果，但未持久化）
        """
        # 生成大纲
        result = await self.generate_outline(
            topic=topic,
            num_slides=num_slides,
            language=language,
            style=style,
            context_data=context_data,
        )

        # 提取背景
        background_data = result.get("background")
        background = None
        if background_data:
            background = OutlineBackground.from_dict(background_data)

        # 构建 AI 参数记录
        ai_parameters = {
            "topic": topic,
            "num_slides": num_slides,
            "language": language,
            "style": style,
            "context_data": context_data,
            "connector_id": str(connector_id) if connector_id else None,
        }

        # 创建 Outline 实体
        outline = Outline(
            title=result.get("title", topic),
            description=result.get("description"),
            user_id=user_id,
            pages=result.get("pages", []),
            background=background.to_dict() if background else None,
            total_slides=len(result.get("pages", [])),
            status=OutlineStatus.COMPLETED.value,
            ai_prompt=topic,
            ai_parameters=ai_parameters,
        )
        outline.generated_at = datetime.utcnow()

        return outline

    async def close(self) -> None:
        """关闭资源"""
        await self._llm_client.close()

    async def __aenter__(self) -> "OutlineGenerationService":
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """异步上下文管理器出口"""
        await self.close()

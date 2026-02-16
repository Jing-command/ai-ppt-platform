"""
AI 聊天服务模块
处理用户与 AI 提示词助手的对话逻辑
"""

import re
from typing import AsyncIterator, List, Optional

from ai_ppt.api.v1.schemas.chat import (
    ChatContext,
    ChatMessage,
    ChatResponseChunk,
    IntentAnalysis,
    IntentType,
    MessageRole,
)
from ai_ppt.infrastructure.ai.client import LLMClient, LLMProvider
from ai_ppt.infrastructure.ai.models import LLMRequest
from ai_ppt.infrastructure.config import settings

# AI 提示词助手的系统提示词
CHAT_SYSTEM_PROMPT = """你是一个专业的 AI 提示词助手，专门帮助用户优化和生成 PPT 提示词。

你的主要职责：
1. 与用户进行友好的对话，了解他们的 PPT 需求
2. 引导用户明确 PPT 的主题、受众、目的和风格
3. 当用户需求明确后，生成优化后的 PPT 提示词

对话风格：
- 友好、专业、有耐心
- 使用清晰的中文
- 适当使用表情符号增加亲和力

## 重要：输出格式规则

### 思考过程（可选）
在回复之前，你可以先进行思考分析。使用以下格式：

[THINKING_START]
你的思考过程...
[THINKING_END]

### 优化提示词（仅在确认生成时使用）
**只有当你明确决定为用户生成优化后的提示词时**，才使用以下格式：

[PROMPT_START]
主题：xxx
目标受众：xxx
演示目的：xxx
设计风格：xxx
[PROMPT_END]

## 关键规则

1. **不要滥用 [PROMPT_START]**：只有当用户明确要求生成提示词，或者你已经充分了解用户需求并决定给出最终优化结果时，才使用这个格式。

2. **正常对话时不要输出标记**：如果你还在和用户聊天、了解需求、提供建议，不要使用 [PROMPT_START]...[PROMPT_END]。

3. **思考过程是可选的**：简单问题可以不写思考过程。

## 示例

**场景1：还在了解需求（不要输出 PROMPT 标记）**
用户：我想做一个PPT
你的回复：好的！请问这个PPT是关于什么主题的呢？是用于什么场合的？

**场景2：需求明确，生成优化提示词**
用户：我想做一个产品发布会的PPT，面向媒体和合作伙伴
你的回复：
[THINKING_START]
用户需求明确：产品发布会PPT，受众是媒体和合作伙伴。可以生成优化提示词。
[THINKING_END]

好的，我来帮你优化提示词！

[PROMPT_START]
主题：新产品发布会
目标受众：媒体、合作伙伴、潜在客户
演示目的：产品发布与品牌宣传
设计风格：科技感、现代简约
[PROMPT_END]

你可以直接使用这个提示词，或者告诉我需要调整的地方！"""


class ChatService:
    """
    AI 聊天服务

    提供提示词优化建议和对话功能
    """

    # 关键词映射 - 用于识别用户意图
    CLARIFICATION_KEYWORDS = [
        "怎么写",
        "如何描述",
        "不知道怎么",
        "帮我",
        "帮忙",
        "求助",
        "不太清楚",
        "不确定",
    ]

    PROMPT_KEYWORDS = [
        "生成",
        "创建",
        "制作",
        "做一个",
        "写一个",
        "帮我写",
        "帮我生成",
        "PPT",
        "幻灯片",
        "演示文稿",
        "报告",
        "汇报",
    ]

    # 缺失信息的提示问题
    MISSING_INFO_QUESTIONS = {
        "主题": "您想制作什么主题的 PPT？",
        "受众": "这个 PPT 的目标受众是谁？（如：客户、领导、同事等）",
        "目的": "您希望通过这个 PPT 达到什么目的？（如：汇报、销售、培训等）",
        "风格": "您希望 PPT 的风格是怎样的？（如：正式、活泼、简约等）",
        "页数": "您期望 PPT 大概有多少页？",
        "数据": "是否有特定的数据或内容需要包含？",
    }

    def __init__(self) -> None:
        """初始化聊天服务"""
        self._llm_client: Optional[LLMClient] = None
        self._use_real_llm = True  # 是否使用真实大模型

    def _get_llm_client(self) -> Optional[LLMClient]:
        """获取或创建 LLM 客户端（使用独立的提示词助手配置）"""
        if self._llm_client is None:
            try:
                # 使用独立的提示词助手配置
                provider = settings.chat_ai_provider
                api_key = settings.chat_ai_api_key.get_secret_value()

                # 如果环境变量中设置了 CHAT_AI_API_KEY，优先使用
                import os

                env_api_key = os.environ.get("CHAT_AI_API_KEY")
                if env_api_key:
                    api_key = env_api_key

                if not api_key:
                    raise ValueError("Chat AI API key not configured")

                self._llm_client = LLMClient(
                    provider=LLMProvider(settings.chat_ai_provider),
                    api_key=api_key,
                    base_url=settings.chat_ai_base_url,
                    model=settings.chat_ai_model,
                    timeout=settings.chat_ai_timeout,
                )
            except Exception as e:
                # 如果无法创建 LLM 客户端，回退到模拟模式
                print(f"Warning: Failed to create chat LLM client: {e}")
                self._use_real_llm = False
                self._llm_client = None
        return self._llm_client

    def analyze_intent(
        self,
        messages: List[ChatMessage],
        context: Optional[ChatContext] = None,
    ) -> IntentAnalysis:
        """
        分析用户意图

        Args:
            messages: 聊天消息列表
            context: 可选的上下文信息

        Returns:
            意图分析结果
        """
        # 获取最后一条用户消息
        user_message = self._get_last_user_message(messages)
        if not user_message:
            return IntentAnalysis(
                intent_type=IntentType.GENERAL,
                confidence=1.0,
                missing_info=[],
                suggested_questions=[],
            )

        content = user_message.content.lower()

        # 检查是否需要澄清
        clarification_score = self._calculate_keyword_score(
            content, self.CLARIFICATION_KEYWORDS
        )

        # 检查是否是提示词优化请求
        prompt_score = self._calculate_keyword_score(
            content, self.PROMPT_KEYWORDS
        )

        # 分析缺失的信息
        missing_info = self._analyze_missing_info(content, context)
        suggested_questions = [
            self.MISSING_INFO_QUESTIONS[info]
            for info in missing_info
            if info in self.MISSING_INFO_QUESTIONS
        ]

        # 判断意图类型
        if clarification_score > 0.3 and missing_info:
            return IntentAnalysis(
                intent_type=IntentType.CLARIFICATION,
                confidence=min(0.9, clarification_score + 0.3),
                missing_info=missing_info,
                suggested_questions=suggested_questions[
                    :3
                ],  # 最多返回3个建议问题
            )

        if prompt_score > 0.4 and len(missing_info) <= 1:
            return IntentAnalysis(
                intent_type=IntentType.PROMPT_OPTIMIZATION,
                confidence=min(0.9, prompt_score + 0.2),
                missing_info=missing_info,
                suggested_questions=suggested_questions[:2],
            )

        if suggested_questions:
            return IntentAnalysis(
                intent_type=IntentType.SUGGESTION,
                confidence=0.7,
                missing_info=missing_info,
                suggested_questions=suggested_questions[:2],
            )

        return IntentAnalysis(
            intent_type=IntentType.GENERAL,
            confidence=0.8,
            missing_info=[],
            suggested_questions=[],
        )

    def _get_last_user_message(
        self, messages: List[ChatMessage]
    ) -> Optional[ChatMessage]:
        """
        获取最后一条用户消息

        Args:
            messages: 聊天消息列表

        Returns:
            最后一条用户消息，如果没有则返回 None
        """
        for message in reversed(messages):
            if message.role == MessageRole.USER:
                return message
        return None

    def _calculate_keyword_score(
        self, content: str, keywords: List[str]
    ) -> float:
        """
        计算关键词匹配分数

        Args:
            content: 消息内容
            keywords: 关键词列表

        Returns:
            匹配分数 (0.0 - 1.0)
        """
        if not content:
            return 0.0

        matches = sum(1 for keyword in keywords if keyword.lower() in content)
        return min(1.0, matches / max(len(keywords) * 0.3, 1))

    def _analyze_missing_info(
        self, content: str, context: Optional[ChatContext] = None
    ) -> List[str]:
        """
        分析缺失的信息

        Args:
            content: 用户消息内容
            context: 上下文信息

        Returns:
            缺失信息列表
        """
        missing = []

        # 检查主题
        if not re.search(r"(关于|主题|题目|标题).{1,20}", content):
            if not context or not context.current_prompt:
                missing.append("主题")

        # 检查受众
        if not re.search(r"(受众|观众|听众|给.*看|向.*汇报)", content):
            missing.append("受众")

        # 检查目的
        if not re.search(r"(目的|目标|希望|想要|为了)", content):
            missing.append("目的")

        # 检查风格
        if not re.search(r"(风格|样式|简约|正式|活泼|商务)", content):
            missing.append("风格")

        return missing

    def generate_optimized_prompt(
        self,
        messages: List[ChatMessage],
        context: Optional[ChatContext] = None,
    ) -> str:
        """
        生成优化后的提示词

        Args:
            messages: 聊天消息列表
            context: 上下文信息

        Returns:
            优化后的提示词
        """
        # 收集所有用户输入
        user_inputs = []
        for message in messages:
            if message.role == MessageRole.USER:
                user_inputs.append(message.content)

        # 合并用户输入
        combined_input = " ".join(user_inputs)

        # 提取关键信息
        topic = self._extract_topic(combined_input)
        audience = self._extract_audience(combined_input)
        purpose = self._extract_purpose(combined_input)
        style = self._extract_style(combined_input)

        # 构建优化后的提示词
        prompt_parts = []

        if topic:
            prompt_parts.append(f"主题：{topic}")
        if audience:
            prompt_parts.append(f"目标受众：{audience}")
        if purpose:
            prompt_parts.append(f"演示目的：{purpose}")
        if style:
            prompt_parts.append(f"设计风格：{style}")

        # 如果有上下文中的当前提示词，进行增强
        if context and context.current_prompt:
            prompt_parts.insert(0, f"基于原始需求：{context.current_prompt}")

        # 添加默认建议
        if len(prompt_parts) < 3:
            prompt_parts.append("请生成结构清晰、内容专业的演示文稿")

        return "\n".join(prompt_parts)

    def _extract_topic(self, content: str) -> Optional[str]:
        """提取主题"""
        # 尝试匹配常见的主题描述模式
        patterns = [
            r"关于(.{2,20}?)(的|PPT|幻灯片|演示)",
            r"主题[是为：:]\s*(.{2,20})",
            r"制作.{0,5}(.{2,20}?)(PPT|幻灯片)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()

        # 如果没有匹配到，尝试提取关键名词
        if "PPT" in content or "幻灯片" in content:
            # 简单提取
            words = re.findall(r"[\u4e00-\u9fa5]{2,10}", content)
            for word in words:
                if word not in ["幻灯片", "演示文稿", "帮我", "制作", "生成"]:
                    return str(word)

        return None

    def _extract_audience(self, content: str) -> Optional[str]:
        """提取受众"""
        patterns = [
            r"给(.{2,10}?)(看|汇报|展示)",
            r"向(.{2,10}?)(汇报|展示)",
            r"受众[是为：:]\s*(.{2,10})",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()

        return None

    def _extract_purpose(self, content: str) -> Optional[str]:
        """提取目的"""
        patterns = [
            r"用于(.{2,10})",
            r"目的是?(.{2,10})",
            r"希望.{0,5}(.{2,10})",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()

        # 根据关键词推断目的
        if "汇报" in content:
            return "工作汇报"
        if "销售" in content or "客户" in content:
            return "销售展示"
        if "培训" in content:
            return "培训教学"

        return None

    def _extract_style(self, content: str) -> Optional[str]:
        """提取风格"""
        style_keywords = {
            "简约": "简约现代",
            "正式": "商务正式",
            "商务": "商务专业",
            "活泼": "活泼生动",
            "创意": "创意新颖",
            "科技": "科技感",
        }

        for keyword, style in style_keywords.items():
            if keyword in content:
                return style

        return None

    async def generate_response_stream(
        self,
        messages: List[ChatMessage],
        context: Optional[ChatContext] = None,
    ) -> AsyncIterator[ChatResponseChunk]:
        """
        生成流式响应

        Args:
            messages: 聊天消息列表
            context: 上下文信息

        Yields:
            响应块
        """
        # 直接使用真实大模型
        async for chunk in self._generate_llm_response_stream(
            messages, context
        ):
            yield chunk

    def _generate_clarification_response(self, intent: IntentAnalysis) -> str:
        """生成澄清类型的响应"""
        response_parts = ["我理解您需要帮助。为了更好地协助您，请告诉我：\n"]

        for i, question in enumerate(intent.suggested_questions or [], 1):
            response_parts.append(f"{i}. {question}\n")

        if not intent.suggested_questions:
            response_parts.append("您具体想制作什么内容的 PPT 呢？")

        return "".join(response_parts)

    def _generate_optimization_response(self, intent: IntentAnalysis) -> str:
        """生成优化类型的响应"""
        response = "根据您的描述，我已经为您优化了提示词：\n\n"

        if intent.suggested_questions:
            response += "另外，您还可以考虑补充以下信息：\n"
            for question in intent.suggested_questions:
                response += f"- {question}\n"

        return response

    def _generate_suggestion_response(self, intent: IntentAnalysis) -> str:
        """生成建议类型的响应"""
        response = "我有一些建议可以帮助您：\n\n"

        for i, question in enumerate(intent.suggested_questions or [], 1):
            response += f"{i}. {question}\n"

        response += "\n请告诉我更多细节，我可以帮您优化提示词。"

        return response

    def _generate_general_response(self, messages: List[ChatMessage]) -> str:
        """生成一般类型的响应"""
        last_message = self._get_last_user_message(messages)

        if last_message:
            content = last_message.content.lower()

            # 简单的回复逻辑
            if "你好" in content or "您好" in content:
                return "您好！我是 AI 提示词助手，可以帮助您优化 PPT 生成的提示词。请告诉我您想制作什么样的 PPT？"

            if "谢谢" in content or "感谢" in content:
                return "不客气！如果还有其他问题，随时可以问我。"

            if "再见" in content or "拜拜" in content:
                return "再见！祝您使用愉快！"

        # 默认响应
        return "我可以帮助您优化 PPT 生成的提示词。请描述您想制作的 PPT 内容，我会提供专业的建议。"

    async def _generate_llm_response_stream(
        self,
        messages: List[ChatMessage],
        context: Optional[ChatContext] = None,
    ) -> AsyncIterator[ChatResponseChunk]:
        """
        使用真实大模型生成流式响应

        Args:
            messages: 聊天消息列表
            context: 上下文信息

        Yields:
            响应块
        """
        # 构建消息列表
        llm_messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]

        # 添加历史消息
        for msg in messages:
            role_value = (
                msg.role.value if hasattr(msg.role, "value") else msg.role
            )
            llm_messages.append({"role": role_value, "content": msg.content})

        # 创建 LLM 请求
        request = LLMRequest(
            messages=llm_messages,
            temperature=settings.chat_ai_temperature,
            max_tokens=settings.chat_ai_max_tokens,
            stream=True,
        )

        # 获取 LLM 客户端
        client = self._get_llm_client()
        if client is None:
            # 如果无法获取客户端，返回错误
            yield ChatResponseChunk(
                content="抱歉，AI 服务暂时不可用，请检查配置后重试。",
                is_finished=True,
                has_optimized_prompt=False,
                optimized_prompt=None,
                thinking_content=None,
            )
            return

        # 调用大模型流式接口
        full_response = ""

        async for chunk in client.complete_stream(request):
            full_response += chunk.content
            # 不再实时输出，先收集完整响应

        # 提取思考内容和优化后的提示词
        thinking_content = self._extract_thinking_content(full_response)
        optimized_prompt = self._extract_optimized_prompt(full_response)

        if optimized_prompt:
            # 如果有优化提示词，只输出固定结束语
            yield ChatResponseChunk(
                content="如果有哪里不满意，可以直接提出来，我再修改 😊",
                is_finished=False,
                has_optimized_prompt=False,
                optimized_prompt=None,
                thinking_content=thinking_content,
            )
            # 然后输出提示词卡片
            yield ChatResponseChunk(
                content="",
                is_finished=True,
                has_optimized_prompt=True,
                optimized_prompt=optimized_prompt,
                thinking_content=thinking_content,
            )
        else:
            # 没有优化提示词时，清理响应中的标记后输出
            clean_response = self._clean_response(full_response)
            yield ChatResponseChunk(
                content=clean_response,
                is_finished=True,
                has_optimized_prompt=False,
                optimized_prompt=None,
                thinking_content=thinking_content,
            )

    def _clean_response(self, response: str) -> str:
        """
        清理响应中的标记

        Args:
            response: 原始响应内容

        Returns:
            清理后的响应内容
        """
        # 移除思考块
        clean = re.sub(r"\[THINKING_START[^\]]*\]", "", response)
        clean = re.sub(r"\[THINKING_END[^\]]*\]", "", clean)
        # 移除提示词块
        clean = re.sub(
            r"\[PROMPT_START[^\]]*\].*?\[PROMPT_END[^\]]*\]",
            "",
            clean,
            flags=re.DOTALL,
        )
        # 清理多余空白
        clean = re.sub(r"\n{3,}", "\n\n", clean)
        return clean.strip()

    def _extract_thinking_content(self, response: str) -> Optional[str]:
        """
        从大模型响应中提取思考内容

        Args:
            response: 大模型的响应内容

        Returns:
            思考内容，如果没有则返回 None
        """
        # 使用正则表达式匹配，支持标记后跟其他字符的情况
        pattern = r"\[THINKING_START[^\]]*\](.*?)\[THINKING_END[^\]]*\]"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            thinking = match.group(1).strip()
            return thinking if thinking else None
        return None

    def _extract_optimized_prompt(self, response: str) -> Optional[str]:
        """
        从大模型响应中提取优化后的提示词

        Args:
            response: 大模型的响应内容

        Returns:
            优化后的提示词，如果没有则返回 None
        """
        # 使用正则表达式匹配，支持标记后跟其他字符的情况
        pattern = r"\[PROMPT_START[^\]]*\](.*?)\[PROMPT_END[^\]]*\]"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            prompt = match.group(1).strip()
            return prompt if prompt else None
        return None


# 创建全局服务实例
chat_service = ChatService()

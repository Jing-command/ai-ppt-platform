"""
AI 聊天服务模块
处理用户与 AI 提示词助手的对话逻辑
"""

import asyncio
import json
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
        pass

    def analyze_intent(
        self, messages: List[ChatMessage], context: Optional[ChatContext] = None
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
        prompt_score = self._calculate_keyword_score(content, self.PROMPT_KEYWORDS)

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
                suggested_questions=suggested_questions[:3],  # 最多返回3个建议问题
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

    def _get_last_user_message(self, messages: List[ChatMessage]) -> Optional[ChatMessage]:
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

    def _calculate_keyword_score(self, content: str, keywords: List[str]) -> float:
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
        self, messages: List[ChatMessage], context: Optional[ChatContext] = None
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
                    return word

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
        self, messages: List[ChatMessage], context: Optional[ChatContext] = None
    ) -> AsyncIterator[ChatResponseChunk]:
        """
        生成流式响应

        Args:
            messages: 聊天消息列表
            context: 上下文信息

        Yields:
            响应块
        """
        # 分析意图
        intent = self.analyze_intent(messages, context)

        # 根据意图生成响应
        if intent.intent_type == IntentType.CLARIFICATION:
            response_text = self._generate_clarification_response(intent)
            has_optimized = False
            optimized_prompt = None

        elif intent.intent_type == IntentType.PROMPT_OPTIMIZATION:
            response_text = self._generate_optimization_response(intent)
            has_optimized = True
            optimized_prompt = self.generate_optimized_prompt(messages, context)

        elif intent.intent_type == IntentType.SUGGESTION:
            response_text = self._generate_suggestion_response(intent)
            has_optimized = False
            optimized_prompt = None

        else:
            response_text = self._generate_general_response(messages)
            has_optimized = False
            optimized_prompt = None

        # 模拟流式输出 - 逐字符发送
        chunk_size = 3  # 每次发送的字符数

        for i in range(0, len(response_text), chunk_size):
            chunk_content = response_text[i : i + chunk_size]
            is_last = i + chunk_size >= len(response_text)

            yield ChatResponseChunk(
                content=chunk_content,
                is_finished=is_last,
                has_optimized_prompt=has_optimized if is_last else False,
                optimized_prompt=optimized_prompt if is_last else None,
            )

            # 模拟打字延迟
            await asyncio.sleep(0.02)

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


# 创建全局服务实例
chat_service = ChatService()

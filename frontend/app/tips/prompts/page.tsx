// app/tips/prompts/page.tsx
// AI 提示词助手页面 - 帮助用户优化和生成 PPT 提示词

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ArrowLeft,
    Sparkles,
    Wand2,
    Target,
    Lightbulb,
    Users,
    MessageSquare
} from 'lucide-react';
import { ChatMessage, ChatInput, QuickEntry, type MessageData, type QuickEntryItem } from '@/components/chat';
import { sendMessage, type ChatMessage as ApiChatMessage } from '@/lib/api/chat';

/**
 * 快捷入口配置列表
 * 定义用户可以快速开始的对话场景
 */
const quickEntries: QuickEntryItem[] = [
    {
        id: 'optimize',
        icon: Wand2,
        title: '优化提示词',
        description: '让 AI 帮你优化现有的 PPT 提示词，使其更加清晰、专业',
        prompt: '请帮我优化一个 PPT 提示词，让生成的效果更好。'
    },
    {
        id: 'topic',
        icon: Target,
        title: '明确主题',
        description: '不确定 PPT 主题？AI 帮你梳理思路，确定核心内容',
        prompt: '我想做一个 PPT，但还不确定具体主题，能帮我梳理一下思路吗？'
    },
    {
        id: 'creative',
        icon: Lightbulb,
        title: '创意灵感',
        description: '获取 PPT 创意灵感和设计建议，让你的演示更出彩',
        prompt: '我需要一些 PPT 创意灵感，能让我的演示更加出彩吗？'
    },
    {
        id: 'audience',
        icon: Users,
        title: '受众分析',
        description: '分析目标受众，定制最适合的内容风格和表达方式',
        prompt: '请帮我分析 PPT 的目标受众，并给出内容风格建议。'
    }
];

/**
 * AI 提示词助手页面组件
 * 提供聊天式交互，帮助用户优化 PPT 提示词
 */
export default function PromptsAssistantPage() {
    const router = useRouter();

    // 消息列表状态
    const [messages, setMessages] = useState<MessageData[]>([]);
    // 是否正在加载（等待 AI 响应）
    const [isLoading, setIsLoading] = useState(false);
    // 消息列表容器引用，用于自动滚动
    const messagesEndRef = useRef<HTMLDivElement>(null);

    /**
     * 生成唯一 ID
     */
    const generateId = () => `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    /**
     * 滚动到消息列表底部
     */
    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, []);

    /**
     * 页面加载时的初始化
     * 添加 AI 欢迎消息
     */
    useEffect(() => {
        // 添加欢迎消息
        const welcomeMessage: MessageData = {
            id: generateId(),
            role: 'assistant',
            content: `你好！我是 AI 提示词助手，专门帮助你优化和生成 PPT 提示词。

你可以：
• 直接输入你的想法，我会帮你优化
• 点击左侧快捷入口，快速开始常见任务
• 询问任何关于 PPT 制作的问题

让我们一起打造完美的 PPT 提示词吧！`
        };
        setMessages([welcomeMessage]);
    }, []);

    /**
     * 消息更新时自动滚动到底部
     */
    useEffect(() => {
        scrollToBottom();
    }, [messages, scrollToBottom]);

    /**
     * 处理发送消息
     * @param content - 用户输入的消息内容
     */
    const handleSendMessage = async (content: string) => {
        // 创建用户消息
        const userMessage: MessageData = {
            id: generateId(),
            role: 'user',
            content
        };

        // 创建 AI 消息占位（用于流式输出）
        const aiMessageId = generateId();
        const aiMessage: MessageData = {
            id: aiMessageId,
            role: 'assistant',
            content: '',
            isStreaming: true
        };

        // 更新消息列表：添加用户消息和 AI 消息占位
        setMessages(prev => [...prev, userMessage, aiMessage]);
        setIsLoading(true);

        // 准备 API 请求的消息历史
        const apiMessages: ApiChatMessage[] = [...messages, userMessage]
            .map(msg => ({
                role: msg.role,
                content: msg.content
            }));

        try {
            // 调用聊天 API，处理流式响应
            await sendMessage({
                messages: apiMessages,
                // 接收到数据块时的回调
                onChunk: (chunk) => {
                    setMessages(prev => prev.map(msg => {
                        // 只更新当前 AI 消息
                        if (msg.id === aiMessageId) {
                            return {
                                ...msg,
                                // 追加内容
                                content: msg.content + chunk.content,
                                // 如果完成，更新状态
                                isStreaming: !chunk.isFinished,
                                // 如果有优化后的提示词，保存
                                optimizedPrompt: chunk.optimizedPrompt || msg.optimizedPrompt
                            };
                        }
                        return msg;
                    }));
                },
                // 错误回调
                onError: (error) => {
                    console.error('聊天请求失败:', error);
                    // 更新 AI 消息为错误状态
                    setMessages(prev => prev.map(msg => {
                        if (msg.id === aiMessageId) {
                            return {
                                ...msg,
                                content: '抱歉，发生了错误，请稍后重试。',
                                isStreaming: false
                            };
                        }
                        return msg;
                    }));
                },
                // 完成回调
                onComplete: () => {
                    setIsLoading(false);
                }
            });
        } catch (error) {
            console.error('发送消息失败:', error);
            setIsLoading(false);
        }
    };

    /**
     * 处理快捷入口点击
     * @param prompt - 快捷入口的提示词
     */
    const handleQuickEntryClick = (prompt: string) => {
        handleSendMessage(prompt);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
            {/* 背景装饰 */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-200/30 rounded-full blur-3xl" />
                <div className="absolute top-1/2 -left-40 w-80 h-80 bg-indigo-200/20 rounded-full blur-3xl" />
                <div className="absolute -bottom-40 right-1/4 w-96 h-96 bg-purple-200/20 rounded-full blur-3xl" />
            </div>

            {/* 导航栏 */}
            <motion.nav
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative z-10 bg-white/80 backdrop-blur-md border-b border-gray-200/50"
            >
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 items-center">
                        {/* 返回按钮 */}
                        <button
                            onClick={() => router.push('/dashboard')}
                            className="flex items-center gap-2 text-gray-500 hover:text-gray-900 transition-colors group"
                        >
                            <div className="p-2 rounded-lg group-hover:bg-gray-100 transition-colors">
                                <ArrowLeft className="w-5 h-5" />
                            </div>
                            <span className="font-medium">返回</span>
                        </button>

                        {/* 标题 */}
                        <div className="ml-6 flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20">
                                <Sparkles className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h1 className="font-semibold text-gray-900">AI 提示词助手</h1>
                                <p className="text-xs text-gray-500">智能优化你的 PPT 提示词</p>
                            </div>
                        </div>
                    </div>
                </div>
            </motion.nav>

            {/* 主内容区域 */}
            <main className="relative z-10 flex h-[calc(100vh-64px)]">
                {/* 左侧：快捷入口区域 */}
                <aside className="w-1/4 min-w-[280px] max-w-[320px] border-r border-gray-200/50 bg-white/50 backdrop-blur-sm p-6 overflow-y-auto">
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        {/* 区域标题 */}
                        <div className="mb-6">
                            <h2 className="text-lg font-semibold text-gray-900 mb-2">快捷入口</h2>
                            <p className="text-sm text-gray-500">选择一个场景快速开始</p>
                        </div>

                        {/* 快捷入口列表 */}
                        <div className="space-y-4">
                            {quickEntries.map((entry, index) => (
                                <QuickEntry
                                    key={entry.id}
                                    item={entry}
                                    onClick={handleQuickEntryClick}
                                    index={index}
                                />
                            ))}
                        </div>

                        {/* 使用提示 */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.5 }}
                            className="mt-8 p-4 bg-blue-50 rounded-xl border border-blue-100"
                        >
                            <div className="flex items-start gap-3">
                                <MessageSquare className="w-5 h-5 text-blue-500 mt-0.5" />
                                <div>
                                    <p className="text-sm font-medium text-blue-700 mb-1">使用提示</p>
                                    <p className="text-xs text-blue-600/80">
                                        直接在右侧输入你的想法，AI 会帮你优化成专业的 PPT 提示词
                                    </p>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                </aside>

                {/* 右侧：聊天区域 */}
                <div className="flex-1 flex flex-col">
                    {/* 消息列表 */}
                    <div className="flex-1 overflow-y-auto p-6">
                        <div className="max-w-3xl mx-auto space-y-6">
                            <AnimatePresence mode="popLayout">
                                {messages.map((message) => (
                                    <ChatMessage key={message.id} message={message} />
                                ))}
                            </AnimatePresence>

                            {/* 滚动锚点 */}
                            <div ref={messagesEndRef} />
                        </div>
                    </div>

                    {/* 输入区域 */}
                    <ChatInput
                        onSend={handleSendMessage}
                        disabled={isLoading}
                        placeholder="输入你的想法或问题..."
                    />
                </div>
            </main>
        </div>
    );
}

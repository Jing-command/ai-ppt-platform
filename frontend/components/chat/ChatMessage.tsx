// components/chat/ChatMessage.tsx
// 聊天消息组件 - 显示用户和 AI 的对话消息

'use client';

import {motion} from 'framer-motion';
import {Sparkles, User} from 'lucide-react';
import PromptCard from './PromptCard';

/**
 * 消息数据类型
 */
export interface MessageData {
    id: string;                    // 消息唯一标识
    role: 'user' | 'assistant';    // 消息角色
    content: string;               // 消息内容
    optimizedPrompt?: string;      // 优化后的提示词（仅 AI 消息）
    isStreaming?: boolean;         // 是否正在流式输出
}

/**
 * ChatMessage 组件属性
 */
interface ChatMessageProps {
    message: MessageData;          // 消息数据
}

/**
 * 聊天消息组件
 * 根据角色显示不同样式的消息气泡
 * AI 消息支持显示优化后的提示词卡片
 */
export default function ChatMessage({message}: ChatMessageProps) {
    // 判断是否是用户消息
    const isUser = message.role === 'user';

    return (
        <motion.div
            // 入场动画：淡入 + 滑动
            initial={{opacity: 0, y: 20}}
            animate={{opacity: 1, y: 0}}
            transition={{duration: 0.3}}
            className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
        >
            {/* 头像区域 */}
            <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
                {isUser ? (
                    // 用户头像：蓝色渐变背景
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                        <User className="w-5 h-5 text-white" />
                    </div>
                ) : (
                    // AI 头像：紫色渐变背景
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
                        <Sparkles className="w-5 h-5 text-white" />
                    </div>
                )}
            </div>

            {/* 消息内容区域 */}
            <div className={`flex-1 max-w-[80%] ${isUser ? 'text-right' : 'text-left'}`}>
                {/* 消息气泡 */}
                <motion.div
                    // 气泡动画：轻微缩放
                    initial={{scale: 0.95}}
                    animate={{scale: 1}}
                    transition={{duration: 0.2}}
                    className={`
                        inline-block px-5 py-3.5 rounded-2xl
                        ${isUser
        // 用户消息：蓝色背景，右对齐
            ? 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white rounded-tr-md'
        // AI 消息：灰色背景，左对齐
            : 'bg-white text-gray-800 rounded-tl-md shadow-sm border border-gray-100'
        }
                    `}
                >
                    {/* 消息文本内容 */}
                    <p className={`text-sm leading-relaxed whitespace-pre-wrap ${isUser ? 'text-white' : 'text-gray-700'}`}>
                        {message.content}
                        {/* 流式输出时的光标动画 */}
                        {message.isStreaming && (
                            <motion.span
                                animate={{opacity: [1, 0]}}
                                transition={{duration: 0.5, repeat: Infinity, repeatType: 'reverse'}}
                                className="inline-block w-2 h-4 ml-0.5 bg-current align-middle"
                            />
                        )}
                    </p>
                </motion.div>

                {/* 优化后的提示词卡片（仅 AI 消息且有优化提示词时显示） */}
                {!isUser && message.optimizedPrompt && (
                    <motion.div
                        // 卡片入场动画：淡入 + 向上滑动
                        initial={{opacity: 0, y: 10}}
                        animate={{opacity: 1, y: 0}}
                        transition={{duration: 0.3, delay: 0.2}}
                        className="mt-3"
                    >
                        <PromptCard optimizedPrompt={message.optimizedPrompt} />
                    </motion.div>
                )}
            </div>
        </motion.div>
    );
}

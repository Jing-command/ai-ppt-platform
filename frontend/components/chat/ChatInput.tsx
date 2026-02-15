// components/chat/ChatInput.tsx
// 聊天输入组件 - 支持文本输入和发送消息

'use client';

import {useState, useRef, useEffect, KeyboardEvent} from 'react';
import {motion} from 'framer-motion';
import {Send, Loader2} from 'lucide-react';

/**
 * ChatInput 组件属性
 */
interface ChatInputProps {
    onSend: (message: string) => void;  // 发送消息回调
    disabled?: boolean;                  // 是否禁用输入
    placeholder?: string;                // 输入框占位符
}

/**
 * 聊天输入组件
 * 支持多行输入、回车发送、自动高度调整
 */
export default function ChatInput({
    onSend,
    disabled = false,
    placeholder = '输入你的问题...'
}: ChatInputProps) {
    // 输入内容状态
    const [input, setInput] = useState('');
    // 文本框引用，用于自动调整高度
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    /**
     * 自动调整文本框高度
     * 根据内容动态调整高度，最大 5 行
     */
    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) {
            // 重置高度以获取正确的 scrollHeight
            textarea.style.height = 'auto';
            // 设置新高度（最大 120px，约 5 行）
            textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
        }
    }, [input]);

    /**
     * 处理发送消息
     */
    const handleSend = () => {
        // 检查输入是否有效
        const trimmedInput = input.trim();
        if (!trimmedInput || disabled) {
            return;
        }

        // 调用发送回调
        onSend(trimmedInput);
        // 清空输入
        setInput('');
    };

    /**
     * 处理键盘事件
     * Enter 发送消息（Shift+Enter 换行）
     */
    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        // Enter 键且未按 Shift，发送消息
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();  // 阻止默认换行行为
            handleSend();
        }
    };

    // 判断是否可以发送（有内容且未禁用）
    const canSend = input.trim().length > 0 && !disabled;

    return (
        <div className="bg-white border-t border-gray-100 p-4">
            {/* 输入区域容器 */}
            <div className="max-w-4xl mx-auto">
                <div className="relative flex items-end gap-3 bg-gray-50 rounded-2xl border-2 border-gray-200/50 p-3 transition-all duration-300 focus-within:border-blue-400 focus-within:shadow-[0_0_20px_rgba(59,130,246,0.1)]">
                    {/* 文本输入框 */}
                    <textarea
                        ref={textareaRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={placeholder}
                        disabled={disabled}
                        rows={1}
                        className="flex-1 bg-transparent text-gray-800 placeholder:text-gray-400 resize-none outline-none text-sm leading-relaxed py-2"
                        style={{minHeight: '40px'}}
                    />

                    {/* 发送按钮 */}
                    <motion.button
                        onClick={handleSend}
                        disabled={!canSend}
                        // 按钮动画：可用时轻微缩放
                        whileHover={canSend ? {scale: 1.05} : {}}
                        whileTap={canSend ? {scale: 0.95} : {}}
                        className={`
                            flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center
                            transition-all duration-200
                            ${canSend
        // 可发送状态：蓝色渐变背景
            ? 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/30 cursor-pointer'
        // 禁用状态：灰色背景
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
        }
                        `}
                    >
                        {disabled ? (
                            // 加载中状态：显示旋转图标
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            // 正常状态：显示发送图标
                            <Send className="w-5 h-5" />
                        )}
                    </motion.button>
                </div>

                {/* 底部提示 */}
                <p className="text-center text-xs text-gray-400 mt-2">
                    按 Enter 发送，Shift + Enter 换行
                </p>
            </div>
        </div>
    );
}

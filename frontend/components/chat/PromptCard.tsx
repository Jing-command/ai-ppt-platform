// components/chat/PromptCard.tsx
// 优化提示词卡片组件 - 显示优化后的提示词并提供操作按钮

'use client';

import {useState} from 'react';
import {useRouter} from 'next/navigation';
import {motion} from 'framer-motion';
import {Copy, Check, ArrowRight, Sparkles} from 'lucide-react';

/**
 * PromptCard 组件属性
 */
interface PromptCardProps {
    optimizedPrompt: string;  // 优化后的提示词内容
}

/**
 * 优化提示词卡片组件
 * 显示 AI 优化后的提示词，支持复制和使用
 */
export default function PromptCard({optimizedPrompt}: PromptCardProps) {
    const router = useRouter();
    // 复制状态：是否已复制
    const [copied, setCopied] = useState(false);

    /**
     * 复制提示词到剪贴板
     */
    const handleCopy = async () => {
        try {
            // 使用 Clipboard API 复制文本
            await navigator.clipboard.writeText(optimizedPrompt);
            // 设置复制成功状态
            setCopied(true);
            // 2 秒后重置状态
            setTimeout(() => setCopied(false), 2000);
        } catch (error) {
            // 复制失败，使用降级方案
            console.error('复制失败:', error);
            // 创建临时文本区域进行复制
            const textarea = document.createElement('textarea');
            textarea.value = optimizedPrompt;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    /**
     * 使用此提示词跳转到大纲生成页面
     */
    const handleUsePrompt = () => {
        // 将提示词存储到 sessionStorage，供目标页面读取
        sessionStorage.setItem('promptFromAssistant', optimizedPrompt);
        // 跳转到大纲生成页面
        router.push('/outlines/new');
    };

    return (
        <motion.div
            // 卡片入场动画：淡入 + 缩放
            initial={{opacity: 0, scale: 0.95}}
            animate={{opacity: 1, scale: 1}}
            transition={{duration: 0.3}}
            className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-2xl border border-blue-200/50 overflow-hidden"
        >
            {/* 卡片头部 */}
            <div className="flex items-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-100/50 to-indigo-100/50 border-b border-blue-200/30">
                {/* AI 图标 */}
                <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                    <Sparkles className="w-3.5 h-3.5 text-white" />
                </div>
                {/* 标题 */}
                <span className="text-sm font-medium text-blue-700">
                    优化后的提示词
                </span>
            </div>

            {/* 提示词内容 */}
            <div className="px-4 py-4">
                <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {optimizedPrompt}
                </p>
            </div>

            {/* 操作按钮区域 */}
            <div className="flex items-center gap-2 px-4 pb-4">
                {/* 复制按钮 */}
                <motion.button
                    onClick={handleCopy}
                    // 按钮动画：悬停缩放
                    whileHover={{scale: 1.02}}
                    whileTap={{scale: 0.98}}
                    className={`
                        flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium
                        transition-all duration-200
                        ${copied
        // 已复制状态：绿色背景
            ? 'bg-green-100 text-green-700 border border-green-200'
        // 默认状态：白色背景
            : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50 hover:border-gray-300'
        }
                    `}
                >
                    {copied ? (
                        // 已复制图标
                        <>
                            <Check className="w-4 h-4" />
                            <span>已复制</span>
                        </>
                    ) : (
                        // 复制图标
                        <>
                            <Copy className="w-4 h-4" />
                            <span>复制</span>
                        </>
                    )}
                </motion.button>

                {/* 使用此提示词按钮 */}
                <motion.button
                    onClick={handleUsePrompt}
                    // 按钮动画：悬停缩放
                    whileHover={{scale: 1.02}}
                    whileTap={{scale: 0.98}}
                    className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-200"
                >
                    <span>使用此提示词</span>
                    <ArrowRight className="w-4 h-4" />
                </motion.button>
            </div>
        </motion.div>
    );
}

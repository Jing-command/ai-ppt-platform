// components/chat/QuickEntry.tsx
// 快捷入口组件 - 显示快捷操作卡片

'use client';

import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';

/**
 * 快捷入口项配置类型
 */
export interface QuickEntryItem {
    id: string;           // 唯一标识
    icon: LucideIcon;     // 图标组件
    title: string;        // 标题
    description: string;  // 描述文本
    prompt: string;       // 点击时发送的提示词
}

/**
 * QuickEntry 组件属性
 */
interface QuickEntryProps {
    item: QuickEntryItem;           // 快捷入口配置
    onClick: (prompt: string) => void;  // 点击回调
    index?: number;                 // 索引用于动画延迟
}

/**
 * 快捷入口组件
 * 显示一个可点击的快捷操作卡片
 */
export default function QuickEntry({ item, onClick, index = 0 }: QuickEntryProps) {
    const Icon = item.icon;

    return (
        <motion.button
            onClick={() => onClick(item.prompt)}
            // 入场动画：淡入 + 向上滑动，带延迟
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            // 悬停动画：缩放 + 上移
            whileHover={{
                scale: 1.03,
                y: -4,
                transition: { duration: 0.2 }
            }}
            // 点击动画：缩小
            whileTap={{ scale: 0.98 }}
            className="group relative w-full bg-white rounded-2xl p-5 shadow-sm hover:shadow-xl border border-gray-200/50 hover:border-blue-300/50 transition-all duration-300 text-left overflow-hidden"
        >
            {/* 悬停背景效果：渐变叠加 */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50/0 via-blue-50/0 to-indigo-50/0 group-hover:from-blue-50/80 group-hover:via-blue-50/40 group-hover:to-indigo-50/60 transition-all duration-500" />

            <div className="relative z-10">
                {/* 图标容器 */}
                <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300">
                    <Icon className="w-6 h-6 text-blue-600" />
                </div>

                {/* 标题 */}
                <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-blue-700 transition-colors">
                    {item.title}
                </h3>

                {/* 描述 */}
                <p className="text-sm text-gray-500 line-clamp-2">
                    {item.description}
                </p>

                {/* 点击提示（悬停时显示） */}
                <div className="mt-3 flex items-center gap-1 text-xs text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <span>点击开始对话</span>
                </div>
            </div>
        </motion.button>
    );
}

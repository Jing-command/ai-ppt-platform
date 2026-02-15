// components/visualization/ChartSelector/ChartCard.tsx
// 图表卡片组件 - 显示单个图表的预览和选择

'use client';

import {motion} from 'framer-motion';
import {Check} from 'lucide-react';
import * as LucideIcons from 'lucide-react';
import type {ChartConfig} from '@/types/visualization';

/**
 * 动态获取 Lucide 图标组件
 * @param iconName - 图标名称
 * @returns 图标组件或默认图标
 */
function getIconComponent(iconName: string): React.ReactNode {
    // 将图标名称转换为 PascalCase 格式
    const pascalCaseName = iconName
        .split('-')
        .map(part => part.charAt(0).toUpperCase() + part.slice(1))
        .join('');

    // 从 Lucide 图标库中获取对应图标
    const IconComponent = (LucideIcons as unknown as Record<string, React.ComponentType<{ className?: string }>>)[pascalCaseName];

    // 返回图标或默认图标
    return IconComponent
        ? <IconComponent className="w-6 h-6" />
        : <LucideIcons.BarChart3 className="w-6 h-6" />;
}

/**
 * ChartCard 组件属性
 */
interface ChartCardProps {
    /** 图表配置信息 */
    config: ChartConfig;
    /** 点击回调 */
    onClick: () => void;
    /** 是否选中 */
    isSelected?: boolean;
}

/**
 * 图表卡片组件
 * 显示图表图标、名称和描述，支持选中和点击交互
 */
export default function ChartCard({
    config,
    onClick,
    isSelected = false
}: ChartCardProps) {
    return (
        <motion.div
            onClick={onClick}
            // 卡片动画：悬停上浮 + 选中缩放
            whileHover={{y: -4, scale: 1.02}}
            whileTap={{scale: 0.98}}
            transition={{duration: 0.1}}
            className={`
                relative p-4 rounded-xl cursor-pointer
                border-2 transition-colors duration-100
                ${isSelected
        // 选中状态：蓝色边框 + 浅蓝背景
            ? 'border-blue-500 bg-blue-50'
        // 非选中状态：灰色边框 + 白色背景
            : 'border-gray-200 bg-white hover:border-blue-300 hover:bg-gray-50'
        }
            `}
        >
            {/* 选中指示器 */}
            {isSelected && (
                <motion.div
                    // 选中标记动画：缩放淡入
                    initial={{scale: 0, opacity: 0}}
                    animate={{scale: 1, opacity: 1}}
                    transition={{duration: 0.1}}
                    className="absolute top-2 right-2 w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center"
                >
                    <Check className="w-3 h-3 text-white" />
                </motion.div>
            )}

            {/* 图标区域 */}
            <div
                className={`
                    w-12 h-12 rounded-lg flex items-center justify-center mb-3
                    transition-colors duration-100
                    ${isSelected
        // 选中状态：蓝色背景
            ? 'bg-blue-100 text-blue-600'
        // 非选中状态：灰色背景
            : 'bg-gray-100 text-gray-600'
        }
                `}
            >
                {getIconComponent(config.icon)}
            </div>

            {/* 图表名称 */}
            <h3
                className={`
                    font-semibold text-sm mb-1
                    transition-colors duration-100
                    ${isSelected ? 'text-blue-700' : 'text-gray-800'}
                `}
            >
                {config.name}
            </h3>

            {/* 图表描述 */}
            <p className="text-xs text-gray-500 line-clamp-2">
                {config.description}
            </p>

            {/* 使用场景标签 */}
            {config.useCases.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                    {config.useCases.slice(0, 2).map((useCase, index) => (
                        <span
                            key={index}
                            className="px-1.5 py-0.5 text-[10px] rounded bg-gray-100 text-gray-500"
                        >
                            {useCase}
                        </span>
                    ))}
                </div>
            )}
        </motion.div>
    );
}

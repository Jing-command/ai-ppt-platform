// components/visualization/ChartPreview/StyleEditor.tsx
// 样式编辑组件 - 用于配置图表的视觉样式

'use client';

import { motion } from 'framer-motion';
import { Palette, Type, Sparkles, Settings2 } from 'lucide-react';
import type { ChartStyleConfig } from '@/types/visualization';

/**
 * 预设配色方案
 */
const COLOR_PALETTES = [
    {
        name: '默认',
        colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']
    },
    {
        name: '科技蓝',
        colors: ['#3b82f6', '#60a5fa', '#93c5fd', '#1d4ed8', '#2563eb', '#1e40af', '#1e3a8a', '#172554']
    },
    {
        name: '自然绿',
        colors: ['#22c55e', '#4ade80', '#86efac', '#16a34a', '#15803d', '#166534', '#14532d', '#052e16']
    },
    {
        name: '温暖橙',
        colors: ['#f97316', '#fb923c', '#fdba74', '#ea580c', '#c2410c', '#9a3412', '#7c2d12', '#431407']
    },
    {
        name: '优雅紫',
        colors: ['#a855f7', '#c084fc', '#d8b4fe', '#9333ea', '#7e22ce', '#6b21a8', '#581c87', '#3b0764']
    },
    {
        name: '商务灰',
        colors: ['#6b7280', '#9ca3af', '#d1d5db', '#4b5563', '#374151', '#1f2937', '#111827', '#030712']
    }
];

/**
 * StyleEditor 组件属性
 */
interface StyleEditorProps {
    /** 当前样式配置 */
    config: ChartStyleConfig;
    /** 样式变更回调 */
    onChange: (config: ChartStyleConfig) => void;
}

/**
 * 样式编辑组件
 * 提供标题、配色主题、动画等样式配置功能
 */
export default function StyleEditor({
    config,
    onChange
}: StyleEditorProps) {
    /**
     * 处理标题变更
     */
    const handleTitleChange = (title: string) => {
        onChange({
            ...config,
            // 通过 customTheme 存储标题
            customTheme: {
                ...config.customTheme,
                title
            }
        });
    };

    /**
     * 处理配色方案变更
     */
    const handlePaletteChange = (colors: string[]) => {
        onChange({
            ...config,
            colorPalette: colors
        });
    };

    /**
     * 处理动画开关变更
     */
    const handleAnimationChange = (enabled: boolean) => {
        onChange({
            ...config,
            animation: {
                ...config.animation,
                enabled
            }
        });
    };

    /**
     * 处理主题变更
     */
    const handleThemeChange = (theme: 'light' | 'dark') => {
        onChange({
            ...config,
            theme
        });
    };

    return (
        <div className="space-y-5">
            {/* 标题 */}
            <div className="flex items-center gap-2 text-sm font-medium text-gray-800">
                <Settings2 className="w-4 h-4 text-blue-500" />
                <span>样式配置</span>
            </div>

            {/* 图表标题输入 */}
            <div className="space-y-1.5">
                <label className="flex items-center gap-1.5 text-sm font-medium text-gray-700">
                    <Type className="w-4 h-4" />
                    <span>图表标题</span>
                </label>
                <input
                    type="text"
                    value={(config.customTheme?.title as string) || ''}
                    onChange={(e) => handleTitleChange(e.target.value)}
                    placeholder="输入图表标题..."
                    className="
                        w-full px-3 py-2 text-sm rounded-lg
                        border border-gray-200 bg-white
                        focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500
                    "
                />
            </div>

            {/* 配色主题选择 */}
            <div className="space-y-2">
                <label className="flex items-center gap-1.5 text-sm font-medium text-gray-700">
                    <Palette className="w-4 h-4" />
                    <span>配色主题</span>
                </label>

                <div className="grid grid-cols-2 gap-2">
                    {COLOR_PALETTES.map((palette) => {
                        // 判断是否为当前选中的配色
                        const isSelected = JSON.stringify(config.colorPalette) === JSON.stringify(palette.colors);

                        return (
                            <motion.button
                                key={palette.name}
                                onClick={() => handlePaletteChange(palette.colors)}
                                // 按钮动画：悬停缩放
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                className={`
                                    p-2 rounded-lg border-2 transition-colors duration-100
                                    ${isSelected
                                        ? 'border-blue-500 bg-blue-50'
                                        : 'border-gray-200 bg-white hover:border-gray-300'
                                    }
                                `}
                            >
                                {/* 配色名称 */}
                                <p className="text-xs font-medium text-gray-700 mb-1.5">
                                    {palette.name}
                                </p>

                                {/* 颜色预览 */}
                                <div className="flex gap-0.5">
                                    {palette.colors.slice(0, 6).map((color, index) => (
                                        <div
                                            key={index}
                                            className="w-4 h-4 rounded-sm"
                                            style={{ backgroundColor: color }}
                                        />
                                    ))}
                                </div>
                            </motion.button>
                        );
                    })}
                </div>
            </div>

            {/* 主题模式切换 */}
            <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                    主题模式
                </label>
                <div className="flex gap-2">
                    <motion.button
                        onClick={() => handleThemeChange('light')}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className={`
                            flex-1 py-2 px-3 rounded-lg text-sm font-medium
                            border-2 transition-colors duration-100
                            ${config.theme === 'light'
                                ? 'border-blue-500 bg-blue-50 text-blue-700'
                                : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                            }
                        `}
                    >
                        浅色
                    </motion.button>
                    <motion.button
                        onClick={() => handleThemeChange('dark')}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className={`
                            flex-1 py-2 px-3 rounded-lg text-sm font-medium
                            border-2 transition-colors duration-100
                            ${config.theme === 'dark'
                                ? 'border-blue-500 bg-blue-50 text-blue-700'
                                : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                            }
                        `}
                    >
                        深色
                    </motion.button>
                </div>
            </div>

            {/* 动画开关 */}
            <div className="flex items-center justify-between">
                <label className="flex items-center gap-1.5 text-sm font-medium text-gray-700">
                    <Sparkles className="w-4 h-4" />
                    <span>启用动画</span>
                </label>

                {/* 开关按钮 */}
                <motion.button
                    onClick={() => handleAnimationChange(!config.animation.enabled)}
                    // 开关动画：切换效果
                    whileTap={{ scale: 0.95 }}
                    className={`
                        relative w-12 h-6 rounded-full transition-colors duration-100
                        ${config.animation.enabled
                            ? 'bg-blue-500'
                            : 'bg-gray-300'
                        }
                    `}
                >
                    {/* 开关滑块 */}
                    <motion.div
                        className="absolute top-1 w-4 h-4 rounded-full bg-white shadow-sm"
                        animate={{
                            left: config.animation.enabled ? '28px' : '4px'
                        }}
                        transition={{ duration: 0.1 }}
                    />
                </motion.button>
            </div>

            {/* 显示选项 */}
            <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                    显示选项
                </label>

                <div className="space-y-1.5">
                    {/* 显示图例 */}
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={config.showLegend}
                            onChange={(e) => onChange({ ...config, showLegend: e.target.checked })}
                            className="w-4 h-4 rounded border-gray-300 text-blue-500 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-600">显示图例</span>
                    </label>

                    {/* 显示工具提示 */}
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={config.showTooltip}
                            onChange={(e) => onChange({ ...config, showTooltip: e.target.checked })}
                            className="w-4 h-4 rounded border-gray-300 text-blue-500 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-600">显示工具提示</span>
                    </label>

                    {/* 显示网格线 */}
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={config.showGrid}
                            onChange={(e) => onChange({ ...config, showGrid: e.target.checked })}
                            className="w-4 h-4 rounded border-gray-300 text-blue-500 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-600">显示网格线</span>
                    </label>
                </div>
            </div>
        </div>
    );
}

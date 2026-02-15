// components/visualization/ChartSelector/CategoryTabs.tsx
// 图表分类标签组件 - 用于切换不同类别的图表

'use client';

import { motion } from 'framer-motion';
import {
    BarChart3,
    TrendingUp,
    Map,
    GitBranch,
    Sparkles
} from 'lucide-react';
import type { ChartCategory } from '@/types/visualization';

/**
 * 分类标签项配置
 * @description 定义每个分类的显示信息
 */
interface CategoryTabItem {
    /** 分类标识 */
    key: ChartCategory;
    /** 分类中文名称 */
    label: string;
    /** 分类图标 */
    icon: React.ReactNode;
}

/**
 * 分类标签列表配置
 */
const CATEGORY_TABS: CategoryTabItem[] = [
    {
        key: 'basic',
        label: '基础图表',
        icon: <BarChart3 className="w-4 h-4" />
    },
    {
        key: 'statistical',
        label: '统计图表',
        icon: <TrendingUp className="w-4 h-4" />
    },
    {
        key: 'map',
        label: '地图',
        icon: <Map className="w-4 h-4" />
    },
    {
        key: 'relation',
        label: '关系图',
        icon: <GitBranch className="w-4 h-4" />
    },
    {
        key: 'special',
        label: '特殊图表',
        icon: <Sparkles className="w-4 h-4" />
    }
];

/**
 * CategoryTabs 组件属性
 */
interface CategoryTabsProps {
    /** 当前激活的分类 */
    activeCategory: ChartCategory;
    /** 分类切换回调 */
    onChange: (category: ChartCategory) => void;
}

/**
 * 图表分类标签组件
 * 显示图表分类选项卡，支持切换不同类型的图表
 */
export default function CategoryTabs({
    activeCategory,
    onChange
}: CategoryTabsProps) {
    return (
        <div className="flex items-center gap-1 p-1 bg-gray-100 rounded-xl">
            {CATEGORY_TABS.map((tab) => {
                // 判断当前标签是否激活
                const isActive = activeCategory === tab.key;

                return (
                    <motion.button
                        key={tab.key}
                        onClick={() => onChange(tab.key)}
                        // 按钮动画：悬停缩放
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className={`
                            relative flex items-center gap-1.5 px-3 py-2 rounded-lg
                            text-sm font-medium transition-colors duration-100
                            ${isActive
                                // 激活状态：白色背景 + 主色调文字
                                ? 'text-blue-600'
                                // 非激活状态：灰色文字
                                : 'text-gray-500 hover:text-gray-700'
                            }
                        `}
                    >
                        {/* 激活状态背景 */}
                        {isActive && (
                            <motion.div
                                // 背景滑入动画
                                layoutId="categoryTabBg"
                                initial={false}
                                transition={{
                                    type: 'spring',
                                    stiffness: 500,
                                    damping: 35
                                }}
                                className="absolute inset-0 bg-white rounded-lg shadow-sm"
                            />
                        )}

                        {/* 图标 */}
                        <span className="relative z-10">
                            {tab.icon}
                        </span>

                        {/* 标签文字 */}
                        <span className="relative z-10 hidden sm:inline">
                            {tab.label}
                        </span>
                    </motion.button>
                );
            })}
        </div>
    );
}

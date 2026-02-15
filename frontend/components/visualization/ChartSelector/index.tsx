// components/visualization/ChartSelector/index.tsx
// 图表选择器主组件 - 显示分类标签和图表卡片网格

'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X } from 'lucide-react';
import type { ChartType, ChartCategory, ChartConfig } from '@/types/visualization';
import { chartConfigs } from '@/lib/charts/chartConfigs';
import CategoryTabs from './CategoryTabs';
import ChartCard from './ChartCard';

// 使用共享的图表配置
const CHART_CONFIGS = chartConfigs;

/**
 * ChartSelector 组件属性
 */
interface ChartSelectorProps {
    /** 图表选择回调 */
    onSelect: (chartType: ChartType) => void;
    /** 当前选中的图表类型 */
    selectedType?: ChartType;
}

/**
 * 图表选择器主组件
 * 提供分类标签筛选、搜索功能和图表卡片网格展示
 */
export default function ChartSelector({
    onSelect,
    selectedType
}: ChartSelectorProps) {
    // 当前选中的分类
    const [activeCategory, setActiveCategory] = useState<ChartCategory>('basic');
    // 搜索关键词
    const [searchKeyword, setSearchKeyword] = useState('');

    /**
     * 根据分类和搜索关键词过滤图表列表
     */
    const filteredCharts = useMemo(() => {
        return CHART_CONFIGS.filter(config => {
            // 分类过滤
            const categoryMatch = config.category === activeCategory;
            // 搜索过滤
            const searchMatch = searchKeyword === '' ||
                config.name.toLowerCase().includes(searchKeyword.toLowerCase()) ||
                config.nameEn.toLowerCase().includes(searchKeyword.toLowerCase()) ||
                config.description.toLowerCase().includes(searchKeyword.toLowerCase());
            return categoryMatch && searchMatch;
        });
    }, [activeCategory, searchKeyword]);

    /**
     * 处理分类切换
     */
    const handleCategoryChange = (category: ChartCategory) => {
        setActiveCategory(category);
        setSearchKeyword('');
    };

    /**
     * 处理图表选择
     */
    const handleChartSelect = (chartType: ChartType) => {
        onSelect(chartType);
    };

    return (
        <div className="flex flex-col gap-4">
            {/* 顶部工具栏：分类标签 + 搜索框 */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                {/* 分类标签 */}
                <CategoryTabs
                    activeCategory={activeCategory}
                    onChange={handleCategoryChange}
                />

                {/* 搜索框 */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                        type="text"
                        value={searchKeyword}
                        onChange={(e) => setSearchKeyword(e.target.value)}
                        placeholder="搜索图表..."
                        className="
                            w-full sm:w-64 pl-10 pr-10 py-2
                            text-sm rounded-lg
                            border border-gray-200 bg-white
                            focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500
                        "
                    />
                    {/* 清空按钮 */}
                    {searchKeyword && (
                        <button
                            onClick={() => setSearchKeyword('')}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    )}
                </div>
            </div>

            {/* 图表卡片网格 */}
            <AnimatePresence mode="wait">
                {filteredCharts.length > 0 ? (
                    <motion.div
                        key={activeCategory}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.1 }}
                        className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4"
                    >
                        {filteredCharts.map((config, index) => (
                            <motion.div
                                key={config.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.02, duration: 0.1 }}
                            >
                                <ChartCard
                                    config={config}
                                    onClick={() => handleChartSelect(config.type as ChartType)}
                                    isSelected={selectedType === config.type}
                                />
                            </motion.div>
                        ))}
                    </motion.div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex flex-col items-center justify-center py-12 text-gray-400"
                    >
                        <Search className="w-12 h-12 mb-4 opacity-50" />
                        <p>未找到匹配的图表</p>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

// 导出图表配置供其他模块使用
export { CHART_CONFIGS };

// components/visualization/StoredCharts/StoredChartCard.tsx
// 暂存图表卡片组件 - 显示单个暂存图表的信息

'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Trash2,
    Clock,
    BarChart3,
    TrendingUp,
    PieChart,
    Image as ImageIcon
} from 'lucide-react';
import type { StoredChart, ChartType } from '@/types/visualization';

/**
 * 图表类型图标映射
 */
const CHART_TYPE_ICONS: Record<ChartType, React.ReactNode> = {
    bar: <BarChart3 className="w-4 h-4" />,
    line: <TrendingUp className="w-4 h-4" />,
    pie: <PieChart className="w-4 h-4" />,
    scatter: <BarChart3 className="w-4 h-4" />,
    area: <TrendingUp className="w-4 h-4" />,
    radar: <BarChart3 className="w-4 h-4" />,
    gauge: <BarChart3 className="w-4 h-4" />,
    histogram: <BarChart3 className="w-4 h-4" />,
    boxplot: <BarChart3 className="w-4 h-4" />,
    heatmap: <BarChart3 className="w-4 h-4" />,
    treemap: <BarChart3 className="w-4 h-4" />,
    sunburst: <PieChart className="w-4 h-4" />,
    funnel: <BarChart3 className="w-4 h-4" />,
    sankey: <BarChart3 className="w-4 h-4" />,
    graph: <BarChart3 className="w-4 h-4" />,
    tree: <BarChart3 className="w-4 h-4" />,
    parallel: <BarChart3 className="w-4 h-4" />,
    map_china: <BarChart3 className="w-4 h-4" />,
    map_world: <BarChart3 className="w-4 h-4" />,
    map_scatter: <BarChart3 className="w-4 h-4" />,
    polar: <BarChart3 className="w-4 h-4" />,
    candlestick: <BarChart3 className="w-4 h-4" />,
    effectScatter: <BarChart3 className="w-4 h-4" />,
    lines: <TrendingUp className="w-4 h-4" />,
    themeRiver: <TrendingUp className="w-4 h-4" />,
    custom: <BarChart3 className="w-4 h-4" />
};

/**
 * StoredChartCard 组件属性
 */
interface StoredChartCardProps {
    /** 暂存图表信息 */
    chart: StoredChart;
    /** 删除回调 */
    onDelete: () => void;
    /** 点击回调 */
    onClick: () => void;
}

/**
 * 暂存图表卡片组件
 * 显示缩略图、标题和存储时间
 */
export default function StoredChartCard({
    chart,
    onDelete,
    onClick
}: StoredChartCardProps) {
    // 删除确认状态
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

    /**
     * 格式化时间
     */
    const formatTime = (timestamp: number): string => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now.getTime() - date.getTime();

        // 小于1分钟
        if (diff < 60 * 1000) {
            return '刚刚';
        }

        // 小于1小时
        if (diff < 60 * 60 * 1000) {
            return `${Math.floor(diff / (60 * 1000))} 分钟前`;
        }

        // 小于24小时
        if (diff < 24 * 60 * 60 * 1000) {
            return `${Math.floor(diff / (60 * 60 * 1000))} 小时前`;
        }

        // 小于7天
        if (diff < 7 * 24 * 60 * 60 * 1000) {
            return `${Math.floor(diff / (24 * 60 * 60 * 1000))} 天前`;
        }

        // 其他显示日期
        return date.toLocaleDateString('zh-CN', {
            month: 'short',
            day: 'numeric'
        });
    };

    /**
     * 处理删除按钮点击
     */
    const handleDeleteClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        setShowDeleteConfirm(true);
    };

    /**
     * 确认删除
     */
    const handleConfirmDelete = (e: React.MouseEvent) => {
        e.stopPropagation();
        onDelete();
    };

    /**
     * 取消删除
     */
    const handleCancelDelete = (e: React.MouseEvent) => {
        e.stopPropagation();
        setShowDeleteConfirm(false);
    };

    return (
        <motion.div
            onClick={onClick}
            // 卡片动画：悬停上浮
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
            transition={{ duration: 0.1 }}
            className="
                relative p-3 rounded-xl border border-gray-200 bg-white
                hover:border-blue-300 hover:shadow-md
                transition-all duration-100 cursor-pointer overflow-hidden
            "
        >
            {/* 缩略图区域 */}
            <div className="relative w-full h-28 rounded-lg bg-gradient-to-br from-gray-50 to-gray-100 mb-3 overflow-hidden">
                {chart.thumbnail ? (
                    // 有缩略图时显示
                    <img
                        src={chart.thumbnail}
                        alt={chart.name}
                        className="w-full h-full object-cover"
                    />
                ) : (
                    // 无缩略图时显示占位
                    <div className="w-full h-full flex items-center justify-center">
                        <div className="text-gray-300">
                            {CHART_TYPE_ICONS[chart.type] || <ImageIcon className="w-8 h-8" />}
                        </div>
                    </div>
                )}

                {/* 图表类型标签 */}
                <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-white/90 backdrop-blur-sm">
                    <span className="text-[10px] font-medium text-gray-600">
                        {chart.type}
                    </span>
                </div>
            </div>

            {/* 图表信息 */}
            <div className="space-y-1">
                {/* 图表名称 */}
                <h4 className="text-sm font-medium text-gray-800 truncate">
                    {chart.name}
                </h4>

                {/* 存储时间 */}
                <div className="flex items-center gap-1 text-xs text-gray-400">
                    <Clock className="w-3 h-3" />
                    <span>{formatTime(chart.updatedAt)}</span>
                </div>
            </div>

            {/* 删除按钮 */}
            <motion.button
                onClick={handleDeleteClick}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="
                    absolute top-2 right-2 p-1.5 rounded-lg
                    bg-white/80 backdrop-blur-sm
                    text-gray-400 hover:text-red-500 hover:bg-red-50
                    transition-colors duration-100
                "
            >
                <Trash2 className="w-3.5 h-3.5" />
            </motion.button>

            {/* 删除确认弹窗 */}
            <AnimatePresence>
                {showDeleteConfirm && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={(e) => e.stopPropagation()}
                        className="absolute inset-0 bg-white/95 backdrop-blur-sm rounded-xl flex flex-col items-center justify-center p-3"
                    >
                        <p className="text-sm text-gray-700 mb-3 text-center">
                            确定删除此图表？
                        </p>
                        <div className="flex gap-2">
                            <motion.button
                                onClick={handleCancelDelete}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="px-3 py-1.5 text-xs rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50"
                            >
                                取消
                            </motion.button>
                            <motion.button
                                onClick={handleConfirmDelete}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="px-3 py-1.5 text-xs rounded-lg bg-red-500 text-white hover:bg-red-600"
                            >
                                删除
                            </motion.button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}

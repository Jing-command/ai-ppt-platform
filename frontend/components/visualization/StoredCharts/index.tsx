// components/visualization/StoredCharts/index.tsx
// 暂存图表主组件 - 显示所有暂存的图表列表

'use client';

import {useState, useEffect} from 'react';
import {motion, AnimatePresence} from 'framer-motion';
import {FolderOpen, Trash2, RefreshCw} from 'lucide-react';
import type {StoredChart} from '@/types/visualization';
import {ChartStorageManager} from '@/types/visualization';
import StoredChartCard from './StoredChartCard';

/**
 * StoredCharts 组件属性
 */
interface StoredChartsProps {
    /** 图表选择回调 */
    onSelect: (chart: StoredChart) => void;
}

/**
 * 暂存图表主组件
 * 显示所有暂存的图表列表，支持删除和选择操作
 */
export default function StoredCharts({
    onSelect
}: StoredChartsProps) {
    // 暂存图表列表
    const [charts, setCharts] = useState<StoredChart[]>([]);
    // 加载状态
    const [isLoading, setIsLoading] = useState(true);

    /**
     * 加载暂存图表列表
     */
    const loadCharts = () => {
        setIsLoading(true);
        // 模拟加载延迟
        setTimeout(() => {
            const storedCharts = ChartStorageManager.getStoredCharts();
            // 按更新时间倒序排列
            storedCharts.sort((a, b) => b.updatedAt - a.updatedAt);
            setCharts(storedCharts);
            setIsLoading(false);
        }, 300);
    };

    /**
     * 组件挂载时加载图表列表
     */
    useEffect(() => {
        loadCharts();
    }, []);

    /**
     * 处理图表删除
     */
    const handleDelete = (chartId: string) => {
        ChartStorageManager.removeChart(chartId);
        // 更新列表
        setCharts(prev => prev.filter(chart => chart.id !== chartId));
    };

    /**
     * 清空所有图表
     */
    const handleClearAll = () => {
        if (confirm('确定要清空所有暂存的图表吗？此操作不可恢复。')) {
            ChartStorageManager.clearAll();
            setCharts([]);
        }
    };

    /**
     * 处理图表选择
     */
    const handleSelect = (chart: StoredChart) => {
        onSelect(chart);
    };

    return (
        <div className="flex flex-col h-full">
            {/* 头部 */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-white">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center">
                        <FolderOpen className="w-4 h-4 text-orange-600" />
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-gray-800">
                            暂存图表
                        </h3>
                        <p className="text-xs text-gray-500">
                            {charts.length} 个图表
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {/* 刷新按钮 */}
                    <motion.button
                        onClick={loadCharts}
                        disabled={isLoading}
                        whileHover={{scale: 1.05}}
                        whileTap={{scale: 0.95}}
                        className={`
                            p-2 rounded-lg border border-gray-200
                            transition-colors duration-100
                            ${isLoading
            ? 'text-gray-300 cursor-not-allowed'
            : 'text-gray-500 hover:bg-gray-50'
        }
                        `}
                        title="刷新"
                    >
                        <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                    </motion.button>

                    {/* 清空按钮 */}
                    {charts.length > 0 && (
                        <motion.button
                            onClick={handleClearAll}
                            whileHover={{scale: 1.05}}
                            whileTap={{scale: 0.95}}
                            className="
                                p-2 rounded-lg border border-gray-200
                                text-gray-500 hover:bg-red-50 hover:text-red-500 hover:border-red-200
                                transition-colors duration-100
                            "
                            title="清空全部"
                        >
                            <Trash2 className="w-4 h-4" />
                        </motion.button>
                    )}
                </div>
            </div>

            {/* 内容区域 */}
            <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
                <AnimatePresence mode="wait">
                    {/* 加载状态 */}
                    {isLoading && (
                        <motion.div
                            key="loading"
                            initial={{opacity: 0}}
                            animate={{opacity: 1}}
                            exit={{opacity: 0}}
                            className="flex items-center justify-center h-full"
                        >
                            <RefreshCw className="w-6 h-6 text-gray-400 animate-spin" />
                        </motion.div>
                    )}

                    {/* 图表列表 */}
                    {!isLoading && charts.length > 0 && (
                        <motion.div
                            key="list"
                            initial={{opacity: 0}}
                            animate={{opacity: 1}}
                            exit={{opacity: 0}}
                            className="grid grid-cols-2 gap-3"
                        >
                            {charts.map((chart, index) => (
                                <motion.div
                                    key={chart.id}
                                    initial={{opacity: 0, y: 20}}
                                    animate={{opacity: 1, y: 0}}
                                    exit={{opacity: 0, y: -20}}
                                    transition={{duration: 0.1, delay: index * 0.05}}
                                >
                                    <StoredChartCard
                                        chart={chart}
                                        onDelete={() => handleDelete(chart.id)}
                                        onClick={() => handleSelect(chart)}
                                    />
                                </motion.div>
                            ))}
                        </motion.div>
                    )}

                    {/* 空状态 */}
                    {!isLoading && charts.length === 0 && (
                        <motion.div
                            key="empty"
                            initial={{opacity: 0}}
                            animate={{opacity: 1}}
                            exit={{opacity: 0}}
                            className="flex flex-col items-center justify-center h-full text-gray-400"
                        >
                            <FolderOpen className="w-16 h-16 mb-4" />
                            <p className="text-sm font-medium text-gray-500 mb-1">
                                暂无存储的图表
                            </p>
                            <p className="text-xs text-gray-400">
                                创建图表后点击&quot;暂存&quot;按钮保存
                            </p>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}

// components/visualization/AIRecommend/RecommendCard.tsx
// AI 推荐卡片组件 - 显示单个推荐图表的信息

'use client';

import {motion} from 'framer-motion';
import {Sparkles, ArrowRight, TrendingUp, BarChart3, PieChart} from 'lucide-react';
import type {ChartType} from '@/types/visualization';

/**
 * 推荐图表接口
 */
export interface RecommendedChart {
    /** 推荐ID */
    id: string;
    /** 图表类型 */
    chartType: ChartType;
    /** 图表名称 */
    name: string;
    /** 推荐置信度 (0-100) */
    confidence: number;
    /** 推荐理由 */
    reason: string;
    /** 适用场景 */
    suitableFor: string[];
    /** 预览配置 */
    previewOption?: Record<string, unknown>;
}

/**
 * 图表类型图标映射
 */
const CHART_TYPE_ICONS: Record<string, React.ReactNode> = {
    bar: <BarChart3 className="w-5 h-5" />,
    line: <TrendingUp className="w-5 h-5" />,
    pie: <PieChart className="w-5 h-5" />,
    scatter: <BarChart3 className="w-5 h-5" />,
    area: <TrendingUp className="w-5 h-5" />
};

/**
 * RecommendCard 组件属性
 */
interface RecommendCardProps {
    /** 推荐图表信息 */
    chart: RecommendedChart;
    /** 点击回调 */
    onClick: () => void;
}

/**
 * AI 推荐卡片组件
 * 显示图表预览、名称、置信度和推荐理由
 */
export default function RecommendCard({
    chart,
    onClick
}: RecommendCardProps) {
    /**
     * 获取置信度颜色
     */
    const getConfidenceColor = (confidence: number): string => {
        if (confidence >= 80) {
            return 'text-green-600 bg-green-50';
        }
        if (confidence >= 60) {
            return 'text-blue-600 bg-blue-50';
        }
        if (confidence >= 40) {
            return 'text-yellow-600 bg-yellow-50';
        }
        return 'text-gray-600 bg-gray-50';
    };

    /**
     * 获取置信度等级标签
     */
    const getConfidenceLabel = (confidence: number): string => {
        if (confidence >= 80) {
            return '强烈推荐';
        }
        if (confidence >= 60) {
            return '推荐';
        }
        if (confidence >= 40) {
            return '可尝试';
        }
        return '备选';
    };

    return (
        <motion.div
            onClick={onClick}
            // 卡片动画：悬停上浮
            whileHover={{y: -4, scale: 1.01}}
            whileTap={{scale: 0.99}}
            transition={{duration: 0.1}}
            className="
                p-4 rounded-xl border border-gray-200 bg-white
                hover:border-blue-300 hover:shadow-md
                transition-all duration-100 cursor-pointer
            "
        >
            {/* 头部：图标和置信度 */}
            <div className="flex items-start justify-between mb-3">
                {/* 图标和名称 */}
                <div className="flex items-center gap-2">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-100 to-indigo-100 flex items-center justify-center text-blue-600">
                        {CHART_TYPE_ICONS[chart.chartType] || <BarChart3 className="w-5 h-5" />}
                    </div>
                    <div>
                        <h4 className="font-semibold text-sm text-gray-800">
                            {chart.name}
                        </h4>
                        <p className="text-xs text-gray-500">
                            {chart.chartType}
                        </p>
                    </div>
                </div>

                {/* 置信度标签 */}
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(chart.confidence)}`}>
                    {getConfidenceLabel(chart.confidence)}
                </div>
            </div>

            {/* 置信度进度条 */}
            <div className="mb-3">
                <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                    <span>匹配度</span>
                    <span>{chart.confidence}%</span>
                </div>
                <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <motion.div
                        className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full"
                        initial={{width: 0}}
                        animate={{width: `${chart.confidence}%`}}
                        transition={{duration: 0.5, delay: 0.2}}
                    />
                </div>
            </div>

            {/* 推荐理由 */}
            <div className="mb-3">
                <div className="flex items-start gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-blue-500 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-gray-600 leading-relaxed">
                        {chart.reason}
                    </p>
                </div>
            </div>

            {/* 适用场景标签 */}
            {chart.suitableFor.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                    {chart.suitableFor.map((scenario, index) => (
                        <span
                            key={index}
                            className="px-2 py-0.5 text-[10px] rounded bg-gray-100 text-gray-500"
                        >
                            {scenario}
                        </span>
                    ))}
                </div>
            )}

            {/* 选择按钮 */}
            <motion.div
                className="flex items-center justify-end gap-1 text-blue-500"
                whileHover={{x: 2}}
            >
                <span className="text-xs font-medium">选择此图表</span>
                <ArrowRight className="w-3.5 h-3.5" />
            </motion.div>
        </motion.div>
    );
}

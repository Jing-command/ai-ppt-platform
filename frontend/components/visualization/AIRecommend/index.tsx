// components/visualization/AIRecommend/index.tsx
// AI 推荐主组件 - 根据数据智能推荐合适的图表类型

'use client';

import {useState, useEffect, useMemo} from 'react';
import {motion, AnimatePresence} from 'framer-motion';
import {Sparkles, RefreshCw, Brain} from 'lucide-react';
import type {ParsedData, DataField} from '@/types/visualization';
import RecommendCard, {type RecommendedChart} from './RecommendCard';

// 重新导出 RecommendedChart 类型供外部使用
export {type RecommendedChart} from './RecommendCard';

/**
 * AIRecommend 组件属性
 */
interface AIRecommendProps {
    /** 解析后的数据 */
    data: ParsedData;
    /** 图表选择回调 */
    onSelect: (chart: RecommendedChart) => void;
}

/**
 * AI 推荐主组件
 * 根据数据特征智能推荐合适的图表类型
 */
export default function AIRecommend({
    data,
    onSelect
}: AIRecommendProps) {
    // 加载状态
    const [isLoading, setIsLoading] = useState(true);
    // 推荐结果列表
    const [recommendations, setRecommendations] = useState<RecommendedChart[]>([]);

    /**
     * 分析数据特征并生成推荐
     */
    const analyzeDataAndRecommend = useMemo(() => {
        return (fields: DataField[], _totalRows: number): RecommendedChart[] => {
            const recommendations: RecommendedChart[] = [];

            // 统计字段类型
            const numericFields = fields.filter(f => f.type === 'number');
            const stringFields = fields.filter(f => f.type === 'string');
            const dateFields = fields.filter(f => f.type === 'date');

            // 判断数据特征
            const hasNumericData = numericFields.length > 0;
            const hasCategoricalData = stringFields.length > 0;
            const hasTimeSeriesData = dateFields.length > 0;
            const hasMultipleMeasures = numericFields.length >= 2;

            // 推荐柱状图
            if (hasCategoricalData && hasNumericData) {
                const dimensionField = stringFields[0];
                const uniqueCount = dimensionField.uniqueCount;

                recommendations.push({
                    id: 'rec_bar',
                    chartType: 'bar',
                    name: '柱状图',
                    confidence: uniqueCount <= 20 && uniqueCount >= 3 ? 85 : 70,
                    reason: `数据包含 ${stringFields.length} 个分类字段和 ${numericFields.length} 个数值字段，柱状图可以清晰展示各类别的数值对比。`,
                    suitableFor: ['数据对比', '排名展示', '分类统计']
                });
            }

            // 推荐折线图/面积图
            if (hasTimeSeriesData && hasNumericData) {
                recommendations.push({
                    id: 'rec_line',
                    chartType: 'line',
                    name: '折线图',
                    confidence: 90,
                    reason: '数据包含时间字段，折线图非常适合展示时间序列数据的趋势变化。',
                    suitableFor: ['趋势分析', '时间序列', '连续数据']
                });

                recommendations.push({
                    id: 'rec_area',
                    chartType: 'area',
                    name: '面积图',
                    confidence: 75,
                    reason: '面积图在折线图基础上填充区域，更强调数量的累积变化趋势。',
                    suitableFor: ['趋势分析', '累积展示', '区间对比']
                });
            }

            // 推荐饼图
            if (hasCategoricalData && hasNumericData) {
                const dimensionField = stringFields[0];
                const uniqueCount = dimensionField.uniqueCount;

                if (uniqueCount <= 8 && uniqueCount >= 2) {
                    recommendations.push({
                        id: 'rec_pie',
                        chartType: 'pie',
                        name: '饼图',
                        confidence: 80,
                        reason: `分类字段 "${dimensionField.name}" 有 ${uniqueCount} 个唯一值，适合用饼图展示各部分占比。`,
                        suitableFor: ['占比分析', '构成展示', '比例对比']
                    });
                }
            }

            // 推荐散点图
            if (hasMultipleMeasures) {
                recommendations.push({
                    id: 'rec_scatter',
                    chartType: 'scatter',
                    name: '散点图',
                    confidence: 75,
                    reason: `数据包含 ${numericFields.length} 个数值字段，散点图可以展示两个变量之间的相关关系。`,
                    suitableFor: ['相关性分析', '分布展示', '异常检测']
                });
            }

            // 推荐雷达图
            if (numericFields.length >= 3 && numericFields.length <= 8) {
                recommendations.push({
                    id: 'rec_radar',
                    chartType: 'radar',
                    name: '雷达图',
                    confidence: 65,
                    reason: `数据包含 ${numericFields.length} 个数值指标，雷达图适合多维度数据的综合对比分析。`,
                    suitableFor: ['能力评估', '多维对比', '综合评价']
                });
            }

            // 推荐热力图
            if (stringFields.length >= 2 && hasNumericData) {
                recommendations.push({
                    id: 'rec_heatmap',
                    chartType: 'heatmap',
                    name: '热力图',
                    confidence: 60,
                    reason: '数据包含多个分类维度，热力图可以用颜色深浅展示二维数据的分布。',
                    suitableFor: ['相关性矩阵', '时序热力', '密度展示']
                });
            }

            // 按置信度排序
            recommendations.sort((a, b) => b.confidence - a.confidence);

            // 返回前5个推荐
            return recommendations.slice(0, 5);
        };
    }, []);

    /**
     * 模拟 AI 分析过程
     */
    useEffect(() => {
        setIsLoading(true);

        // 模拟加载延迟
        const timer = setTimeout(() => {
            const results = analyzeDataAndRecommend(data.fields, data.totalRows);
            setRecommendations(results);
            setIsLoading(false);
        }, 1500);

        return () => clearTimeout(timer);
    }, [data, analyzeDataAndRecommend]);

    /**
     * 重新分析
     */
    const handleRefresh = () => {
        setIsLoading(true);
        setTimeout(() => {
            const results = analyzeDataAndRecommend(data.fields, data.totalRows);
            setRecommendations(results);
            setIsLoading(false);
        }, 1000);
    };

    return (
        <div className="flex flex-col h-full">
            {/* 头部 */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-white">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
                        <Brain className="w-4 h-4 text-white" />
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-gray-800">
                            AI 智能推荐
                        </h3>
                        <p className="text-xs text-gray-500">
                            基于数据特征分析
                        </p>
                    </div>
                </div>

                {/* 刷新按钮 */}
                <motion.button
                    onClick={handleRefresh}
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
                >
                    <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                </motion.button>
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
                            className="flex flex-col items-center justify-center h-full"
                        >
                            {/* 加载动画 */}
                            <div className="relative mb-4">
                                <div className="w-16 h-16 rounded-full border-4 border-gray-200" />
                                <div className="absolute inset-0 w-16 h-16 rounded-full border-4 border-transparent border-t-blue-500 animate-spin" />
                                <Sparkles className="absolute inset-0 m-auto w-6 h-6 text-blue-500" />
                            </div>

                            {/* 加载文字 */}
                            <p className="text-sm font-medium text-gray-700 mb-1">
                                AI 正在分析数据...
                            </p>
                            <p className="text-xs text-gray-500">
                                识别数据特征，匹配最佳图表
                            </p>
                        </motion.div>
                    )}

                    {/* 推荐结果 */}
                    {!isLoading && recommendations.length > 0 && (
                        <motion.div
                            key="results"
                            initial={{opacity: 0}}
                            animate={{opacity: 1}}
                            exit={{opacity: 0}}
                            className="space-y-3"
                        >
                            {/* 数据概览 */}
                            <div className="p-3 rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100">
                                <p className="text-xs text-gray-600 mb-2">
                                    数据分析结果：
                                </p>
                                <div className="flex flex-wrap gap-2">
                                    <span className="px-2 py-1 text-xs rounded bg-white text-gray-600">
                                        {data.totalRows} 行数据
                                    </span>
                                    <span className="px-2 py-1 text-xs rounded bg-white text-gray-600">
                                        {data.fields.length} 个字段
                                    </span>
                                    <span className="px-2 py-1 text-xs rounded bg-white text-gray-600">
                                        {data.fields.filter(f => f.type === 'number').length} 个数值字段
                                    </span>
                                    <span className="px-2 py-1 text-xs rounded bg-white text-gray-600">
                                        {data.fields.filter(f => f.type === 'string').length} 个文本字段
                                    </span>
                                </div>
                            </div>

                            {/* 推荐卡片列表 */}
                            {recommendations.map((chart, index) => (
                                <motion.div
                                    key={chart.id}
                                    initial={{opacity: 0, y: 20}}
                                    animate={{opacity: 1, y: 0}}
                                    transition={{duration: 0.1, delay: index * 0.1}}
                                >
                                    <RecommendCard
                                        chart={chart}
                                        onClick={() => onSelect(chart)}
                                    />
                                </motion.div>
                            ))}
                        </motion.div>
                    )}

                    {/* 无推荐结果 */}
                    {!isLoading && recommendations.length === 0 && (
                        <motion.div
                            key="empty"
                            initial={{opacity: 0}}
                            animate={{opacity: 1}}
                            exit={{opacity: 0}}
                            className="flex flex-col items-center justify-center h-full text-gray-400"
                        >
                            <Sparkles className="w-12 h-12 mb-3" />
                            <p className="text-sm">暂无推荐</p>
                            <p className="text-xs mt-1">请尝试上传其他数据</p>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}

// components/visualization/ChartPreview/index.tsx
// 图表预览主组件 - 整合字段映射、图表渲染和样式编辑

'use client';

import { useState, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
    Save,
    Download,
    RefreshCw,
    Settings,
    ChevronRight,
    ChevronLeft
} from 'lucide-react';
import type { EChartsOption } from 'echarts';
import type {
    ChartType,
    ParsedData,
    ChartFieldMapping,
    ChartStyleConfig,
    StoredChart,
    ChartStorageManager
} from '@/types/visualization';
import { ChartStorageManager as StorageManager } from '@/types/visualization';
import EChartsRenderer from './EChartsRenderer';
import FieldMapper from './FieldMapper';
import StyleEditor from './StyleEditor';

/**
 * ChartPreview 组件属性
 */
interface ChartPreviewProps {
    /** 图表类型 */
    chartType: ChartType;
    /** 解析后的数据 */
    data: ParsedData;
    /** 图表暂存回调 */
    onStore: () => void;
}

/**
 * 默认样式配置
 */
const DEFAULT_STYLE_CONFIG: ChartStyleConfig = {
    theme: 'light',
    colorPalette: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4'],
    showTitle: true,
    showLegend: true,
    showTooltip: true,
    showGrid: true,
    animation: {
        enabled: true,
        duration: 1000,
        easing: 'cubicOut'
    },
    font: {
        family: 'sans-serif',
        size: 12,
        weight: 'normal'
    }
};

/**
 * 图表预览主组件
 * 整合字段映射、图表渲染和样式编辑功能
 */
export default function ChartPreview({
    chartType,
    data,
    onStore
}: ChartPreviewProps) {
    // 字段映射配置
    const [fieldMapping, setFieldMapping] = useState<ChartFieldMapping>({
        dimension: undefined,
        measures: [],
        colorField: undefined
    });

    // 样式配置
    const [styleConfig, setStyleConfig] = useState<ChartStyleConfig>(DEFAULT_STYLE_CONFIG);

    // 侧边栏展开状态
    const [sidebarOpen, setSidebarOpen] = useState(true);

    // 当前激活的侧边栏标签
    const [activeTab, setActiveTab] = useState<'mapping' | 'style'>('mapping');

    /**
     * 生成 ECharts 配置项
     */
    const chartOption = useMemo((): EChartsOption => {
        // 基础配置
        const option: EChartsOption = {
            // 标题配置
            title: {
                text: (styleConfig.customTheme?.title as string) || '',
                show: styleConfig.showTitle,
                left: 'center',
                textStyle: {
                    fontSize: 16,
                    fontWeight: 'bold'
                }
            },
            // 工具提示配置
            tooltip: {
                show: styleConfig.showTooltip,
                trigger: chartType === 'pie' ? 'item' : 'axis'
            },
            // 图例配置
            legend: {
                show: styleConfig.showLegend,
                bottom: 10
            },
            // 网格配置
            grid: {
                show: styleConfig.showGrid,
                left: '3%',
                right: '4%',
                bottom: '15%',
                top: '10%',
                containLabel: true
            },
            // 颜色配置
            color: styleConfig.colorPalette,
            // 动画配置
            animation: styleConfig.animation.enabled,
            animationDuration: styleConfig.animation.duration
            // animationEasing 由 ECharts 自动处理，不显式设置
        };

        // 根据图表类型和数据映射生成系列配置
        if (chartType === 'pie') {
            // 饼图配置
            const dimensionField = fieldMapping.dimension;
            const measureField = fieldMapping.measures[0];

            if (dimensionField && measureField) {
                const pieData = data.rows.map(row => ({
                    name: String(row[dimensionField] || ''),
                    value: Number(row[measureField]) || 0
                }));

                option.series = [{
                    type: 'pie',
                    radius: ['40%', '70%'],
                    center: ['50%', '50%'],
                    data: pieData,
                    label: {
                        show: true,
                        formatter: '{b}: {d}%'
                    },
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }];
            }
        } else if (chartType === 'bar' || chartType === 'line' || chartType === 'area') {
            // 柱状图/折线图/面积图配置
            const dimensionField = fieldMapping.dimension;
            const measureFields = fieldMapping.measures;

            if (dimensionField && measureFields.length > 0) {
                // 提取维度数据
                const categories = data.rows.map(row => String(row[dimensionField] || ''));

                // X轴配置
                option.xAxis = {
                    type: 'category',
                    data: categories,
                    axisLabel: {
                        rotate: categories.length > 10 ? 45 : 0
                    }
                };

                // Y轴配置
                option.yAxis = {
                    type: 'value'
                };

                // 系列配置
                option.series = measureFields.map(field => {
                    const seriesData = data.rows.map(row => Number(row[field]) || 0);

                    const series: Record<string, unknown> = {
                        name: field,
                        data: seriesData,
                        type: chartType === 'area' ? 'line' : chartType,
                        smooth: true
                    };

                    // 面积图添加填充
                    if (chartType === 'area') {
                        series.areaStyle = {};
                    }

                    return series;
                });
            }
        } else if (chartType === 'scatter') {
            // 散点图配置
            const measureFields = fieldMapping.measures;

            if (measureFields.length >= 2) {
                const scatterData = data.rows.map(row => [
                    Number(row[measureFields[0]]) || 0,
                    Number(row[measureFields[1]]) || 0
                ]);

                option.xAxis = {
                    type: 'value',
                    name: measureFields[0]
                };

                option.yAxis = {
                    type: 'value',
                    name: measureFields[1]
                };

                option.series = [{
                    type: 'scatter',
                    data: scatterData,
                    symbolSize: 10,
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }];
            }
        } else {
            // 其他图表类型的默认配置
            option.xAxis = {
                type: 'category',
                data: data.rows.slice(0, 10).map((_, index) => `类别${index + 1}`)
            };

            option.yAxis = {
                type: 'value'
            };

            option.series = [{
                type: chartType as 'bar',
                data: data.rows.slice(0, 10).map(() => Math.random() * 100)
            }];
        }

        return option;
    }, [chartType, data, fieldMapping, styleConfig]);

    /**
     * 处理图表暂存
     */
    const handleStore = useCallback(() => {
        // 创建存储图表对象
        const storedChart: StoredChart = {
            id: `chart_${Date.now()}`,
            name: (styleConfig.customTheme?.title as string) || `图表 ${new Date().toLocaleDateString()}`,
            type: chartType,
            dataSourceId: data.source.id,
            fieldMapping,
            style: styleConfig,
            option: JSON.stringify(chartOption),
            createdAt: Date.now(),
            updatedAt: Date.now()
        };

        // 保存到本地存储
        StorageManager.addChart(storedChart);

        // 回调通知父组件
        onStore();
    }, [chartType, data, fieldMapping, styleConfig, chartOption, onStore]);

    /**
     * 处理图表导出
     */
    const handleExport = useCallback(() => {
        // TODO: 实现图表导出功能（PNG/SVG）
        console.log('导出图表');
    }, []);

    /**
     * 重置配置
     */
    const handleReset = useCallback(() => {
        setFieldMapping({
            dimension: undefined,
            measures: [],
            colorField: undefined
        });
        setStyleConfig(DEFAULT_STYLE_CONFIG);
    }, []);

    /**
     * 判断配置是否有效
     */
    const isConfigValid = useMemo(() => {
        return fieldMapping.dimension && fieldMapping.measures.length > 0;
    }, [fieldMapping]);

    return (
        <div className="flex h-full">
            {/* 图表渲染区域 */}
            <div className="flex-1 flex flex-col">
                {/* 工具栏 */}
                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-white">
                    <div className="flex items-center gap-2">
                        <h3 className="text-sm font-medium text-gray-800">
                            图表预览
                        </h3>
                        <span className="px-2 py-0.5 text-xs rounded bg-blue-100 text-blue-600">
                            {chartType}
                        </span>
                    </div>

                    <div className="flex items-center gap-2">
                        {/* 重置按钮 */}
                        <motion.button
                            onClick={handleReset}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="
                                flex items-center gap-1 px-3 py-1.5 text-sm
                                rounded-lg border border-gray-200 text-gray-600
                                hover:bg-gray-50 transition-colors
                            "
                        >
                            <RefreshCw className="w-4 h-4" />
                            <span>重置</span>
                        </motion.button>

                        {/* 导出按钮 */}
                        <motion.button
                            onClick={handleExport}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="
                                flex items-center gap-1 px-3 py-1.5 text-sm
                                rounded-lg border border-gray-200 text-gray-600
                                hover:bg-gray-50 transition-colors
                            "
                        >
                            <Download className="w-4 h-4" />
                            <span>导出</span>
                        </motion.button>

                        {/* 暂存按钮 */}
                        <motion.button
                            onClick={handleStore}
                            disabled={!isConfigValid}
                            whileHover={isConfigValid ? { scale: 1.05 } : {}}
                            whileTap={isConfigValid ? { scale: 0.95 } : {}}
                            className={`
                                flex items-center gap-1 px-3 py-1.5 text-sm
                                rounded-lg font-medium transition-colors
                                ${isConfigValid
                                    ? 'bg-blue-500 text-white hover:bg-blue-600'
                                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                }
                            `}
                        >
                            <Save className="w-4 h-4" />
                            <span>暂存</span>
                        </motion.button>
                    </div>
                </div>

                {/* 图表渲染区 */}
                <div className="flex-1 p-4 bg-gray-50">
                    {isConfigValid ? (
                        <EChartsRenderer
                            option={chartOption}
                            className="w-full h-full min-h-[400px] bg-white rounded-lg shadow-sm"
                        />
                    ) : (
                        <div className="flex flex-col items-center justify-center h-full text-gray-400">
                            <Settings className="w-16 h-16 mb-4" />
                            <p className="text-sm">请先配置字段映射</p>
                            <p className="text-xs mt-1">选择维度字段和至少一个度量字段</p>
                        </div>
                    )}
                </div>
            </div>

            {/* 侧边栏 */}
            <motion.div
                animate={{ width: sidebarOpen ? 320 : 48 }}
                transition={{ duration: 0.1 }}
                className="border-l border-gray-200 bg-white flex flex-col"
            >
                {/* 展开/收起按钮 */}
                <motion.button
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="
                        absolute top-1/2 -translate-y-1/2 -translate-x-3
                        w-6 h-6 rounded-full bg-white border border-gray-200
                        flex items-center justify-center shadow-sm
                        hover:bg-gray-50 transition-colors
                    "
                    style={{ zIndex: 10 }}
                >
                    {sidebarOpen ? (
                        <ChevronRight className="w-4 h-4 text-gray-500" />
                    ) : (
                        <ChevronLeft className="w-4 h-4 text-gray-500" />
                    )}
                </motion.button>

                {sidebarOpen && (
                    <div className="flex-1 flex flex-col">
                        {/* 标签切换 */}
                        <div className="flex border-b border-gray-200">
                            <button
                                onClick={() => setActiveTab('mapping')}
                                className={`
                                    flex-1 py-3 text-sm font-medium transition-colors
                                    ${activeTab === 'mapping'
                                        ? 'text-blue-600 border-b-2 border-blue-500'
                                        : 'text-gray-500 hover:text-gray-700'
                                    }
                                `}
                            >
                                字段映射
                            </button>
                            <button
                                onClick={() => setActiveTab('style')}
                                className={`
                                    flex-1 py-3 text-sm font-medium transition-colors
                                    ${activeTab === 'style'
                                        ? 'text-blue-600 border-b-2 border-blue-500'
                                        : 'text-gray-500 hover:text-gray-700'
                                    }
                                `}
                            >
                                样式配置
                            </button>
                        </div>

                        {/* 配置内容 */}
                        <div className="flex-1 overflow-y-auto p-4">
                            {activeTab === 'mapping' ? (
                                <FieldMapper
                                    fields={data.fields}
                                    mapping={fieldMapping}
                                    onChange={setFieldMapping}
                                />
                            ) : (
                                <StyleEditor
                                    config={styleConfig}
                                    onChange={setStyleConfig}
                                />
                            )}
                        </div>
                    </div>
                )}
            </motion.div>
        </div>
    );
}

// components/visualization/ChartPreview/EChartsRenderer.tsx
// ECharts 图表渲染组件 - 封装 echarts-for-react 实现响应式图表

'use client';

import {useRef, useEffect, useCallback} from 'react';
import ReactECharts from 'echarts-for-react';
import type {EChartsOption, ECharts} from 'echarts';

// EChartsReact 组件类型
type EChartsReactInstance = InstanceType<typeof ReactECharts>;

/**
 * EChartsRenderer 组件属性
 */
interface EChartsRendererProps {
    /** ECharts 配置项 */
    option: EChartsOption;
    /** 图表就绪回调 */
    onChartReady?: (instance: ECharts) => void;
    /** 图表点击事件回调 */
    onChartClick?: (params: unknown) => void;
    /** 自定义样式 */
    style?: React.CSSProperties;
    /** 自定义类名 */
    className?: string;
    /** 主题配置 */
    theme?: string | Record<string, unknown>;
    /** 是否显示加载状态 */
    loading?: boolean;
    /** 加载配置 */
    loadingOption?: Record<string, unknown>;
}

/**
 * ECharts 图表渲染组件
 * 封装 echarts-for-react，支持响应式大小和事件处理
 */
export default function EChartsRenderer({
    option,
    onChartReady,
    onChartClick,
    style,
    className,
    theme,
    loading = false,
    loadingOption
}: EChartsRendererProps) {
    // 图表实例引用
    const chartRef = useRef<EChartsReactInstance | null>(null);

    /**
     * 获取 ECharts 实例
     */
    const getInstance = useCallback(() => {
        if (chartRef.current) {
            return chartRef.current.getEchartsInstance();
        }
        return null;
    }, []);

    /**
     * 处理图表就绪事件
     */
    const handleChartReady = useCallback(() => {
        const instance = getInstance();
        if (instance && onChartReady) {
            onChartReady(instance);
        }
    }, [getInstance, onChartReady]);

    /**
     * 处理窗口大小变化，自动调整图表大小
     */
    useEffect(() => {
        const handleResize = () => {
            const instance = getInstance();
            if (instance) {
                instance.resize();
            }
        };

        // 监听窗口大小变化
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, [getInstance]);

    /**
     * 默认加载配置
     */
    const defaultLoadingOption = {
        text: '加载中...',
        color: '#3b82f6',
        textColor: '#6b7280',
        maskColor: 'rgba(255, 255, 255, 0.8)',
        zlevel: 0,
        fontSize: 12,
        showSpinner: true,
        spinnerRadius: 10,
        lineWidth: 2
    };

    /**
     * 默认样式
     */
    const defaultStyle: React.CSSProperties = {
        width: '100%',
        height: '100%',
        minHeight: '300px'
    };

    return (
        <div className={`w-full h-full ${className || ''}`} style={style}>
            <ReactECharts
                ref={chartRef}
                option={option}
                theme={theme}
                style={defaultStyle}
                onChartReady={handleChartReady}
                onEvents={onChartClick ? {click: onChartClick} : undefined}
                showLoading={loading}
                loadingOption={loadingOption || defaultLoadingOption}
                // 响应式配置
                opts={{
                    // 渲染器类型：canvas 或 svg
                    renderer: 'canvas'
                }}
            />
        </div>
    );
}

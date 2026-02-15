/**
 * @fileoverview 数据可视化 API 模块
 * @author Frontend Agent
 * @date 2026-02-15
 * @description 提供图表数据分析、生成、推荐相关的 API 函数
 */

import {apiClient} from './client';
import type {
    ApiChartStyleConfig,
    ApiFieldMapping,
    ChartGenerateRequest,
    ChartGenerateResponse,
    ChartRecommendRequest,
    ChartRecommendResponse,
    DataAnalyzeRequest,
    DataAnalyzeResponse
} from '@/types/visualization';

// ============================================
// API 端点常量
// ============================================

/** 图表模块 API 基础路径 */
const CHARTS_BASE_PATH = '/charts';

// ============================================
// API 函数
// ============================================

/**
 * 分析数据
 * @description 分析数据集，返回字段信息和统计信息
 * @param data - 分析请求参数
 * @returns 数据分析结果
 * @throws {Error} 当请求失败时抛出错误
 * @example
 * const result = await analyzeData({
 *   data: [{ category: 'A', value: 100 }, { category: 'B', value: 200 }],
 *   sampleSize: 100
 * });
 */
export async function analyzeData(data: DataAnalyzeRequest): Promise<DataAnalyzeResponse> {
    // 发送 POST 请求到数据分析端点
    const response = await apiClient.post<DataAnalyzeResponse>(
        `${CHARTS_BASE_PATH}/analyze`,
        data
    );
    // 返回分析结果
    return response.data;
}

/**
 * 生成图表
 * @description 根据图表类型、数据和字段映射生成 ECharts 配置
 * @param data - 图表生成请求参数
 * @returns 图表生成结果，包含 ECharts 配置
 * @throws {Error} 当请求失败时抛出错误
 * @example
 * const result = await generateChart({
 *   chartType: 'bar',
 *   data: [{ category: 'A', value: 100 }, { category: 'B', value: 200 }],
 *   fieldMapping: { xField: 'category', yField: 'value' },
 *   styleConfig: { title: '销售数据', showLegend: true }
 * });
 */
export async function generateChart(data: ChartGenerateRequest): Promise<ChartGenerateResponse> {
    // 发送 POST 请求到图表生成端点
    const response = await apiClient.post<ChartGenerateResponse>(
        `${CHARTS_BASE_PATH}/generate`,
        data
    );
    // 返回生成结果
    return response.data;
}

/**
 * 推荐图表
 * @description 根据数据特征智能推荐适合的图表类型
 * @param data - 图表推荐请求参数
 * @returns 图表推荐结果，包含推荐列表和数据摘要
 * @throws {Error} 当请求失败时抛出错误
 * @example
 * const result = await recommendCharts({
 *   data: [{ category: 'A', value: 100, date: '2024-01-01' }],
 *   context: '销售数据分析',
 *   maxRecommendations: 3
 * });
 */
export async function recommendCharts(data: ChartRecommendRequest): Promise<ChartRecommendResponse> {
    // 发送 POST 请求到图表推荐端点
    const response = await apiClient.post<ChartRecommendResponse>(
        `${CHARTS_BASE_PATH}/recommend`,
        data
    );
    // 返回推荐结果
    return response.data;
}

// ============================================
// 辅助函数
// ============================================

/**
 * 创建字段映射配置
 * @description 快速创建常用的字段映射配置
 * @param xField - X 轴字段名
 * @param yField - Y 轴字段名
 * @param options - 其他可选字段映射
 * @returns 字段映射配置对象
 * @example
 * const mapping = createFieldMapping('category', 'value', { seriesField: 'type' });
 */
export function createFieldMapping(
    xField: string,
    yField: string,
    options?: {
        seriesField?: string;
        valueField?: string;
        nameField?: string;
        sizeField?: string;
    }
): ApiFieldMapping {
    // 构建基础字段映射
    const mapping: ApiFieldMapping = {
        xField,
        yField
    };

    // 如果有额外选项，合并到映射中
    if (options) {
        // 添加系列字段（可选）
        if (options.seriesField) {
            mapping.seriesField = options.seriesField;
        }
        // 添加值字段（可选，用于饼图等）
        if (options.valueField) {
            mapping.valueField = options.valueField;
        }
        // 添加名称字段（可选）
        if (options.nameField) {
            mapping.nameField = options.nameField;
        }
        // 添加大小字段（可选，用于散点图）
        if (options.sizeField) {
            mapping.sizeField = options.sizeField;
        }
    }

    // 返回完整的字段映射配置
    return mapping;
}

/**
 * 创建图表样式配置
 * @description 快速创建图表样式配置
 * @param title - 图表标题
 * @param options - 其他可选样式配置
 * @returns 样式配置对象
 * @example
 * const style = createChartStyle('销售数据', { showLegend: true, theme: 'dark' });
 */
export function createChartStyle(
    title: string,
    options?: {
        subtitle?: string;
        width?: number;
        height?: number;
        colorPalette?: string[];
        showLegend?: boolean;
        showTooltip?: boolean;
        showGrid?: boolean;
        animation?: boolean;
        theme?: string;
    }
): ApiChartStyleConfig {
    // 构建基础样式配置
    const style: ApiChartStyleConfig = {
        title,
        // 设置默认值
        showLegend: true,
        showTooltip: true,
        showGrid: true,
        animation: true,
        theme: 'default'
    };

    // 如果有额外选项，合并到样式中
    if (options) {
        // 添加副标题（可选）
        if (options.subtitle !== undefined) {
            style.subtitle = options.subtitle;
        }
        // 添加宽度（可选）
        if (options.width !== undefined) {
            style.width = options.width;
        }
        // 添加高度（可选）
        if (options.height !== undefined) {
            style.height = options.height;
        }
        // 添加颜色调色板（可选）
        if (options.colorPalette) {
            style.colorPalette = options.colorPalette;
        }
        // 覆盖图例显示设置
        if (options.showLegend !== undefined) {
            style.showLegend = options.showLegend;
        }
        // 覆盖提示框显示设置
        if (options.showTooltip !== undefined) {
            style.showTooltip = options.showTooltip;
        }
        // 覆盖网格显示设置
        if (options.showGrid !== undefined) {
            style.showGrid = options.showGrid;
        }
        // 覆盖动画设置
        if (options.animation !== undefined) {
            style.animation = options.animation;
        }
        // 覆盖主题设置
        if (options.theme !== undefined) {
            style.theme = options.theme;
        }
    }

    // 返回完整的样式配置
    return style;
}

/**
 * 验证数据是否适合生成图表
 * @description 检查数据是否满足生成图表的基本要求
 * @param data - 待验证的数据数组
 * @returns 验证结果，包含是否有效和错误信息
 * @example
 * const result = validateChartData([{ category: 'A', value: 100 }]);
 * if (!result.valid) {
 *   console.error(result.message);
 * }
 */
export function validateChartData(data: Record<string, unknown>[]): {
    valid: boolean;
    message?: string;
} {
    // 检查数据是否为空
    if (!data || data.length === 0) {
        return {
            valid: false,
            message: '数据不能为空'
        };
    }

    // 检查数据是否为数组
    if (!Array.isArray(data)) {
        return {
            valid: false,
            message: '数据必须是数组格式'
        };
    }

    // 检查第一条数据是否为对象
    if (typeof data[0] !== 'object' || data[0] === null) {
        return {
            valid: false,
            message: '数据项必须是对象格式'
        };
    }

    // 获取第一条数据的字段数量
    const fieldCount = Object.keys(data[0]).length;

    // 检查是否有足够的字段
    if (fieldCount < 2) {
        return {
            valid: false,
            message: '数据至少需要包含两个字段'
        };
    }

    // 验证通过
    return {valid: true};
}

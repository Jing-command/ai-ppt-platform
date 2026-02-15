/**
 * 数据可视化模块类型定义
 * @module types/visualization
 * @description 定义图表类型、数据源、配置等相关类型
 */

import type { EChartsOption } from 'echarts';

// ============================================
// 图表分类类型
// ============================================

/**
 * 图表分类枚举
 * @description 用于对图表进行大类划分
 */
export type ChartCategory =
    | 'basic'        // 基础图表
    | 'statistical'  // 统计图表
    | 'map'          // 地图图表
    | 'relation'     // 关系图表
    | 'special';     // 特殊图表

/**
 * 图表类型枚举
 * @description 支持的所有图表类型
 */
export type ChartType =
    // 基础图表
    | 'bar'                    // 柱状图
    | 'line'                   // 折线图
    | 'pie'                    // 饼图
    | 'scatter'                // 散点图
    | 'area'                   // 面积图
    | 'radar'                  // 雷达图
    | 'gauge'                  // 仪表盘
    // 统计图表
    | 'histogram'              // 直方图
    | 'boxplot'                // 箱线图
    | 'heatmap'                // 热力图
    | 'treemap'                // 矩形树图
    | 'sunburst'               // 旭日图
    | 'funnel'                 // 漏斗图
    | 'sankey'                 // 桑基图
    // 关系图表
    | 'graph'                  // 关系图
    | 'tree'                   // 树图
    | 'parallel'               // 平行坐标系
    // 地图图表
    | 'map_china'              // 中国地图
    | 'map_world'              // 世界地图
    | 'map_scatter'            // 地图散点
    // 特殊图表
    | 'polar'                  // 极坐标图
    | 'candlestick'            // K线图
    | 'effectScatter'          // 涟漪散点图
    | 'lines'                  // 线图
    | 'themeRiver'             // 主题河流图
    | 'custom';                // 自定义图表

// ============================================
// 图表配置接口
// ============================================

/**
 * 图表配置接口
 * @description 定义单个图表的完整配置信息
 */
export interface ChartConfig {
    /** 图表唯一标识 */
    id: string;
    /** 图表类型 */
    type: ChartType;
    /** 图表分类 */
    category: ChartCategory;
    /** 图表中文名称 */
    name: string;
    /** 图表英文名称 */
    nameEn: string;
    /** 图标标识（Lucide图标名称） */
    icon: string;
    /** 图表描述 */
    description: string;
    /** 使用场景列表 */
    useCases: string[];
    /** 数据要求说明 */
    dataRequirements: string[];
    /** ECharts默认配置项 */
    defaultOption: EChartsOption;
}

// ============================================
// 数据源相关类型
// ============================================

/**
 * 数据源类型枚举
 * @description 定义数据来源的类型
 */
export type DataSourceType =
    | 'file'       // 文件上传
    | 'database'   // 数据库连接
    | 'api'        // API接口
    | 'manual';    // 手动输入

/**
 * 文件类型枚举
 * @description 支持上传的文件格式
 */
export type FileType =
    | 'xlsx'   // Excel文件
    | 'xls'    // 旧版Excel文件
    | 'csv'    // CSV文件
    | 'json';  // JSON文件

/**
 * 数据字段类型枚举
 * @description 字段的数据类型分类
 */
export type FieldDataType =
    | 'string'   // 字符串
    | 'number'   // 数值
    | 'boolean'  // 布尔值
    | 'date'     // 日期
    | 'object';  // 对象

/**
 * 数据字段接口
 * @description 描述数据集中的单个字段信息
 */
export interface DataField {
    /** 字段名称 */
    name: string;
    /** 字段类型 */
    type: FieldDataType;
    /** 字段在数据中的索引位置 */
    index: number;
    /** 是否为空值 */
    nullable: boolean;
    /** 唯一值数量（用于判断是否适合作为维度） */
    uniqueCount: number;
    /** 示例值列表 */
    sampleValues: unknown[];
    /** 统计信息（数值类型字段） */
    stats?: {
        min: number;
        max: number;
        mean: number;
        median: number;
        sum: number;
    };
}

/**
 * 数据源接口
 * @description 定义数据源的完整信息
 */
export interface DataSource {
    /** 数据源唯一标识 */
    id: string;
    /** 数据源名称 */
    name: string;
    /** 数据源类型 */
    type: DataSourceType;
    /** 文件类型（仅文件类型数据源） */
    fileType?: FileType;
    /** 文件大小（字节） */
    fileSize?: number;
    /** 创建时间 */
    createdAt: Date;
    /** 更新时间 */
    updatedAt: Date;
    /** 原始文件名 */
    originalFileName?: string;
}

/**
 * 解析后的数据接口
 * @description 文件解析后的数据结构
 */
export interface ParsedData {
    /** 数据源信息 */
    source: DataSource;
    /** 字段定义列表 */
    fields: DataField[];
    /** 数据行数组 */
    rows: Record<string, unknown>[];
    /** 总行数 */
    totalRows: number;
    /** 解析时间 */
    parsedAt: Date;
    /** 解析错误信息（如有） */
    errors?: string[];
}

// ============================================
// 图表字段映射接口
// ============================================

/**
 * 图表字段映射接口
 * @description 定义数据字段与图表维度的映射关系
 */
export interface ChartFieldMapping {
    /** X轴/维度字段名称 */
    dimension?: string;
    /** Y轴/度量字段名称列表 */
    measures: string[];
    /** 颜色分组字段 */
    colorField?: string;
    /** 大小映射字段（气泡图等） */
    sizeField?: string;
    /** 系列字段 */
    seriesField?: string;
    /** 地理位置字段（地图图表） */
    geoField?: string;
    /** 时间字段（时间序列图表） */
    timeField?: string;
}

// ============================================
// 图表样式配置接口
// ============================================

/**
 * 图表样式配置接口
 * @description 定义图表的视觉样式设置
 */
export interface ChartStyleConfig {
    /** 主题名称 */
    theme: 'light' | 'dark' | 'custom';
    /** 自定义主题配置 */
    customTheme?: Record<string, unknown>;
    /** 调色板 */
    colorPalette: string[];
    /** 背景色 */
    backgroundColor?: string;
    /** 是否显示标题 */
    showTitle: boolean;
    /** 是否显示图例 */
    showLegend: boolean;
    /** 是否显示工具栏 */
    showTooltip: boolean;
    /** 是否显示网格线 */
    showGrid: boolean;
    /** 动画配置 */
    animation: {
        enabled: boolean;
        duration: number;
        easing: string;
    };
    /** 字体配置 */
    font: {
        family: string;
        size: number;
        weight: string;
    };
}

// ============================================
// 图表实例接口
// ============================================

/**
 * 图表实例接口
 * @description 定义运行时图表实例的完整状态
 */
export interface ChartInstance {
    /** 实例唯一标识 */
    id: string;
    /** 图表配置 */
    config: ChartConfig;
    /** 数据源ID */
    dataSourceId: string;
    /** 字段映射 */
    fieldMapping: ChartFieldMapping;
    /** 样式配置 */
    style: ChartStyleConfig;
    /** 当前ECharts配置 */
    option: EChartsOption;
    /** 创建时间 */
    createdAt: Date;
    /** 更新时间 */
    updatedAt: Date;
    /** 是否已保存 */
    saved: boolean;
}

// ============================================
// 存储相关类型
// ============================================

/**
 * 存储的图表接口
 * @description 用于持久化存储的图表数据结构
 */
export interface StoredChart {
    /** 图表唯一标识 */
    id: string;
    /** 图表名称 */
    name: string;
    /** 图表类型 */
    type: ChartType;
    /** 关联的数据源ID */
    dataSourceId: string;
    /** 字段映射配置 */
    fieldMapping: ChartFieldMapping;
    /** 样式配置 */
    style: ChartStyleConfig;
    /** ECharts配置（JSON序列化） */
    option: string;
    /** 创建时间戳 */
    createdAt: number;
    /** 更新时间戳 */
    updatedAt: number;
    /** 缩略图Base64 */
    thumbnail?: string;
}

/**
 * 本地存储键名常量
 * @description 定义所有本地存储使用的键名
 */
export const STORAGE_KEYS = {
    /** 存储的图表列表键名 */
    STORED_CHARTS: 'ai_ppt_stored_charts',
    /** 数据源列表键名 */
    DATA_SOURCES: 'ai_ppt_data_sources',
    /** 图表配置缓存键名 */
    CHART_CONFIG_CACHE: 'ai_ppt_chart_config_cache',
    /** 用户偏好设置键名 */
    USER_PREFERENCES: 'ai_ppt_user_preferences',
    /** 最近使用的数据源键名 */
    RECENT_DATA_SOURCES: 'ai_ppt_recent_data_sources'
} as const;

// ============================================
// 图表存储管理类
// ============================================

/**
 * 图表存储管理类
 * @description 提供图表数据的本地存储管理功能
 */
export class ChartStorageManager {
    /**
     * 获取所有存储的图表
     * @returns 存储的图表数组
     */
    static getStoredCharts(): StoredChart[] {
        // 检查运行环境
        if (typeof window === 'undefined') {
            return [];
        }

        try {
            // 从本地存储获取数据
            const data = localStorage.getItem(STORAGE_KEYS.STORED_CHARTS);
            // 解析JSON数据，无数据则返回空数组
            return data ? JSON.parse(data) : [];
        } catch (error) {
            // 解析失败时输出警告并返回空数组
            console.warn('读取存储的图表失败:', error);
            return [];
        }
    }

    /**
     * 添加新图表到存储
     * @param chart - 要存储的图表数据
     * @returns 是否添加成功
     */
    static addChart(chart: StoredChart): boolean {
        // 检查运行环境
        if (typeof window === 'undefined') {
            return false;
        }

        try {
            // 获取现有图表列表
            const charts = this.getStoredCharts();
            // 添加新图表到列表
            charts.push(chart);
            // 保存到本地存储
            localStorage.setItem(STORAGE_KEYS.STORED_CHARTS, JSON.stringify(charts));
            return true;
        } catch (error) {
            // 存储失败时输出警告
            console.warn('存储图表失败:', error);
            return false;
        }
    }

    /**
     * 从存储中移除图表
     * @param chartId - 要移除的图表ID
     * @returns 是否移除成功
     */
    static removeChart(chartId: string): boolean {
        // 检查运行环境
        if (typeof window === 'undefined') {
            return false;
        }

        try {
            // 获取现有图表列表
            const charts = this.getStoredCharts();
            // 过滤掉要删除的图表
            const filteredCharts = charts.filter(chart => chart.id !== chartId);
            // 保存过滤后的列表
            localStorage.setItem(STORAGE_KEYS.STORED_CHARTS, JSON.stringify(filteredCharts));
            return true;
        } catch (error) {
            // 删除失败时输出警告
            console.warn('删除图表失败:', error);
            return false;
        }
    }

    /**
     * 更新存储中的图表
     * @param chartId - 要更新的图表ID
     * @param updates - 要更新的字段
     * @returns 是否更新成功
     */
    static updateChart(chartId: string, updates: Partial<StoredChart>): boolean {
        // 检查运行环境
        if (typeof window === 'undefined') {
            return false;
        }

        try {
            // 获取现有图表列表
            const charts = this.getStoredCharts();
            // 查找并更新指定图表
            const updatedCharts = charts.map(chart => {
                if (chart.id === chartId) {
                    return {
                        ...chart,
                        ...updates,
                        updatedAt: Date.now()
                    };
                }
                return chart;
            });
            // 保存更新后的列表
            localStorage.setItem(STORAGE_KEYS.STORED_CHARTS, JSON.stringify(updatedCharts));
            return true;
        } catch (error) {
            // 更新失败时输出警告
            console.warn('更新图表失败:', error);
            return false;
        }
    }

    /**
     * 清空所有存储的图表
     * @returns 是否清空成功
     */
    static clearAll(): boolean {
        // 检查运行环境
        if (typeof window === 'undefined') {
            return false;
        }

        try {
            // 移除存储项
            localStorage.removeItem(STORAGE_KEYS.STORED_CHARTS);
            return true;
        } catch (error) {
            // 清空失败时输出警告
            console.warn('清空图表存储失败:', error);
            return false;
        }
    }

    /**
     * 根据ID获取单个图表
     * @param chartId - 图表ID
     * @returns 图表数据或undefined
     */
    static getChartById(chartId: string): StoredChart | undefined {
        // 获取所有图表并查找指定ID
        const charts = this.getStoredCharts();
        return charts.find(chart => chart.id === chartId);
    }

    /**
     * 根据数据源ID获取关联的图表
     * @param dataSourceId - 数据源ID
     * @returns 关联的图表数组
     */
    static getChartsByDataSource(dataSourceId: string): StoredChart[] {
        // 获取所有图表并过滤指定数据源
        const charts = this.getStoredCharts();
        return charts.filter(chart => chart.dataSourceId === dataSourceId);
    }
}

// ============================================
// API 请求/响应类型定义
// ============================================

/**
 * 图表类型枚举（API 使用）
 * @description API 支持的图表类型
 */
export type ApiChartType =
    | 'bar'        // 柱状图
    | 'line'       // 折线图
    | 'pie'        // 饼图
    | 'scatter'    // 散点图
    | 'area'       // 面积图
    | 'radar'      // 雷达图
    | 'funnel'     // 漏斗图
    | 'gauge'      // 仪表盘
    | 'treemap'    // 矩形树图
    | 'sunburst';  // 旭日图

/**
 * 字段类型枚举（API 使用）
 * @description 字段在图表中的角色类型
 */
export type ApiFieldType = 'dimension' | 'measure';

/**
 * 数据字段类型枚举（API 使用）
 * @description 字段的数据类型
 */
export type ApiDataFieldType = 'string' | 'number' | 'date' | 'boolean';

/**
 * 数据字段信息接口（API 响应）
 * @description API 返回的字段分析信息
 */
export interface ApiDataFieldInfo {
    /** 字段名称 */
    name: string;
    /** 字段类型：维度/度量 */
    fieldType: ApiFieldType;
    /** 数据类型：string/number/date/boolean */
    dataType: ApiDataFieldType;
    /** 唯一值数量 */
    uniqueCount: number;
    /** 空值数量 */
    nullCount: number;
    /** 样本值列表 */
    sampleValues?: unknown[];
    /** 最小值（数值字段） */
    minValue?: number;
    /** 最大值（数值字段） */
    maxValue?: number;
    /** 平均值（数值字段） */
    avgValue?: number;
}

/**
 * 数据分析请求接口
 * @description 请求数据分析接口的参数
 */
export interface DataAnalyzeRequest {
    /** 数据列表 */
    data: Record<string, unknown>[];
    /** 采样大小，默认 100 */
    sampleSize?: number;
}

/**
 * 数据分析响应接口
 * @description 数据分析接口返回的结果
 */
export interface DataAnalyzeResponse {
    /** 总行数 */
    totalRows: number;
    /** 总列数 */
    totalColumns: number;
    /** 字段信息列表 */
    fields: ApiDataFieldInfo[];
    /** 数据建议列表 */
    suggestions?: string[];
}

/**
 * 字段映射接口（API 使用）
 * @description 定义数据字段与图表维度的映射关系
 */
export interface ApiFieldMapping {
    /** X 轴字段 */
    xField?: string;
    /** Y 轴字段 */
    yField?: string;
    /** 系列字段 */
    seriesField?: string;
    /** 值字段（饼图等） */
    valueField?: string;
    /** 名称字段 */
    nameField?: string;
    /** 大小字段（散点图） */
    sizeField?: string;
}

/**
 * 图表样式配置接口（API 使用）
 * @description API 请求中的样式配置
 */
export interface ApiChartStyleConfig {
    /** 图表标题 */
    title?: string;
    /** 图表副标题 */
    subtitle?: string;
    /** 图表宽度 */
    width?: number;
    /** 图表高度 */
    height?: number;
    /** 颜色调色板 */
    colorPalette?: string[];
    /** 是否显示图例，默认 true */
    showLegend?: boolean;
    /** 是否显示提示框，默认 true */
    showTooltip?: boolean;
    /** 是否显示网格，默认 true */
    showGrid?: boolean;
    /** 是否启用动画，默认 true */
    animation?: boolean;
    /** 主题名称，默认 default */
    theme?: string;
}

/**
 * 图表生成请求接口
 * @description 请求图表生成接口的参数
 */
export interface ChartGenerateRequest {
    /** 图表类型 */
    chartType: ApiChartType;
    /** 数据列表 */
    data: Record<string, unknown>[];
    /** 字段映射配置 */
    fieldMapping: ApiFieldMapping;
    /** 样式配置 */
    styleConfig?: ApiChartStyleConfig;
}

/**
 * 图表生成响应接口
 * @description 图表生成接口返回的结果
 */
export interface ChartGenerateResponse {
    /** 图表类型 */
    chartType: ApiChartType;
    /** ECharts 配置对象 */
    echartsOption: Record<string, unknown>;
    /** 数据条数 */
    dataCount: number;
    /** 生成时间，ISO 8601 格式 */
    generatedAt: string;
}

/**
 * 推荐图表接口
 * @description 单个推荐图表的信息
 */
export interface RecommendedChart {
    /** 推荐图表类型 */
    chartType: ApiChartType;
    /** 推荐置信度 (0.0 - 1.0) */
    confidence: number;
    /** 推荐理由 */
    reason: string;
    /** 建议的字段映射 */
    fieldMapping: ApiFieldMapping;
    /** 预览配置（可选） */
    previewOption?: Record<string, unknown>;
}

/**
 * 图表推荐请求接口
 * @description 请求图表推荐接口的参数
 */
export interface ChartRecommendRequest {
    /** 数据列表 */
    data: Record<string, unknown>[];
    /** 上下文描述（可选） */
    context?: string;
    /** 最大推荐数量，范围 1-5，默认 3 */
    maxRecommendations?: number;
}

/**
 * 图表推荐响应接口
 * @description 图表推荐接口返回的结果
 */
export interface ChartRecommendResponse {
    /** 推荐图表列表 */
    recommendations: RecommendedChart[];
    /** 数据摘要 */
    dataSummary: string;
    /** 分析时间，ISO 8601 格式 */
    analyzedAt: string;
}
